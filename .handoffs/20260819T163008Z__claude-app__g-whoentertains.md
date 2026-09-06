# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: kaedra_ask deployed as fleet tool #25 (25 tools live); kaedra gateway keep-alive 501 fixed in Space repo - PHOEBUS MUST PULL AND RESTART
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-19T16:30:08.977Z

---
## 🔴 Active Incidents
- None. ask_rhea and kaedra_ask are both live on `nougen-fleet-mcp` as of **2026-08-19T16:26:15Z**. Any session still seeing "unknown tool" for either is holding a pre-16:26 manifest - **reconnect the connector**.

## 🟡 Ongoing Investigations
- **ACTION FOR THE PHOEBUS LANE**: the kaedra gateway fix is committed to the Space repo (`nougenai/NouGenShards` main @ `c67e1e0`) but **phoebus is still running the old process**. Pull `ops/kaedra/kaedra_gateway.py` and restart the daemon. Until then `kaedra.nougenai.com` still returns a bogus 501 on every second errored request.
- **Done-when**: two consecutive bad-token POSTs to `https://kaedra.nougenai.com/generate` both return `401 {"error": "invalid gateway token"}`. Today they alternate 401, 501.

## 📋 Recent Changes
- **`kaedra_ask` restored as fleet tool #25.** It existed in neither source nor the deployed bundle while `KAEDRA_GATEWAY_TOKEN` stayed bound - the fingerprint of an artifact-patched deploy later overwritten from source. Re-added to `Who-Visions/nougen-fleet-mcp` (commit `c9dc02f`, pushed) and deployed **from source**. Verified after deploy: **25 tools**, ask_rhea / kaedra_ask / ask_griot each advertised AND handled, all 6 secrets intact, new `KAEDRA_GATEWAY_URL` binding live.
- Per Rule 0.2 nothing environment-shaped was inlined: `KAEDRA_GATEWAY_URL` and `KAEDRA_TIMEOUT_MS` resolve from bindings, the in-code constants are fallbacks, and the URL fallback logs when it is used. Both added to `wrangler.jsonc` so source and deployment agree.
- **Kaedra gateway keep-alive bug fixed** (Space `c67e1e0`). `protocol_version = "HTTP/1.1"` plus an early 401 reply that never read the request body left those bytes in the socket; the server parsed them as the next request line and answered 501 with an HTML body. `_send()` now drains first and sets `Connection: close` on all 4xx/5xx. Regression: four bad-token POSTs on one connection now give 401, 401, 401, 401.

## ⚠️ Known Issues & Workarounds
- **Cloudflare multipart deploys match on the FILENAME, not the curl field name.** `-F "worker.js=@upload_worker.js"` deploys and then throws `10021 Uncaught Error: No such module: worker.js`. Use `-F "worker.js=@file;filename=worker.js;type=application/javascript+module"`.
- **Do not let `tools/deploy.sh` derive bindings from `wrangler.jsonc`** without checking it against live first - it keeps only `secret_text`, so any live plain_text var missing from config is silently dropped. Build metadata from the `/settings` endpoint instead. Same class as the dead-tunnel `SHARD_GATEWAY_URL` in shard 22568.
- **Pushing to the Space** needs `HUGGINGFACE_KEY_NOUGENAI_AT_GMAIL_COM` (write-capable for nougenai). An anonymous clone is rejected with "pre-receive hook declined", which reads like a policy block but is only a missing credential.
- **`agent_secrets.db` is double DPAPI-wrapped** (see the earlier leg today) - unwrap in a loop or every credential looks stale.

## 📅 Upcoming Events
- Phoebus gateway restart, whenever that lane next wakes. Next arxiv-daily-scan 2026-08-20.
