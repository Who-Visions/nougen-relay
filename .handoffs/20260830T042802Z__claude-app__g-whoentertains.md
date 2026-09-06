# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: P1 SOLVED (diagnosis): recall hangs because nougen-fleet-mcp speaks SSE to an upstream that only implements HTTP — one env var fixes it; earlier root causes disproved
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T04:28:02.070Z

---
**Supersedes the root cause in** `20260830T035240Z`, `20260830T041700Z`, and agy's baton `20260830T040800Z`. Diagnosis is now positive, not inferential.

## Method
Read the **DEPLOYED** `nougen-fleet-mcp` source via the Cloudflare API (`workers_get_worker_code`) rather than trusting on-disk copies — neither `nougen-shard-gateway/` nor `nougen-shards-mcp/` is the worker bound to `/mcp`. Then probed the upstream directly from blade.

## The defect
Chain: `shards.nougenai.com/mcp` → worker `nougen-fleet-mcp` → `SHARD_GATEWAY_URL` = `https://nougen-shard-failover.whoentertains.workers.dev` (confirmed via `fleet_whoami`; **not** a self-proxy loop).

The worker selects its transport from `SHARD_GATEWAY_STYLE`:
- `"http"` → fetches `base + "/mcp/"` **with** `AbortSignal.timeout(SHARD_HTTP_TIMEOUT_MS || 45000)`
- **any other value, including unset (the effective default)** → SSE: opens `base + "/sse"` under a 30s abort, then POSTs JSON-RPC to the URL that stream advertises

Measured against the upstream, 2026-08-30 from blade:
| probe | result |
|---|---|
| `POST /mcp/` | **401 in 0.51s** — endpoint exists, challenges for its token = healthy |
| `GET /sse` | **404 in 0.26s** — endpoint does not exist |

**The worker is speaking SSE to an upstream that has no SSE endpoint.** Compounding it: the SSE message-POST helper `post()` is the single fetch in the worker with **no `signal` and no deadline** (`ctrl` is never passed to it), so the 30s SSE-open abort cannot reach it, and `SHARD_CALL_MAX_ATTEMPTS` retries network-class failures on top. Every POST `tools/call` therefore hangs until the *client* times out, while `GET /mcp` short-circuits to 405 before any subrequest and looks instantly healthy.

## Three earlier theories, disproved
1. **"Worker hangs on decommissioned `nga_hgf_Space` (404)"** (agy) — the deployed worker contains no reference to `nga_hgf_Space`, `cfargotunnel`, `trycloudflare`, or any hardcoded tunnel host. Only the unrelated tracker lane touches Hugging Face.
2. **"`/health` 200 proves the gateway is fine"** — `nougen-fleet-mcp` has **no `/health` route at all** (falls through to 404). That 200 is served by something else and never measured the shard path. A green that cannot see the failure.
3. **`NODE_URL` self-proxy loop in `nougen-shards-mcp`** (my own earlier lead) — real in that file, but irrelevant here: a different worker serves `/mcp`.

## Fix — GM action, one command, reversible
Smallest blast radius, no code change, no deploy of new logic:
```
wrangler secret put SHARD_GATEWAY_STYLE --name nougen-fleet-mcp
# value: http
```
(or set it as a plain var in the worker's settings). This switches it to the transport the upstream actually implements **and** the one that already carries a timeout. Revert by unsetting.

Then verify: `POST https://shards.nougenai.com/mcp` with a real JSON-RPC `tools/call`, and re-run a narrow `shards_search`.

**Durable hardening (separate, do after):** pass `signal: ctrl.signal` to the SSE `post()` so no fetch in this worker can hang unbounded again — the config fix routes around that path, it does not repair it.

**Not executed by me**: production deploys stay human-in-the-loop per playbook; wrangler is installed on blade and ready.

## Note
`shards_capture` again returned bare `{}` for this finding, so the shard write is **unverified** — the `20260829T120001Z` defect is still live. This relay leg is the reliable record.
