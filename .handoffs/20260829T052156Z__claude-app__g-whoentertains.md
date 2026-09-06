# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Unify token counters across tracker connector and machine wide reports
**When**: 2026-08-29T05:21:56.540Z

---
FINDING: ChatGPT connector tracker_spend for 2026-08-22..2026-08-29 reports 994,889,354 total_activity across blade1tb, phoebus, whoart. Shards preserve a richer machine-wide tracker snapshot for Sat 2026-08-22 through Fri 2026-08-28 at 1.166B blended tokens, composed of 734M exact + 432M estimated, with Antigravity estimates included. These are different accounting surfaces, so the user can correctly remember crossing >1B while the connector appears below 1B. Known related gaps: active session activity may exist before a daily is published, free-fleet/ledger calls have been invisible in some reports, and stale lane exports can block or distort fleet sums.

ROOT DEFECT: there is no single canonical fleet token counter contract exposed consistently to CLI/dashboard/MCP. tracker_spend currently surfaces published daily exact activity, while richer reports may blend exact + estimated and unpublished/current-day activity. This creates contradictory headline totals.

FIX REQUEST:
1. Define one canonical counter schema/version for fleet throughput, with explicit fields: exact_tokens, estimated_tokens, blended_total, cache_read, cache_creation, fresh_input, output, reasoning where applicable, invocations, coverage window, generated_at, lane freshness, partial/unpublished flags, and provenance per lane.
2. Make MCP tracker_spend consume the same canonical summary object as token_tracker/fleet_summary instead of independently summing a narrower daily subset.
3. Include active/current-day partials safely, or clearly expose published_total vs live_total rather than silently omitting live activity.
4. Reconcile Antigravity estimated usage into the same API response with estimated provenance instead of excluding it from headline throughput.
5. Detect stale lane exports and telemetry holes. Return warnings naming the lane and last export date. Never let a stale lane silently masquerade as a complete fleet total.
6. Fold fleet/free-lane ledger usage into the canonical counter or explicitly mark it unavailable. Zero should mean measured zero, not missing telemetry.
7. Support time-of-day windows, specifically user asks like 'since Saturday 5 PM', rather than daily-only boundaries. If source granularity prevents exact cutoff, return lower/upper or partial estimate with provenance.
8. Add invariant tests: CLI, dashboard, shard-captured report, and MCP queried for the same frozen window must return the same blended_total and exact/estimated split. Regression fixture should reproduce this 994.889M vs 1.166B discrepancy and fail until unified.
9. Preserve the Jevons reporting order separately from accounting: TOTAL TOKENS is the hero metric, but it must be one authoritative number everywhere.

DONE WHEN: For any identical window, all public surfaces agree on the same canonical blended throughput, expose the same exact/estimated decomposition, flag freshness/coverage gaps, and can explain precisely why a number differs if live partials or unavailable telemetry remain.
