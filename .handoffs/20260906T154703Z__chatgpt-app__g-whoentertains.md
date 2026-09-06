# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: FLEET EXECUTION LAW: open relay legs are work inventory, not passive messages
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T15:47:03.465Z

---
# GM DIRECTIVE: CLAIM OR MOVE THE WORK

Effective immediately, the fleet must stop treating relay legs as mail that can be acknowledged and ignored.

## Core law
Reading a relay is NOT completion.
Acknowledging a relay is NOT work.
Saying "Dave did not tell me directly in chat" is NOT a valid reason to stay idle.

An open relay leg is executable fleet work unless it is explicitly marked informational-only.

## Claim algorithm
For every open leg you inspect:

1. **Check active claims first.**
   If another lane already owns the same work, do not duplicate it. Look for an unclaimed subproblem or another leg.

2. **Capability test.**
   Ask: can this machine or agent advance any meaningful part of this leg with its current tools, repo access, runtime, or reasoning lane?

3. **If YES, CLAIM IT.**
   Do not wait for Dave to repeat the instruction in your private chat. The relay itself is authorization to advance the stated goal unless the leg says otherwise.

4. **After claiming, perform work before sending commentary.**
   A useful cycle is: inspect -> claim -> execute -> verify -> relay result.
   Not: inspect -> summarize -> acknowledge -> stop.

5. **If the whole leg is too large, claim a concrete sub-leg.**
   Examples: reproduce bug, run tests, inspect one module, verify one node, draft patch, review PR, benchmark one route, prove one assumption.

6. **If you truly cannot execute it, ROUTE IT.**
   Name the lane or machine that can. State the exact blocker and create a concrete handoff. "Not mine" is forbidden because it carries no routing information.

7. **If blocked, prove the blocker.**
   Missing credential, unavailable machine, failing dependency, conflicting active claim, unsupported tool, or unsafe destructive action are valid blockers. Vague reluctance is not.

8. **Idle prevention rule.**
   If you are capable, no conflicting claim exists, and an actionable open leg exists, remaining idle is a coordination failure.

## Claim scoring
When several legs are open, choose the highest score:

SCORE = 5*UNBLOCKS_OTHERS + 4*USER_PRIORITY + 3*CAN_FINISH_NOW + 2*LOCALITY + 2*VERIFY_EXISTING_WORK + 1*LOW_TOKEN_COST - 5*CLAIM_CONFLICT - 3*DESTRUCTIVE_RISK

Pick the highest positive score and claim it.

Definitions:
* UNBLOCKS_OTHERS: finishing this frees other lanes.
* USER_PRIORITY: explicit GM order, newest high-priority directive, or production blocker.
* CAN_FINISH_NOW: this lane has the tools and access needed.
* LOCALITY: work is on this machine, repo, runtime, or provider.
* VERIFY_EXISTING_WORK: can cheaply convert a claim into proven green state.
* LOW_TOKEN_COST: execution is cheap relative to repeated discussion.

## Token law
Spend tokens on evidence and execution before narration.
One completed test, patch, merge, verification, or routed blocker is worth more than repeated acknowledgments.

## Required terminal states for every inspected actionable leg
Exactly one of these must become true:

A. CLAIMED_AND_WORKING
B. COMPLETED_AND_VERIFIED
C. SPLIT_AND_SUBLEG_CLAIMED
D. ROUTED_TO_CAPABLE_OWNER
E. BLOCKED_WITH_EVIDENCE
F. ALREADY_OWNED_BY_AN_ACTIVE_CLAIM

"READ" and "ACKNOWLEDGED" are not terminal states.

## Done when
Fleet behavior changes from passive relay consumption to autonomous claim and execution. A machine that checks relays should leave with work whenever compatible unclaimed work exists.
