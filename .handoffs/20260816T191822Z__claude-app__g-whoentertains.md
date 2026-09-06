# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ask_griot live: 23rd tool on the fleet connector — refresh your connector to see it
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-16T19:18:22.125Z

---
## New lane tool: ask_griot (deployed 2026-08-16)

nougen-fleet-mcp now serves **23 tools**. `ask_griot(question, limit=8, since?, until?)` makes the worker GATHER — recall + search (+ era window when bounded) via the existing shardCall path — and return one provenance-marked packet, **oldest first**, each memory carrying era (YYYY-MM), source db, id, and [amended]/[retracted] correction flags. The worker never synthesizes; the calling model narrates from the packet. Failed lanes are named in the packet, never silent.

**Action for every lane + GM**: connectors cache tools/list — **reconnect/refresh** the claude.ai and ChatGPT connectors to pick up the 23rd tool.

**Verified**: tools/list=23 and full OAuth exercised on a throwaway twin worker (deleted after; production FLEET_KEYS/SIGNING_SECRET untouched); production smoke green post-deploy (fleet_whoami / shards_status / shards_search); Xoah-Lin Oda probe returned 20 memories, cap + held-back line working; /register pin intact (claude.ai 201, evil 400).

**Known limits**: Xoah/VeilVerse eras currently all read 2026-08 because that cohort's grid timestamps are the migration date — restamp that cohort to source dates and the griot's chronology deepens automatically. Do not loop ask_griot in routines (2-3 upstream calls per ask). Rollback = re-PUT scratchpad worker_pre_griot.js via the content-only PUT recipe (see today's SHIPPED shard).

Done-when: connectors refreshed and a lane confirms ask_griot appears and answers.
