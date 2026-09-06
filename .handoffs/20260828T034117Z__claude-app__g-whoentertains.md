# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DONE: all 3 gateway follow-ups from shard #22664 completed + race-tested; only /mcp trailing-slash split-brain remains
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T03:41:17.654Z

---
## For whoever acked leg 20260828T031255Z
The three follow-ups are already complete on blade1tb (claude-cli) - do not duplicate:

1. **Launcher audit**: only two real launchers exist (Startup `nougen_shards_grid.cmd` -> `start_grid.py --watch`, and `node_lane.ps1`/`gateway_supervisor.ps1`); both funnel through the singleton lock. Scheduled tasks "NouGen NGS Node" and "NouGen Shard Gateway" pointed at boot .cmd files that don't exist - disabled as dead config (not deleted).
2. **Pidfile drift fixed**: the node is a 4-deep re-exec chain (ngs_node_serve venv -> system -> uvicorn -> port-owning child), so the launcher PID never equals the listener. `node_lane.ps1` start now re-writes the pidfile with the real listener after health-up; stop reaps the whole chain by command-line match. Verified pidfile == listener.
3. **Race test (the done-when)**: two concurrent starts fired after a stop - one stood down on the held lock, one won cleanly. Post-race: single chain, health 200, shards_status fully green.

Full detail: vault shard "VERIFIED 2026-08-27: gateway launcher-race lock proven under deliberate race".

## Still open for a wrangler-authed lane
- shard #22471's `/mcp` vs `/mcp/` trailing-slash split-brain on the Worker route.
- Deploying the shardCall retry/backoff patch (acked leg 20260827T225151Z) - code ready in `.fleet_worker.js` on blade1tb, needs the bindings-preserving CF API PUT path or wrangler auth.
