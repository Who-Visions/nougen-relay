# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: WEEKEND SEALED: 6 commits public, grid multi-vendor + era-true + fast; queue handed to the next lane
**Branch**: `main`
**When**: 2026-08-17T10:04:43.251Z

---
## 🔴 Active Incidents
- None. Node fast and healthy (/health 0.01s, /search 6.75s), public edge 200, tunnel up.

## 🟡 Ongoing Investigations
- Residual ~6s floor on /search = grid keyword double-pass (ledgered follow-up).
- Ledger open: coverage-count discrepancy, stale dedup-index ghosts, dedup-shadowing provenance, sol_memory_vault adapter (4,890 finding/logic rows), lore_explorer.db (zero tables — GM call), `test_mcp_endpoint.py` pre-existing merge markers (blocks the public gateway auth tests — fix early).
- ~2,863 migrated rows have genuinely unrecoverable eras (ledgered, no invented dates).

## 📋 Recent Changes (the milestone weekend, 2026-08-15/16)
- **Six commits pushed to public main**: b2ef94a recall engine (domain-mask fusion, FTS OR-fallback, bm25 normalization) · cd3c372 coverage federated_stores · 6cff987 capture(original_timestamp) · 78bb0b0 NouGenTube · bf133eb dynamic secrets-vault discovery · f140747 federation tiering + per-store budget + health cache. Suite 584 passed / 4 skipped.
- **Connector stack multi-vendor**: shards.nougenai.com/mcp serving **23 tools** incl. `ask_griot` (lineage told oldest-first, corrections flagged); REDIRECT_ALLOW additively opened to chatgpt.com + platform.openai.com; Claude, ChatGPT and a third-party client lane all verified.
- **Grid**: era re-stamp of 147,124 rows (floor 2026-06 → 2025-11-30; Apr-2024 conversation archive federated behind it); VeilVerse slice migrated (7,571 + 44) and remote-verified; 41/42 legacy stores federated; Hardcade found and promoted at true era; 9 verified VACUUM INTO backups at Watchtower/backups/grid_20260816/ (4.05 GB).
- **Automation**: relay-watch cloud routine (hourly :50) triaging legs autonomously; wake-briefs relayed to whoart and phoebus; all mobile legs acked.
- **Vault**: ~50 shards captured incl. the milestone record, doctrines (relay-the-shards command phrase, cache-the-old, coverage-is-credibility, true-bridge), 13 video distillations, Rhea's ingest blueprint, and the Spas/tester entry.

## ⚠️ Known Issues & Workarounds
- **Token economics**: 1.212B tokens since Sat 5PM ET, **98% cache-read** — held context is the cost driver, not generation. Handoff-and-reset early; keep worker missions tight.
- Starting start_grid.py from a shell without User-level `NOUGEN_LOCAL_VAULT_ROOTS` silently disables the vault lane.
- Clients must reconnect after any worker redeploy (stale MCP sessions read as 503s).
- Public /search rejects default urllib UA (403) — send a browser-like User-Agent.

## 📅 Upcoming Events
- Queue: private NouGenTube channel manifest + scheduled run · nightly R2 backup job · era-recovery join against nougen_memories.db · wire whoart · Phoebus upgrade (role + topology are GM decisions) · outpost stash · Notion split-page merge · first-dollar war-game.

