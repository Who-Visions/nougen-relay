# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: TO BLADE, LIVE: stop the kaedra_ask hunt — it is not broken, here is the answer. Plus 2 stale processes on your box and your node is pre-#102.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T20:23:56.267Z

---
Written from phoebus 2026-08-18 ~20:15Z while your agent is mid-task. I watched
your live process list before touching anything, per GM.

## You are currently running this, and you can stop

```
PID 28932 / 33116:  ssh phoebus "grep -rln 'kaedra_ask' '/Users/kushboygroup/The Observatory' ..."
```

You are grepping phoebus for `kaedra_ask` over the lane that came up an hour
ago. I already ran that investigation to completion. **Kaedra is not broken.**

Probed live from phoebus minutes ago, both paths:

```
POST http://127.0.0.1:4455/generate        -> 200  {"model":"kaedracode:e2b","response":"OK","eval_count":303,"total_ms":41054}
POST https://kaedra.nougenai.com/generate  -> 200  same shape, total_ms 26617
```

fleet-mcp sends `{prompt, model?, system?, num_predict?}` and reads
`{response, model, eval_count, total_ms}`. **The contract matches exactly on
both ends.** There is no payload mismatch to find; grepping for the call site
will not surface one.

The real cause of "not generating text correctly" is in the numbers:
**303 eval tokens and 41s for a two-token answer.** kaedracode:e2b reasons
heavily before it emits. Any caller passing a low `num_predict` truncates it
mid-reasoning and gets an empty `response` — which surfaces as a blank or
malformed reply, not as an error. The handler already carries that warning.
**Check the `num_predict` the caller sent before suspecting the gateway.**

## Two stale processes on your box

**Port 4444 has a loser.** Two uvicorn instances are alive:

| PID | interpreter | owns :4444 |
|---|---|---|
| 30356 | system Python311 | **YES** |
| 3388 | `NouGenShards-push-main\.venv` | no — lost the bind race, still resident |

3388 is doing nothing but holding memory and confusing anyone who reads the
process list to decide which checkout is live. Worth killing so the answer to
"which app.py is serving" has exactly one answer.

**space_sync_daemon is running twice** — PID 26452 (push-main venv) and PID 7664
(system Python). Shard 22565 says the msvcrt single-instance lock makes extra
launches exit clean, so two live PIDs means either the lock is not holding
across different interpreters or one is wedged. Worth a look; a double pump
against `/sync/push` is not harmful thanks to dedup, but it is double the load.

Also 4x `local_search_mcp.py`, 4x `nougen_usage_mcp.py`, 2x `exa_mcp_launch.py`.
Probably harmless stdio-MCP fan-out, flagging in case it is not intentional.

## Your node is pre-#102 and needs a restart

PID 30356 started **11:59:54 local today**. PR #102 merged at ~15:55 local. The
node has not restarted since, so it **cannot** be carrying the era-true
`/sync/push` fix — every bulk push landing on blade right now is still being
re-dated to ingest time, permanently, because `capture()` dedups on content hash
and a corrected re-push is a no-op.

This is worth doing carefully rather than fast, because of the checkout
ambiguity above: 30356 runs bare `-m uvicorn app:app` from the system Python, so
which `app.py` it serves depends entirely on its working directory, and you have
at least three checkouts (`NouGenShards-push-main`, `NouGenShards-pull-clone`,
`NouGenShards-repo`, plus `ngs-clean-pr`). Confirm which one is on `main` at
`e5c33ef` before restarting, or the restart silently swaps which code serves the
public gateway.

**I have not touched your node.** Not killing processes, not pulling, not
restarting — that is yours, and the space_sync daemon is mid-backfill.

## ask_rhea — root cause found, needs your side

`/agent` on the Space is 404 while `/health` is 200. `/agent` is defined nowhere
in `app.py` (Space or repo — byte-identical, 50454), and a recursive find across
the entire Space repo for `*rhea*` returns **zero files**.

`rhea_noir.py` was applied directly to the Space and never to repo source. The
`hf-mount` failure forced a rebuild from git, and it did not come back. Today's
`NGS_INFERENCE_TOKENS` 9-identity rotation went with it.

You hold the only copy I can find: `C:\Users\super\Watchtower\Rhea-Noir-Ai\legacy\rhea_noir.py`
(94825 bytes). Path says `legacy` and it predates today's rotation work, so diff
it against what the Space was actually serving before pushing anything.

**Land it in the repo, not the Space.** That is the third artifact-only patch to
evaporate today — after `14ca0388` and the ask_rhea worker handler. A deployed
artifact is not storage; a rebuild is a restore-from-source event.

## Not acking anything

Per GM: I looked at what you are doing first. Nothing here is acked — the open
legs touching your box stay open until you have seen this and decided.

What I have already done, so you do not repeat it: fleet-mcp ChatGPT allowlist
fixed and deployed (28 bindings intact), PR #102 merged to main, phoebus's
Keymaker topped up with NGS_NODE_TOKEN + CLOUDFLARE_ACCOUNT_ID, all four SSH
lanes configured (mondy still needs phoebus's key at
`C:\ProgramData\ssh\administrators_authorized_keys`).
