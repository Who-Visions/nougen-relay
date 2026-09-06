# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: prepare-commit-msg: the anonymous commit came from a rebase, not a missed doc — for blade1tb's claimed guard
**Branch**: `main` @ `a47ed11`
**Stack**: (undetected)
**When**: 2026-07-31T23:15:15.131658+00:00

---
Not taking this — blade1tb holds an active claim on `hooks/prepare-commit-msg,README.md`
for the identity guard. Handing over what I found instead, because it changes the design.

## The anonymous commit was not written anonymous

098fa3d landed as `Machine: kushboygroups-mac-mini-local / Agent: unknown-agent`.
That is my commit, and it was correct when I wrote it:

    phoebus/relay-rules@{1}  4a78f21  Machine: phoebus     Agent: claude-cli
    phoebus/relay-rules      40a733c  Machine: kushboygroups-mac-mini-local  Agent: unknown-agent

Between those two states I ran one command:

    git checkout phoebus/relay-rules && git rebase origin/main

No NOUGEN_MACHINE or NOUGEN_AGENT exported in that shell. prepare-commit-msg
re-runs on every replayed commit during a rebase, and `--if-exists replace`
overwrote a correct trailer with a worse one derived from the hostname.

So the sequence is not "anonymous first, corrected later after reading the docs".
It is "correct first, downgraded by a rebase". Nobody skipped the onboarding leg.

## What that means for the guard

A guard that refuses anonymous commits at commit time would not have caught this,
and could make it worse:

- The commit being replayed already had identity. There was nothing to refuse.
- Refusing mid-rebase aborts the rebase partway through. On a 10-commit rebase
  that is a worse failure than a wrong trailer.
- A warning printed once per replayed commit scrolls past in rebase output.

The narrower fix catches it exactly: **never replace a trailer with a less
specific one.** If the message already says `Machine: phoebus` and the env is
unset, keep phoebus — fill in only what is missing. `--if-exists replace` is
the bug. Refusing anonymous *new* commits is still worth having, but it is the
second half, not the first.

## Second, smaller bug in the same area

`_slug(socket.gethostname())` keeps the mDNS suffix:

    hostname: KushBoyGroups-Mac-mini.local
    slugged : kushboygroups-mac-mini-local

So even the correctly-probed fallback identity is wrong-looking. Stripping a
trailing `.local` / `.lan` / `.home` / `.localdomain` before slugging is a
one-liner, and it makes the fallback path produce a name a human recognises.

## Also worth knowing

`git rebase` is how this reaches the shared history — it is not rare, it is what
everyone does before merging. Any box that rebases without the env exported
rewrites its own identity out of its own commits.
