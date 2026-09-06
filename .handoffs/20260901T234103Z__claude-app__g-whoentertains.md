# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ChatGPT 404 fixed (/openapi.json route had no handler); and evidence that restarting phoebus does NOT fix it under fan-out load — PR #174
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T23:41:03.186Z

---
Two results, one shipped fix and one corrected assumption. Both matter to anyone touching the fleet worker or phoebus.

## 1. ChatGPT 404 — fixed, deployed 23:26:46Z
`nougen-fleet-mcp`'s fetch handler is a `switch` on path with `default: 404`. The Cloudflare routes for `/openapi.json` and `/openapi*` have pointed at this worker since before today, **but no case existed**, so every request fell through to that default. The ChatGPT *action* lane was broken the whole time while the MCP lane was healthy — `/mcp` answered **401, never 404**.

**A route with no handler is a 404 that reads like an outage**, and it's invisible from the worker side because nothing logs a request that matched no case. Confirmed *not* caused by today's fan-out deploys — the pre-deploy bundle had zero occurrences of `openapi` either.

Fix: `openapiDocument(origin)` **generated from the live TOOLS array**, not hand-written — a hand-maintained spec drifts the moment either side changes, and a spec that disagrees with the server is worse than none. OpenAPI 3.1.0, 27.6 KB, all 26 tools in the `params.name` enum with each tool's real `inputSchema` under `components.schemas`, OAuth pointing at the worker's own `/authorize` and `/token`, `servers[]` from request origin. Validated **before** deploy by extracting the function into a node harness and asserting the emitted document — syntax-checking a bundle does not prove the JSON it emits is well-formed.

## 2. Correction: restarting phoebus does NOT fix it right now
I built a scheduled restart on the belief that uptime degradation was the problem. **The first live run measured `before=20.4s`, `after=20.3s`** — the restart bought nothing.

What changed since the 16s→3s restart benefit at 21:12Z is that **the fan-out went live at 22:59Z**, so phoebus now serves continuous fleet read traffic. Verified rather than assumed: the node's uvicorn log shows `POST /mcp/` arriving from **Cloudflare IPv6 addresses** (`2a06:98c0:3600::103:0`) through the tunnel, 28 requests in a recent window.

**Two distinct effects were being conflated**: (a) genuine uptime degradation — real, measured with fan-out *off*; (b) concurrency load from the fan-out — now dominant, and no restart recovers it. Schedule cut from six-hourly to **nightly** on that evidence: four restarts a day would buy four cold-start outages of 95–250s and very little speed. **The real fix is still the node's concurrency ceiling.**

## 3. Cold start is network-dependent — this broke my first script version
The node blocks on outbound calls to **`api.gradio.app`** (analytics + version check) before uvicorn binds, so boot measured **~95s and ~250s on the same box hours apart**. My 180s poll ceiling logged a healthy node as FAILED; now 420s. *A restart that is merely slow must not be recorded as one that failed.* Worth doing: `GRADIO_ANALYTICS_ENABLED=False` removes a third-party network dependency from the node's boot path entirely.

**PR #174** — `ops/ngs-node-refresh.sh` + plist template, following the existing `install-launch-agents.sh` convention. The script logs recall latency either side of every restart, so the schedule accumulates the dataset that can find the leak rather than only papering over it. That logging caught finding 2 within minutes of being written.

**Done when**: #174 reviewed/merged, and someone takes the node concurrency work — that is the blocker, not uptime.
