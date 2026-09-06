# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: BLADE: take the Space-sqlite P1 — repair/quarantine malformed grid DBs 1,2,4,6,7,9 (routed from phoebus, supersedes open leg 20260901T070113Z)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T08:02:35.867Z

---
# 🎯 Directed to blade1tb — fix the malformed grid DBs now

**From**: phoebus (GM request, 2026-09-01T08:02Z)
**Priority**: P1
**Supersedes / routes**: `20260901T070113Z__ccr__claude-cli` (acked on phoebus with a note pointing here — do NOT also ack that one, ack THIS leg when you start)

## Situation

Space-sqlite grid DB indices **1, 2, 4, 6, 7, 9** are returning `disk image is malformed` — six of nine indices, materially wider than the tracked DB8-only corruption (`20260830T205317Z`). Surfaced by [NouGenShards PR #166](https://github.com/Who-Visions/NouGenShards/pull/166) (rhea-dedicated-executor), which bounds the *symptom* (stuck-scan thread starvation) but not the corruption itself.

## Ask

1. Triage: run `shards_coverage` / grid fan-out diagnostics against live state — confirm the current per-index footprint (it may be narrower if `7087c75a`'s zero-loss recovery already applied; see `20260831T015347Z`).
2. Determine whether this is spread from the DB8 incident or a distinct replica/snapshot incident — GitHub-branch vs HF-Space snapshot lineages were already drifting (`20260830T195855Z`, `20260830T200301Z`).
3. Apply the DB8 repair/quarantine treatment to each confirmed-bad index, and re-verify `recall_trustworthy` doesn't launder degraded state.
4. Do not block PR #166 on this — corruption is orthogonal to its scope.

## Done when

Indices 1, 2, 4, 6, 7, 9 are repaired or safely quarantined, recall from healthy indices is unaffected, and `recall_trustworthy` accurately reflects retrieval-path state (same acceptance bar as the DB8 leg). Relay the result — including a correction leg if the footprint turns out different than reported.
