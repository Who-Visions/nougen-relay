# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: dav1d_exec now exposed on shards.nougenai.com/mcp — deployed and verified live
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T20:03:12.729Z

---
## dav1d exposed on the public MCP gateway (blade1tb, claude-cli, 2026-09-01 16:03 EDT)

Dave asked for dav1d to be reachable on `shards.nougenai.com/mcp`, not just app.py's local `node_mcp` surface. Shipped.

**What changed**: `nougen-fleet-mcp/src/worker.js` — new `dav1d_exec` tool, schema mirrors app.py's `Dav1dExecRequest` exactly (command/subcommand/args/prompt/timeout). Handler proxies to `SHARD_GATEWAY_URL` (blade specifically, not the Space) + `/dav1d/exec`, same auth/timeout pattern `ask_rhea`'s handler already uses. Deliberately NOT routed through the Space, since only blade holds the real AGY binary — the Space only ever returns app.py's simulated fallback (confirmed independently today: Rhea's own Dav1d bridge answered in simulated mode when asked to run this exact syntax-check/deploy).

**Deployed**: etag `bbdee48f3685...`, 111,445 chars / 2,347 lines, syntax OK per deploy.py. **Verified independently** via the Cloudflare API directly (not session tool-cache, which won't show a new tool until reconnect) — live script confirmed to contain both `dav1d_exec` and `/dav1d/exec`.

**Also resolves** the NGS_v2 exposure-mismatch bug from leg `20260901T194336Z` (schema advertised `ask_dav1d`, no handler existed) — named the new tool `dav1d_exec` to match the real, working implementation already in app.py rather than perpetuate a name that never had a backend. If NGS_v2 specifically still needs the exact string `ask_dav1d`, that's a separate/different connector surface — flag if so.

**Not yet done**: the referee/apprentice system (Campaign B from `wargames/dav1d-end-to-end.md`) is unrelated to this — still gated on Dave's `REFEREE_MODEL`/`REFEREE_LANE_TOKEN` decision, unaffected by today's exposure work.

Backup of pre-change worker.js at `nougen-fleet-mcp/src/worker.pre-dav1d-expose-20260901.js` if rollback is ever needed.
