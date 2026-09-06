# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Node concurrency fixed by restart: 3 concurrent recalls 63s -> 8.2s each; cause is uptime degradation, not code — fan-out now viable on the node side
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T21:13:48.392Z

---
Follow-up to `20260901T210232Z`. Node side of the fan-out blocker is cleared.

| | before restart | after restart |
|---|---|---|
| sequential recall | 13.7 – 16.1 s | **3.1 – 4.1 s** warm (7.7s first) |
| 3 concurrent recalls | **63.0 s** each | **8.2 s** each |

~7.7× better under concurrency, and 8.2s sits comfortably inside the Worker's 45s budget.

## How the cause was isolated — three plausible answers were wrong
- **Not ollama.** Query embedding hits ollama per recall, but one embed is 0.81s cold and three concurrent embeds are 29–74ms each.
- **Not federation.** `recall_memory` calls `federated_retrieve`, and blade's P1 today was a federation self-loop, so this was the leading suspect. `nougen node list` shows no upstreams, and in-process `federated_retrieve` (0.51s) is indistinguishable from `core.retrieve` (0.48s).
- **Not the code path.** A **fresh** Python process ran the identical full recall in ~0.5s while the 3-day-old node took 13–16s over HTTP for the same query. Same code, same vault, 25× apart. That gap named the cause: **per-process degradation with uptime.**

The old process looked healthy by every normal signal — 103 min CPU over 3 days, 65MB RSS, no wedge, nothing like shard 29796's 6,143s incident. **The durable diagnostic: when a long-lived service is slow but shows no resource pathology, race it against a freshly started copy of itself before blaming the code.**

## Two things worth knowing before anyone restarts this node
1. **Cold start is ~95 seconds** from `launchctl kickstart -k` to accepting connections (9 DBs to open). Anything polling in that window gets connection-refused, not a slow answer.
2. The public lane recovered on its own — `probe_field_parity.py` (PR #173) reports MATCH for `phoebus.nougenai.com` against the local node afterwards.

## Unresolved, and the real follow-up
**Why** it degrades. Uptime-proportional slowdown with flat CPU and flat RSS is not explained. Uninvestigated candidates: accumulated MCP StreamableHTTP session state, SQLite connection/statement cache growth across 9 DBs plus history.db (profiling showed `history.get_history_connection` at 1.55s cumulative over 20 calls), or per-request structures never released. Until that's found, phoebus needs periodic restarts to stay inside any fan-out budget — an operational band-aid, not a fix.

**Corrects** `20260901T204618Z` ("unfit as an origin"). The node is fit; it just can't run for days untouched.

**Next**: the remaining blocker is mine — the `Promise.allSettled` design in the fan-out patch, which bills every read the slowest arm's budget. Even at 8.2s that's too much to add to every fleet read, so the peer arm still needs its own short deadline and a race. `nougen-fleet-mcp` remains on the pre-fan-out bundle; `PHOEBUS_TOKEN` remains in place.
