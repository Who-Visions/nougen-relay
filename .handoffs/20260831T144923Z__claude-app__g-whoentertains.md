# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FIXED: daemon retry thrash root cause - acquire_lease reset retry_count on every reclaim, making dead_letter unreachable; carry-forward + 4 tests deployed
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T14:49:23.347Z

---
# Retry thrash fixed at the lease layer

**Finding credit:** claude-app connector lane - 148 `retry_pending` releases vs 17 `complete` since 08-30, single legs claimed 45/43/20 times, ~108 no-op CI runs, Actions billing exhausted.

**Root cause** (`NouGenRelay-main/src/nougen_relay/core.py`): the backoff and dead-letter machinery was all present and correct (max 3 retries, exponential backoff to 300s) but unreachable - `acquire_lease` built every RECLAIMED lease as a fresh record with `retry_count: 0`. Fail, release retry_pending(1), backoff elapses, reclaim resets to 0, forever. The ~10-minute cadence claude-app measured is exactly backoff-cap plus heartbeat.

**Fix:** reclaims now carry `retry_count`/`max_retries` forward from the inactive lease, and an exhausted or dead-lettered leg is refused at the lease layer (`acquire_lease` returns None without force). Third failure = dead_letter, permanently. Human-addressed relay-watch TODOs the daemon can never complete now cost at most 3 attempts instead of infinity.

**Evidence:** `tests/test_retry_carryforward.py` - 4 tests including the full three-failures-across-reclaims dead-letter path and the backoff-window block; 60/60 across all lease/claim/daemon test files; daemon restarted on the fix (stable singleton holder PID 4124). Reported-not-verified from other lanes: re-run the test files on blade.

**CI-bill note for GM:** with the ceiling live, claim-commit volume drops to at most 3+1 commits per failing leg ever, not 45+/day. Existing thrash legs (015318Z/011512Z targets already released or corrected) will dead-letter within 3 cycles if re-picked.

**Not fixed here, other lanes:** registry re-truncation past 1,000 files (claude-app leg 20260831T144115Z, worker lane); PR #152 CodeQL conversation block (nougen-71 lane); credential rotations (GM, ledger state reported separately).
