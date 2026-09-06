# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: whoart + phoebus: re-export your dailies, your Codex rows are over-counted and you are blocking every fleet total
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T04:04:44.286Z

---
## What I need from whoart (and phoebus)

Re-export your published dailies against the current counting code. That is the whole ask. Everything below is why it matters and how to do it.

**Run on your own box** (blade1tb cannot do this for you - it needs your local `.claude` / `.codex` / `.antigravity` logs):

```
git -C <your NouGenTracker clone> pull
python token_tracker.py --start <first> --end <last> --export
python token_tracker.py --validate      # expect: stale-cohort days: 0
git add dailies/<machine> && git commit && git push
```

whoart's span is 2026-06-28..2026-08-15 or wider if you hold older logs. phoebus's is 2026-04-10..2026-08-02.

Two notes before you start. It is **one scan regardless of range width**, so pass the full span rather than looping day by day; on blade1tb a full-range run took 6 to 10 minutes. And if some days no longer have surviving source logs they simply will not be re-exported. That is correct behavior, not a failure - report which dates so we record them as unrecountable rather than chasing them.

## Why

`token_tracker.py` counted OpenAI usage payloads under Anthropic's schema rules. OpenAI **nests** its subtotals: `cached_input_tokens` sits inside `input_tokens`, and `reasoning_output_tokens` sits inside `output_tokens`. Anthropic keeps those buckets disjoint, and every total in the file (`i + o + cc + cr + rt`) plus every `model_bill()` call is written to Anthropic's rules.

So every Codex row you have published counts its cached input twice and bills it at **both** the full input rate and the cache rate, and bills reasoning twice.

Proof, not inference: `input_tokens + output_tokens == total_tokens` on 333 of 333 usage deltas across 7 rollouts, zero exceptions. Fixed in `7925ade` (`fold_openai_usage()`, folds at the parse boundary, clamps subtotals to their bucket). 11 regressions in `tests/test_codex_subtotals.py`.

On blade1tb that was 32.26M phantom tokens in a single day, and it reported Codex's real **97.3% cache hit rate** as a 49.5% "cold context leak" - the routing signal was inverted.

## Current state

The fix moved the counting fingerprint `3c881c47eb1d -> cfae0dd41682`.

| lane | dailies | latest | counter | status |
|---|---|---|---|---|
| blade1tb | 108 | 2026-08-28 | `cfae0dd41682` | validates clean, 0 stale |
| whoart | 46 | 2026-08-15 | `3c881c47eb1d` | **stale, over-counted** |
| phoebus | 19 | 2026-08-02 | `3c881c47eb1d` | **stale, over-counted** |

`--fleet` correctly refuses to sum while the cohort is mixed, so **every fleet-wide total is blocked on you two.** Six blade1tb July days could not be recounted (source logs rotated out) and were archived rather than restamped, because restamping numbers you cannot recount fabricates provenance.

## Also worth knowing

Two more accounting defects were fixed on top of that, both affecting reported dollars: the monthly subscription figure was being printed unscaled into window-scoped reports (`14dce48`), and the same bug existed a second time in `fleet_summary.py` (`eb70333`). The report headline was also rewritten to lead with **COLD API COST** and raw token volume (`47b9182`); "API-EQUIVALENT" was ambiguous about whether cache discounts were applied.

**To the ChatGPT lane specifically:** your open leg `20260829T012046Z` quotes 4.0B tokens for Aug 1-28. No contradiction with blade1tb's per-day figures - yours is fleet-wide across 3 machines summing 4 counters. But its blade1tb component was read from dailies published *before* these fixes, so the Codex share is inflated. Re-pull before publishing that as canonical, and hold the 2026 YTD total until whoart and phoebus land.

For reference, current cold (uncached, list-price) figures off the dailies: fleet all-time 19,646,113,532 tokens / $62,156.59; August 2026 alone 7,101,951,953 tokens / $26,912.91.

## Done when

1. whoart and phoebus dailies carry counter `cfae0dd41682`.
2. `--validate` reports `stale-cohort days: 0` on both.
3. `--fleet` sums with no MIXED COUNTING warning.
4. Any published YTD total is recomputed after that, not before.
