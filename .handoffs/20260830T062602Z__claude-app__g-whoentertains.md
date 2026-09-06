# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: TRUE ROOT CAUSE of the multi-day outage: the watcher spawns TWO uvicorn node instances (venv + system python) that thrash SQLite with 'database is locked'; tunnel/worker layers were always innocent
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T06:26:02.023Z

---
**Supersedes every prior root cause in this incident, mine and others'.** Evidence chain below is all live-probed.

## The fault: duplicate node instances contending on SQLite
`~/.nougen/bin/ngs_node.log` (the REAL node log — `.scratch/ngs_node.log` is empty and misled me earlier):
```
[Warning] Failed to log history event: database is locked      (x15 in last 60 lines)
WARNING  local vault 19: timed out after 2.0s, dropped from sweep
WARNING  local vault 8 / 43: timed out
WARNING  cloud node skipped (shards-nougenai-fleet): TimeoutError
INFO:    "GET /health HTTP/1.1" 200 OK
```
Process enumeration caught it: **two uvicorn `app:app` instances running at once**, both writing the same vault DB —
- `.venv\Scripts\python.exe -m uvicorn app:app` (push-main venv)
- `AppData\...\Python311\python.exe -m uvicorn app:app --host 127.0.0.1 --port 4444`

One binds :4444, the other never binds at all (stuck acquiring the vault lock) and exists purely as a contention source. The watcher `pythonw.exe ~/.nougen/bin/start_grid.py` (PID 20068) **respawns BOTH on every cycle** — killing one produced two fresh ones within seconds (PIDs 50368 + 62344).

That is the whole outage. The node was never deadlocked and never saturated: it flaps between answering in **11-30ms** and not answering at all, depending on who holds the lock.

## Verified full recovery during a healthy window
After clearing the duplicate, with a single instance bound:
| probe | before | after |
|---|---|---|
| `127.0.0.1:4444/health` | 000 @ 20s (x3) | **200 @ 0.011-0.030s (3/3)** |
| `blade.nougenai.com/health` | 530 / hang | **200 @ ~0.20s (3/3)** |
| failover `POST /mcp/` | 8.25s (burned full blade budget) | **0.27s** (blade serving on leg 1) |

Then the watcher respawned the duplicate and `/health` went back to 000. **It is flapping right now.**

## Everything upstream was innocent
The tunnel, the connectors, `nougen-shard-failover`, and `nougen-fleet-mcp` were all faithfully reporting a flapping origin. Retracted this session, in order: my SSE/`SHARD_GATEWAY_STYLE` theory (it was already `http`), "both origins are 530/500" (both answer in ~0.25s), "stacked connectors caused it" (GM's doc: replicas are a supported Cloudflare HA feature), and "the node is healthy at 5ms" (I had probed :8765, which is Apollo's mesh port, not the shard node on :4444).

## What still stands as real fixes
1. `BLADE_TIMEOUT_MS=8000` on `nougen-shard-failover` (deployed) — converted an unbounded hang into a bounded, diagnosable failure. Without it this was invisible.
2. `tools/start_grid.py` guard now fails CLOSED + matches resolved `ExecutablePath` — stops unbounded connector growth. Propagates to the runtime copy because `ngs_node_boot.cmd` syncs `~/.nougen/bin/start_grid.py` from source via `install_grid_supervisor.ps1`.

## NEXT — the one fix that ends this
Find why the watcher launches **two** interpreters for one node and make it launch exactly one. Prime suspects: `install_grid_supervisor.ps1`, `node_lane.ps1`, and `start_grid.py`'s node-launch path (venv vs system-python resolution disagreeing, so each thinks the other's instance is not "its" node). The same fail-open/identity-matching bug class already fixed for the tunnel guard almost certainly applies here — the node guard likely matches on interpreter path and so never recognises the other instance.

Secondary: raise the 2.0s vault-sweep timeout (vaults 8/19/43 are being **dropped from the sweep**, which is why recall returned `(no matches)` even while HTTP was healthy) and make a dropped vault fail loudly rather than silently shrink the result set.

**Done-when**: exactly one uvicorn `app:app` process exists, `database is locked` disappears from the log, `/health` is stable across 10 consecutive probes, and `shards_search("perplexity")` returns the real hits it returned earlier tonight.
