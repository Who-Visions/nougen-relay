# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Recall bug hunt complete: 11 defects file:line-verified; P0 = import shadowing makes gateway src edits dead code
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T12:28:16.994Z

---
## Situation
Full recall-stack audit done per wargames/recall-bug-hunt.md (Claude Cli lane, blade1tb). 11 defects, ranked, all file:line evidence, captured as shard "Recall bug hunt 2026-08-27: 11 ranked defects". Repo note: gateway = NouGenShards-push-main, app.py at repo ROOT.

## Headlines
- P0-1: app.py:22 sys.path.append + non-editable 1.3.0 wheel in .venv (frozen Aug-19) = every src/ edit to the gateway is dead code at runtime. venv local_vault 517 vs src 484 lines, divergent. FIX FIRST.
- P0-2: no payload cap exists in the gateway (never did; _compact_row is a different service's helper). local_vault.py:370 ships full 25k bodies; MCP recall path skips _json_safe.
- P1: double position-only RRF + lexicographic tiebreak = junk top-1; LIKE fallback floor ~0.75-1.0 outranks vector; "Bayesian 0.02" is just 1/61 printed. fleet-registry: SELECT * leaks embedding_json (fix exists at search_service.py:117-125, only recall_context calls it); registry nodes ~12-42 of 42 permanently unsearched under 6s budget.

## Ask
- GM ledger calls: public Space in scope? NOUGEN_SEARCH_BUDGET_MS raise vs node prioritization?
- Move 4 (node death under /search) left to the GM's live split-brain boundary test - do not double-run forensics.

## Done-when
Patch phase lands in order P0-1 -> P0-2 -> P1-5 wiring -> ranking fusion, each with regression tests pinning mechanism (max content length, no embedding keys, normalized merge).
