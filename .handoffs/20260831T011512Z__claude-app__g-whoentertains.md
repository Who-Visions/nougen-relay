# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: GRID INCIDENT: DB1+DB3 corrupt from power losses; originals deleted by parallel lane; salvage running - COORDINATE before touching the vault
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T01:15:12.556Z

---
# Grid corruption incident - unified picture, blade / claude-cli (Fable 5), 2026-08-30 ~20:30 ET

READ BEFORE TOUCHING C:\Users\super\.nougen\shards - multiple lanes collided on this today.

## Root cause (delegated triage, verified)
- NOT the NVMe: zero disk/stornvme/Ntfs errors in 72h, SMART healthy.
- TWO hard power losses on the battery-removed Stadium: 8/29 06:38 and 8/30 13:57 (Event 41 + 6008). Instant AC cuts mid-write = classic sqlite WAL corruption. GM: a UPS is the actual fix.
- Aggravated by duplicate daemons writing the same files (2x uvicorn :4444 on DIFFERENT interpreters, 2x local_mesh_service, start_grid --watch) - 62 python + 187 node processes at triage time.

## What happened to DB1/DB3
- This morning they were 1.19GB / 31,381 and 27,096 rows, quick_check ok. Corruption surfaced ~18:5x.
- The Gemini/agy lane (working the same incident in parallel, then quota-stalled) DELETED the corrupt originals and restored 8/7 .bak files. VERIFIED: those baks are THEMSELVES corrupt (quick_check fails on both). The .corrupted renames are gone from disk. Net: originals lost, restored files bad.
- Rows added 8/7-8/30 to DB1/DB3 survive as: (a) the ~168k .md shard files in the vault dir (re-ingest rebuilds them - shard_vault_files.py, the script the Gemini lane was already running), (b) whatever synced to the HF Space (80k+ there), (c) dedupe-index entries.

## In flight (claude-cli lane)
- Salvage running NOW: chunked best-effort extraction from the corrupt DB1/DB3 into nougen_shards_{1,3}.db.new - NON-destructive, originals untouched, evidence copies in Watchtower\vault_snapshot_20260830. Swap happens only after quick_check green and no open handles.
- Write-path quarantine (PR #148, MERGED + deployed to Space): capture() now routes writes around malformed DBs instead of 500ing /sync/push batches. The push-main working tree still runs OLD code - local captures there still raise until the tree syncs or the swap lands.
- Space backfill paused mid-round-3; resumes after local grid is healthy.

## Asks
1. NOBODY delete or restore anything in the vault until the salvage report posts.
2. Gemini lane: hold the sharder until DB1/DB3 are swapped healthy, then re-run - it will succeed.
3. GM: UPS for the Stadium; two AC drops in 48h WILL corrupt again.
