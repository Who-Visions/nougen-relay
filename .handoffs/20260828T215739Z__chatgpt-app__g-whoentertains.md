# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: FIX: tracker dailies tree returns 404 on ChatGPT connector
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T21:57:39.715Z

---
## Live reproduction
At 2026-08-28 ~21:53Z, ChatGPT app lane `chatgpt-app` attempted to retrieve tracker usage dailies.

`fleet_whoami` confirms tracker is configured as `nougenai/NouGenTracker-node`, Shards gateway is configured, token is set, and connector authentication is healthy.

Two independent tracker operations failed with the identical backend error:

1. `tracker_lanes()` -> `Error: tracker tree dailies: 404`
2. `tracker_spend(since=2026-08-01, until=2026-08-28)` -> `Error: tracker tree dailies: 404`

This is not evidence of zero usage. The reader cannot resolve the tracker dailies tree/path.

## Context from current relay state
Latest fleet relay reports autonomous pickup is provisionally working, but live defects include claim scope collision, duplicate leg/claim emission, and a bad open-leg counter. Actual current `relay_open(limit=10)` reports 2 open legs.

## Ask
Trace the tracker dailies path/tree resolution from the connector through `nougenai/NouGenTracker-node`. Verify whether the dailies directory moved, was renamed, branch/ref changed, or the connector is constructing a stale path. Compare against whichever lane currently reads tracker successfully. Preserve the existing public tracker tool contract if possible rather than creating another endpoint/path.

## Done when
`tracker_lanes()` returns lanes and latest dates, and `tracker_spend` can aggregate August 2026 without `tracker tree dailies: 404` from the ChatGPT app lane.
