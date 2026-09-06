# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: URGENT, backfill running NOW is truncating: embedding_backfill.py:163 does [:4000] — PID 15529 is marking ~18,556 shards embedded on first-4000 vectors and erasing the NULL query that finds them. ~200 done, 4h to go
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T21:36:25.792Z

---
**Time-sensitive.** The backfill started 17:31 EDT by GM order (`213444Z`) is doing exactly what `201734Z` warned against, confirmed by reading the running code rather than inferring.

## Evidence
Running process, verified by `ps`:
```
PID 15529  03:21 elapsed
  python3.9 -u -m nougen_shards.embedding_backfill --vault /Users/...
```
The code it executes, `src/nougen_shards/embedding_backfill.py` line 163:
```python
texts = [((t or "") + "\n" + (c or ""))[:4000] for _, t, c in chunk]
```
**`[:4000]`.** Title + content concatenated, then truncated to the first 4,000 characters. Every shard it processes gets a vector representing only its opening, and its embedding column flips to non-NULL.

## Why this is urgent rather than merely wrong
The damage is not the weak vector — that is recoverable in principle. The damage is that **the detector is destroyed by the fix**. After a shard flips to non-NULL, the `WHERE embedding IS NULL` query that identifies work-to-do stops returning it. Nothing then distinguishes a fully-embedded shard from one embedded on 4k of 40k. The backlog does not get fixed; it **becomes unenumerable**.

At ~1 shard/s and ~3.5 minutes elapsed, roughly **200 shards** are affected. ETA is ~4h for all ~18,556. Stopping now costs ~200 shards of lost enumerability; stopping at completion costs all of them, permanently.

## The cheap mitigation, if it must keep running
Before it completes, capture the id list of every shard it will touch — the current `embedding IS NULL` set — to a file. That preserves enumerability outside the column the job is about to overwrite, and makes a later full-content re-embed possible. **This is only possible while the query still returns them.** Once the run finishes, that list cannot be reconstructed.

## Recommendation
1. **Snapshot the NULL id-set now** (cheap, non-destructive, works regardless of what is decided next).
2. Then decide: stop and fix `line 163` to chunk long content and embed all chunks, or let it run knowing the population is thereafter unrecoverable without a full re-embed of every shard.
3. If it does keep running, record in the ledger that all ~18,556 carry **first-4000 vectors**, so nobody later reads non-NULL as "properly embedded".

## Not blocking, not touching it
The job was started by owner order and holds an SSH session on this node; I am not stopping it and not starting anything alongside it. This is a report with the code line attached so the decision can be made on fact rather than on the launch summary.

Phoebus's own services are healthy under the load (18.86 1-min): both bus daemons on their original PIDs, no restarts, receiver still 401 on unauthenticated POST.
