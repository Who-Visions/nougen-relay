---
name: nougen-relay
description: Coordinates work across the machines that share a repo (whoart, blade1tb, phoebus). Claims scope before editing files and writes a handoff after. Use whenever starting work in a git repo that contains a .handoffs directory, before editing any file, and before ending a working session.
---

# NouGenRelay — do not start work blind

Several machines work these repos at once, each running its own agent lane.
They do not see each other's screens; they see this registry. On 2026-07-31 the
same work was done **twice on three separate occasions** — the app scaffold, the
handoff tooling itself, and an OAuth host fix — because handoffs were written
when work *ended* and nothing announced work *beginning*.

You have no hook system. Nothing will stop you. That makes following this your
responsibility rather than the harness's.

## When this applies

Any git repo containing a `.handoffs/` directory. Check once at the start of a
session; if it is there, this skill governs the whole session.

## Before you touch a file

```
relay_check           → has another machine moved? did histories diverge?
relay_claim_list      → what is someone else working on RIGHT NOW?
relay_claim_take      → announce your scope BEFORE editing
```

`relay_claim_take(scope, goal)` — `scope` is the paths or topics you are about
to touch, `goal` is why. **If it refuses, that refusal is the product.** Another
machine holds an overlapping scope. Read their claim, then either stand down and
pick different work, or decide deliberately to override. Do not retry with a
narrower string to slip past it.

Standing down is a success, not a failure. Two lanes did exactly that today and
each saved the other a duplicated guard.

## While working

```
relay_open            → legs another machine handed over and nobody picked up
relay_ack             → take the baton on one; it stays open until someone does
```

## Before you go quiet

```
relay_claim_release   → free your scope
relay_create          → what you did, and where you left off
relay_shards          → publish what you LEARNED, not just what you did
```

Then commit and push `.handoffs` so the other machines can actually read it —
a record that never leaves your box protects nobody.

`relay_shards` is the other half of that sentence. A handoff says where you left
off; the shard vault holds what you found out, and it is local — no other machine
can open it. The tool reads it and writes `docs/FLEET-LOG-<date>.md`, which does
travel. Push that too. It withholds brand/personal shards and refuses to write
credential-shaped values; `dry=True` shows the log without writing it.

## Identity

Run `relay_whoami` if anything looks wrong. Records are stamped with a machine
and an agent lane. `NOUGEN_AGENT` has no OS equivalent, so if it is unset your
records land as `unknown-agent` — that has already happened once in a live
registry. The machine name comes from the hostname unless `NOUGEN_MACHINE` says
otherwise; on the Mac mini it must be `phoebus`.

## Writing a good handoff

State what is DONE, what is DELIBERATELY NOT done and who holds it, and what the
next lane should know that is not obvious from the diff. Include evidence —
commit SHAs, test counts, what you verified rather than assumed. A handoff that
says "made some changes" costs the next lane the same investigation you just
finished.
