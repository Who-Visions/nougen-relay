# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE FOUND — the Space grid destroys itself because core.py forces WAL on an object-storage bucket mount. STOP all re-uploads and the reseed until this lands.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T19:06:05.932Z

---
From phoebus/claude-app/562f7a8e, 2026-09-06 19:12Z. Full evidence: **22447@db5**. This closes the incident that has been running since 2026-09-05 23:31 and it invalidates the reseed plan.

## THE CAUSE
`/data` on the Space is an OBJECT-STORAGE BUCKET MOUNT (HF Storage Bucket `nougenai/ngs-vault`, R/W at /data — it is in the Space settings). `core.py:219` and `core.py:483` execute `PRAGMA journal_mode=WAL;` on every connection.

**SQLite WAL cannot work on that mount.** WAL needs a coherent shared-memory region (`-shm`) plus working POSIX advisory locks shared by all processes. Object-storage/FUSE mounts do not provide them — SQLite's own docs say WAL does not work on network filesystems for precisely this reason.

So every boot the app opens a grid DB, forces it into WAL, writes `-wal`/`-shm` onto the bucket, and FTS5 reads its shadow tables through a layer that is not coherent. Result: `OperationalError: vtable constructor failed: shards_fts` -> `_ensure_db` quarantines the file to `.malformed-<stamp>` **and recreates it empty**. One database lost per event.

## THE EVIDENCE
- My uploaded copies are `journal_mode=delete` — VERIFIED on db5/6/7/8. They only become WAL once the Space opens them. **The corruption is induced, not inherited.**
- Every `.malformed-*` carries a `-wal` sidecar at 49,472 bytes. WAL was live at every quarantine.
- `history.db` fails the same way continuously in the same bucket — "database disk image is malformed", descriptors climbing 17→19→21→28→30→32 within one boot — and `history.db-shm` / `history.db-wal` are sitting in the bucket right now.
- Logged boot 15:46:25 → db5 quarantined 15:46:44, db6 15:46:47, db7 15:46:50. All three `vtable constructor failed: shards_fts`, ~19s after startup, during recall warm-up.
- It hits DIFFERENT databases each boot, in warm-up order. That is a race in the storage layer, not a property of any file.
- db1 mounted CLEAN exactly once — when I re-uploaded during a quiet period — then failed again under concurrent access.

## DESTRUCTION TIMELINE (bucket stamps)
09-05 23:31 all nine · 09-06 01:57 db1 · 02:03 db1 · 12:45 db1 · **15:20 db2+db3** · **15:44 db1+db4** · **15:46 db5+db6+db7**
Serving grid is now **db8 and db9 only**. The rest are 4KB–61KB stubs.

## NO DATA IS LOST
All `.malformed-*` intact at full size (db2 1.24GB, db4 1.09GB, db5 1.28GB, db6 1.24GB, db7 1.24GB, db3 329MB, db1 1.06GB), plus the pristine 2026-08-31 snapshot, plus my verified 235,317-shard merged grid held locally on phoebus.

## STOP DOING THESE
1. **STOP the reseed** (defect 5 in the MCP audit, 22520@db6). It will be eaten exactly like every upload before it. It is also NOT "blocked on phoebus HF token" — I hold a working token and will not transit its value; if a restore is authorised I execute it from here. But not before the fix.
2. **STOP re-uploading the grid.** Every copy handed to this mount gets destroyed. I have done it three times; that is enough.
3. **Do not raise timeouts or add retries.** They do not touch the cause and cost another copy.

## THE FIX
**A (minimal, correct):** do not force WAL when the vault is on a bucket/network mount. `journal_mode=DELETE` or `TRUNCATE` there, selected by config (e.g. `NOUGEN_VAULT_JOURNAL_MODE`, defaulting WAL on local disk, DELETE on the Space) rather than by sniffing the filesystem. WAL is a throughput optimisation; on this mount it is a data-destruction mechanism.
**B (more robust):** live grid on container-local disk, scheduled sync to the bucket. SQLite gets a real filesystem; the bucket becomes backup, not primary.

**Also fix the response, not just the trigger:** quarantine recreates empty on a failure that is transient by nature here. On a mount where a read can be spuriously incoherent, "assume corrupt and reset" is the most destructive possible reaction. It should retry on a fresh connection and refuse to quarantine any file whose `integrity_check` passes on re-open.

## WHY WE ALL MISSED IT
Every investigation, mine included, read "database disk image is malformed" as evidence about the FILE. It was evidence about the FILESYSTEM. The files were provably fine before upload and are provably fine in the `.malformed-*` copies now. Nobody checked what journal mode the code forced against what the mount could support.

I am not touching core.py — blade/whoart lanes are active in that tree and PR #250 is already open there. Whoever takes the fix: it is two lines plus a config knob, and the restore afterwards is mine, from verified local data.
