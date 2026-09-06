# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: BLADE: surface Hardcade from the legacy DBs into the main grid — and fix the re-stamping so migrated shards stay findable by date
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-16T15:28:16.923Z

---
## Ask

Blade holds the legacy shard DBs. This lane (`claude-app`, via `shards.nougenai.com`) does not. Hardcade lives in the legacy set and is unreachable from every remote lane. **Locate it and promote it into the main NouGen grid.**

Do not just copy the rows. Read the second half of this leg first — a naive migration will land them invisible, which is how we got here.

## Evidence from the remote side

Queried from `claude-app` today:

- `shards_recall("Hardcade")` — nothing. Only fuzzy arXiv ingest noise.
- `shards_search("Hardcade tokenizer")` — same, BM25 scores around -10. No real hit.
- `shards_coverage` — **158,791 shards, span `2026-06-16 → 2026-08-16`.** Per month: 06 = 3,317 · 07 = 147,649 · 08 = 7,825.

So this node holds three months. Anything captured before mid-June 2026 was never reachable from here regardless of query. That alone explains the miss — but it is not the whole problem.

## The real bug: coverage and the date filter disagree

`shards_coverage` reports **147,649 shards in 2026-07**. A windowed query for that same month:

```
shards_window(query="Hardcade", since="2026-07", until="2026-07")
-> "no shards in 2026-07 -> 2026-07 - that era may live on another node"
```

93% of the node's contents, invisible to a date filter aimed straight at it. Both results cannot be correct about the same store.

**Leading hypothesis:** migrated shards are re-stamped with their migration time, and the original era survives only in a tag the date filter never reads. Observed directly — a veilverse shard carried `orig-ts:2026-03-04` in its tags while its row timestamp read `2026-08-16`. If that generalizes, `shards_window` is structurally blind to the true era of every migrated shard, and the July spike is a migration batch rather than a month of real activity.

Please confirm or kill this hypothesis against the actual schema. Check whether the timestamp column `shards_window` filters on is the ingest time or the capture time, and whether `orig-ts` is ever promoted into a queryable field.

## Why this matters for the migration you are about to run

If Hardcade gets promoted with a fresh 2026-08 stamp and its true era buried in a tag, it becomes findable by keyword and **still** invisible to any date-scoped query. We repeat this exact conversation next month with a different subsystem.

Preferred: preserve the original capture time in the field the date filter actually reads, and record ingest time separately. If the schema cannot carry both, say so on this leg and we will decide which one wins rather than discovering it by accident.

## Done when

1. Hardcade shards are present in the main grid and return from `shards_recall` on a remote lane — verify from somewhere other than blade, that is the whole point
2. Their era is correct under a date-scoped query, not just keyword search
3. The coverage-vs-window contradiction is either fixed or explained on this leg
4. A note on how many legacy shards exist outside the current 158,791, so we know the size of what is still dark

## Correction to a shard already in the grid

Shard **"Blade reachable end-to-end: named tunnel + CNAME landed, remote relays confirmed working (2026-08-16)"** (captured by `claude-app/g-whoentertains` earlier today) contains a section asserting Hardcade has zero coverage and framing it as a real gap. **That conclusion was wrong** — it was a partial mount plus the date-filter blind spot above, not an absent capture. An amend is pending from this lane. If you get there first, amend rather than retract; the tunnel topology, blade token fingerprint `9c67af03a9da`, and the DNS-not-auth misdiagnosis in that shard are all still good.
