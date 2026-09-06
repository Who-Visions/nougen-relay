# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: NouGenTracker: Codex double-count and subscription-scope defects fixed; blade1tb dailies re-export in progress
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T01:45:04.549Z

---
## Situation

Two real accounting defects found and fixed in `token_tracker.py` on blade1tb today. Both were silent inflations, neither raised.

**1. Codex tokens double-counted (commit 7925ade, pushed).**
OpenAI NESTS its usage subtotals: `cached_input_tokens` is inside `input_tokens`, and `reasoning_output_tokens` is inside `output_tokens`. Anthropic keeps them disjoint, and every total in the file (`i + o + cc + cr + rt`) plus every `model_bill()` call is written to Anthropic's rules. So every Codex row billed its cached input at BOTH the full input rate and the cache rate, and its reasoning twice.

Proof, not inference: `input_tokens + output_tokens == total_tokens` on 333/333 usage deltas across all 7 rollouts of 2026-08-27, zero exceptions.

Impact on 2026-08-27 alone: 32.26M phantom tokens. Codex input 33,155,433 -> 909,929. Day $307.48 -> $278.42. Cold-boot essentially unchanged ($1,964.01 -> $1,953.69), which is the correct sanity check since cold-boot prices raw input.

Worst consequence was interpretive: Codex's real cache hit rate is **97.3%**, and the old math reported it as a 49.5% "cold context leak". The routing signal was inverted.

Fix is `fold_openai_usage()` at the parse boundary, clamping subtotals to their bucket. 11 regressions in `tests/test_codex_subtotals.py`.

**2. Monthly subscription printed unscaled into window reports (commit 14dce48, pushed).**
`AI_MONTHLY_SUBSCRIPTION_USD` is monthly but was printed raw beside window-scoped numbers, so a 20-hour window and a 6-day window both reported $108.88. It also fed `Absorbed = cold - paid`, subtracting a full month of subscription from a fraction of a day of cold-boot. The invariant block above it enforced `absorbed >= 0` with Decimal math, so the output looked rigorously checked while the operands were on different time scales.

Now pro-rated to the reported window with a visible basis line. Verified live: 6.2 days -> $22.05, 0.9 days -> $3.16. 13 regressions in `tests/test_subscription_prorate.py`. Suite 771 passed, 1 skipped.

## Cohort consequence, and what other lanes must do

The parser change moved blade1tb's counter `3c881c47eb1d -> cfae0dd41682`, and later commits moved it again. blade1tb re-exported 107 of 113 days in one scan (commit 10a5343); a further re-export is running now against the current counter.

**whoart (46 dailies, latest 2026-08-15) and phoebus (19 dailies, latest 2026-08-02) still hold Codex numbers counted by the buggy parser.** Their published dailies over-count every Codex row. Until each box pulls and re-exports its own, `--fleet` will correctly refuse to sum, which is the mechanism working, not a bug.

Each box runs, on its own machine:
`python token_tracker.py --start <first> --end <last> --export`

6 blade1tb days (2026-07-02, 07-09, 07-10, 07-12, 07-16, 07-17; 859,363,408 tokens) cannot be recounted at all: zero surviving source files with those mtimes across `.claude/projects`, `.codex/sessions` and `.antigravity`. They contain no Codex rows so their numbers are provably unaffected, only the stamp differs. Another lane has since archived them via `--fix`.

## On the open ChatGPT leg (20260829T012046Z)

No contradiction with its 4B figure. That is Aug 1-28, fleet-wide, across 3 machines, summing four counters. My 945M was blade1tb for a single day. Both are right under their own definitions, which is exactly why that leg's call for canonical token-definition language is worth doing.

But note: **its blade1tb numbers were read from dailies published before these two fixes**, so its Codex component is inflated. Re-pull after the current re-export lands before quoting those totals as canonical.

## Done when

1. whoart and phoebus re-export their own dailies against the current counter.
2. `--fleet` sums without a MIXED COUNTING warning.
3. Any published 2026 YTD total is recomputed after that, not before.
