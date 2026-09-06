# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CONNECTOR FIX 3/4 (tracker_spend): fold the estimated bucket and reasoning into totals — total_activity/v1 undercounts real fleet throughput by 53.9%
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T15:26:33.404Z

---
Three of four independent connector fixes, dispatched in parallel. **Self-contained — touches `tracker_spend` and the `totalActivity` helper.** Full analysis in `20260829T053555Z` and `20260829T060021Z`.

## Exact patch sites

`nougen-fleet-mcp` line 564:

```js
var TOTAL_ACTIVITY_DEF = "input_tokens + output_tokens + cache_read + cache_creation";
var TOTAL_ACTIVITY_VERSION = "total_activity/v1";
function totalActivity(t) {
  return (t.input_tokens || 0) + (t.output_tokens || 0) + (t.cache_read || 0) + (t.cache_creation || 0);
}
```

and line 1569, inside `tracker_spend`:

```js
const e = daily.exact || {};
totals.input_tokens    += e.input_tokens    || 0;
totals.output_tokens   += e.output_tokens   || 0;
totals.cache_read      += e.cache_read      || 0;
totals.cache_creation  += e.cache_creation  || 0;
```

**`daily.estimated` is never referenced anywhere in the summing path** — only `daily.exact`, at lines 1520 and 1569.

## The size of the error

Measured over 2026-08-22..2026-08-29 against live dailies:

```
v1 total_activity      994,889,354
true blended         2,158,468,269
```

**Missing 1,163,578,915 tokens — 53.9% of real throughput.** Two exclusions:

- **all estimated usage** (1,163,404,402) — Antigravity lanes are almost entirely estimated, so they were nearly invisible
- **all reasoning tokens** (174,513)

The reasoning omission is at least documented in the tool description. **The estimated omission is documented nowhere and is by far the larger half.**

## Patch

```js
const e = daily.exact || {};
const s = daily.estimated || {};
for (const k of ["input_tokens","output_tokens","cache_read","cache_creation","reasoning"]) {
  totals.exact_tokens     += e[k] || 0;
  totals.estimated_tokens += s[k] || 0;
  totals[k]               += (e[k] || 0) + (s[k] || 0);
}
totals.blended_total = totals.exact_tokens + totals.estimated_tokens;
```

Retire `total_activity/v1` for `total_activity/v2` so no consumer silently reads v1 semantics from a v2 payload.

## Mirror the Python side — do not invent a second shape

`fleet_summary.canonical_summary()` already landed in NouGenTracker (`a2ceae3`, PR #19) and emits exactly this: exact and estimated **separately AND blended**, plus per-lane counting cohort, `generated_by`, partial days, last export, age and staleness. **Use those field names** so CLI, dashboard and MCP are diffable.

The regression fixture exists: `tests/test_canonical_counter.py`, and `legacy_total_activity_v1()` reproduces the current worker number **byte-for-byte** — so the patch can be proven against the real value rather than a guess.

## Done when

`tracker_spend`, the CLI and the dashboard return the same `blended_total` and the same exact/estimated split for an identical window. Right now the fleet crossed **2.1B** in that window and the connector reports **1.0B**.
