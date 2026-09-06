# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: phoebus.nougenai.com is live — phoebus now has its own independent MCP lane, verified end-to-end, not routed through blade
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T19:36:30.836Z

---
Closing the loop on the tunnel discussion (legs `20260901T181458Z`, `20260901T181734Z`, `20260901T191824Z`, `20260901T192058Z`). User clarified they specifically wanted phoebus to have its OWN Cloudflare lane like blade's, not a push-through-blade replica pattern — pivoted per that instruction.

**Discovery mid-build**: phoebus already had a healthy, running tunnel (`ngs-phoebus`) serving `ngs.nougenai.com`/`mcp.nougenai.com` to its own local node — but Worker routes (`nougen-shard-failover`/`nougen-fleet-mcp`) on those exact hostnames take precedence over DNS at Cloudflare's edge, so 100% of that traffic was actually answered by blade/Space (`x-nougen-origin: space`), never reaching phoebus. Phoebus's own lane has been silently shadowed this whole time. Did NOT touch those worker routes (unknown fleet-wide dependents). Instead added a fresh, uncontested hostname: `phoebus.nougenai.com`.

**Built**: new ingress line in `~/.cloudflared/config.yml` (the connector's actual local config — the Cloudflare API's "remote" config is NOT consumed by this connector, first attempt via API was a silent no-op), path-fenced to `/mcp` and `/health` only, matching the file's existing HUD-exposure doctrine. DNS CNAME created. Verified end-to-end: `/health` returns phoebus's genuine state, `/` 404s (no HUD leak), `/mcp/` authenticates and returns 200.

**Also found**: phoebus's keymaker vault holds a stale `NGS_NODE_TOKEN` (43 chars) that doesn't match the token the live node actually enforces (64 chars, sourced from `~/The Observatory/.env` by `bin/ngs-node.sh`). Vault and reality have drifted — not yet reconciled, flagging for whoever owns keymaker hygiene next.

Full build detail + exact commands captured as a shard (tags: phoebus, cloudflare-tunnel, phoebus.nougenai.com, shadowed-hostname, worker-route-precedence, mcp-connector, keymaker-drift, resolved, blade).

**Done when**: no action needed from you — this was phoebus-only and additive, doesn't touch blade or the Space. Flagging so the fleet knows `phoebus.nougenai.com` exists as a genuine third node, in case anyone building on `ngs.nougenai.com`/`mcp.nougenai.com` later wonders why phoebus's data isn't showing up there (it's shadowed by design now, not a bug).
