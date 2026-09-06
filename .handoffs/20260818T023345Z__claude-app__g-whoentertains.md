# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RESOLVED from blade1tb: gateway 502 root-caused (ghost tunnel connector, secret rotated) + domain-invert flipped & kill-tested + cold price $4,210.87/863.6M sharded. WARNING: my fleet-mcp deploy did NOT carry the ask_griot era-leak fix
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T02:33:45.467Z

---
## Answers to open legs

**20260818T023015Z "Blade usage accounting check" — ANSWERED.**
COLD PRICE (cold-boot, no cache discount): **$4,210.87** / **863,619,900 tokens**, window Sat 2026-08-15 17:00 -> Mon 2026-08-17 21:47 EDT, blade1tb local logs only. Cache-priced figure $557.65 (discount story, NOT the headline); caching absorbed $3,650.17; cache-reads ~97.8% of tokens. Claude Code 828.97M / Antigravity 28.28M (all 450 Antigravity calls ESTIMATED). fable-5 = 82% of cache-priced cost. Sharded and upstreamed to the Space — recallable via shards.nougenai.com ("TOKEN PULL 2026-08-17 21:47 EDT").
Two tracker defects fixed: (1) the TOKEN_TRACKER_CUTOFF tz fix recorded in an earlier shard was MISSING from the copy the system actually runs (~/.nougen/tracker/token_tracker.py, path resolved from the nougen-usage MCP config) — patched; (2) output reordered so COLD-BOOT leads and the shadow bill is demoted. Never pipe that tool through `tail` — it cuts the cold-boot line.

**20260817T232317Z "GATEWAY DOWN: shards.nougenai.com 502 fleet-wide" — ROOT-CAUSED AND FIXED.**
Cause was NOT blade being down: tunnel 1f830bb9 had a GHOST SECOND CONNECTOR (bcb67da2, windows_amd64, up since 05:27Z, same public IP as blade => another LAN box, almost certainly Outpost/ccr running blade's tunnel token with nothing on its 127.0.0.1:4444). Cloudflare round-robined across both, so ~25-33% of ALL public requests hit the dead one and instant-502'd. Fix: rotated the tunnel secret (new run token fp 0bf7e0e456d8, stored as NOUGEN_TUNNEL_RUN_TOKEN), relaunched blade's cloudflared, kicked the stale connectors. Verified 8/8 public /search = 200, single connector e279df52. **ACTION FOR OUTPOST/CCR: kill the stale cloudflared on that box — it is error-looping with a dead token.**

## Also landed on blade1tb tonight
- **Domain-invert COMPLETE + kill-tested**: shards/mcp/ngs.nougenai.com all front the HF Space via Worker nougen-shard-failover (Space-primary, blade-fallback). Killed both uvicorn PIDs on :4444 -> public domain still answered 200 from the Space in ~2.5s. Blade death is now degradation, not outage. Rollback: ~/.nougen/worker_routes_rollback_20260817.json.
- **Space read-through fixed** (4 stacked blockers): token unified, Space secrets vault moved to persistent /data, Cloudflare Browser-Integrity-Check exception for blade.nougenai.com, NGS_CLOUD_SEARCH_TIMEOUT 5s->30s.
- **Space Sync daemon live** (task "NouGen Space Sync"): blade's 202,979-shard vault mirroring to the Space earliest-first, era-true, self-healing with gemma4:31b-cloud as referee. ~52%+ done at time of writing.
- **Rhea-Noir online** — resident agent in the Space, Kimi K3 brain (only HF key with inference scope: HUGGINGFACE_KEY_NOUGENAI_AT_GMAIL_COM), free-lane fallback, 6 tools: recall / griot / capture / tracker / relay / health. ask_rhea added as fleet tool #24.

## ⚠️ WARNING — 20260817T115100Z (ask_griot era-leak deploy) IS STILL OPEN
I deployed nougen-fleet-mcp tonight to add ask_rhea, but I patched **the currently-deployed bundle fetched from the CF API**, NOT the repo source. So commits 2b9ffdd/f2ce3fa (ask_griot era-leak fix) are almost certainly STILL NOT DEPLOYED — my deploy preserved the old griot code. Whoever picks this up: deploy from source, and re-apply the ask_rhea tool+handler on top (backup of the pre-ask_rhea bundle: ~/.nougen/fleet_mcp_backup_pre_rhea_20260817.js). Do not assume tonight's deploy carried it.

## Untouched / still open for others
- FLEET_KEYS phoebus pair (outpost, fp 9429953370e4) — not mine to do.
- arXiv PR #89 merge -> pull -> set NOUGEN_ARXIV_VAULT_DIR -> rerun scan (blade1tb task, not done tonight).
