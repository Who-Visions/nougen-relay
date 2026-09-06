# 🤝 Git Handoff — whoart / claude-cli

**Goal**: a registry that exists is not shared; and the session fix that did nothing until it read the harness
**Branch**: `main` @ `1b7dfd5`
**Stack**: (undetected)
**When**: 2026-08-04T05:59:05.912150+00:00

---
TWO FAILURES THAT REPORT SUCCESS, BOTH CLOSED. AND THE FIRST FIX FOR ONE OF
THEM DID NOTHING, WHICH IS THE PART WORTH READING.

1. A REGISTRY THAT EXISTS IS NOT A REGISTRY THAT IS SHARED.

NouGen carried 130+ handoff records under a `.handoffs/` line in .gitignore
since June. The directory was there, so `registry.exists()` was true, `relay
adopt` reported "registry already present", and it installed hooks with nothing
to publish into. Every check said covered. Not one leg ever left the box that
wrote it.

`exists()` is a filesystem question. Whether the fleet can READ it is a git
question, and nothing was asking it. adopt and guard now both ask. An ignored
registry is reported and deliberately does NOT resolve itself — only a human
decides which records are worth sharing. Fixed in NouGen by narrowing the
ignore to the pre-relay naming; the 130 legacy records stay local, anything
relay writes is shared.

Check any repo in one line:  git ls-files .handoffs | wc -l
Zero, with records on disk, means the registry is inert.

2. TWO SESSIONS ON ONE LANE, AND THE RELEASE THAT TOOK THE WRONG CLAIM.

Claim identity is machine+lane. Two Claude Code sessions ran on whoart as
`claude-cli` at once — invisible to each other, and a bare `claim release` in
one freed the other's claim mid-work. That is what released MY claim twice
today, and it is also why phoebus and I have been stepping on each other in a
way the registry could not explain.

MY FIRST FIX WAS INERT AND I SHIPPED IT ANYWAY. I added a `session` field
sourced from NOUGEN_SESSION. Correct logic, and both colliding sessions had
NOUGEN_SESSION unset — as did mine. Minutes after pushing the mitigation, the
sibling released my claim A SECOND TIME. A mitigation that requires
configuration nobody applied prevents nothing.

The working version reads what the harness ALREADY exports:
CLAUDE_CODE_SESSION_ID is in every tool call and matches the session's own
scratchpad directory. Zero configuration. Verified live — a claim taken after
the change records session c158477b, which is this session.

Rules I would keep if you extend this:
  - OMIT the field when nothing answers. Never write an empty string. "A
    different session" and "nobody recorded one" need different answers.
  - Only VERIFIED env vars go in the fallback list. One that is usually unset
    makes the mechanism look configured while doing nothing — the same failure
    one level up.
  - A fleet that sets nothing must behave exactly as before. That regression
    test matters more than the feature; three machines run this today.
  - `--all-sessions` exists because a guard that cannot be overridden gets
    uninstalled.

TEST BUG WORTH KNOWING ON ANY WINDOWS BOX: I built claim filenames in a test
helper from a timestamp alone. Windows clock granularity is coarse enough that
two consecutive calls produce the SAME value, so the second record silently
overwrote the first — and a test asserting "both were released" passed while
reading one file twice. The product was never exposed: unique_record_name
already disambiguates with an in-timestamp counter. The helper reimplemented a
product invariant and inherited none of its guarantees.

238 passed, 4 skipped, 1 xfailed.

CORRECTION TO MY LAST LEG: I said NouGen had three stale worktree registrations
pointing into a deleted scratchpad. Wrong — I assumed instead of checking. All
three directories exist, one (ngs-rel) has uncommitted changes, and `git
worktree prune` correctly removed nothing. They belong to session 2a158210.
Leave them alone. Same error I have now made twice this week: matching a
plausible story to a symptom and reporting it as identification.

Also: NouGen's remote pointed at the pre-rename who-visions/nougenshards and
printed "This repository moved" on every push. Now Who-Visions/NouGenShards.

STILL OPEN: DaveWhoSpace has relay coverage locally but cannot be pushed — its
HF Space remote carries an embedded hf_ token that no longer authenticates. The
token should be revoked and taken out of the remote URL, not refreshed in place.
