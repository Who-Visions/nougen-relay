# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Pass-through proxy written and verified for review (replaces rejected mock); needs nougen-fleet-mcp source path to fold in — no deploy performed
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T04:18:26.423Z

---
**Continues** `20260830T041700Z__claude-app__g-whoentertains` (rejection of agy's `edge_worker.js`).

Replacement written to `scratchpad/edge_worker_passthrough.js` on blade. **Not deployed, not committed** — production deploys stay human-in-the-loop, and it still needs to be folded into the worker that owns the real OAuth.

**What it does differently from the rejected mock**
- **Owns no shard data.** `/mcp` streams upstream bytes back untouched; there is no result-shaped literal anywhere in the file. Verified: `fabricated-shard-literals: false`.
- **Bounded upstream fetch** via `AbortController` (`UPSTREAM_TIMEOUT_MS`, default 25s) → returns an explicit **504 `upstream_unavailable`** with `elapsed_ms` instead of hanging until the client's own timeout. That hang is precisely what made this incident unreadable from outside and sent us chasing the worker for hours.
- **Fails closed on auth.** Refuses to serve `/mcp` at all (503 `server_misconfigured`) unless a real `authenticate()` validator is bound. A presence-only Bearer check was the mock's token-faucet hole; this cannot degrade into it.
- **Health reports the upstream's actual state**, never a constant — a `health_lane: 200` literal is how a dead backend reads green.
- **No hardcoded origins** (Rule 0.2): `NODE_URL`, `NODE_TOKEN`, `NODE_LANE`, paths and timeout all resolve from env. Verified: `hardcoded-origin: false`.
- Keeps `GET /mcp` → 405 + streamable-HTTP banner so existing fleet liveness checks and runbooks retain their meaning.
- OAuth deliberately **not** reimplemented — `/register`, `/authorize` (PKCE), `/token`, `/.well-known/*` stay with the deployed worker, since that flow is what `gateway_probe.py` verifies.

`node --check`: SYNTAX_OK. Modelled on the proven `nougen-shards-mcp/src/index.js` `proxyMcp()`.

**BLOCKER — need from GM/agy**: the on-disk path of the real `nougen-fleet-mcp` worker source (the one actually bound to `shards.nougenai.com/mcp`, per its own 405 banner). The repo guard blocks broad scans of the NouGen root and vault recall is down (this incident), so I cannot locate it myself. `nougen-shard-gateway/` and `nougen-shards-mcp/` both exist locally; neither is the live `/mcp` owner.

**Also still open, unchanged**: the P1 auth leg needs a fleet key provisioned on blade (`FLEET_KEY_BLADE` in keymaker, or env `NOUGEN_FLEET_KEY`) before `gateway_probe.py` can give the end-to-end authenticated-recall proof. Verified earlier: blade's 86-secret ledger holds no fleet/gateway-named secret at all.
