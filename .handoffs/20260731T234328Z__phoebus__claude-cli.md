# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: hook's suffix strip was GNU-sed-only: fixed, plus platform-independent guards
**Branch**: `main` @ `da06391`
**Stack**: (undetected)
**When**: 2026-07-31T23:43:28.987869+00:00

---
## The guard was refusing every Mac commit

`hooks/prepare-commit-msg` stripped the network suffix with

    sed 's/\.\(local\|lan\|home\|internal\|localdomain\)$//'

`\|` alternation is a GNU extension. BSD sed matches it literally, so on macOS
the strip no-opped, this box derived `kushboygroups-mac-mini-local`, and the new
unknown-machine guard correctly refused it. Any Mac committing without
NOUGEN_MACHINE exported was blocked. Suite was 87 on Windows and 86+1 failing
here — `test_a_probed_hostname_drops_its_network_suffix`.

Replaced with a POSIX `case`, which needs no sed. 91 passing on Darwin, ruff clean.

## Why the existing test could not catch it

It depends on the real hostname of the box running it, so it only ever fails on
a machine whose hostname carries a suffix. On Windows and Linux it is dead
weight. Two new guards in `tests/test_hook_portability.py` fire anywhere:

- an assertion that the hook contains no GNU-only sed alternation or flags
- a PATH shim for `hostname`, so every box exercises `probe-box.local` and
  `build.corp.example.com` identically

Both fail against the previous hook. The FQDN case still keeps its domain.

## Verified, not assumed

Rule 1 holds. I rebased this commit onto main with NOUGEN_MACHINE exported and
the trailer survived as `phoebus` — the same operation that produced the
original incident. blade1tb's fix does what it says.

## Attribution correction

`8dcabcd` ("A network suffix is not part of a machine's name") is recorded in
the correction shard as phoebus's. It is not: author and committer are Dave
Meralus, co-authored by Claude Fable 5, and it carries no Machine/Agent
trailers at all. I published the `.local` finding in
20260731T231515Z__phoebus__claude-cli and that lane picked it up — good outcome,
wrong credit. Worth fixing in the shard, since the whole incident is about
attribution being trustworthy.

That commit having no trailers also means a third box has never run
`git config core.hooksPath hooks` — same gap blade1tb found on itself.
