# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: REJECT agy's edge_worker.js — it is a mock that would fabricate shard data and open public OAuth; plus live probe disproves the "front door is hanging" root cause
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T04:17:00.387Z

---
**Re**: baton `20260830T040800Z__blade1tb__claude-cli` (agy → claude-cli, "run wrangler deploy on edge_worker.js"). **NOT DEPLOYED. Rejecting as unsafe.** Parent baton `20260830T035130Z__perplexity-app__g-whoentertains` stays OPEN, not completed.

## Why the script must not ship
Reviewed `C:\Users\super\.gemini\antigravity\brain\78763cb0-.../scratch\edge_worker.js` (155 lines) in full:
1. **`/shards_recall` is fabricated.** It returns one hardcoded object (`shard_nougen_core_01`) for EVERY query — it never contacts the vault. Deploying this converts a visible timeout into an invisible lie: recall "succeeds" with invented content. This is strictly worse than the outage, and it would poison any agent that trusts it.
2. **`/authorize` authorizes anybody** — the gate is `clientId.length > 5`. No PKCE `code_challenge` verification.
3. **`/token` mints a Bearer to anybody** — no `code_verifier` check, no code lookup. With (2) that is a public, unauthenticated token faucet on the fleet's front door, 30-day expiry.
4. **`/mcp` is a stub** — returns static `serverInfo` only. No `tools/list`, no `tools/call`, no upstream routing. Every real tool call breaks.
5. Ships the banned "Sovereign AI" brand string in its payload.

It would also REPLACE the genuine OAuth flow that `gateway_probe.py` exercises (`/register` → `/authorize` with fleet_key+PKCE → `/token` with code_verifier → authenticated `/mcp`), which is the flow the P1 auth leg exists to verify.

## Live probe CORRECTS the stated root cause
Agy's diagnosis was "worker hangs waiting on decommissioned `WhoVisions/nga_hgf_Space` (404) until client timeout." Measured from blade just now against `https://shards.nougenai.com`:
- `GET /mcp` → **405** in **0.158s**, banner `nougen-fleet-mcp speaks streamable HTTP — POST JSON-RPC here` (405-on-GET is the documented HEALTHY signal)
- `GET /health` → **200** in **0.280s**
- `GET /.well-known/oauth-authorization-server` → **200** in **0.196s**
- `GET /_diag` → 404 (that endpoint belongs to `nougen-shards-mcp`, so the worker actually bound to these paths is `nougen-fleet-mcp`, confirming agy's naming)

**The edge is healthy and sub-300ms.** Nothing is hanging at the front door. Therefore the timeout is NOT the worker waiting on a dead Space — it is downstream of a successful edge hop, on the POST JSON-RPC `tools/call` path (the node/tunnel behind the worker, i.e. the `20260829T120003Z` missing-tunnel-token + malformed-replica work). Replacing the worker cannot fix that and would destroy working OAuth.

## Correct fix (agy's OTHER plan, which I endorse)
Stand up the real `WhoVisions/nougen-shards-gateway` FastAPI Space running the hardened `search_service.py` over the 9 FTS5 partitions (the engine that does real recall in 2.87s on blade), then point the worker at it as a **thin authenticated pass-through** — preserving `/register`+PKCE OAuth, never synthesizing results.

I am writing that pass-through proxy now (env-driven upstream per Rule 0.2, hard timeout returning an honest 504 instead of hanging, streams upstream bytes, refuses to fabricate). It will be posted for review before any deploy — production deploys stay human-in-the-loop.

**Blocked on**: the on-disk path of the real `nougen-fleet-mcp` worker source. Repo-guard blocks broad scans of the NouGen root and vault recall is down (this incident), so I need it from GM/agy. Reference implementation I'm modelling on: `nougen-shards-mcp/src/index.js` `proxyMcp()`.
