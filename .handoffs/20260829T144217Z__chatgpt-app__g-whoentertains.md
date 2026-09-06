# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Make tracker current: reconcile live counters into daily upstream with freshness and lag guarantees
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T14:42:17.175Z

---
Observed from ChatGPT connector on 2026-08-29: tracker_spend for 2026-08-22..2026-08-29 reports 1,015,475,151 total_activity across 14,369 invocations, but Blade dailies only reach 2026-08-28 while the user's live counter is reportedly >2B since Saturday 17:00. The current upstream is therefore accurate for landed dailies but materially stale for 'now'.

Please fix the existing tracker path so downstream consumers can trust both correctness and freshness.

Required design:
1. Add a live reconciliation layer that merges provider/session counters with landed dailies without double counting. Use stable event/session ids or hashes where available.
2. Expose explicit freshness fields on tracker_lanes/tracker_spend/tracker_daily: generated_at, source_latest_event_at, ingest_lag_seconds, is_current, and completeness window.
3. Add an option or default behavior for tracker_spend to include current partial-day live activity, clearly marked partial/live, instead of silently stopping at the latest daily.
4. Preserve exact vs estimated token classes separately. Never coerce estimated provider activity into exact totals.
5. Reconcile live -> daily deterministically at daily close. The post-close daily total should equal the prior live accumulated amount modulo documented late-arriving events/corrections.
6. Surface per-lane reconciliation delta: live_total, daily_total, pending_unlanded, late_arrivals, duplicate_suppressed.
7. Add a precise time-window path for queries like 'since Saturday 5 PM', using event timestamps rather than calendar-day approximation.
8. Add alerts/invariants: if ingest lag exceeds a threshold or live-vs-daily delta exceeds tolerance, mark results stale/degraded instead of green.
9. Keep one canonical tracker endpoint family. Do not create parallel replacement endpoints unless unavoidable.
10. Regression test from the connector: query a rolling 24h window and compare against machine-local live counters; then verify the next daily close absorbs the same events exactly once.

Done when: a connector query for current spend returns a number no more than the accepted ingest SLA behind the live machine counters, exposes its lag explicitly, supports exact timestamp windows, and reconciles to closed dailies without duplication.
