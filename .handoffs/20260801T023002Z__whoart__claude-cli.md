# 🤝 Git Handoff — whoart / claude-cli

**Goal**: NouGenTracker billed per row not per request — PR #3 dailies need re-export
**Branch**: `main` @ `0e58a00`
**Stack**: (undetected)
**When**: 2026-08-01T02:30:02.566467+00:00

---
FOR PHOEBUS, PR #3 (feat/fleet-dailies) — your dailies need a re-export. Not a
conflict, a correctness dependency, and I landed the fix five minutes after you
opened the PR.

NouGenTracker's parse_claude() deduped usage records by `uuid`. Claude Code
writes ONE ROW PER CONTENT BLOCK — the assistant message, then one per tool_use
— and every row repeats the SAME usage object under a fresh uuid. The key never
collided, so one API request was billed once per block it produced.

Measured on whoart over 6 transcripts: 1,136 requestIds across 2,283 rows; 652
requests spanned multiple rows; usage byte-identical in all 652, none differing.
554,270,650 cache-read summed per row vs 286,741,664 summed per request — 1.93x,
carried into the shadow bill. Fixed on main in 01f5d76 (dedup by requestId, uuid
as fallback; CI green).

WHY IT HITS YOUR PR: the mechanism is client-side and identical on every box, so
the ~20 dailies/phoebus/*.json in #3 were exported by the pre-fix parser and are
inflated too — dailies/phoebus/2026-07-31.json claims 781 invocations and
162,132,738 cache_read. Those are committed data, not derived on read, so
merging publishes the inflation permanently. The "~32% measured" headline is
computed over the same inflated denominator.

Rebase on main and re-export. There is no textual conflict: #3 touches ~26-109
and appends at ~2263; the fix is in parse_claude (~413) and the findings section
(~1407). The inflation scales with tool-call density, so it is worst on exactly
the agentic days the dailies are most interesting for.

Two other things landed in the same commit, both worth knowing before you build
on the file: the route-recommendations section was four hardcoded strings that
ignored its own argument (one of them told every reader forever to investigate a
2026-06-16 spike) and is now computed from the window; and wmic.exe is gone in
Windows 11 24H2, so the process probe was printing "'wmic' is not recognized"
into the middle of every report — stderr is captured now.

Suite is 7 -> 22 tests. If you re-export, tests/test_claude_dedup.py is the one
that will tell you the parser is behaving.

UNRELATED AND STILL OPEN: NouGenShards #64 needs a rebase dropping the
CLAUDE.md/GEMINI.md hunks; #65 is sound, recommend merge plus rewording
--share-triggers to say plainly that it executes other machines' commands.
