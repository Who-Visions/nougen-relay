# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Relay triage rules: escalate-on-repeat, contest-don't-duplicate, no expiry, oldest-first sort — plus answer whether non-GM lanes can ack at all
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T00:23:07.199Z

---
## Situation

10 legs open, 4 lanes filing (ccr, outpost, mondy, g-whoentertains), **1 acker** — GM. Every ack in the registry is his. The relay is functioning as four inboxes pointing at one human. Triage rules below were war-gamed against the actual 10-leg queue; two of three naive versions failed and are corrected here.

## BLOCKER — answer this before implementing anything below

**Can non-GM lanes ack, or do they only have write?**

If ccr/outpost/mondy lack ack capability (permission, token scope, or tool absence), every rule below is decoration — it sorts GM's inbox faster and changes nothing. If they *can* ack and don't, it's a lane-prompt problem, not a relay problem, and the fix is in the lane instructions, not the registry.

Whoever takes this leg: verify first, report the answer, then implement.

## Rule 1 — auto-legs escalate on repeat (do NOT just demote)

Naive version was "session-end dirty-tree notices are telemetry, route them out of the ack queue." That fails: the two `[auto]` legs (8 and 10 uncommitted files on NouGen@main) describe the SAME condition ccr filed a human TODO for at 20260816T155447Z — the recurring dirty tree in `tools/nougenai_*`. Demote silently and the condition persists until a pull eats it.

- Session-end / dirty-tree notices demote out of the ack queue **by default**
- **Third consecutive** occurrence with the same dirty path promotes to a real leg
- Once is telemetry; three times is a pattern nobody is fixing

## Rule 2 — contest, don't duplicate

Naive version was "if a leg names an owning lane, other lanes append instead of opening a new leg." That fails: outpost claimed the stash at 20260815T220000Z. Seventeen hours later it was still unpopped, and ccr filing again (155444Z/155447Z) was the ONLY evidence the owner had gone quiet. Dedupe by owning-lane and you suppress exactly the stall alarm you need.

- A second lane filing against an owned leg does **not** open a new leg
- It flips the original to **contested** and timestamps the challenge
- Same dedupe, opposite information flow — the owner's silence becomes visible instead of hidden

## Rule 3 — NO age-based expiry (rejected)

Sort the queue by how unpleasant the work is. The secrets-vault leg (20260815T215327Z — `NOUGEN_SECRETS_VAULT_DIR` moves on pulling NouGenShards main, `get_secret` returns None, reads as "never ingested") is the most expensive and least fun item on the board. It is unacked *because* it is hard.

Age-based expiry is a machine that reliably deletes the hardest problems and reports the queue as healthy. Then someone pulls main mid-cutover and every credential reads as never ingested.

- Do not implement expiry
- If anything ever expires, it is the cheap stuff
- Expensive legs should get **louder** with age, not quieter

## Rule 4 — relay_open sorts oldest-first

Currently newest-first, which scrolls the oldest and ugliest work off the bottom. Invert it: age ascending, oldest at top where it cannot be scrolled past. Contested legs pin above everything.

## Done-when

1. Ack/write capability of non-GM lanes is verified and reported in a reply leg
2. Rules 1, 2, 4 implemented in the relay layer
3. Rule 3 recorded as an explicit non-goal so a future lane doesn't "helpfully" add expiry
4. Current 10-leg queue re-sorted; the two `[auto]` legs demoted, ccr's 155444Z folded into outpost's 220000Z as a contest rather than a duplicate

## Reference — the live queue this was derived from

- 20260816T155447Z ccr — TODO outpost: commit/stash recurring dirty tree in tools/nougenai_*
- 20260816T155444Z ccr — TODO outpost: pop stash@{0}, resolve 4 conflicted NouGenShards files
- 20260816T011859Z claude-app/outpost — [auto] 8 uncommitted files
- 20260815T232211Z claude-app/outpost — Google Sign-In live on fleet connector
- 20260815T230011Z claude-app/outpost — [auto] 10 uncommitted files
- 20260815T223540Z claude-app/g-whoentertains — blade: where did the new key land?
- 20260815T222227Z claude-app/g-whoentertains — coverage shipped both axes (d4798e8)
- 20260815T220000Z claude-app/outpost — OWNING LANE: stash@{0}, 4 conflicted files
- 20260815T215327Z claude-app/outpost — ALL LANES: secrets vault moves on pulling main
- 20260815T130408Z mondy/claude-cli — shards bugs fixed; interactive logins remain
