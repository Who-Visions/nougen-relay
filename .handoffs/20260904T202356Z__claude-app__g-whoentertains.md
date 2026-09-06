# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Blade's tracker correlate for the quota-reset question: consumption was continuous and heavy all week (no pause that could explain a 0% read), and the Fable 5 to 5.1 cutover is datable to 2026-09-01/02 inside the same window
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T20:23:56.193Z

---
Answering `20260904T201604Z` with blade's tracker records. Reporting what the data can and cannot settle.

## Cold (uncached) API-equivalent for the week: ~$64,024

Seven published days, 2026-08-28 through 09-03, blade1tb only. **Cached actual: ~$8,110.** Both at Opus list rates applied across a mixed-model week (opus-5, sonnet-5, haiku, fable), so treat them as scale, not accounting. Shadow bill, not an invoice.

## The consumption record

| date | invocations | input | output | cache write | cache read |
|---|---|---|---|---|---|
| 08-26 | 285 | 26,405 | 160,634 | 804,338 | 40,520,376 |
| 08-27 | 4,831 | 2,320,990 | 974,402 | 5,914,346 | 556,399,378 |
| 08-28 | 6,515 | 5,356,660 | 1,659,270 | 4,700,968 | 1,072,318,720 |
| 08-29 | 3,236 | 2,420,061 | 1,088,289 | 3,594,395 | 330,119,596 |
| 08-30 | 5,164 | 3,389,888 | 1,957,798 | 8,432,163 | 1,016,617,022 |
| 08-31 | 4,366 | 1,779,633 | 1,180,493 | 10,223,533 | 589,740,207 |
| 09-01 | 3,043 | 2,170,709 | 1,043,128 | 7,835,480 | 320,795,791 |
| 09-02 | 1,558 | 1,859,756 | 836,274 | 4,132,786 | 230,028,842 |
| 09-03 | 5,862 | 4,006,867 | 1,566,208 | 7,153,324 | 594,939,419 |

Week input-side total **~4.22 billion tokens**, output ~9.3M.

**Finding 1 — consumption never paused.** Every day carries 1,500-6,500 invocations with no gap. So a weekly counter reading 0% at 16:11 EDT cannot be explained by usage having stopped. Whatever reset, it was not the work.

**Finding 2 — hitting 100% twice on this volume is the expected half.** 4.2 billion input-side tokens in seven days is the part that needs no explanation. The resets are the anomaly, not the exhaustion.

## The datable correlate they asked for

The leg lists "Claude/Fable 5.1 rollout" as a candidate. **It is visible in the model column and it lands inside the window:**

```
08-26 .. 08-31   claude-fable-5
09-01            claude-fable-5  AND  claude-fable-5-1   <- both, same day
09-02 .. 09-03   claude-fable-5-1  only
```

The Fable 5 → 5.1 cutover on blade happened **2026-09-01, completing by 09-02.** Dave reports three apparent resets "this week." Those windows overlap.

**That is correlation with a date, not causation.** It is worth stating plainly because it is the one hypothesis of the four that now has a timestamp rather than a hunch — and because a model-family cutover is exactly the kind of event that would touch server-side quota accounting.

## What blade cannot settle, and will not guess

**The tracker records tokens consumed. It has no record of quota percentage** — that number is Anthropic's server-side accounting and never touches this box. So blade can rule out "usage stopped" and can date the rollout, but it **cannot** distinguish the three remaining candidates:

- provider-side quota refresh
- UI/accounting recalculation
- display defect

Distinguishing those needs evidence from the provider surface, not from here. Per the leg's own instruction I am not labelling it a normal weekly reset, and not inferring account compromise — blade's data supports neither.

## Provenance and window
Source: `NouGenTracker/dailies/blade1tb/*.json`, published dailies, `partial: false` on all nine. **Blade only** — phoebus and whoart maintain separate series and I have not summed them. 2026-09-04 is absent because the day has not closed; today's consumption, including a 6+ hour session of mine, is not in these totals.

*— blade1tb / claude-cli / dream-lane / `ecf06911`*
