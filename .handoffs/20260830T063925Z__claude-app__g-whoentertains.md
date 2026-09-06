# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: INCIDENT RESOLVED at the infra layer: node stable, lock storm gone, blade 200 fast, tunnel guard proved in production. Remaining defect is CONFIG: node runs with persistent_storage=false so recall is empty
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T06:39:25.391Z

---
**Closes the infrastructure half of the multi-day outage.** All figures live-probed on blade.

## Verified stable
| probe | during outage | now |
|---|---|---|
| `127.0.0.1:4444/health` | 000 @ 20s | **200 @ 0.012-0.028s (6/6)** |
| `blade.nougenai.com/health` | 530 / hang | **200 @ 0.18-0.24s (3/3)** |
| failover `POST /mcp/` | hang, then 8.25s | **0.27s** |
| node log | `database is locked` x15 / 60 lines | **clean, zero occurrences** |

## What actually fixed it
The outage was **two uvicorn `app:app` instances bound to the same port via different bind specs** — `0.0.0.0:4444` and `127.0.0.1:4444`. Windows permits both simultaneously, so loopback traffic hit one and external traffic the other while both wrote the same SQLite vault. That produced the `database is locked` storm, which made `/health` time out, which made the launcher's health-based guard conclude "no node running" and start yet another — the same self-feeding fail-open loop as the connector leak. Collapsing to one interpreter ended it.

## Both guard patches now proven
1. **Tunnel guard** — proved in production this run. `start_grid.py` printed:
   `tunnel already up (1 connector(s) for this binary); not starting a duplicate`
   It correctly detected the Windows service's connector and stood down, exactly where the old fail-open version stacked another.
2. **Node guard (new this session)** — `port_up()` (an HTTP health check) could not distinguish an empty port from a bound-but-wedged node, so a wedged node read as absent and got a rival spawned on top of it. Added `port_bound()` (raw TCP connect, env-tunable via `NOUGEN_PORT_PROBE_TIMEOUT_S`) and a third branch that refuses to start a second instance and says so. Compile-checked; behaviourally verified (`:4444` → bound True, empty port → False). Synced to the runtime copy via `install_grid_supervisor.ps1` (backup `start_grid.py.bak-20260830T023140650`).

## REMAINING DEFECT — config, and it is serious
`GET :4444/health` reports:
```json
"status":"ignited", "storage":"default", "persistent_storage":false,
"warnings":["persistent storage not detected: memories are wiped on every restart/deploy"]
```
**The node runs on ephemeral default storage.** That is why `shards_search` returns `(no matches)` even now that every layer is healthy — the restart wiped the instance's working set. Earlier tonight `perplexity` returned 5 hits only because that instance had accumulated data during its uptime. Every node restart silently empties recall.

**No data was lost.** Verified on disk: `~/.nougen/shards` holds **168,821** files, and `Watchtower/vault/*.db` are intact (e.g. `c_leaks_vault.db` 335MB, `blerd_hub_vault.db` 142MB). The durable corpus is fine — the node simply is not pointed at it.

## NEXT (highest value remaining)
Point the node at persistent storage so it serves the real vault instead of an empty default. Until then recall is **responsive and wrong**, which is more dangerous than the outage was: `(no matches)` is indistinguishable from a genuine empty result. Anyone consuming recall right now should treat it as unreliable.

Secondary: the two launchers (scheduled task + Startup-folder copy) still race on a cold start — `ngs_node_boot.cmd` asserts they "can safely overlap", which this incident disproves. The new guard only helps once something is bound.
