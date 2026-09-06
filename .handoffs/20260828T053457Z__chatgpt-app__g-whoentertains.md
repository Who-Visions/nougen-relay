# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Add invariant: monthly shard coverage should be dense from Oct 2025 onward
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T05:34:57.520Z

---
Additional critical context from Dave: every month since October 2025 had hundreds of code executions that should have been sharded. Therefore March 2026 showing zero proven bounded memories cannot be treated as a quiet-month possibility.

Observed immediately after this clarification:
- shards_coverage() itself timed out with `Error: The operation was aborted due to timeout`.
- Earlier bounded Griot query for March 2026 returned total=12, held_back=12, shown=0.
- Follow-up Griot attempt to expose those candidates timed out in recall.
- Direct raw-grid attempt for March also timed out.
- Rhea /agent path previously returned 500.

Expected invariant for debugging:
1. From 2025-10 through present, month-level coverage should be dense, likely hundreds of code-execution-derived records per month.
2. If month counts are sparse/zero, investigate mount completeness, ingestion jobs, timestamp normalization, source-created timestamps, and index rebuild history before concluding data absence.
3. Coverage endpoint must return quickly even when recall/index search is degraded; it should operate from precomputed metadata or cheap DB aggregation.
4. Add diagnostics per month: raw row count, indexed row count, rows with event_time, rows with source_created_at, rows only carrying captured_at, undated rows, and source-store/db_index breakdown.
5. Add an integrity audit for Oct 2025 onward that compares source execution/log inventory against shard inventory and reports missing IDs/time spans.
6. Held-back temporal candidates need inspectable metadata so we can repair provenance rather than losing them behind a count.

Done when: coverage succeeds without timeout; Oct 2025 onward is enumerated month by month; March candidates are inspectable; provenance gaps are classified; missing ingestion can be backfilled without overwriting historical timestamps.
