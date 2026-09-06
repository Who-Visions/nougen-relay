# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Backfill blocker fixed: write-path quarantine merged+deploying (PR #148); final sweep to 260k underway
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T00:54:06.576Z

---
# Space replica repair, leg 3 - blade / claude-cli (Fable 5), 2026-08-30

ROOT CAUSE of the deterministic backfill failures: capture() routes writes by content hash; shards whose hash routed to the Space's malformed DB8 raised DatabaseError out of capture and /sync/push 500'd the whole batch. ~1/9 of missing content was un-ingestable by construction - the 'poison batches' were poison hash routes, same offsets failing across code versions.

FIX MERGED: PR #148 - capture quarantines a corruption-failing DB index (process-level), logs DB_DEGRADED, reroutes the write to the next healthy DB; OperationalError (locked) still raises, IntegrityError keeps its stale-index repair; /sync/push now reports per-row 'errored' instead of 500ing. Regression tests in tests/test_write_quarantine.py.

ALSO LIVE TODAY: #143 (recall perf: 14-35s -> 1.6-3.2s local), #145 (NOUGEN_VECTOR_CACHE=0 is now a loud lane switch). Deploy path CONFIRMED: a GitHub Action auto-snapshots main to the HF Space on every merge - no manual hf push; the 8/28 fetch transport break affects fetch only.

IN FLIGHT: final backfill sweep (round 4) auto-launches when the #148 build reaches RUNNING; logs/space_backfill_r4.log on blade. Expected end state: Space coverage converges toward blade's 260,551; DB8's file stays malformed-but-quarantined (recall_trustworthy=false until a storage-level wipe) while its content lives in healthy DBs.

Blade grid remains healthy (9/9 quick_check ok). ChatGPT/Perplexity connectors will see counts climb as the sweep lands.
