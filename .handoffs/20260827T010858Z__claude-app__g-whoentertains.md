# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Diagnose and restore shards.nougenai.com/mcp exposure
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T01:08:58.396Z

---
# Incident baton: shards.nougenai.com/mcp

## Current observed state

From the ChatGPT NouGenShards connector on 2026-08-26, `fleet_whoami` succeeds and reports:

- authenticated key: `g-whoentertains`
- connector lane: `claude-app`
- relay repo: `Who-Visions/NouGenRelay`
- relay token: set
- tracker space: `nougenai/NouGenTracker-node`
- shard gateway configured URL: `https://shards.nougenai.com`
- shard gateway token: set
- shard lane: `claude-client`

So the connector itself is authenticated and configuration is present.

## Exact shard gateway failure

`shards_status` returns:

```json
{"up":false,"health_up":false,"mcp_up":false,"configured":true}
```

Interpretation:

1. `configured=true`: the connector knows about the shard gateway and has configuration for it.
2. `up=false`: the gateway is not considered reachable/healthy by the connector.
3. `health_up=false`: the gateway health probe is failing.
4. `mcp_up=false`: the MCP exposure/probe is also failing.

This strongly points away from a missing local connector configuration and toward the public service path, gateway process, reverse proxy, route exposure, service binding, TLS/DNS, or upstream health.

## Important URL/path discrepancy to verify

`fleet_whoami` reports the configured gateway base as:

`https://shards.nougenai.com`

Dave expects the exposed MCP endpoint at:

`https://shards.nougenai.com/mcp`

Verify whether the connector intentionally stores a base URL and appends `/mcp`, or whether the configured URL itself must include `/mcp`. A base/path contract mismatch could produce `mcp_up=false` while credentials remain valid.

## Other connector behavior observed in this session

The relay backend remains reachable enough to create this baton and `fleet_whoami` can read configuration. `shards_capture` also succeeded and stored a FAILURE shard for this incident. That narrows the breakage: this is not a total NouGen connector outage. The failure is specifically in the Blade shard gateway / MCP health path as currently reported by `shards_status`.

Earlier in the same session an attempted Dav1d path was reported as `unknown tool: ask_dav1d`. Treat that as a separate tool exposure/schema issue unless logs prove it shares the same MCP registration failure. Do not conflate it with the shard gateway outage without evidence.

## Checks to execute

1. Confirm DNS for `shards.nougenai.com` resolves to the intended host.
2. Confirm TLS termination and certificate validity for the hostname.
3. Confirm the reverse proxy has a live route for `/mcp` and any health route used by the connector.
4. Confirm the shard gateway process/container is running and listening on the expected internal port/interface.
5. Curl or equivalent from the Blade host itself against localhost/internal service, then against `https://shards.nougenai.com`, then specifically `https://shards.nougenai.com/mcp` to isolate app vs proxy vs public-edge failure.
6. Inspect proxy and gateway logs for 404, 401, 403, 502, 503, connection refused, timeout, redirect loops, or route mismatch.
7. Verify auth header/token forwarding on the MCP route. Token is present from connector perspective, but proxy stripping or incorrect audience/secret lookup could still break the request.
8. Verify whether health checks require authentication or use a distinct unauthenticated endpoint.
9. Verify connector contract: base URL `https://shards.nougenai.com` plus appended `/mcp` versus literal configured endpoint `https://shards.nougenai.com/mcp`.
10. After repair, rerun `shards_status`; done state must report `up=true`, `health_up=true`, and `mcp_up=true`.
11. Then smoke test both `shards_search` and `shards_recall` from this connector lane.
12. If Dav1d exposure is expected through the same server, separately enumerate MCP tools and verify `ask_dav1d`/`ask_david` registration after the shard gateway is healthy.

## Done when

The incident is resolved only when `shards_status` is fully green, recall/search execute successfully from the ChatGPT connector, and the public `/mcp` route is confirmed to match the connector's expected URL contract. Capture the root cause and permanent fix into a FAILURE or DECISION shard so future lanes do not rediscover the same outage.
