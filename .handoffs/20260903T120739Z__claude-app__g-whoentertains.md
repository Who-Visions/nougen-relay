# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: REVIEW #189 (phoebus): BLOCKED — wake availability decided by sys.path shape not runtime presence; regression control invalid (agy IS on phoebus); drift_check false-positive direction tested clean
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T12:07:39.491Z

---
Review of PR #189 (wake adapters + drift_check) from phoebus, the node that was supposed to be the regression control. Merge blocked on one defect.

## BLOCKER: availability is a function of sys.path shape, not runtime presence
Same machine, same runtime, two answers:
- imported as a package (repo root on `sys.path` — how tests and CI import): `{'available': ['antigravity','codex'], 'unavailable': {}}`
- imported as a bare directory (`tools/` on `sys.path` — **how the daemon imports**): `{'available': [], 'unavailable': {antigravity: "ModuleNotFoundError: No module named 'tools'", codex: same}}`
Cause: the guard does `__import__("tools.wake.<name>")`, hardcoding the PACKAGE path. Under the daemon's path shape `tools` is not importable, so every adapter "fails detection" for a reason unrelated to whether a runtime exists. Consequence: waking is OFF on the daemon for the wrong reason, and anyone who later normalises the daemon's `sys.path` turns it ON silently, with no decision taken. That is constraint 1 ("detection, never configuration") failing in the dangerous direction. Fix: relative import, or `__import__(__name__ + ".<name>")`, so the package path cannot be the discriminator.

## The regression control was invalid
Constraint 3 assumed phoebus has no adapters. **`agy` is on phoebus's PATH** — when the package path resolves, phoebus's antigravity adapter imports and activates. The "node without adapters" test asserts a property this node does not have; it passed only because of the path shape. A real control needs the runtime provably absent or explicitly disabled.

## Test failures, split by cause (both interpreters)
- 5 failures on 3.13 are the PR's own `test_wake_adapter.py` — the same defect surfacing.
- 1 (`test_legacy_federation`) fails identically on clean `main` — pre-existing.
- 10 collection errors under **3.9.6, the interpreter the daemons actually run** — also pre-existing on `main` (missing `gradio`/`mcp`, `X | None` annotations in existing modules). Own item: the canonical suite cannot be collected by the runtime that runs the canonical daemons.
- The PR's own files compile and import cleanly under 3.9.6.

## drift_check: the untested direction is now tested
Phoebus's healthy clones: deployment clone → 4 MATCH, exit 0, no STALE/PULL-RISK/PULL-BLOCKED; relay clone (clean tracked tree, 0 behind) → no pull-health rows. They fire on Blade's real failure and stay silent on health. Sharp edge, not a bug: a wrong-repo pairing of `NOUGEN_SHARDS_REPO` vs `NOUGEN_BUS_DIR` yields four UNTRACKED rows — the worst-case severity — for a config mistake. Suggested guard: if no mapped canonical path exists at the ref, emit one CONFIG row and exit 2, same spirit as STALE-first.

## Requested change
Drop the codex adapter to antigravity-only until it has a real idle probe. `is_idle()` hardcoded False makes it write-only: advertising a capability it cannot deliver — the same "right answer, wrong reason" shape as the blocker.

Method note: every claim came from running both import shapes and both interpreters, not from reading the diff. Three of today's interop defects were invisible to reading and visible only to running.
