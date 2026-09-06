# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Repair NouGenTracker truth path and automate daily publish so live usage does not go stale
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T04:23:20.422Z

---
Inbound from claude-app sign-off leg 20260903T035242Z. Blade tracker dailies stopped at 2026-08-31 because publish is manual; live clone is `Watchtower/NouGen/NouGenTracker`, while the nougen-usage MCP was pointed at stale `~/.nougen/tracker` on a branch 77 commits behind. Owner lane: (1) check whether the background `token_tracker.py --publish` produced a new `dailies/blade1tb` commit; if yes push/open PR/merge/pull, otherwise rerun publish safely, (2) repoint the MCP tracker directory through portable config/discovery rather than a Dave-specific hardcode, (3) automate/schedule daily publish with observable last-success state, (4) preserve the unrelated uncommitted cold-boot-headline patch, (5) add `nougen tracker doctor` or equivalent to compare live source vs served dailies and warn on staleness. Done when current usage is served from the authoritative clone and future dailies publish automatically with proof.
