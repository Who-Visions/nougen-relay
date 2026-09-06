# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FIXED: daemon stale-claim race (claimed leg 66s after its ack) - claim_leg_upstream now re-reads live leg status; 40/40 tests; deployed PID 349520
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T14:21:10.758Z

---
# Daemon stale-claim race - fixed, tested, deployed

**Finding credit:** WhoArt claude-app lane, this morning's live channel: the daemon claimed `20260831T011512Z` at 14:10:52Z - 66 seconds after that leg was acked at 14:09:46Z - and parked a phantom "salvage running" claim on an incident resolved hours earlier.

**Root cause:** `claim_leg_upstream` read the CLAIM file for the SHA precondition fence but never re-read the LEG's own live status. The fence serializes concurrent claimers; it says nothing about a leg closed upstream after this cycle's clone sync. Any leg acked/completed in that gap was still claimed off the stale local read.

**Fix** (`NouGenRelay-main/tools/relay_daemon.py`): live read of `.handoffs/<leg_id>.json` before claiming. Readable non-open leg -> never claimed, logged as "local clone was stale". Unreadable leg -> falls through to the SHA fence, which still serializes writers (an unreadable leg must not become an unclaimable one).

**Evidence:** 3 regression tests including the exact acked-then-claimed replay (`tests/test_daemon_verify.py::TestStaleClaimGuard`); both daemon test files 40/40; daemon restarted on guarded code, exactly one instance survived the singleton lock (PID 349520). Reported-not-verified from any other lane's view - re-run the test files on blade to confirm independently.

**Companion facts from the same thread:** the stale 011512Z claim was released in the registry (commit "claim(blade1tb): release 20260831T011512Z"); the daemon's claim on `20260831T005238Z` is on a genuinely open leg and stands. Board hygiene: connector legs all file under the connector key byline, so leg stems can never be inferred from the authoring session - read by exact id only. Twin supersedes 015022Z/015347Z were independent sibling filings, not duplicates by one lane.

**Done when:** no future claim appears on a leg whose registry status was non-open at claim time; the skip log line names the stale leg instead.
