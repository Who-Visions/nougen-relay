# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Correct relay diagnosis: gateway-to-git works batched; git-to-gateway state changes are lost and down-sync clobbers CLI progress
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T17:41:46.105Z

---
Evidence from Claude CLI on Blade: (1) gateway -> git works in batches and connector legs reach Blade disk with full bodies, so prior 'connector cannot read Blade git' framing was incomplete. (2) git -> gateway does not propagate state changes: CLI ack/checkpoint updates git only and gateway never learns. (3) the next gateway down-sync overwrites CLI-made git state with stale gateway state, destroying progress. This explains AGY lost checkpoint and repeated reversions after manual repair. Recommended repair order: before lease/reconcile automation, change sync semantics from whole-file overwrite to merge. Union relay events, preserve furthest-along monotonic status, never regress ack/checkpoint/completion, then add write-through from git-side state mutations back to canonical gateway/event stream. Reconcile() must not run atop clobbering sync or it will redispatch completed work. Also consolidate HUDs: three agents independently built race views; prefer one shared span/telemetry source rather than duplicate metrics stores.
