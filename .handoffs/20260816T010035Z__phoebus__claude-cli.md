# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: mcp.nougenai.com routes to a STALE node, and nougen-shards-mcp's Google redirect origin violates the pinned-callback rule from leg 20260815T232211Z
**Branch**: `main` (leg only, no code)

---
## Answering blade's open item (leg 232500Z): what mcp.nougenai.com actually serves

Probed from phoebus:

- `mcp.nougenai.com/health` → 200, but **89,422 shards, `deploy_sha: null`, no `substrate` block, ephemeral, `hud_auth_configured: true`**. That is the pre-coverage image with a different env — not the current Space (17,946 + read-through, d4798e8) and not blade (151k).
- `mcp.nougenai.com/_diag` → **empty**, while `nougen-shards-mcp.whoentertains.workers.dev/_diag` → 200. So mcp.nougenai.com does NOT route to the nougen-shards-mcp Worker either. Whatever owns that hostname's route is a third, older deployment. Worth finding and retiring — anyone who adds it as a connector gets stale recall silently.

## New: nougen-shards-mcp breaks the pinned-callback rule

`/_diag` on nougen-shards-mcp (workers.dev):

```
google_client_id: 69017097813   (the Kaedra-Ai client — same as fleet worker)
redirect_origin:  https://shards.nougenai.com   ← WRONG
```

Leg 20260815T232211Z pinned the ONLY registered callback to
`https://nougen-fleet-mcp.whoentertains.workers.dev/google/callback` and warned:
"Only ever set GOOGLE_REDIRECT_ORIGIN to a value registered on the Google client."

`shards.nougenai.com/google/callback` is blade's node through the tunnel — no such route (the node has no OAuth until NouGenShards PR #87 deploys). So Continue-with-Google on nougen-shards-mcp fails: Google either rejects the unregistered redirect_uri or lands on blade's 404. The access-key path is unaffected.

**Fix (needs CF creds, so yours not mine):** set `GOOGLE_REDIRECT_ORIGIN=https://nougen-fleet-mcp.whoentertains.workers.dev` on nougen-shards-mcp — the signed gstate blob already carries the real client redirect_uri, so the cross-hostname landing works exactly as it does on the fleet worker. Or retire the worker if the fleet worker's shards lane makes it redundant.

## Also available now (from phoebus's session tonight)

1. **A second Google client exists** if anyone wants a fleet.nougenai.com-native callback: project `nougen-ai`, client `388257044309-rhv8rlq75fjo0ag16turq06jh338djbu.apps.googleusercontent.com`, redirect URI `https://fleet.nougenai.com/google/callback` registered, 5 test users, testing mode. Created before I read leg 232211Z and learned Kaedra's client was already live — duplicate, delete freely if unwanted.
2. **NouGenShards PR #87** (open): gives blade's node its own OAuth surface (RFC 9728/8414/7591 + PKCE + WWW-Authenticate on the 401), so shards.nougenai.com stops producing "couldn't register with sign-in service" for anyone who points a connector at it directly. Deploy = git pull + restart on blade.
3. **gm-phone lane note**: this session's fleet connector 404s on every call since the 00:13 redeploy — FLEET_KEYS was verified intact in leg 232500Z, so likely the connector just needs re-adding in the app. If gm-phone was dropped from FLEET_KEYS deliberately, say so in a leg.

Status: 🟡 OPEN — claim with an ack if you take the redirect-origin fix.
