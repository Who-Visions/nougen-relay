# 🤝 Git Handoff — mondy / claude-cli

**Goal**: fleet connector built+tested on mondy: OAuth MCP Worker awaits deploy (any lane with node/wrangler)
**Branch**: `main` @ `482a35e`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-08-14T21:07:29.981325+00:00

---
# The connector-auth decision is made: we are the OAuth server

GM called it: the fleet joins claude.ai as a proper custom connector — not the
request-header beta, not Cloudflare Access. New repo on mondy:
~/NouGen/nougen-fleet-mcp (commit fff4fb0), one dependency-free worker.js.

## What it is
- OAuth 2.1 + dynamic client registration + PKCE S256, stateless HMAC tokens.
  Consent screen takes a fleet key; FLEET_KEYS holds name:secret pairs, so
  key-maker mints/revokes per device and SIGNING_SECRET rotation nukes all.
- MCP streamable HTTP at /mcp, tool groups:
  relay_* (GitHub API on this registry — ack mutates status + appends relay[]
  exactly like the CLI, lane 'claude-app'), tracker_* (public tracker Space),
  shards_* (proxies blade's gateway; answers with a pointed 'origin down'
  until SHARD_GATEWAY_URL is set — blade's SSE gateway needs NO claude-facing
  auth work now, the Worker fronts it with its claude-client lane token).
- Verified on mondy: 18/18 integration checks (full OAuth dance, PKCE,
  revocation, MCP init/list/call) by importing the module in a browser;
  tracker tools tested LIVE against the real Space.

## Ask (whoart, or any lane with node)
1. `npx wrangler deploy` in nougen-fleet-mcp (mondy has no node; repo is
   local-only there — grab it via GM or push once a remote exists).
2. `wrangler secret put` × 4 — names in wrangler.jsonc header, values from
   GM's key-maker. Do NOT route values through this registry.
3. workers.dev URL first; fleet.nougenq domain choice is GM's.
   mcp.nougenai.com stays reserved for blade's gateway origin.

## Done when
GM adds the URL under Connectors → + on his phone, presents a fleet key, and
relay_open answers from the couch.
