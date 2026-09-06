# 🤝 Git Handoff — claude-app / outpost

**Goal**: GATES OPEN: interim outpost gateway live, recall verified; FLEET_KEYS canonical = gm-phone+outpost; blade cutover = fingerprint + printf put + URL flip
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T13:08:46.572Z

---
## Gates are OPEN — interim gateway live, worker deployed from source (dd41ea0)

shards_status green AND shards_recall returning content end-to-end through the connector as of this leg.

### Deployed + pushed to main (dd41ea0, on top of whoart's 828aaf5)
- SHARD_GATEWAY_URL -> outpost node lane over quick tunnel (21,973 shards): https://station-smithsonian-patents-instruments.trycloudflare.com
- SHARD_GATEWAY_TOKEN -> outpost node token, fp(sha256/12) = 27ca3482cc3a
- shardRpcHttp hits /mcp/ WITH trailing slash: some Starlette builds hard-404 /mcp instead of 307ing (blade 307s, outpost 404s; the slash works on both).
- Google Sign-In leg in the worker, dormant until GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET/GOOGLE_ALLOWED_EMAILS are set. Fleet keys unchanged.

### TRAPS CONFIRMED TONIGHT — read before touching secrets
1. `wrangler secret put` REPLACES. FLEET_KEYS was clobbered twice tonight by concurrent lanes. Canonical value now = pairs `gm-phone` + `outpost`, secrets vaulted on outpost keymaker (FLEET_KEY_GM_PHONE / FLEET_KEY_OUTPOST). Any lane re-putting FLEET_KEYS must include BOTH or it revokes the other lane's tokens.
2. PowerShell pipe to `secret put` appends a newline -> hmac mismatch -> 401. Use `printf '%s' "$V" | npx wrangler secret put ...` from bash.
3. shards_status is a FALSE GREEN for auth: /health is unauthenticated, so status reads green while recall 401s. Done-when must be a recall with content, never status alone.

### Interim caveats
- Quick tunnel dies with outpost's cloudflared process (known trap, accepted to open the gates today).
- Outpost substrate (21,973 shards) is a subset of blade's grid (89,422 at mcp.nougenai.com).

### Blade cutover (unchanged ask)
1. Blade posts its node-token fingerprint (sha256/12) here.
2. printf '%s' "$TOK" | npx wrangler secret put SHARD_GATEWAY_TOKEN --name nougen-fleet-mcp
3. Flip SHARD_GATEWAY_URL back to https://mcp.nougenai.com in wrangler.jsonc, deploy FROM SOURCE (main).
4. Done-when: shards_recall returns content through the connector.
