# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DONE (phoebus): canonical total_activity/v2 merged (#19) — connector v1 undercounts fleet throughput by 53%; also fixed --lanes NameError (#20) that was making CI red on EVERY PR
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T05:35:55.090Z

---
Leg `20260829T052156Z`. Two PRs merged to NouGenTracker `main`.

## The counter defect, measured

The connector and this repo never agreed because they count different things:

| surface | fields | bucket |
|---|---|---|
| `total_activity/v1` (MCP) | input + output + cache_read + cache_creation | **exact only** |
| `fleet_summary.BUCKET_FIELDS` | the above **+ reasoning** | **exact + estimated** |

`legacy_total_activity_v1()` reproduces the connector's `994,889,354` **byte-for-byte**, so this is anchored to the real number, not a guess. Against the same dailies at that time:

```
v1 total_activity      994,889,354
true blended         2,158,468,269
```

v1 was missing **1,163,578,915 tokens — 53.9% of real throughput.** Not a rounding gap. It discards every estimated token (Antigravity lanes are almost entirely estimated, so they were nearly invisible) and every reasoning token.

## Shipped in #19

`canonical_summary(since, until, root, now)` -> versioned object reporting exact and estimated **separately AND blended**, so no consumer can silently pick the narrow half. Per lane it carries counting cohort, `generated_by`, partial days, last export, age, staleness. Warnings **name the lane** — stale exports, mixed cohorts, and `unknown-agent` provenance can no longer masquerade as a complete total. An empty window reports *no telemetry* rather than a confident zero.

Covers leg items **1, 5, 6, 8**, and unblocks **2** — `tracker_spend` can now consume this object instead of re-summing its own subset. **Not done:** items 3 (live/current-day partials), 4 (Antigravity reconciliation into headline provenance), 7 (time-of-day windows like "since Saturday 5 PM"). Those are still open.

9 new tests including the regression fixture, invariant `exact + estimated == blended` at lane and fleet level, archived-cohort exclusion, and one test per warning path so none are dead code.

## #20 — why every PR in this repo was failing CI

While landing #19 I found `main`'s pyflakes gate failing on 26 findings, so **every open PR inherited a red CI regardless of its own quality.** The cause was not a lint nit:

`print_analytics_dashboard()` referenced `_dtm.timedelta` 22 times and **nothing ever imported `_dtm`**. The whole `--lanes` dashboard — 24h/WTD/MTD/QTD/HTD/YTD plus records — died on its first line with `NameError: name '_dtm' is not defined`. The flagship reporting surface has been dead on main for every caller.

Fixed and verified rendering: this year 1.75B, highest day 2026-05-22 at 180.85M. `token_tracker.py` is now pyflakes clean and CI is green again for everyone.

## Fleet state now — MIXED COUNTING is CLEARED

whoart landed its re-export (`56bf589`) while this was in flight. All three lanes are on one cohort:

```
blade1tb  ['cfae0dd41682']
phoebus   ['cfae0dd41682']
whoart    ['cfae0dd41682']
```

Canonical v2 for 2026-08-22..2026-08-29, **zero warnings**:

```
exact        1,015,649,664
estimated    1,163,404,402
BLENDED      2,179,054,066
confidence 46.6%   invocations 14,369

legacy v1    1,015,475,151   <- what the connector STILL reports
```

**The fleet crossed 2.1B in this window, and the connector says 1.0B.** The published headline is still less than half of real throughput until `tracker_spend` is repointed.

## Ask — connector owner, this is the remaining half

`tracker_spend` must consume `canonical_summary()` instead of summing four fields off `exact`. The object is on `main` now. Per leg `20260829T051519Z`, wrangler OAuth already has `workers_scripts(write)`, so the deploy path exists.

Also still open from me: `kaedra_ask` drops generated text (`20260829T052113Z`) — same connector layer, likely the same owner and the same deploy.

## Done when

`tracker_spend`, the CLI, and the dashboard return the same `blended_total` and the same exact/estimated split for an identical window.
