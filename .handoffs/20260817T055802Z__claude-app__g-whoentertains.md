# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: whoart: shard highway + local e2b routes landed (db251c13); gateway shards.nougenai.com up 200
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T05:58:02.973Z

---
## Situation
- Lane: `claude-app` / key `g-whoentertains`, repo `C:\Users\super\Outpost\NouGen`, branch `agent/nougen-assurance-sprint` (clean).
- Shard gateway `https://shards.nougenai.com` health-checked from this connector: **up, 200, configured**.
- Head commit **db251c13** `feat: establish shard highway and local e2b routes` (machine whoart, agent claude-cli) — 29 files, +1163/-51.

## What landed in db251c13
- **Highway/transport**: `tools/highway_lane.ps1`, `tools/tunnel_lane.ps1`, `tools/shard_primary_proxy.ps1`, `tools/standby_sync.ps1`, reworked `tools/node_lane.ps1`.
- **Relay push**: `tools/relay_push.py` (+ `tests/test_relay_push.py`).
- **Vault union**: `tools/union_vaults.py` (+ `tests/test_union_vaults.py`), `tools/build_whoart_vault.py` updates.
- **e2b lane (Rule 0.7)**: `skills/e2b/SKILL.md`, `skills/e2b/agents/openai.yaml`, `models_client.py` route changes, `docs/continuous-sync-design-DRAFT.md`.
- **Core/API**: `core.py`, `dynamic_api.py`, `dream.py`, `agents.py`, `app.py`, plus `tests/test_node_api.py`, `tests/test_audit_fixes.py`.

## Still open on the relay (not touched here)
1. `20260817T055605Z` — node perf fix f140747 (/search 52.7s → 6.8s) awaiting ack.
2. `20260817T024250Z` / `20260817T025407Z` — **ask_griot era-bounds leak**: `until`/`since` not enforced on all search arms.
3. `20260817T015226Z` — blade1tb: pull arXiv vault fix `904a773f`, set `NOUGEN_ARXIV_VAULT_DIR`, rerun arxiv-daily-scan.
4. `20260817T015224Z` / `20260817T010119Z` — blade1tb + phoebus: tracker dailies stale since 2026-08-01/02.
5. `20260817T011421Z` / `20260817T015225Z` — phoebus upgrade checklist (role decision, tool surface, weekend parity pull, key fingerprints).

## Ask
Any lane with blade/phoebus access: pick up (2) the era-bounds leak and (4) the stale tracker dailies — both are blocking accurate recall/spend reporting.

## Done when
Highway tooling verified from a second machine (not whoart), and the ask_griot bounds leak has a regression test.
