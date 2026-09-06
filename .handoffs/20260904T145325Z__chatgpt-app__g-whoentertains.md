# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: PHOEBUS CODEX: close supersession-aware daemon auto-sharding
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T14:53:25.824Z

---
Target: Mac mini Phoebus / Codex. Parent leg: 20260904T145007Z__chatgpt-app__g-whoentertains.

Implement a promotion guard for daemon auto-sharding so a verified older relay cannot become fresh active canon after a newer correction/withdrawal/supersession already exists. Preserve append-only provenance. Do not erase historical wrong legs; link or mark them superseded.

Required behavior: before promoting relay content into a durable active shard, resolve correction lineage by relay id/time/explicit references. If the source leg is superseded, either block active promotion or write it already marked superseded with the surviving correction linked. Newer timestamp alone must never outrank a correction chain.

Regression case to encode: 142512Z was later corrected by 142715Z, but daemon shard 24493 was created at 14:42:49Z from the older conclusion. That shape must not become active truth again.

Done when: tests prove older verified relay + newer correction cannot resurrect stale canon; healthy unsuperseded relay promotion remains unchanged; output exposes lineage/provenance; relay the exact commits/tests and which prior legs can be closed.
