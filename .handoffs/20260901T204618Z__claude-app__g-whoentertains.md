# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Fan-out shipped and rolled back in 4 min — code proven correct, phoebus node unfit as origin (107s initialize); nougen-fleet-mcp is back to the 20:21Z bundle
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T20:46:18.920Z

---
Following legs `20260901T202643Z` (patch built) — GM authorized, so I added the token and deployed. **Deployed 20:41:25Z, rolled back 20:45:06Z.** `nougen-fleet-mcp` is currently running the same bundle it ran at 20:21Z. All 32 bindings intact in both directions. If you deploy this script, you are deploying onto the pre-fan-out code, unchanged.

## What worked — proven live, not theorized
The patch ran correctly. Hits came back tagged `source_node:"blade"`, and the partial-failure path fired exactly as designed:

```
"fanout": {"blade":"ok","phoebus":"The operation was aborted due to timeout"}, "complete": false
```

It disclosed that it was returning half the fleet instead of passing blade-only off as complete. That was the most important line in the patch and it's the line that earned its keep.

## Why it came back out
**phoebus's node cannot serve as an origin.** Timed direct against `127.0.0.1:4444` — no tunnel, no Cloudflare — a bare MCP `initialize` handshake, not a query, took **107 seconds**. Default `SHARD_HTTP_TIMEOUT_MS` is 45s, so phoebus could never answer inside any sane budget.

## The lesson worth keeping, separate from phoebus being slow
`shardCallFanout` used `Promise.allSettled`, which resolves only when *every* origin settles. A dead-slow peer therefore doesn't merely fail to contribute — **it taxes every read fleet-wide with its full timeout before the fast origin's answer can return.** blade answered in single-digit seconds and the caller still waited ~45s.

A fan-out that waits on all origins inherits the *slowest* origin's failure budget. Same shape as shard 29796's "timeout budgets must shrink as you go inward." Any retry of this feature needs a short peer-specific budget (the failover Worker's `HEALTH_TIMEOUT_MS=8s` pattern) or a race that returns the primary as soon as it lands — **fixed before redeploying, regardless of whether phoebus gets faster.**

## State left behind
- `PHOEBUS_TOKEN` secret stays on the Worker (added via the dedicated `/secrets` endpoint — additive, did not disturb the other 7 secrets, unlike the settings PATCH that drops them). Unused while fan-out is out, already in place for the retry.
- Validated patch preserved; base bundle backed up at `~/.nougen/worker-backups/nougen-fleet-mcp.20260901T202135Z.LIVE.{js,multipart}`.
- Rollback was *proven*, per your P1 gate: content-only PUT with `keep_bindings`, guarded on `modified_on` so a concurrent lane deploy aborts rather than gets reverted, bindings re-read after each deploy because the PUT response is not evidence. Total exposure 3m41s.

## Open question for whoever picks it up
Why does phoebus's node take 107s on a bare `initialize`? Up since Sat 2026-08-29, serving effectively no traffic (its hostnames were Worker-shadowed — leg `20260901T193630Z`). Candidates before assuming a code fault: a wedged long-lived process like blade's 6,143s-CPU incident (shard 29796), per-call federation fan-out, or MCP session setup touching the 108k-shard vault. A node restart is the cheap first probe — the vault is on real disk, and phoebus's `persistent_storage:false` is a HuggingFace mount check that is always false on macOS, not data loss.

**Done when**: phoebus's node latency is diagnosed and the peer-budget fix is in, then the preserved patch redeploys unchanged apart from that fix.
