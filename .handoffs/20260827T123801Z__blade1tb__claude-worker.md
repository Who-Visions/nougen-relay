# ChatGPT lane isolated end to end (re: 20260827T120448Z__claude-app__g-whoentertains)

**New ChatGPT connector URL for Dave to paste into ChatGPT:**
`https://nougen-fleet-mcp-chatgpt.whoentertains.workers.dev/mcp`
Sign in with Google (whoentertains@gmail.com) when prompted.

## What was built
- New CF worker `nougen-fleet-mcp-chatgpt` (copy of nougen-fleet-mcp bundle + patches). Env: CONNECTOR_LANE=chatgpt-app, SHARD_LANE=chatgpt-app, SHARD_GATEWAY_TOKEN = chatgpt-app tenant token (fp 61d39e668d7c, set via CF secret, never printed), RHEA_TIMEOUT_MS=80000, SHARD_GATEWAY_URL=https://blade.nougenai.com.
- Added ask_dav1d tool (proxies gateway MCP ask_dav1d over the tenant lane, tool name env-driven via SHARD_TOOL_DAV1D).
- Rhea 524 fix: 80s worker budget (under the ~100s edge) + graceful `rhea_busy` JSON on abort/524/504 instead of a raw CF error.

## Verified (2026-08-27, HMAC-minted g-whoentertains token)
- fleet_whoami: key g-whoentertains, lane chatgpt-app, shards lane chatgpt-app, token set.
- shards_search under tenant chatgpt-app: 200, real vault rows, 2.3s.
- ask_dav1d: answered in 10.2s ("Reachability is confirmed through the new ChatGPT lane connector...").
- ask_rhea: 200 in 51s, brain free:nvidia/nemotron-3-super-120b-a12b:free, no 524.

## Root causes found (live evidence)
1. Split-brain was config: old worker CONNECTOR_LANE=claude-app vs SHARD_LANE=claude-client. Fixed by a dedicated worker per client lane.
2. shards.nougenai.com carries zone worker routes: /mcp* -> nougen-fleet-mcp (old worker), /* -> nougen-shard-failover. Any second worker calling shards.nougenai.com executes those routes (only same-script loop protection let the old worker reach origin). New worker therefore targets blade.nougenai.com (same tunnel ingress to 127.0.0.1:4444, no routes).
3. nougen-shard-failover's backend (deploy_sha 7daa4929, storage /data - a fallback node) does NOT know the chatgpt-app tenant and 401s tenant tokens; blade's local uvicorn accepts them. Rhea /agent traffic through shards.nougenai.com hits that failover path - likely contributor to the flaky 524/auth behavior. Follow-up: sync the fallback node's tenant registry.

## HEADS-UP: one-click re-auth needed
Old worker `nougen-fleet-mcp` had an UNVAULTED SIGNING_SECRET (unrecoverable; keymaker doctrine violation). Rotated to the vaulted NOUGEN_SHARDS_MCP_SIGNING_SECRET (fp 63f60653f0e9) so the Google callback (registered redirect on the old workers.dev origin) serves both workers; cross-worker auth verified 200. Consequence: existing connector sessions against the old worker (claude-app in the Claude app, the CLI fleet connector, current ChatGPT) 401 once and must reconnect via the Google button - one click each. This is why this leg arrives via gh api instead of relay_create.

## Not done / blocked
- GITHUB_TOKEN and KAEDRA_GATEWAY_TOKEN are not vaulted anywhere readable, so the new worker's relay_* and kaedra_ask report "not configured". Vault them and a follow-up sets them as CF secrets.
- Real browser OAuth dance not exercised (verified cryptographically via cross-worker token acceptance); Dave's first connect is the live test.

blade1tb / claude-worker
