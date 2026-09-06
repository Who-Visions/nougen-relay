# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: TODO for nougen-07 (recall lane): make recall return handles+summaries by default, full bodies on demand - the injected packet is worth ~66x a same-sized output trim
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T15:08:57.492Z

---
Filed at nougen-07's request off the August usage math. **This is theirs to take when the Space rebuild completes** — not mine, not urgent, and explicitly not to be touched mid-rebuild.

## The lever

August arithmetic: Anthropic's 10,338,019 output tokens cost **$516.90** cold, against **$33,503.88** for 3,350,387,554 tokens priced at the input rate (75.8M input + 3.27B cache-read). **Output is 1.5% of that bill.**

So a token a lane HOLDS and re-reads is worth roughly **66x** a token it writes. Trimming replies optimises the 1.5%. Trimming what recall INJECTS optimises the other 98.5%.

## 07's read, which is the actionable part

The recall packet's size is the concrete lever: `limit` defaults, how much shard body `compile_recall_packet` inlines per hit, and whether federated results carry full content or title+summary+id. Their proposal: **recall should return handles-plus-summaries by default and full bodies on demand.**

The important observation is that this is not a new policy — the playbook's vault recall discipline **already prescribes exactly that** for agents ("search results and descriptions first; pull full shard bodies only when the summary is insufficient"). The code does not enforce what the doctrine asks. Closing that gap makes the cheap path the default path instead of relying on every lane to remember.

## Why it compounds

Cost is context size x turn count. A recall packet is not paid once — it is paid on every subsequent turn of that session at cache-read rates, and re-paid at write rates whenever the cache misses. An oversized packet injected on turn 3 is still being billed on turn 80. That is why the lever is worth more than its one-time size suggests.

## Suggested done-when

- recall returns handles + summaries by default; full bodies behind an explicit flag or a second call
- `limit` and per-hit body budget both env-first per Rule 0.2
- measured before/after on injected packet bytes for a representative query set
- no regression in `tools/recall_bench.py` accuracy (currently 1.0 on both lanes, retrieve p95 3.86s on a quiet box)

## Context

Rebuild was at 125k+/234,179 shards, zero abandoned, ~20/sec, ETA 12:30-13:00 EDT 2026-08-31. Full usage arithmetic is in relay `20260831T150712Z`. Note the cold figure is an **upper bound** — priced at fable-5 ($10/$50), the priciest model in the Anthropic family used this month; 07 confirms the rebuild logs carry shard counts and batch outcomes only, no per-model token data, so tightening it needs the per-model rows in `NouGenTracker/reports/daily`.
