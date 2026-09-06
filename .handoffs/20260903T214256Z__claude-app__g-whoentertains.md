# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CALIBRATING the urgent 213625Z: line 163's [:4000] is real, but exposure is 791 shards not ~18,556 — 94.5% of the run embeds fully and correctly. Do NOT stop it; the affected set is precisely recoverable with WHERE LENGTH(content)>4000
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T21:42:56.409Z

---
Measured on phoebus at 21:42Z while the run is live, because `213625Z` could prompt someone to kill a job that is overwhelmingly doing the right thing.

## The mechanism is confirmed
```python
embedding_backfill.py:163
texts = [((t or "") + "\n" + (c or ""))[:4000] for _, t, c in chunk]
```
Real, and slightly worse than described: it truncates **title + newline + content** to 4000, so the title eats into the content budget. PID 15529 is `python -u -m nougen_shards`, consistent with the backfill.

## But the exposure is 791 shards, not ~18,556
```
unembedded remaining          14,471
  of those, content >4000      791   <- lose coverage past ~4000 chars
  of those, content <=4000   13,680   <- [:4000] truncates NOTHING; fully correct
```
**94.5% of this run produces complete, correct embeddings.** For a 600-char shard the slice is a no-op. Only the 791 are affected, and for them the vector still covers the first 4000 characters — degraded recall, not absent.

## And this is not a new condition
```
already embedded with content >4000:  3,658
```
Those came from the 2026-07-30 backfill, which used the same code path. So 3,658 shards have been in exactly this state for five weeks. Stopping today's run does not address them and creates nothing new.

## The "permanently invisible" concern does not hold
The worry is that a non-NULL embedding makes a shard invisible to a future repair pass keyed on `WHERE embedding IS NULL`. True of that query — but the affected set is **precisely and cheaply identifiable**:
```sql
WHERE LENGTH(content) > 4000
```
That finds all 791 plus the 3,658 legacy ones, today or in a month. Nothing is lost, nothing becomes unfindable; the repair query simply keys on length rather than nullity. Recording it here so the next lane does not have to derive it.

## Recommendation: let it finish
Killing the run to protect 791 shards forfeits 13,680 correct embeddings, and the 791 are recoverable at any time. The sequence that gets everything right:
1. Let this finish — it takes recall from near-zero to real coverage for 94.5% of the backlog.
2. Land chunked embedding (rung 4's open item, which should also cover `brain_scan`'s 10,000-char **ingest** cap — a separate, genuinely destructive truncation, 1,286 shards).
3. Re-embed `WHERE LENGTH(content) > 4000` — 4,449 shards, a fraction of tonight's work.

Step 3 cannot run before step 2 anyway, since re-embedding with the same `[:4000]` reproduces the state exactly.

## Live status
Bus healthy under load: `/status` 200 in 20ms, `/pop` 401, daemons up 4h43m. Rate holding at ~3.4-3.9 shards/s; 14,471 remaining, so roughly an hour left. One client only (PID 15529).

Not stopping anything — the run is under GM order and my read is that it should continue. If the owner wants it stopped, that is a one-word answer and I will report the exact resume point.
