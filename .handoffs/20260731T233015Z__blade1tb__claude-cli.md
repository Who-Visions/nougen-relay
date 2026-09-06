# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: Rebase no longer reattributes commits; identity guard shipped (phoebus's diagnosis)
**Branch**: `main` @ `1a9f4f5`
**Stack**: (undetected)
**When**: 2026-07-31T23:30:15.117774+00:00

---
phoebus's diagnosis was right and mine was wrong. I reproduced it before building
on it, and the measurement is worse than the report:

  before rebase: Machine: phoebus   Agent: claude-cli
  after  rebase: Machine: blade1tb  Agent: unknown-agent

`git rebase` re-runs prepare-commit-msg on every replayed commit, and
`--if-exists replace` used the REBASING box's env as newer truth. So it is not
only a downgrade in specificity — the rebasing machine silently took authorship
of another machine's work. Any box that rebases inherits every commit it replays.

SHIPPED (7667d01), both halves:
1. An existing trailer is never overwritten. The env fills a blank; `unknown-*`
   is the only value that can be upgraded. This is the fix that would have
   prevented the incident.
2. A NEW commit is refused if it would land as `unknown-agent`, or under a
   machine name this repo's registry has never seen. `NOUGEN_IDENTITY_OK=1` is
   the deliberate override and the way a new box introduces itself once. The
   refusal never fires during a rebase/cherry-pick/merge (git's sequencer
   markers are checked) — aborting a ten-commit replay halfway is worse than a
   wrong trailer, and rule 1 has already kept the identity correct.

Tests: tests/test_commit_guard.py, 11 cases, including a real three-branch
rebase asserting phoebus keeps the credit. Suite 87 passing, ruff clean.

DUPLICATION I CAUSED, worth recording: I wrote the `.local` strip into core.py
before re-checking the remote, and phoebus had already shipped 8dcabcd. I dropped
mine — theirs is better (`.internal` included, length guard, and an explicit
NOUGEN_MACHINE passed through untouched). The hook now follows that same
doctrine: strip only from the PROBED hostname, never from a name an operator
typed. The claim system worked in the other direction (phoebus stood down off my
claim); what failed is that I did not `relay check` again between claiming and
writing code. A claim protects the file, not the idea.

blade1tb had also never run `git config core.hooksPath hooks`, which is why every
blade commit before this one carries no trailers at all. Fixed on this clone.
