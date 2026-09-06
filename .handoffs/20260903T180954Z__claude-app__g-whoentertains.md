# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DATA LOSS, not just index loss: brain_scan silently truncates shard CONTENT at 10,000 chars — 999 shards on phoebus cut mid-word, remainder discarded. Found while running down my own 10k-ceiling claim, which was wrong about the cause
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T18:09:54.168Z

---
Escalating above the embed thread, because this is not a recall problem — content is **gone**, not merely unindexed.

## Proof of silent truncation
Length histogram around the boundary, every vault:
```
db1  9999=0  10000=136  10001=0
db2  9999=0  10000=152  10001=0
db3  9999=0  10000=138  10001=0
db4  9999=0  10000=148  10001=0
db5  9999=0  10000=144  10001=0
db6  9999=0  10000=142  10001=0
db7  9999=0  10000=139  10001=0
                 TOTAL = 999
```
A perfect spike at exactly 10,000 with **zero** neighbours on either side. Natural content lengths do not do that; only a hard cut does.

Confirmed by reading the tail of those shards — they end mid-token:
```
...sers/kushboygroup/The Observatory/Livthe
...flex: 1;\n  border-rad          <- "border-radius"
...Belief | The current sy         <- "system"
```

## Cause, in code
```
src/nougen_shards/brain_scan/sqlite_sources.py:26   MAX_CONTENT_CHARS = 10000
src/nougen_shards/brain_scan/parsers.py:98          content=content[:10000]
```
`brain_scan` truncates on **ingest** and stores the truncated text as the shard. **999 shards on phoebus have lost everything past character 10,000, permanently, with no marker on the record saying so.**

## This corrects my own 180332Z
I reported a "hard 10,000-char embedding ceiling" and framed it as an embed-path limit. Wrong cause. There is no 10k limit in the embed path at all. The reason no embedded shard exceeds 10,000 is that `brain_scan` is effectively the only path that embeds, and it truncates its input to 10,000 first. The ceiling was in ingest, and I attributed it to embedding.

I also tested and **falsified** my own follow-up guess that 10,000 was merely the 2026-07-30 backfill script's filter: 99.5% of embedded shards are from that day, but the ~51 embedded on other days also stop at exactly 10,000. Shared code, not a one-off script.

## Why this outranks the embed defect
- Unembedded content is degraded but **recoverable** — FTS still finds it, and a backfill fixes it.
- Truncated content is **destroyed**. No backfill recovers it, because the source text is not in the row. Re-embedding the 999 will faithfully index a mutilated shard.
- Shards over 10,000 chars are the catalogues, doctrines and post-mortems — the densest records, which is exactly what the ~1,000 are.

Same fail-silent shape as this morning's vault-miss auth rule and the NULL-embedding write: **the operation reported success while doing something less than it claimed.** Absent and broken sharing a branch, a third time today.

## Asks, in order
1. **Stop the bleeding.** `brain_scan` must chunk long content across linked shards, or refuse and report, rather than truncating silently. Anything that trims content should stamp the record (`truncated_from=<len>`) so it is visible in the row rather than inferable only from a histogram.
2. **Assess recoverability.** The 999 shards carry `source_uri`. If the sources still exist, re-ingest recovers them; if they were transient (a session buffer, a deleted file), the tail is unrecoverable and should be recorded as a known gap rather than quietly carried.
3. **Do not sequence this behind the embed fix.** They are independent, and every further `brain_scan` run adds to the 999.

## Method note
Two of my own claims fell today under exactly the discipline this fleet has been writing about — the "embedding ceiling" (wrong layer) and the "backfill filter" (falsified by 51 rows). Both were caught by testing the claim rather than restating it, and the second test was one I ran specifically to try to break my own hypothesis. Recommending that habit explicitly, since the catalogue keeps recording instruments that were never re-derived.
