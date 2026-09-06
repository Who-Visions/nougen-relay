# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: GM decisions for Phase B: push/PR and make relay-live persistent
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T02:52:46.427Z

---
Dave's operator decisions on the Phase B handoff:

1. YES: push `claude/daemon-hardening` and open the PR for commit `881a591` after confirming the reported 345-green suite is still green on the exact branch head. Include the lease/fencing/admission/sweeper changes and the batched pre-commit claim-read speedup in the PR evidence.

2. YES: fix the `NouGenRelayLive` scheduled task so it is persistent. Remove the 72-hour execution limit, configure restart-on-failure with a sane bounded interval, preserve the existing hidden/background/no-focus behavior, and do not reintroduce visible PowerShell/cmd windows. Inspect current task settings first, mutate minimally, then verify the effective task settings and a live restart. Prefer no execution time limit (`ExecutionTimeLimit` equivalent of zero) and restart-on-failure; do not destroy unrelated existing settings.

3. After restart, verify the running relay-live/daemon path is actually on the new code, not merely that the branch exists. Capture exact process/task evidence, commit/PR refs, test counts, and any rollback command.

4. Then stop the fat session and let a fresh Claude session pick up the remaining Hardcade/FleetThoughts/Xoah/HF/Codex legs from the relay. Do not burn the old context just because the queue exists.

GM note: the work is landing. Keep the same quality bar: live, reversible, evidence-backed, no terminal flash.
