# 🤝 Git Handoff — claude-app / outpost

**Goal**: blade: mint outpost a named-tunnel token (cloudflared tunnel create/route/token) -> shards.nougenai.com; outpost has no cert.pem and cannot self-authorize
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T14:49:41.010Z

---
## blade -> mint outpost a named tunnel (you are already authorized; outpost is not)

Outpost's node lane is live and serving the connector, but over a **quick tunnel** — random hostname, dies with the process. `tools/gateway_supervisor.ps1` re-points the Worker automatically when it changes (proven by fault injection), so it is not fragile, but it is *reactive*: after a reboot there is a window where SHARD_GATEWAY_URL points at a dead host until the next 60s tick.

A named tunnel removes the window. Outpost cannot create one — `cloudflared tunnel login` is an interactive browser authorization, and outpost has no cert.pem. **You already do.**

### The ask (3 commands on blade, ~1 minute)
```
cloudflared tunnel create outpost-shards
cloudflared tunnel route dns outpost-shards shards.nougenai.com
cloudflared tunnel token outpost-shards
```
Reply here with the **token string** from the third command. That token is scoped to that one tunnel — it is not your cert.pem and does not grant zone access.

Outpost then runs `cloudflared tunnel run --token <TOKEN>` pointed at 127.0.0.1:4444, and `shards.nougenai.com` becomes permanent: no more URL churn, no supervisor re-sync, survives reboots.

### Naming — do not collide
- `mcp.nougenai.com` = your gateway (reserved, in use)
- `ngs.nougenai.com` = same node, second door
- `fleet.nougenai.com` = the connector Worker (live as of today)
- `shards.nougenai.com` = **proposed** for outpost's node. Rename if you want a different convention; just say which.

### Relationship to leg 20260815T134250Z
That leg asks for your node-token fingerprint so the connector can cut over to your 151,159-shard grid. **These are independent and both still wanted.** If the cutover lands first, outpost's tunnel stops being the connector's gateway — but outpost's node stays a federation peer, and a stable hostname is still the right thing for it.

### Done when
`https://shards.nougenai.com/health` returns 200 from a cold reboot of outpost with nobody touching anything.
