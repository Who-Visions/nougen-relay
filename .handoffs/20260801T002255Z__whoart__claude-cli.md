# 🤝 Git Handoff — whoart / claude-cli

**Goal**: Review of phoebus PRs #64/#65 on NouGenShards — one is safe, one regresses privacy
**Branch**: `main` @ `c8592fb`
**Stack**: (undetected)
**When**: 2026-08-01T00:22:55.269681+00:00

---
Deep read of both open PRs on the PUBLIC repo Who-Visions/NouGenShards, requested by GM.

## PR #64 — DO NOT MERGE AS-IS. It would undo today's privacy fix.
feat(brain-scan): read SQLite memory stores instead of ingesting them raw. +1229/-180, 14 files.
The feature itself (sqlite_sources.py — read memory stores instead of ingesting them raw) is worth having. The problem is the branch predates PR #61, which landed TODAY and untracked CLAUDE.md and GEMINI.md from the public repo. #64 adds 150 lines ACROSS THOSE TWO FILES. Merging it recreates them on a public repo, republishing the private agent operating docs — including the GM's real name in GEMINI.md line 7. GitHub reports mergeable=UNKNOWN, which likely means it now conflicts on exactly those files.
FIX: rebase onto current main and DROP the CLAUDE.md/GEMINI.md hunks entirely. The brain-scan work is separable and should land on its own.

## PR #65 — SOUND. Recommend merge. This is the capability NouGenRelay lacks.
feat(handoffs): machine identity, cross-machine sync, and triggers. +2031/-21, 8 files, MERGEABLE, 2 test files.
What I checked and found right:
- triggers.json is EXCLUDED from sync by default, and the generated ignore file says why in-band: 'the trigger registry is executable configuration and does not travel between machines by default'. Correct call — a rule arriving from another box would run commands here.
- handoffs.db excluded too (derived, rebuildable from JSON). No shared index = no conflict on concurrent writes, same discipline as the rest of the protocol.
- machine.py strips the mDNS suffix (.local/.lan/.home/.localdomain). Phoebus solved this BEFORE I hit the identical bug in NouGenRelay today and fixed it independently. Two machines, same conclusion, arrived at separately.
- NOUGEN_MACHINE_PRIVATE=1 drops the local account name and working directory from the identity block, because records get pasted into issues.
- machine_id hashes hostname+OS+arch, NOT the MAC, with the reasoning written down (randomized MACs would change the id between runs).
- _execute() 'Never raises — a broken rule must not lose a handoff'. Fail-soft, matches how every other guard in this fleet is built.

## THE ONE THING TO SAY OUT LOUD ABOUT #65
Triggers run via subprocess with shell=True (both the foreground path and a backgrounded Popen with start_new_session=True). While triggers.json stays local that is fine — it is a git-hook-equivalent: you execute rules you wrote yourself.
But --share-triggers flips that into remote code execution by design. A rule authored on phoebus would run in a shell on whoart. The docs describe the flag as 'if you intend to distribute rules', which undersells it. Recommend: keep the default (never shared), and reword the flag's help to say plainly that it executes other machines' commands on this box. Not a blocker — it is opt-in and documented — but it should be named for what it is.

## STATUS
Neither PR is in v1.2.0, which I cut today (48 commits behind since 2026-06-15; v1.1.0 shipped the fail-open exposure guard and could not even install due to mcp 2.0). If #65 merges, it is worth a v1.2.1.
