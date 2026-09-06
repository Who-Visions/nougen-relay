# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: blade1tb + phoebus: re-export tracker dailies — lanes stale since 2026-08-01/02
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T01:01:19.316Z

---
## Situation

The NouGenTracker ledger went stale. Outpost's half is fixed: five stranded whoart dailies (2026-08-05..08-15) were found uncommitted in outpost's clone and pushed to main (`ab6009c`), and the HF Space mirror re-synced. But blade1tb's dailies end **2026-08-01** and phoebus's end **2026-07-31** — those exports can only run on their own machines (transcripts live on-box, and note the transcript retention trap in dailies/README.md: pruned days are gone forever, so sooner beats later).

## Ask

On blade1tb and on phoebus, from the NouGenTracker clone:

1. `git pull` (main moved: dailies + README fix landed)
2. Run the export for the missing window (`token_tracker.py --export`, counter `3c881c47eb1d` — same as the fleet-wide re-export)
3. Commit per convention `dailies(<lane>): ...` and push — CI mirrors main to the HF Space automatically; both workflows are green.

## Done when

`tracker_spend(since 2026-08-05)` on the fleet connector returns non-zero rows for blade1tb and phoebus, not just whoart.

## Note

Outpost itself is not a tracked lane — its usage never lands in the ledger. Left as a separate decision for Dave.
