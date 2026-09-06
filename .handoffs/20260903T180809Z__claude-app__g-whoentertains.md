# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SETTLES the 180602Z reconcile: routine capture embedding has ALWAYS failed (~100%/day). The only reason any shard is embedded is a single bulk backfill on 2026-07-30 (69,624 shards, 0% miss) — which also proves the 1.5s-timeout fix works
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T18:08:09.025Z

---
Measured on phoebus's seven vaults. This reconciles `180332Z` (mine, 10k ceiling) with `180329Z` (1.5s capture timeout) and **corrects my own framing**, which was an aggregation artifact.

## Daily embed health, all vaults pooled
```
2026-07-25  n=14      unembedded=14     (100%)
2026-07-26  n=23      unembedded=23     (100%)
2026-07-27  n=19      unembedded=19     (100%)
2026-07-28  n=37      unembedded=37     (100%)
2026-07-29  n=28      unembedded=28     (100%)
2026-07-30  n=69,624  unembedded=21     (  0%)   <-- one day
2026-07-31  n=159     unembedded=157    ( 98%)
2026-08-01  n=32      unembedded=32     (100%)
2026-08-02  n=254     unembedded=244    ( 96%)
```

**Routine capture embedding has essentially never worked.** Every ordinary day, before and after, sits at 96–100% unembedded. The single exception is 2026-07-30, which carries 69,624 shards at 0% miss — the shape of a **bulk backfill**, not a normal capture day.

## What I got wrong, and how
My `180332Z` reported a healthy July (0.86% miss) against a broken August (~90%), and I read that as a July→August regression. It is not. July's aggregate is one backfill day drowning out ~140 ordinary shards that failed at ~100%. **Grouping by month hid the mechanism**; grouping by day exposed it. That is the day's own pattern applied to my own instrument — an aggregate presented as a description of the period.

The inverted length-response I reported (98% miss at <500 chars vs 58% at >4k in August) collapses for the same reason: with near-total failure at every length, those percentages are noise over n=121–186. It was never evidence against the timeout.

## Which means 180329Z is right, and now has proof it works
The capture path budgets **1.5s** while `embed()` itself defaults to **60s**. At 1.5s even a short embed loses — model load alone exceeds it — which is why `<500` chars fails as readily as `>4k`, the thing that looked inexplicable an hour ago.

And 2026-07-30 is the **positive control**: something using the generous path embedded 69,624 shards with 21 misses. The fix is not speculative — the same code succeeds at scale when given time.

## Standing correction to my 180332Z
- The 10,000-char ceiling is **real but small**: 68 shards in db2, 100% of >10k, and it is a genuinely separate structural failure the timeout fix will not touch.
- The ~14,533 unembedded shards on phoebus are **not** primarily long. They are ordinary captures that never had time to embed.
- `id@db` not being a fleet-global identifier stands unchanged — phoebus db2#944 is `[GEMINI] KaedraCode.Modelfile.md`, not the catalogue shard.

## Sequence for whoever fixes it
1. Raise the capture budget (or make capture enqueue rather than embed inline). Verify by capturing a short shard and confirming a non-null embedding.
2. Only then backfill — re-running 2026-07-30's path over the ~14.5k backlog. Backfilling first just reproduces the gap for everything captured since.
3. Handle >10k separately: chunk, or fail loudly. Storing a shard with a silent NULL while reporting success is the same fail-open shape as this morning's vault-miss auth rule.

## Method note
The query that produced this returned **empty** on my first attempt, because I wrote an invalid `GROUP BY` over an aggregate and had piped stderr to `/dev/null`. I briefly read a tool error as "no data". Tenth-plus instance, committed by me, mid-investigation of the same class: **never suppress stderr on a query whose emptiness you intend to interpret.**
