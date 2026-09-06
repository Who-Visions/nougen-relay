# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: BLADE parallel work: HUD tracker+relay panels shipped (7578ad5), live vendor pricing, search --json crash fixed, named tunnel up; quick tunnel retired, DNS is the only gap
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T22:18:48.380Z

---
## What blade did this session, in parallel with the tunnel work

### 1. Shipped `7578ad5` to origin/main (public repo, privacy guard PASS)

Cortex HUD went from 3 panels to 5:

- **Tracker** — `billing.usage_summary()` aggregates the existing `usage_logs` ledger nothing was reading: blended tokens, cache-read rate (measured against prompt tokens, since only input is cacheable), shadow cost, free-lane share, per-model breakdown. New `nougen usage [--period] [--json]` + `token_usage` Tauri command.
- **Relay** — `handoff.handoff_feed()` exposes the handoff registry as structured records. New `handoff list --json` + `relay_feed` Tauri command. **Note for other lanes: `--limit` already existed on that parser; do not re-add it.**

Defects fixed on the way: substrate grid hardcoded 9 partitions (now follows engine `MAX_DB_COUNT`, newly reported by `status --json` along with `active_db`); the engine was reporting the active partition and the UI silently discarded it; partition capacity divided by a literal 1024.

### 2. Vendor pricing is now pulled from the vendor's own URI

`tools/import_pricing.py` — Google (section-per-model), Anthropic (matrix incl. cache columns), OpenRouter (JSON catalogue at `/api/v1/models`, avoids their JS-rendered page). 448 models. Sources in `data/pricing/sources.json`, so adding a provider is config, not code.

Dated increases are stored as a **schedule**, not flattened: Gemini 3.7 Flash resolves to 0.75/3.75 today and 1.50/7.50 after 2027-01-01. A single stored number is correct only until a date the vendor has already published.

**OpenAI is configured but disabled** — its page renders the same models at four service tiers under identical headings; a trial parse mispriced gpt-5.6-sol at $10/$45 (real range $2.50–$10) and ingested `chatgpt`/`codex` as models. Quarantined rather than shipped.

### 3. Live crash fixed: `nougen search --json`

`cmd_search` decoded embeddings as UTF-8 JSON text, but they have been float32 BLOBs since the binary migration. Any shard with a real embedding raised `UnicodeDecodeError: 0x99` and took the whole query down. **This is the exact command the Tauri HUD calls, so desktop search was broken.** Now reads both formats and degrades an unreadable vector to `null` instead of failing the query. 5 regression tests added; suite 481 passed / 7 skipped.

Found only because the demo fixtures were regenerated from a real run instead of being hand-written — invented sample data had no embeddings and hid it completely.

### 4. Counts reconciled — three different stores were being conflated

| Endpoint | Shards | Persistent |
|---|---|---|
| blade CLI vault | 151,178 | yes |
| blade node via tunnel (`:4444`) | 151,179 | **no** |
| `mcp.nougenai.com` | 89,422 | **no** |
| connector's configured gateway | 21,982 | **no** |

The long-argued "151k vs 89k" was never one number drifting — they are **different origins**. `mcp.nougenai.com` is served by a different Worker than `nougen-shard-gateway` and points at another node entirely.

## Tunnel status — quick tunnel retired

- Named tunnel `nougen-shards-blade` (`1f830bb9-1b73-490c-b525-b75089ac6316`) is **running, 4 QUIC connections** (mia08/09/10). Run token in Keymaker (`NOUGEN_TUNNEL_RUN_TOKEN`, fp `7c10413467f2`). `NGS_PORT` pinned to 4444.
- **Root cause of the endless hostname churn found**: Scheduled Task **"NouGen Shard Gateway"** respawned `ngs_gateway_publish.py`, which mints a fresh quick tunnel and redeploys the Worker every cycle — and it was running **twice** (venv python + system python), two loops racing to repoint the same Worker. Task now **stopped and disabled**; quick tunnel process killed.
- **Tried and failed — record this so nobody repeats it**: pointing the Worker at `<uuid>.cfargotunnel.com` to skip DNS entirely. The Worker resolves and sends it (confirmed via `X-Gateway-Origin-Host`), but Cloudflare's edge returns **403**. A Worker subrequest is not "traffic through the owning account" in the sense the tunnel requires. **The CNAME is mandatory.**

## The one blocking action (GM only)

`CLOUDFLARE_API_TOKEN` (fp `655061650c12`) is account-scoped — tunnel CRUD ✓, Workers ✓, zone list ✓, **DNS ✗** (`Authentication error`). Wrangler's OAuth token is Workers-scoped and also refused. No lane can create this record.

**Create: CNAME · `shards` · `1f830bb9-1b73-490c-b525-b75089ac6316.cfargotunnel.com` · Proxied ON** (or add Zone→DNS→Edit to the token and re-run `tools/ngs_named_tunnel.py`, which is idempotent).

Then one final `wrangler deploy --var NODE_ORIGIN:https://shards.nougenai.com` and the origin never moves again.

## Current exposure

`nougen-shard-gateway.workers.dev` currently returns 403 (origin is the tunnel, DNS missing). **Nothing the fleet consumes is affected** — `mcp.nougenai.com` (200) and the connector's configured gateway (200) are served by other paths and are untouched. Do not "fix" this by re-enabling the Scheduled Task; that reintroduces the churn this session removed.

## Still open

- Node reports `persistent_storage: false` — that is a property of the **node**, not the tunnel. The named tunnel fixes hostname churn; it does not make the store durable. Separate fix.
- `cloudflared tunnel run --token <secret>` puts the token in the process table. Move to `TUNNEL_TOKEN` before this becomes a standing service.
