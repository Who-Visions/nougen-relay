# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: IN FLIGHT: PR #139 (codex/shards-capture-main -> main) - merging, fixing 3 F821 lint errors in core.py
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T19:58:42.619Z

---
## What I am doing right now (Claude Cli, blade1tb)
Do not touch `codex/shards-capture-main` or `src/nougen_shards/core.py` lines ~1680-1950 until this leg closes.

1. Opened PR #139: `codex/shards-capture-main` -> `main` (16 commits: grid boot, watchdog honesty, corrupt-DB read degradation, `/v1/chat/completions` router).
2. Merged `origin/main` into the branch in an isolated worktree (the push-main tree has another lane's uncommitted work - untouched). One conflict, `tools/tunnel_lane.ps1`: kept main's `Get-NodeHealth` version (it fixed the root cause - /health withholds the substrate block from unauthenticated callers) over the branch's probe-and-warn workaround. Also made `Get-NodeHealth` use `$NodeHealth` instead of the inlined `http://127.0.0.1:4444/health` (Rule 0.2).
3. Local suite on the merged tree: 635 passed, 10 failed - all 10 fail identically on the `origin/main` baseline, so the merge adds zero regressions. Pre-existing red on main: `test_auto_research` (VRAM gate), `test_models_client` (5), `test_mcp_endpoint`, `test_mcp_oauth`, `test_node_api`.
4. Merge is BLOCKED by branch protection: `Python tests` required check fails at the **Lint** step, not the tests. Three real F821s from the fan-out guard commit - `history` is undefined at `core.py:1690`, `:1815`, `:1941`. Each sits inside a `try/except Exception: pass`, so the DB_DEGRADED event silently never logs. Fixing now.

## Flagged, NOT fixed by me
- `ops/fleet-ssh-keepalive.sh:11` carries a private LAN IP and is **already on origin/main** in a PUBLIC repo. Privacy guard rates it LOW; the merge does not introduce it. Owner's call - say the word and I will send a separate PR.

## Done-when
PR #139 green on all four required checks and merged to main.
