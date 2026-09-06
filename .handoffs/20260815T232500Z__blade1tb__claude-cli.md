## DONE — the chain is closed. Connector URL is the fleet Worker, not shards.nougenai.com.

### 1. CNAME created, permanent hostname live
`shards.nougenai.com CNAME 1f830bb9-1b73-490c-b525-b75089ac6316.cfargotunnel.com` (proxied) → **HTTP 200 in 0.29s**, 151,184 shards, 9/9 mounted.

The blocker was a token SCOPE, not a dead token. Cloudflare splits policies by resource: an "Entire Account" policy grants `Account DNS Settings` / `DNS Firewall` / `DNS View` — none of which touch zone DNS records. The needed permission is plainly named `DNS` and only appears under a policy whose resource is **All Domains**. Symptom: `GET zones/{id}` 200 while `GET zones/{id}/dns_records` 403. GM added the second policy; the token already in Keymaker started working with no re-paste (editing a token does not change its value).

Also correcting my own earlier claim: a `cfat_` token verified against `/user/tokens/verify` ALWAYS returns 401. Use `/accounts/{acct}/tokens/verify`. I called a live token dead on that basis.

### 2. Quick tunnel RETIRED
pid killed. The old `holland-analyst-increased-paragraphs.trycloudflare.com` now returns 530. Only the named tunnel remains (4 QUIC conns).

### 3. THE ACTUAL CONNECTOR FIX — two stale Worker vars

Both Workers still pointed at the dead quick tunnel. Repointed via the CF API:

| Worker | var | now |
| --- | --- | --- |
| `nougen-fleet-mcp` | `SHARD_GATEWAY_URL` | `https://shards.nougenai.com` |
| `nougen-shard-gateway` | `NODE_ORIGIN` | `https://shards.nougenai.com` |

All 5 secrets on the fleet Worker verified intact after the patch (`FLEET_KEYS`, `GITHUB_TOKEN`, `GOOGLE_CLIENT_SECRET`, `SHARD_GATEWAY_TOKEN`, `SIGNING_SECRET`). Note the settings PATCH requires `multipart/form-data`, not JSON, and secrets must be re-sent as `{"type":"inherit"}` or they are dropped.

### 4. Connector URL — I had this wrong and it cost the GM time

`https://shards.nougenai.com` is NOT the connector endpoint. It has no OAuth: `/.well-known/oauth-authorization-server` 404, `/` 404, `/mcp/` 401. Pointing claude.ai at it produces exactly *"Couldn't register with NouGenShards's sign-in service."*

**The connector URL is `https://nougen-fleet-mcp.whoentertains.workers.dev`** — the OAuth 2.1 + DCR + PKCE Worker built on mondy (leg `20260814T210729Z`), which already carries `GOOGLE_CLIENT_ID`, `GOOGLE_ALLOWED_EMAILS` (7 addresses) and `GOOGLE_REDIRECT_ORIGIN`. Verified: `/.well-known/oauth-authorization-server` → 200, `/mcp` → 405 on GET (correct for streamable HTTP). It fronts blade with its `claude-client` lane token, so blade needs no Claude-facing auth — exactly as that leg said.

### DUPLICATED WORK — my fault, flagging so it stops

Legs `220112Z`, `220803Z`, `221848Z` are another lane on this same key. It had already answered the node-token fingerprint, already brought the named tunnel up, already minted `NOUGEN_TUNNEL_RUN_TOKEN`, already pinned `NGS_PORT=4444`, and already hit the identical Cloudflare DNS wall. I redid all of it because I did not read the legs first. **Read the legs before probing.**

### Also fixed on blade this session
- Node restarted onto `d4798e8` — it had been serving pre-coverage code since 14:34, so `/health` had no `substrate` block.
- Removed `{'name':'n1','url':'https://node.invalid'}` from `cloud_nodes` — a test fixture live since 2026-08-07 that made every federated search burn the 5s timeout on a dead host.
- Blade runs under the repo `.venv` (gradio 6.18), NOT system Python. I killed the node before checking that and it stayed down ~1 min. Read the running process's CommandLine before restarting anything.

### Open
- HF Space `nougenai/NouGenShards` has `NGS_UPSTREAM_URL=https://shards.nougenai.com` set but its public image is stale (no `substrate` block, still 89,422). Space direct URL already federates correctly: 17,946 local + upstream blade, `read_through: true`, persistent `/data`. `mcp.nougenai.com` serves the OLD image — worth confirming what that hostname actually routes to.
