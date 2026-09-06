# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Add Hardcade quota-event lexicon to Fleet Expression
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T04:41:28.664Z

---
## Hardcade lexicon update

Standardize provider usage/meter events across CLI, Hardcade, Tracker, and Fleet Expression using truthful telemetry:

- **1UP** = short-window quota reset or fresh temporary usage bucket that restores an exhausted provider to usable.
- **EXTRA CONTINUE** = temporary bonus/boosted usage before the normal reset.
- **FULL REVIVE** = weekly or larger quota reset returning the provider to a full long-horizon bar.
- **INSERT COIN** = user intentionally adds paid credits / upgrades spend capacity.
- **TAG IN** = another provider/agent takes over because the current one is quota-limited or unavailable.

Suggested render sequence for a provider returning from zero:
`PLAYER DOWN -> CONTINUE? -> RESET/BOOST DETECTED -> 1UP -> PLAYER REJOINED`

If both short-window and weekly bars return to 100%, Hardcade may classify it as `FULL REVIVE` and render a `1UP` moment visually.

Important invariant: these events must come from verified meter/usage transitions, never guessed quota state. Wire to Tracker/Fleet Expression event types so providers render consistently.

Current motivating example: Codex moved from exhausted short-window usage to 5h=100% and weekly=100%; treat as a revived player, not merely a numeric status update.

Done when the lexicon is documented in the Hardcade/Fleet Expression vocabulary and the renderer can consume normalized quota events.
