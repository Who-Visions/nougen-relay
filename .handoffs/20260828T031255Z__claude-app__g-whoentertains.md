# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Shard gateway restored + hardened; 3 follow-ups open for parallel pickup (shard #22664 has full detail)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T03:12:55.687Z

---
## Situation
shards_status was down (up/health_up/mcp_up all false), shards_search/recall timing out. Root cause: node_lane.ps1 (manual/gateway_supervisor.ps1 path) and start_grid.py --watch (named-tunnel watchdog) are two uncoordinated launchers that both try to keep uvicorn alive on :4444 with zero shared lock — a manual restart raced the watchdog's own restart within the same second and stacked 4 processes on the port, one of which silently "won" the bind while the others looked alive to a PID check. Full root-cause chain and evidence in vault shard **#22664**.

## Fixed this session (Claude Cli, blade1tb)
- `tools/bin/cloudflared.exe` was missing from this checkout — populated it, and made `gateway_supervisor.ps1`'s `$Cloudflared` resolve dynamically (env → repo copy → PATH → known install) instead of one hardcoded path.
- `Sync-Worker` in `gateway_supervisor.ps1` no longer throws when the sibling `nougen-fleet-mcp` worker checkout is missing — logs and degrades instead of killing the tick.
- **Added a real cross-process singleton lock** shared by `start_grid.py` (msvcrt.locking) and `node_lane.ps1` (`[System.IO.File]::Open` + `FileShare.None`), default path `~/.nougen/bin/node_lane.lock`, override via `NOUGEN_NODE_LOCK`. Both re-check health after acquiring the lock and stand down cleanly if another launcher is mid-start. Verified live: py_compile clean, PSParser clean, functional tick end-to-end, `shards_status` now `{up:true, health_up:true, mcp_up:true}`, `shards_search` returning real ranked results.
- Cleaned up the accumulated duplicate uvicorn/ngs_node_serve processes (identified precisely by CommandLine+ParentProcessId, not a blind kill).

## Ask — pick up any of these independently
1. **Audit the Windows Scheduled Task** (`nougen_shards_grid.cmd`, wired at Startup per shard #22471) — confirm it isn't launching a THIRD independent `start_grid.py` invocation outside the `--watch` loop already running (PID currently 33944 on blade1tb). If it is, it already goes through the same lock since the lock lives inside `start_grid.py` itself, but worth confirming.
2. **Reconcile `node_lane.ps1`'s pidfile drift** — post-fix it shows `launcher=29824 listener=43568` (different PIDs). Health is fine either way since the lock now prevents new races, but the pidfile tracking a stale/wrong PID is worth cleaning up so `stop`/`status` report accurately.
3. **shard #22471's flagged `/mcp` vs `/mcp/` trailing-slash split-brain** on the `nougen-fleet-mcp` Worker route is still untouched and still fragile — separate from tonight's incident but adjacent.

## Done-when
`shards_status` stays green across a manual node kill + immediate watchdog-window restart attempt (i.e. force the race on purpose and confirm only one process wins cleanly, no port-4444 pileup).

Gemini is in parallel on this same repo tonight (rhea_noir.py relay_create tool + final-synthesis fix, shard #22381) — different files, no overlap expected.
