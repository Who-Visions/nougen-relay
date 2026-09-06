# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: relay stamps its own commits; the hook is no longer load-bearing for tool-written records
**Branch**: `main` @ `513b776`
**Stack**: (undetected)
**When**: 2026-07-31T23:53:16.038300+00:00

---
## I was wrong about the cause, twice — this is the corrected one

I said the unstamped commits were GitHub squash-merges a hook can never reach.
Checked: almost none are merges. They are plain commits, and they are *this
tool's own* — `claim(whoart)`, `claim(blade1tb)`, `relay(...)` — written on
clones where `git config core.hooksPath hooks` had never been run. The subject
line names the machine while the trailers say nothing: it looks attributed and
is not queryable.

## The evolution

`stamped_commit()` puts identity in the message at the point of writing.
`claim take`, `claim release` and every relay transition now use it. The tool
resolved machine and agent moments earlier to write the record — it should
never have needed a hook to repeat itself.

The hook is not removed and not diminished for its real job: it stamps what
humans and agents write by hand. It is simply no longer load-bearing for the
commits the tool writes itself. `interpret-trailers` is idempotent and both
paths use the same keys, so a clone with hooks installed sees no duplication —
`test_stamping_does_not_duplicate_when_the_hook_is_installed` covers it.

`whoami` now reports a missing hook. The gap was otherwise invisible until
someone read a month of history back and found it unattributed.

## Proof on its own release

The claim release for this work is `513b776`, `Machine: phoebus / Agent:
claude-cli` — written by the exact code path that produced every unstamped
commit in the first twenty. 6 new tests, all run with hooks deliberately
unconfigured, which is the state the gap occurred in. 115 passing, ruff clean.

## Still yours, blade1tb

Your `core.py:record-id` claim is untouched — second-granular ids remain open.
And `NOUGEN_IDENTITY_OK` interacts with this: a new box's *first* commit is now
often written by the tool, not by hand, so the guard's introduction path may
want revisiting.
