# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PR #135 (focused, Rhea + CLI + bootstrap + doctrine + init) is green except 3 CodeQL false positives needing an owner dismissal; PR #136 is the draft omnibus awaiting rebase.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T10:27:41.651Z

---
## State

Both PRs open against `Who-Visions/NouGenShards`.

**#135 — focused, ready but BLOCKED.** 9 commits cherry-picked onto current
`main`. Green on: Python 3.10/3.11/3.12, TypeScript, CodeQL (python),
CodeQL (javascript-typescript), secret scan full history, dependency scan,
zizmor, GitGuardian. Suite 670 passed / 0 failed.

Blocked only by the aggregate `CodeQL` check: 3 highs,
`py/clear-text-logging-sensitive-data`, in `tools/bootstrap.py`.

**These are false positives.** What reaches stdout is the NAME of an env var
(`OPENROUTER_API_KEY`), published in `.env.example` and the README. The taint is
inherited because `SECRETS`' keys contain KEY/TOKEN. No credential value is read
anywhere in that file — presence is membership (`name in os.environ`), enforced
by an AST test that fails the build if `os.environ.get` reappears.

Inline `# codeql[...]` suppressions were tried and **do not work**: this repo
uses default-setup code scanning, which ignores them. Verified — the alerts
re-reported on the commit that added them. Markers removed rather than left
implying a suppression that is not happening.

**Unblock requires an owner decision, one of:**
1. Dismiss the 3 as false positives in the Security tab (needs security-alert
   write access).
2. Move CodeQL to advanced setup with a query filter.
3. Stop printing unconfigured variable names — satisfies the scanner, makes the
   output less actionable. Not done without an explicit call.

**#136 — draft omnibus.** ~40 remaining sprint commits. Must be rebased onto
`main` AFTER #135 merges; they overlap under different SHAs and will conflict.
Do not mark ready before re-running the suite post-rebase.

## Regression caught during this work

Lifting `rhea_noir.py` wholesale from the sprint branch dropped main's
compose-at-round-limit pass and reverted `NOUGEN_RHEA_MAX_ROUNDS` from 8 to 4,
because that branch is 16 commits behind main. Restored. Caught by
`tests/test_rhea_loop.py`, which exists on main and NOT on the sprint branch —
the reason to verify against main, not against the branch work was written on.

## Still an operator action

The exposed OpenRouter key was shared in plaintext and must be **rotated**, then
the replacement set as `OPENROUTER_API_KEY` in the Space secrets. That remains
the actual fix for Rhea's `brain=none`, independent of either PR. Also update
`mcp_config.json`'s `openrouter-nougenai` route after rotating, or that route
will start failing.

## Not done

Legs `20260829T045608Z` and `20260829T045709Z` — gateway worker, not in this
repo. Evidence in leg `20260829T054519Z`.
