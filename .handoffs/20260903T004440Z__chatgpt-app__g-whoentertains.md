# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Propagate NouGenMsg busy-pipe retry correction and persistent relay-live notifier
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:44:40.738Z

---
The live NouGenRelay -> NouGenMsg -> Claude path exposed a second-order reliability bug after initial success: a transient busy/waiting named pipe could be misclassified as a dead session and pruned from the session registry. The bridge now retries transient pipe failures and prunes only errors positively classified as endpoint-gone. Live proof at ~20:44 EDT surfaced `NouGenMsg from NouGenMsg-blade: RETRY FIX TEST...` in-session; focused tests report 7/7. The `NouGenRelayLive` scheduled task was successfully created, so the notifier now survives logon/reboot. Durable rule for every provider adapter: transport timeout/busy is not identity death; remove registrations only on positively classified endpoint disappearance.
