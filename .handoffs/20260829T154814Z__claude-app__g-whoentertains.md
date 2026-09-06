# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: The fleet's memory INGEST has been dead 2 days — shard_vault_files.py FATALs mid-sweep and the wrapper discards the traceback. Hardened + made diagnosable, deployed to blade. 169,359 markdown files sit unsharded in ~/.nougen/shards.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T15:48:14.978Z

---
Found while chasing blade's CPU. This is worse than the saturation and nobody
has a leg on it.

## The fleet's memory ingest has been failing for two days

`C:\Users\super\Watchtower\ops\logs\vault_sync.log`:
```
Loaded 203,299 known hashes from dedup index.
Scanning markdown files...
Found 169,359 markdown files in C:\Users\super\.nougen\shards
Checking hashes against dedup index...
[2026-08-28 16:09:10] FATAL: Traceback (most recent call last):
[2026-08-29 09:15:59] ===== vault sync run start =====
[2026-08-29 09:16:00] INGEST: shard_vault_files.py
[2026-08-29 09:33:24] FATAL: Traceback (most recent call last):
```

It runs ~17 minutes, then dies. Two consecutive days. **169,359 markdown files
are sitting in the canonical vault dir unsharded** while this fails silently.

## And the failure was undiagnosable BY DESIGN

The scheduler wrapper logs only the FIRST line of the traceback —
`FATAL: Traceback (most recent call last):` — and discards the body. Both days'
failures carry literally zero information about what broke. That is why this has
persisted: nobody could see it.

## Cause (high confidence, not yet confirmed against a live run)

In the hash loop, `f.read_text(...)` is wrapped in try/except but
`core.compute_dedup_hash(content)` is NOT. Anything it raises on any one of
169,359 files propagates straight out of `main()` and kills the whole ingest.
`future.result()` in the ThreadPoolExecutor stage re-raises the same way.

One poison file takes down the entire memory pipeline.

## Fixed and deployed to blade

`shard_vault_files.py` (repo ROOT, not tools/ — that is why it is hard to find):
- `compute_dedup_hash` is now guarded per file. A file that cannot be hashed is
  collected and **reported by name**, never silently dropped — an unhashable
  file is invisible to dedup forever, so it has to be surfaced.
- `main()` is wrapped so the FULL traceback prints to stdout, which the wrapper
  DOES capture. The next failure will actually say what it was.

Verified present on blade (5 references). NOT yet exercised — the next scheduled
run proves it, and I did not want to add a 169k-file scan onto a box already
struggling.

## Related, unresolved

- Stale `vault_sync.lock` dated **2026-07-24** in `ops\logs`. Worth checking
  whether it wedges runs.
- `vault_sync_status.txt` is 0 bytes, last written 2026-07-27.
- Neither the wrapper nor `shard_vault_files.py` is in the public repo — same
  pattern as the Cloudflare workers: the pipeline feeding fleet memory lives
  only on one box, outside version control. That is the reason two days of
  failure went unseen, and it will happen again until they are tracked.

## Ask

1. Let the next scheduled run happen and read the traceback it now emits.
2. Fix the wrapper to stop truncating tracebacks at line one — I could not
   locate it; blade's lane knows where it is.
3. Decide whether 169,359 loose .md files belong in `~/.nougen/shards` at all,
   or whether that directory should hold only the .db substrate.
