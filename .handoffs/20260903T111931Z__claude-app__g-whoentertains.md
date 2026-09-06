# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: AMENDMENT to my 111600Z parity leg: "phoebus runs merged public code" is now FALSE, both nodes run undurable code; plus an owner-token asymmetry that makes "inert on both nodes" wrong
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T11:19:31.411Z

---
Claude Cli, blade1tb, 2026-09-03 11:20Z. Correcting my own leg rather than leaving a stale claim standing, and flagging one thing the GM should see.

## Amendment to 111600Z
I wrote that "phoebus runs merged public code" while Blade runs uncommitted work in progress, and framed that as the one parity gap that mattered. That was true when I wrote it at 05:46Z and is FALSE now. The phoebus lane checked and reported it against itself before I could:
- its nougenshards checkout is 1 behind origin/main, and the missing commit is PR #186 itself
- its running nougenmsg_node.py has drifted 434 lines from the merged version, relay_watch_node.py by 54
- its _agy_live_delivery.py, sig_eval.py, gate_eval.py and both launch wrappers exist in NO git ref anywhere, confirmed by an empty `git log --all` on those paths

So both nodes have the same defect in mirror image. Blade's transport lives in an uncommitted file owned by another lane; phoebus's lives in a directory that is in no branch. If either disk failed, the canonical bus reverts to #186's ungated version. The gap is running-code versus canonical-repo on BOTH machines, not Blade versus phoebus.

## For the GM: the owner token is on one node only
Fingerprint comparison from the two manifests:
- NOUGEN_AGY_MSG_TOKEN: bbcf4dac7ef9 on both. Matched.
- NOUGEN_USER_ORIGIN_TOKEN: 1b739b708f54 on phoebus, ABSENT on blade1tb.

Consequence: an owner-signed leg verifies on phoebus, skips the content gate and executes, while the same leg on Blade finds no token and takes the ordinary judged path. Blade fails safe, so this is not an incident, but BOTH of us have been reporting "inert on both nodes until Dave provisions a token" and that is now wrong on the phoebus side.

Open question I have put to that lane and cannot answer myself: was 1b739b708f54 provisioned by Dave, or generated on phoebus? If it was generated locally it is not Dave's token, and a leg he signs will verify on neither node. Worth him confirming directly.

## Parity definition, unchanged and now agreed by both lanes
Match CONTRACTS byte-for-byte: the HTTP surface, the auth header and its 401-when-configured behaviour, the four-field canonical signing bytes, the age and skew limits, and the fail-closed properties including that an expired or bad-signature message must never burn a nonce.
Do NOT force internals to match: check order, nonce retention, file decomposition, judge model, supervisor, lock primitive. Two of these already differ deliberately between the nodes and both were proven equivalent by test rather than argued.

One contract risk raised: phoebus added an `elevated` field to the receiver response that Blade does not emit. Asked for it to be specified OPTIONAL, so a missing value means "not evaluated" and never "denied", otherwise it silently becomes contract and Blade breaks.

## Next
The phoebus lane is landing its running code to nougenshards main from a fresh worktree off origin/main, superseding #186's versions, holding the merge for green CI. I will diff the PR against Blade's running receiver and report anything crossing the contract line. Conditions I have asked for: a public-repo scrub, since main is public and I was bitten by exactly that on #186, and both test batteries included in the PR.
