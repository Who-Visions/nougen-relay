# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: MERGED by GM: NouGenRelay#19 (b29435a) - all five daemon hardenings on main; whoart/phoebus pull to inherit; daemon parity fleet-wide on next pull
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T22:49:35.035Z

---
# Daemon hardening merged to main (GM, 22:46:42Z)

Who-Visions/NouGenRelay#19 merged by WhoVisions as `b29435a` - GM-run admin merge from his own terminal after two agent-side classifier blocks (correctly: production merges are human-in-the-loop by doctrine).

**What main now carries** (all production-soaked on blade before merging, each with a regression test replaying its incident):
1. Probe-grounded verification - execution-shaped legs ack only on whitelisted read-only probes of live state judged against the leg's done-when.
2. Stale-claim guard - claims re-validate live leg status (the 66-second acked-then-claimed race).
3. Retry carry-forward - lease reclaims keep retry history; dead_letter reachable; max 3 attempts per failing leg ever (was 45/day, burned the Actions budget).
4. Attributed ack events - daemon acks write into the relay events array; no more authorless-ack illusion through event-only readers.
5. Defect/TODO guard - defect-marker legs and leading-"TODO:" queue items can never be closed by generated fleet-answers; question answers judged against the leg's own goal for responsiveness.

**Distribution:** whoart and phoebus inherit on next NouGenRelay pull + daemon restart. Their watchdogs restart-if-dead, so a pull followed by killing the old daemon PID completes rollout per machine.

**Still with the GM, unchanged:** Actions billing (checks on this PR died in 2s to the day's end - merge was on production-soak evidence), launcher choice, 2 credential exposures, reopened Keymaker decision 155326Z. Connector-side items with the worker lane: relay_read ack-field surfacing (specced), store-qualified capture receipts, receipt-shape flapping.
