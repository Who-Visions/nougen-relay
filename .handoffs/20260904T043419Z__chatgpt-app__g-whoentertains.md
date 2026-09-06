# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Deep diagnosis: current 1033 tunnel loss plus Phoebus federation deadline bug
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T04:34:19.626Z

---
Deep probe from chatgpt-app, 2026-09-04 ~04:34Z. This supersedes the generic restore ticket with a layered diagnosis.

## Layer 0: Phoebus compute is alive
A live `kaedra_ask` to Phoebus succeeded while shard transport was failing. Kaedra explicitly confirmed it cannot directly inspect external shard/MCP health unless those signals are piped into its runtime. Therefore P-LANE-01 / Kaedra reachability proves only the local inference plane, not the shard transport plane.

## Layer 1: CURRENT immediate failure is Cloudflare Tunnel, proven by live write probe
`shards_status` from chatgpt-app: `up=false, health_up=false, mcp_up=false, configured=true`.
Then a real `shards_capture` diagnostic write returned exactly:

`Error: gateway 530: error code: 1033`

Cloudflare's current official docs define 1033 as a Cloudflare Tunnel error where Cloudflare cannot find a healthy `cloudflared` instance connected to its network. That is categorically different from a 502, which would mean the tunnel is connected but the local origin is unreachable.

This is especially important because relay `20260904T042257Z` measured only ~12 minutes earlier on Phoebus:
* cloudflared running pid 61573
* node pid 90428 listening :4444
* local /health 200 in 0.025s
* /mcp tools/list 200 in 0.42s
* public https://shards.nougenai.com/health 200 in 0.21s

So the system changed state between that probe and this write probe. The strongest current hypothesis is tunnel loss/flap or connector health loss, NOT a dead Kaedra process and NOT necessarily a dead shard node. Verify with `cloudflared tunnel list`, connector status, cloudflared logs, edge connection count, network/DNS/QUIC/TCP errors, then re-establish the tunnel. Do not restart unrelated Kaedra inference to fix a 1033.

Official Cloudflare source used to classify the error: https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-1xxx-errors/error-1033/

## Layer 2: AFTER tunnel restoration, Phoebus still has a separate federation deadline defect
Relay `20260904T042257Z` already proved Phoebus is omitted from fanout because `/search` is ~20.41s cold and ~5.59s warm against a 6000ms peer grace. Federated queries therefore return `phoebus: peer exceeded 6000ms grace after primary`, blade-only, `complete:false`.

Root cause already traced: live tree `The Observatory/NouGen/nougenshards`, branch `node-tool-concurrency`, is 24 commits behind `origin/main` and missing PR #185 / commit `134a85b`, the startup vector-cache warmup written for this exact first-recall deadline symptom.

## Layer 3: deployment cutover has two traps
The staged deployment clone `~/.nougen/src/nougenshards` is on fresh main but cannot just be pointed live:
1. no `.venv`, while `bin/ngs-node.sh` executes `./.venv/bin/python app.py`
2. `app.py` uses `sys.path.append`, so the live checkout's editable `.pth` can win and import the OLD `nougen_shards` package even when the new clone's app.py starts. Fix import isolation or build a clean venv and verify `nougen_shards.__file__` before declaring cutover successful.

Also do not blindly switch the old live checkout to main because the Kaedra gateway process has been running from that same tree for ~3 days. Isolate the shard node deployment from Kaedra before swapping code.

## Layer 4: `.vault` false-success mechanism is separately fixed
Relay `20260904T042746Z` / PR #207 reproduced and fixed the CWD-relative `.vault` autodetect that stranded 8,289 rows. `shards_capture` itself was not losing writes. It was writing to the wrong selected store. PR #207 makes repo-local vault opt-in, resolves paths absolute, and warns on non-default vaults. 62 existing tests + 6 new tests passed. Merge/deploy this independently of the Phoebus timeout repair.

## Recommended execution order
1. Restore Cloudflare Tunnel first. A live 1033 means no external shard route exists from chatgpt-app regardless of node code.
2. Prove external `/health`, MCP tools/list, and one `shards_capture` from chatgpt-app.
3. Prove recall of that exact test shard.
4. Fix Phoebus deployment isolation: fresh venv, deterministic import path, verify loaded package path.
5. Deploy main containing #185 startup warmup and PR #207 vault safety.
6. Re-measure cold and warm `/search`. Do not accept a warm-only pass. Cold first recall must beat the peer deadline with margin.
7. If cold recall still cannot reliably beat 6s, either optimize startup further or temporarily increase peer grace. Do not use periodic warm pings as the durable fix.
8. Run a federated recall and require `phoebus` present with `complete:true`.
9. Restart shard node and tunnel, then rerun cold capture + recall + federation to prove restart survival.
10. Preserve no-focus-stealing background launch behavior for cloudflared/node/MCP processes.

## Done means all planes independently green
* Kaedra local inference green
* Cloudflare tunnel Active/Healthy
* external gateway health green
* MCP health/tools green
* capture green from chatgpt-app
* exact shard recall green
* Phoebus fanout included on COLD first query, not just warm
* `complete:true`
* deterministic vault path
* new code actually imported from intended deployment path
* restart proof passes without terminal windows stealing focus

Do not collapse these into one 'Phoebus up/down' boolean. They are separate compute, tunnel, gateway, storage, and federation planes.
