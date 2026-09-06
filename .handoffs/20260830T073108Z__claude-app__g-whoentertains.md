# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Storage bug FIXED (NOUGEN_HOME now propagated; storage no longer "default"); infra fully green. Recall still empty — narrowed to node-side search/tenant, NOT storage, NOT plumbing
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T07:31:08.009Z

---
**Continues** `20260830T063925Z`.

## FIXED: launcher dropped its own resolved NOUGEN_HOME
`tools/start_grid.py` resolves `NOUGEN_HOME` at line ~24 (env → `~/.nougen`), but `_start_node()`'s child env never passed it — the node inherited it only if the parent shell happened to have it. **Only `ngs_node_boot.cmd` exported it**, so a node started any other way (hand-run, Startup-folder copy, watchdog respawn) silently fell back to default storage and served an empty vault, while every layer above looked healthy. Classic Rule 0.2: resolve a value correctly, then fail to propagate it.

Patch: added `NOUGEN_HOME=str(NOUGEN_HOME)` to the child env. Compile-checked, synced to runtime (`install_grid_supervisor.ps1`, backup `start_grid.py.bak-20260830T032631494`).

**Verified**: `/health` `"storage"` went from `"default"` → `"C:\\Users\\super\\.nougen"`.

## Note: `persistent_storage: false` is a FALSE ALARM on blade
`app.py:836`: `persistent = os.path.isdir("/data") and os.path.ismount("/data")`. That is a **Hugging Face Space** check — `/data` never exists on Windows, so this is permanently false on blade and says nothing about data durability. It should be skipped or reworded off-HF; as written it invites exactly the panic it caused here.

## Data is present and healthy — recall is NOT a storage problem
`NOUGEN_VAULT_DIR=C:\Users\super\.nougen\shards` is set correctly, and that directory holds:
- **168,821** shard files
- 9 FTS partitions, ~1.0-1.24 GB each (`nougen_shards_1..7+`), plus `history.db` at 1.0 GB
- **all written minutes ago (03:07-03:28)** — actively growing, not stale

Infra all green: node `/health` 200 @ 12-28ms, `blade.nougenai.com` 200 @ ~0.2s, failover 0.27s, `database is locked` gone.

## STILL OPEN: `shards_search` returns `(no matches)`
Not storage, not the tunnel, not the workers — all disproved. Remaining candidates, in order:
1. **Tenant/lane isolation.** `/health` reports `tenant_registry_configured: true`, and the gateway sends lane `claude-client`. If that lane resolves to a tenant with no rows, results are legitimately empty while the node is full. **This is my leading hypothesis.**
2. Tool-arg mismatch: gateway maps both `SHARD_TOOL_SEARCH` and `SHARD_TOOL_RECALL` to `recall_memory`; worth confirming its expected argument shape.
3. Index built but not registered for the queried partitions.

**How to settle it in one step**: run an authenticated `recall_memory` straight at `http://127.0.0.1:4444/mcp/` with `X-NGS-Token`, bypassing the gateway entirely. If it returns rows, the fault is tenant/lane resolution in the gateway; if empty, it is the node's index/tenant binding. I could not complete this — `keymaker_peel.load()` returns `List[Tuple]` and did not match `NGS_NODE_TOKEN` for me, though `start_grid.py` resolves it fine via its own `peel()` wrapper (it printed `secret NGS_NODE_TOKEN fp=9c67af03a9da rotated=2026-08-14`). Use start_grid's `peel()`, not `keymaker_peel.load()`.

## Fleet lanes were unavailable this whole incident
`ask_rhea` → `502 both origins unreachable` (she runs on the same infra). `agy` CLI → `timeout waiting for response`, empty output, twice. Neither delegate lane is usable during an infra outage — worth designing around, since that is exactly when they are wanted.
