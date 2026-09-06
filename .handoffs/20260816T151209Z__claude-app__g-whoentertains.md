# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: BACKUP GAP (P1): the 151k-shard grid has no replica — nightly VACUUM INTO → R2 with lifecycle, ~1hr of work
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-16T15:12:09.995Z

---
## Situation

The grid is single-copy. Nine SQLite DBs, ~366-397 MB each, ~151,200 shards total, living at `C:/Users/super/.nougen/shards` on blade and nowhere else. Phoebus is a **gateway lane, not a replica** — it fronts `ngs.nougenai.com` and exposes the memory-four tools, but blade's vault remains the superset. If that disk dies, the grid is gone: every correction, every dated amend, every retracted-but-preserved wrong belief. The append-only doctrine that makes this system worth anything assumes the append log survives.

We already had the rehearsal. On 2026-08-15, `core.py` resolved `NOUGEN_VAULT_DIR` against a stale Watchtower path from a shell that didn't have the env var set, `capture_experience` failed with "no such table: shards", and the operating lane believed for a minute that 8 of 9 databases had been deleted (see shard 16968). That one ended fine because the data was never actually gone. A disk failure won't have that ending.

Everything else in this stack is enterprise-shaped — named tunnel with ingress restricted to `/mcp`, OAuth with dynamic client registration plus a `GOOGLE_ALLOWED_EMAILS` revocation switch, launchd KeepAlive supervision on Phoebus, a 536-test suite with a regression test written for each of the three ranking defects closed 2026-08-16 (shard 16632). Durability is the one leg missing, and it's the cheapest one to add.

## The ask

Nightly backup of all nine DBs to Cloudflare R2. Same account that already holds the zone, the Worker, and the tunnel — no new vendor, no new bill of consequence.

1. **`VACUUM INTO`, not file copy.** `sqlite3.connect(db).execute("VACUUM INTO ?", [dated_path])` produces a consistent snapshot of a live, in-use database and compacts it on the way out. Copying the `.db` file while the node holds it open can capture a torn write plus an orphaned `-wal`. Do not use `cp`.
2. **Resolve the vault path from the running process, not the shell.** Rule 0.2, learned the hard way. Ask the node for its own vault path (`shards_coverage` / `substrate_coverage` returns it) rather than trusting whatever `NOUGEN_VAULT_DIR` resolves to in the backup script's environment — that is exactly the failure mode from 16968, and a backup job silently snapshotting an empty stale grid is worse than no backup at all, because it reports success.
3. **Dated keys:** `shards/YYYY-MM-DD/nougen_shards_{1..9}.db`. R2 lifecycle rule to expire dailies past ~30 days; keep the 1st-of-month copies longer.
4. **Verify, don't assume.** After upload, re-open each snapshot and run `PRAGMA integrity_check` plus a `SELECT COUNT(*) FROM shards`, and compare the summed count against what `shards_coverage` reports live. Log the delta. A backup nobody has restored from is a hypothesis, not a backup.
5. **Restore drill once.** Pull one dated snapshot into a scratch dir, point a node at it with `NOUGEN_VAULT_DIR`, run one `shards_recall`, confirm hits come back. Then write down how long it took.

## Done when

- Nine dated objects land in R2 on a schedule without hand-holding, and a failed run is loud rather than silent.
- Integrity check + row count logged per DB per run, with the live-vs-snapshot delta recorded.
- One documented restore has actually been performed end to end, with the wall-clock time written down.
- A shard is captured covering the runbook and the restore timing, so the next lane doesn't reverse-engineer it.

## Notes for whoever takes this

Blade is Windows — Task Scheduler, or extend the existing `C:\Users\super\.nougen\bin\start_grid.py` pattern (idempotent, keymaker_peel, fingerprints only) rather than inventing a second credential path. R2 credentials go through keymaker and `vault_put`; the fleet connector is write-only on the vault by design, so nothing needs to read them back over the network.

One judgment call left to the GM, not to be decided by the lane taking this: whether off-Cloudflare copies are wanted too. Right now the zone, the Worker, the tunnel and the proposed backup bucket would all sit inside one provider account — meaning one compromised or suspended account takes the grid with it. A weekly copy to a second location (external disk, or a different provider) removes that. Ask before assuming.
