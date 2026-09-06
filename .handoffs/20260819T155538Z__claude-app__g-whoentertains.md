# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ask_rhea verified registered + live in deployed fleet worker; root blockers were double-DPAPI-wrapped vault and wrong CF account; kaedra_ask genuinely missing
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-19T15:55:38.756Z

---
## 🔴 Active Incidents
- None from this lane. **ask_rhea "unknown tool" is NOT reproducible against the artifact.** Deployed `nougen-fleet-mcp` (version deployed via api at 2026-08-19T15:45:50Z) advertises ask_rhea in TOOLS and carries `async ask_rhea` in HANDLERS. Source `Who-Visions/nougen-fleet-mcp @ a4d1d74` matches the deployed bundle with a whitespace-only diff. Any session still seeing "unknown tool: ask_rhea" opened before 15:45:50Z and holds a frozen manifest - **reconnect the connector, then re-probe** (shard 22437 behaviour).

## 🟡 Ongoing Investigations
- **kaedra_ask is genuinely absent** from both source and the deployed bundle (0 hits), while the worker still carries a live `KAEDRA_GATEWAY_TOKEN` secret binding. Deployed tool count is **24**, not the 25 recorded in shard 22642. A binding with no tool = artifact-patched deploy later overwritten from source. Needs a decision: re-add kaedra_ask to source and deploy, or drop the orphan binding.
- **agent_secrets.db is double DPAPI-wrapped** on at least the CLOUDFLARE_* and NGS_* keys. Not yet remediated - left as-is pending GM call, since rewriting the credential store is a mutation with blast radius.

## 📋 Recent Changes
- No code or config changed. Read-only verification only: cloned source, pulled the deployed bundle via the CF API, stripped the multipart envelope, diffed, and read version history.
- Diagnostic added to the vault (FAILURE shard) with three reusable rules: unwrap DPAPI in a **loop**; a wrong-length decrypted secret is a decode failure, never a rotation; and error-message punctuation fingerprints the backend (`unknown tool: X` with a colon = fleet worker worker.js:1710; `unknown tool X` no colon = rhea_noir.py:258 in the Space).

## ⚠️ Known Issues & Workarounds
- **Vault decrypt**: single `CryptUnprotectData` yields a 372-char "AQAA..." blob that base64-decodes to the DPAPI magic `\x01\x00\x00\x00\xd0\x8c\x9d\xdf`. Decrypt again to get the real value. This is the true origin of shard 22642's retracted "stale NGS_NODE_TOKEN_SPACE" claim - correctly unwrapped it is 47 chars, fp `15c96012efbf`.
- **Cloudflare account trap**: `CLOUDFLARE_API_TOKEN` opens account `da43369a808d156278ddf6b8c7f55f4b` (Aiwithdav3, **zero workers**) and returns a confident 404 for nougen-fleet-mcp. The worker is on `0d4ac187acceea4d9692619097927d1e` (Whoentertains, 9 workers) via `CLOUDFLARE_TOKEN_WHOENTERTAINS`. Sweep tokens against /accounts then /workers/scripts; never trust the un-suffixed key name.
- `shards.nougenai.com/agent` answers **401 with the gate message** (healthy). The gate names the `?token=` query form because Claude connectors cannot set custom headers. blade's local store does not hold the `/agent` gate credential.

## 📅 Upcoming Events
- None scheduled. Next arxiv-daily-scan 2026-08-20.
