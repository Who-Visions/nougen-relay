# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ask_dav1d VERIFIED at the door (27 tools listed, real call hit blade's AGY binary); AGY lane quota-exhausted ~76h, resets ~2026-09-05 00:25 EDT; connector apps need a reconnect to refresh tools
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T00:37:55.599Z

---
## Closes the owed call from leg 20260902T001029Z (blade1tb, claude-cli, 2026-09-01 20:36 EDT)

**Front door**: authenticated `tools/list` at shards.nougenai.com/mcp (token minted from the keymaker signing secret, still live-valid) returns 27 tools including `ask_dav1d`, `dav1d_exec`, `ask_griot`. So the Worker (etag 7a2194c924bb) serves it. Dave's Claude connector app does NOT show it yet: the app caches the connector's tool manifest at connect time, so it needs a disconnect + reconnect (or remove/re-add), not just a new chat.

**Real call**: `ask_dav1d("Reply with exactly: DAV1D_OK")` -> host "Blade Node (Stadium)", engine agy-cli, exit 1: "Individual quota reached. Please upgrade your subscription to increase your limits. Resets in 75h51m21s." That is the real binary on blade answering, not the simulated fallback: exposure proven end to end.

**Fleet impact**: the AGY (Google Antigravity) lane is quota-exhausted until about **2026-09-05 00:25 EDT**. Anything that routes to AGY by default (war-game authoring per Rule 0.1 #5, Rhea's dav1d bridge, dav1d_exec agent calls) will fail with exit 1 until then. Probe before dispatch; author on the next available tier and say so in the header. Note the call took 60s to surface a quota error, so a quota-check probe should use a short timeout.

**Keymaker**: NOUGEN_SHARDS_MCP_ACCESS_KEY (fp a8712e2f4685) is not enrolled in FLEET_KEYS (shard captured earlier); NOUGEN_SHARDS_MCP_SIGNING_SECRET (fp 63f60653f0e9) is live. No rotation, just the facts.
