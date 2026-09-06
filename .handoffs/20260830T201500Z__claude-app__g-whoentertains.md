# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CLOSED: PR #139 squash-merged to main (10b755a) - grid boot, watchdog honesty, corrupt-DB degradation, /v1 router
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T20:15:00.427Z

---
## Done
PR #139 merged to `main` at `10b755a`. Closes my in-flight leg `20260830T195842Z` - `codex/shards-capture-main` and `core.py` are free again.

Squash, not merge: `main` has `required_linear_history`, so merge commits are rejected. A local rebase of the 17 commits conflicted immediately, so I squashed and put the full commit list in the body rather than fighting it.

## Fixed on the way in
`core.py` imports `history` per function, not at module level. Three degrade handlers (`locate_shard`, `decay_utility_scores`, `retrieve_semantic_rules`) called `history.log_event()` with no import, inside `try: ... except Exception: pass` - so the NameError was swallowed and DB_DEGRADED never reached the ledger while the suite stayed green. Only ruff F821 caught it, at the CI gate. Added the imports plus an AST invariant in `test_grid_fanout_guard_invariant.py` (verified against a negative control).

Merge conflict `tools/tunnel_lane.ps1`: kept main's `Get-NodeHealth` (root cause - /health withholds substrate from unauthenticated callers) over the branch's probe-and-warn workaround, and pointed it at `$NodeHealth` instead of an inlined `127.0.0.1:4444`.

## Verified on merged main
Tree byte-identical to the tested branch head. ruff clean. 4/4 required checks green. Local suite 636 passed / 10 failed - all 10 reproduce identically on the pre-merge `origin/main` baseline (env-dependent: auto_research VRAM gate, models_client x5, mcp_endpoint, mcp_oauth, node_api). They pass in CI.

## Still open for whoever owns it
- `ops/fleet-ssh-keepalive.sh:11` has a private LAN IP, already on `main` in a PUBLIC repo. Guard rates it LOW. Not introduced by this PR; needs its own one-line PR.
- The push-main working tree has another lane actively editing right now (18 modified, ~26 untracked, growing during my session). Untouched by me.

## New standing rule
NouGen Rule 0.3 "Keymaker First": ask `agent_secrets.db` (unwrap DPAPI in a loop) before ever asking the GM for a credential. Added to `NouGen/CLAUDE.md`.
