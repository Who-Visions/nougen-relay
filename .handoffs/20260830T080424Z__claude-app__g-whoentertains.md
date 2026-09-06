# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RESOLVED: recall works end-to-end. Final cause was BLADE_TIMEOUT_MS=8000 too short (fell through to empty Space) + a runaway query pinning the node at 6143s CPU. Now 30000, node restarted, real shards returning
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T08:04:24.957Z

---
**Incident closed.** `shards_search("perplexity")` now returns real shards through the public gateway (shard 22462 "Canonical MCP ingress invariant" + a local-vault hit).

## The node-direct test settled it
Authenticated `recall_memory` straight at `127.0.0.1:4444/mcp/` with `X-NGS-Token` returned **HTTP 200 with real data** for `perplexity`, while the same query through the gateway returned `(no matches)`. That proved the node held the corpus and the fault was in the path above it.

(For the next lane: get the token with `keymaker_peel.load("NGS_NODE_TOKEN", db=~/.nougen/secrets/shards_secrets.db)` — the `db=` argument is required, and omitting it silently returns an empty list.)

## Final cause — my own earlier fix, plus a runaway query
1. **`BLADE_TIMEOUT_MS=8000` was too short.** Real queries over 9 partitions of ~1.2GB exceed 8s, so the failover abandoned blade and fell through to the **empty Space replica**, which honestly answered "no matches". The 8000 value cured the original unbounded hang but traded it for fast wrong answers. Raised to **30000** (still under `nougen-fleet-mcp`'s 45s outer budget).
2. **A broad query pinned the node.** My own `recall_memory("NouGen")` probe never returned and drove one process to **6,143 seconds of CPU and 1.7GB RSS**, starving `/health` to 10s and then to timeouts. This is the "24,523s CPU" note in `gateway_probe.py` reproducing live. Killing that process and restarting the node restored service immediately.

## Verified green
- node `/health` 200; `shards_search("perplexity")` returns real shards via `shards.nougenai.com`
- `blade.nougenai.com` 200 @ ~0.2s; `database is locked` storm gone
- `/health` `storage` = `C:\Users\super\.nougen` (was `"default"`)

## HIGHEST-VALUE REMAINING WORK: bound the query cost
**A single broad recall can pin the node and take the whole fleet down.** That is the real fragility behind this entire multi-day incident — not the tunnel, not the workers, not storage. Recommend, in order:
1. A hard server-side wall-clock budget per query, returning a partial/timeout result instead of running unbounded.
2. Cap candidate rows scanned per partition (`LOCAL_VAULT_MAX_ROWS` exists — verify it is actually enforced on the recall path).
3. Reject or degrade very low-selectivity terms rather than scanning everything.
Until that lands, treat broad single-word recalls as a denial-of-service against your own fleet.

## Also still open
- Empty/malformed Space replica (`20260829T120003Z`) — it is the fallback, and it silently answers `(no matches)`. A replica with no rows should FAIL, never impersonate an empty result.
- Cold-start double-launch race (two launchers, `ngs_node_boot.cmd` wrongly claims they "can safely overlap").
- `app.py:836` `persistent_storage` is an HF `/data` mount check — a permanent false alarm off-HF; reword or skip it.
- `start_grid.py` carries three uncommitted fixes from this session (tunnel guard fails closed + ExecutablePath match; `port_bound()` so a wedged node never gets a rival; `NOUGEN_HOME` propagated to the child). File owner's call to commit.
