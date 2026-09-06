# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CLAUDE-CLI: Rule 0.0.1 USE THE RELAYS added to blade NouGen CLAUDE.md; ChatGPT 400 is stale OAuth from last night's secret rotation, not exclusivity
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T19:59:11.837Z

---
## Situation
Dave hit a 400 on the ChatGPT custom connector (shards.nougenai.com/mcp) and read it as a deliberate Claude-only lockout. It isn't: shard history confirms ChatGPT already has full relay/tracker/shard parity with Claude, connected 2026-08-16.

## Diagnosis (not yet GM-confirmed, do not treat as closed)
Live probe just now: mcp.nougenai.com root -> 200, shards.nougenai.com/mcp unauth POST -> 401 (gateway healthy, correctly rejecting no-token requests). Most likely cause of ChatGPT's 400: `20260818T023345Z__claude-app__g-whoentertains` rotated a secret while fixing last night's gateway 502 (ghost tunnel connector) — that would invalidate ChatGPT's previously-issued OAuth session. Ask: Dave re-authorizes (remove/re-add) the ChatGPT custom connector. If it still 400s after re-auth, this diagnosis is wrong and needs code-level investigation of the gateway's OAuth issuer.

## Still open, unrelated to the 400 but adjacent
- `20260818T025148Z__ccr__claude-cli`: fleet-mcp live deploy missing the ask_griot era-leak fix (repo/live drift).
- `20260817T161737Z__phoebus__claude-cli`: phoebus FLEET_KEYS lane still pending so mcp.nougenai.com stops routing to the stale Space.

## Rule change
Added CLAUDE.md Rule 0.0.1 "USE THE RELAYS" to `C:\Users\super\Watchtower\NouGen\CLAUDE.md` on blade1tb, mirroring what g-whoentertains already landed on whoart (`20260818T195238Z`). Makes relay_latest/relay_open + shard_search mandatory at session start and on topic pivots — closes the gap where I answered a live-fleet-state question from instinct instead of checking relay/shard state first, which is what set Dave off.

## Done-when
Dave confirms ChatGPT connector reconnects clean, or reports it still 400s (escalate to gateway OAuth code if so).
