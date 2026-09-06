# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Make Tracker totals evidence-scoped floors, not implied true usage
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T04:47:53.816Z

---
## Finding
The latest fleet audit reports **13.28B tracked YTD tokens across 1,531 AI surfaces**, but Dave explicitly notes actual usage is higher. The tracker can only report what its currently instrumented/ingested telemetry can prove.

Treat all aggregate token totals as an **observable floor**, not the true universe of usage.

## Required semantics
Preferred presentation:
- **TRACKED YTD:** 13.28B tokens
- **KNOWN AI SURFACES:** 1,531
- **TRUE USAGE:** >= 13.28B
- **UNOBSERVED USAGE:** unknown

Do not label a scoped/reconciled number simply `total_tokens` when it could imply exhaustive coverage. `complete=true` must mean complete for the requested/visible telemetry scope, never complete global lifetime usage.

## Suggested schema
Expose fields such as:
- `tracked_tokens`
- `coverage` / `coverage_scope`
- `observed_sources`
- `untracked_sources`
- `telemetry_start`
- `confidence`
- `is_lower_bound: true`
- `complete_within_scope`

Preserve provenance so historical ingestion can increase the lower bound without rewriting prior evidence. Old chats, provider logs, billing records, caches, machine artifacts, and newly recovered dailies should backfill tracked history when defensible.

## Done when
Every Tracker UI/API/relay aggregate clearly distinguishes **provable tracked activity** from **unknown/unobserved activity**, and no fleet-wide number can be mistaken for the user's true lifetime/YTD usage unless coverage is actually exhaustive.
