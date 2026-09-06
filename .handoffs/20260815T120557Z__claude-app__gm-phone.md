# 🤝 Git Handoff — claude-app / gm-phone

**Goal**: mondy: set SHARD_GATEWAY_URL in nougen-fleet-mcp wrangler.toml + redeploy — blade's node is up and tunnelled, var is bound but not pointed
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T12:05:57.790Z

---
## Blade's side is done. The last hop needs mondy, because the worker source is there.

**Blade NGS node is up, boot-persistent, and reachable from the public internet.**

| | |
|---|---|
| tunnel URL | `https://river-open-continued-geo.trycloudflare.com` |
| LAN URL | `http://10.0.0.87:4444` |
| `/health` through the tunnel | `status: ignited`, `node_token_configured: true`, **151,159 shards** |
| auth | `X-NGS-Token` — no header → 401, correct header → 200 |
| boot | Scheduled Task `NouGen NGS Node`, at-logon, runs as `super` |

## The ask

`wrangler secret put SHARD_GATEWAY_URL --name nougen-fleet-mcp` from blade **fails**:

```
Binding name 'SHARD_GATEWAY_URL' already in use. [code: 10053]
```

The name is already bound as a **plain var**, which means it is declared in `nougen-fleet-mcp`'s `wrangler.toml` — and that repo is on mondy, not blade (relay `20260814T210729Z`: "fleet connector built+tested on mondy"). A plain var can only be changed where it is declared, so it needs a source edit plus `wrangler deploy` from mondy. Blade has `workers write` and can deploy, but has no copy of the source and will not guess a bundle back into existence.

**Do this on mondy:**
1. In `nougen-fleet-mcp`'s `wrangler.toml`, set `SHARD_GATEWAY_URL = "https://river-open-continued-geo.trycloudflare.com"`
2. `wrangler deploy`
3. Check whether the worker also needs the node's `X-NGS-Token` to call `/search`. Bound secrets today are `FLEET_KEYS`, `GITHUB_TOKEN`, `SIGNING_SECRET` — **nothing carries the NGS node token.** If the shards_* path 401s, that is why. The token is in blade's keymaker as `NGS_NODE_TOKEN` (DPAPI, user-bound to `super` — it cannot be read off-box; ask blade to hand it over on a private channel, do not put it in a leg).

## Read this before you paste that URL

**It is a quick tunnel, so the hostname is ephemeral — it changes every time cloudflared restarts.** Baking it into `wrangler.toml` means the worker breaks on blade's next reboot and every reboot after. Treat this as a today-only unblock, not the wiring.

`cloudflared` on blade has no `cert.pem` — it has never been logged in, so a *named* tunnel with a stable hostname (e.g. the `mcp.nougenai.com` that was already planned) cannot be created from here. That needs one of:
- GM runs `cloudflared tunnel login` once (interactive browser authorization — an agent should not be doing that), or
- a Cloudflare API token with `Tunnel:Edit` lands in keymaker (there is no Cloudflare credential in there today — 50 secrets, all Gemini/OpenRouter/HF/Google).

Once either exists, blade converts to a named tunnel and `SHARD_GATEWAY_URL` becomes a constant nobody edits again.

## Done when

`shards_status` / `shards_recall` through the fleet connector return blade's shards instead of a gateway error, and GM can run the VeilVerse recall from chat.

## Context worth having

Federated `/search` latency was 50.7s this morning and is now ~4.1s (unbounded fuzzy full-scan in `core.py`, fixed — see leg `20260814T232123Z`). The connector's default search timeout is 5s, so **the margin is about 0.9s**. If recall through the worker comes back empty rather than erroring, suspect the timeout before suspecting the vault — `query_cloud_shards` swallows a timeout, logs "cloud node skipped", and contributes nothing. `NGS_CLOUD_SEARCH_TIMEOUT` now exists to widen it.
