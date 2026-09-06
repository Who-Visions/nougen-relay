# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: DONE: restore tracker dailies tree and eliminate connector 404
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T22:49:21.193Z

---
## Root cause
The HF Space deploy workflow used `delete_patterns=["*"]` while staging only the dashboard and deploy metadata. That removed the public `dailies/` tree, so the connector's correct `.../tree/main/dailies` path returned 404.

## Fixed and shipped
- NouGenTracker PR #18 merged: https://github.com/WhoVisions/NouGenTracker/pull/18
- GitHub merge: `2d98f1ed14c8c1a128ebc8305d4dda3fb100a073`
- HF deploy run: https://github.com/WhoVisions/NouGenTracker/actions/runs/33218049060 (success)
- HF Space revision: `234c0cd0ab7e743b59650b14f1dfa79dc73b0c64`
- Workflow now stages reviewed `dailies/`, refuses empty snapshots, writes `data_root`, and verifies the Hub dailies tree.

## Evidence
- 537 focused public-surface + deploy tests passed locally.
- CI passed on Python 3.10, 3.11, and 3.12.
- Live HF tree: 185 files total, 180 `dailies/*` entries.
- Live connector: `tracker_lanes()` returns blade1tb (114), phoebus (19), whoart (46); `tracker_spend(2026-08-01..2026-08-28)` returns 32,976 invocations and no 404.

## Done when
Future dashboard deploys keep the dailies tree and the post-deploy check fails if it disappears.
