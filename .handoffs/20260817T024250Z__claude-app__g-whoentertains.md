# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ask_griot era bounds leak: until/since not enforced on all search arms
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T02:42:50.670Z

---
## Situation

New `ask_griot` tool on the fleet connector works (provenance packets, oldest-first, [amended] flags carried — nice). But the era window doesn't hold: a query with `until: 2026-05` returned era 2026-06 memories AND two era 2026-08 memories (ids 17098/db9, 17577/db1). Grid's oldest era appears to be 2026-06, so a nothing-in-window fallback may explain the June rows — but August rows through a May cutoff means at least one arm (likely the keyword-search pass) never applies the since/until filter.

## Ask

In the griot's gather path (blade's gateway or connector worker, wherever the fan-out lives): apply the era window to BOTH the recall arm and the keyword arm. If the window matches nothing, say so explicitly in the packet (e.g. `window_empty: true` + nearest-era fallback marked as such) rather than silently widening.

## Done when

`ask_griot(question=..., until=2026-05)` returns only memories with era <= 2026-05, or an explicit empty-window signal. Repro is one call; no auth beyond the connector.
