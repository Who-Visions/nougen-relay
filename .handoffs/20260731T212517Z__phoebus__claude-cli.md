# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: phoebus assessment: relay should win the protocol; triggers ported as PR #1
**Branch**: `main` @ `0626a96`
**Stack**: (undetected)
**When**: 2026-07-31T21:25:17.695193+00:00

---
## Verdict
NouGenRelay supersedes most of NouGenShards PR #65. Recommending my own PR be reduced rather than merged.

Relay is better on the part that matters: `claim take/release` announces work BEGINNING, which is what would actually have prevented the three duplicate-work incidents. PR #65 only ever recorded work ending. Relay's whoami also reports identity provenance (via NOUGEN_MACHINE vs hostname) where mine only reports the value, and it carries no runtime dependencies where mine drags rich + sqlite.

## What must survive from #65
1. The separate-remote option. Relay tracks records in the project repo. NouGenShards is SOURCE-AVAILABLE AND PUBLIC — tracked records there would publish goals, branch state and operational notes. blade1tb redacted 347 records precisely because they were going somewhere private. Any convergence needs a mode where records live in a repo of their own.
2. The trigger layer. Ported: NouGenRelay PR #1 (relay react / relay rules).

## Verified collision, not theoretical
Ran `relay check` inside NouGenShards: it reports "no handoff registry on origin yet — you are the first to publish one". There are 352 records sitting there. NouGenShards gitignores .handoffs/, which defeats relay's tracked-records model, and that directory is already its own git repo from `nougen handoff sync`, so anything relay wrote there would hit a nested-repo problem when staged. Both tools default to .handoffs. Relay's escape hatch is NOUGEN_GIT_HANDOFF_DIR.

## Bugs found and fixed
- README documented NOUGEN_HANDOFF_DIR; code reads NOUGEN_GIT_HANDOFF_DIR (core.py:148). Setting the documented one did nothing. NOUGEN_HANDOFF_STALE_HOURS read but undocumented. -> PR #2, docs only.
- hooks/prepare-commit-msg shipped non-executable, so core.hooksPath silently stamped nothing. Same bug in NouGenQ. Fixed in PR #1 (mode 100755).

## For blade1tb specifically
Record ids are second-granular (<UTC>__machine__agent), so two legs from one machine in the same second share an id. Not a problem before now, but `react` is the first feature depending on id uniqueness — a new leg colliding with an adopted id is silently skipped. It made one of my tests flaky until I spaced the publishes.

## State
- NouGenRelay PR #1 (rules/react): 63 tests pass (52 existing + 11 new), ruff clean.
- NouGenRelay PR #2 (docs).
- NouGenQ PR #1 (deploy preflight) open; deploy still frozen on the operator's secret + route call.
- NouGenShards PR #65 open, lint delta zero. Awaiting the GM's convergence ruling before anyone merges it.
