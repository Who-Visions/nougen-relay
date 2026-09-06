# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: NAMED TUNNEL LIVE on blade (4 QUIC conns) — one dashboard action left: CNAME shards -> 1f830bb9-1b73-490c-b525-b75089ac6316.cfargotunnel.com
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T22:08:03.005Z

---
## Done

Quick tunnel is being retired. The permanent replacement is up on blade.

- **Tunnel**: `nougen-shards-blade`, id `1f830bb9-1b73-490c-b525-b75089ac6316` (adopted, not duplicated)
- **Ingress**: `shards.nougenai.com -> http://127.0.0.1:4444`, everything else `http_status:404`
- **Status**: connector running, **4 QUIC connections registered** (mia08, mia10)
- **Run token**: minted and stored DPAPI-encrypted in Keymaker as `NOUGEN_TUNNEL_RUN_TOKEN` (fp `7c10413467f2`)
- **NGS_PORT**: now **pinned to 4444** in User scope (was unset — the port was a runtime default, per the earlier ask)

## Blocked on one thing — Zone DNS

`shards.nougenai.com` does not resolve yet. `CLOUDFLARE_API_TOKEN` (fp `655061650c12`) is **account-scoped**: tunnel CRUD ✓, Workers ✓, zone list ✓ — but `GET /zones/{id}/dns_records` returns **Authentication error**. It has no Zone:DNS permission, so the tool cannot create the record.

**GM action (30 seconds, either one):**

1. Add **Zone → DNS → Edit** on zone `nougenai.com` to the existing token, then re-run `tools/ngs_named_tunnel.py` — it is idempotent and will finish the DNS step by itself; **or**
2. Create the record by hand:
   - Type **CNAME**, name **shards**, target **`1f830bb9-1b73-490c-b525-b75089ac6316.cfargotunnel.com`**, **Proxied ON**

## Cutover order — do NOT reorder, step 3 before step 1 causes an outage

The Worker `nougen-shard-gateway` (fronting `mcp.nougenai.com`) currently has `NODE_ORIGIN` pointed at the **rotating quick-tunnel hostname**. Killing the quick tunnel first would leave the Worker pointing at a dead origin and take the fleet gateway down. I left it running for exactly that reason.

1. Create the DNS record (above); confirm `https://shards.nougenai.com/health` answers.
2. Repoint the Worker once: `wrangler deploy --var NODE_ORIGIN:shards.nougenai.com` from the gateway dir. This is the **last** deploy — the hostname never changes again.
3. Stop the publish loop, then kill the quick tunnel (`cloudflared tunnel --url http://127.0.0.1:4444`, PID 11884 at time of writing).

## Two defects found while doing this

- **The publish loop is running twice**: PID 18796 (`.venv` python) and PID 31056 (system python), both `tools/ngs_gateway_publish.py`. Two loops each minting quick tunnels and racing to redeploy the same Worker. Whichever survives cutover, only one should exist — and after step 3 neither should.
- **The run token is passed as a command-line argument** (`cloudflared tunnel run --token <secret>`), so the secret is visible to anything that can read the process table. Move it to a credentials file or `TUNNEL_TOKEN` env before this becomes a standing service.

## Persistence note — the storage half is a separate problem

The interim gateway currently answering reports `persistent_storage: false` with *"memories are wiped on every restart/deploy"* and serves 21,982 shards. Blade's origin behind this tunnel is the real vault: **151,178 shards, 9 partitions, persistent**. Once DNS lands and the Worker is repointed, the ephemeral-storage problem disappears with it — the origin becomes durable disk instead of a resettable working set.
