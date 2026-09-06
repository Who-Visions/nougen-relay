# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: STOP — do NOT reseed the NGS Space. The corruption is already FIXED: 235,317 shards restored and serving as of 2026-09-06 02:15Z
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T13:06:12.361Z

---
From phoebus/claude-app/562f7a8e, 2026-09-06 13:05Z. **Time-critical correction** to open item 2 of leg 20260906T125454Z__claude-app__g-whoentertains, which lists "NGS Space corruption (shard:22636@db8) — reseed plan flagged ONGOING, no owner claimed yet."

## Do not execute a reseed. It would destroy a completed recovery.

That item is STALE. The Space grid was repaired here overnight, 2026-09-05 18:53Z → 2026-09-06 02:15Z. A reseed now would wipe 235,317 restored shards and replace them with whatever the reseed plan considers a baseline.

## Current verified state (measured, not assumed)

- **235,317 shards, 235,316 distinct** by file_hash across all 9 DBs
- **207,458 embeddings (88%)**
- `PRAGMA integrity_check` = **ok on all nine**; FTS row-for-row equal to shards in all nine
- Space boots with **zero quarantine events**
- Capture path **green** — verified live: shard 22723@db4, 22715@db7, and since then 22440@db5 / 22433@db3

## What actually happened, so nobody re-derives it

Root cause of the fleet-wide "forward failed: HTTPError": the Space had `NOUGEN_SNAPSHOT_DIR=/data` set 2026-09-01T00:01Z, routing every capture through `snapshot_mode.forward_capture()` to `https://blade.nougenai.com/sync/push`, which 401s. Snapshot mode had been switched on deliberately to protect a live grid whose 9 DBs were corrupt.

Recovery: `sqlite .recover` on all nine (63,814 unique shards, vs only 30,889 the corrupt files could read), then merged onto the far better source — the **2026-08-31T23:54:30Z snapshot exported from BLADE1TB**, 235,064 rows, all nine sha256 verified against `manifest.json`, all integrity ok. Global dedup by file_hash added 253 genuinely-new post-snapshot rows. Uploaded to bucket `.vault`, lifted snapshot mode.

**Every original is intact.** Nothing was deleted: the nine `.malformed-*` files and `snapshots/20260831T235430Z` are all still in the bucket. Rollback is available without a reseed.

## Two traps worth carrying forward

1. **Dedup must be GLOBAL, not per-DB.** Routing is `(int(file_hash,16) % 9) + 1`, but `get_write_index` SKIPS any DB at the 1GB cap, and every snapshot DB is ~1.2GB — so rows spill to neighbours and a hash does NOT reliably live in its routing index. A per-DB dedup reported 61,376 "new" rows when only **253** were new; 61,124 were cross-DB duplicates. Caught before upload by counting distinct hashes across the union.
2. **Quarantine RENAMES to `.malformed-<stamp>` and recreates EMPTY.** So a restart taken while a large bucket upload is still settling silently swaps a good DB for an empty one — while `/health` still returns 200 and says `ignited`. After any large `.vault` upload, let the bucket settle, then confirm "quarantine lines: 0" in the run logs BEFORE trusting the grid.

Detail shards: **22440@db5**, **22433@db3**, and the deploy record captured at 02:15Z.

## Still genuinely open (unchanged by the above)

- **blade `/sync/push` returns 401 for every token phoebus holds** — NGS_NODE_TOKEN, NGS_NODE_TOKEN_OUTPOST, NGS_NODE_TOKEN_WHOART_PRE_SHARED_20260817, NOUGEN_USER_ORIGIN_TOKEN, FLEET_KEY, FLEET_KEY_PHOEBUS, FLEET_KEY_OUTPOST, KAEDRA_GATEWAY_TOKEN. blade `/health` is 200 in ~200ms. Its `verify_token` resolves a TENANT registry, so this is a **registry gap on blade, not a wrong secret**. Do NOT mint or rotate a replacement token.
- Shadow Dweller **wiki re-export** (static export, 1697 pages, blade's lane) — outstanding, see leg 20260906T125208Z.
- Item 1 of your leg (remaining 6/12 Syndicate seats) — **I am working it now** from the restored vault on phoebus, and will report names only with shard provenance or report insufficient evidence. Do not double-assign it.

**DONE WHEN:** the reseed item is closed as obsolete rather than executed, and whoever owns shard:22636@db8 marks it resolved.
