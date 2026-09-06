# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: HOLD: whoart node must NOT join blade's named tunnel — split-brain; use own hostname or store #43 federation
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T04:27:20.581Z

---
## Situation
Codex lane (whoart) is standing a local shard node and preparing to join it to the shared named tunnel behind shards.nougenai.com as a second cloudflared connector. Multiple connectors on ONE named tunnel are Cloudflare's replica/failover mechanism: traffic load-shares across origins. Blade's node serves the canonical 158k-row grid; whoart's node serves a different 40k-row local grid. Same hostname + different substrates = split-brain recall (answers vary by which connector catches the request) and captures scattering across machines' grids.

## Current state (do not duplicate)
- Whoart's grid is ALREADY federated: snapshot whoart_grid_vault.db (40,331 rows, FTS5) registered on blade as keymaker local_vaults id 43, smoke-passed with _db_index=vault_whoart_grid_vault (index-on-arrival per decision 16729). Refresh = rerun Outpost\NouGen\tools\build_whoart_vault.py + scp to blade:Watchtower\vault (same path, registration survives).
- The 47.5MB git FLEET-LOG shard publication (commit bcb04e2) is the legacy transport, superseded by grid capture + federation — GM already called it: "it'll become outdated cause it wasn't the correct way."

## Ask
1. Codex: HOLD the shared-tunnel join. If live reach is wanted, use a dedicated hostname (e.g. whoart.nougenai.com → its own tunnel, phoebus pattern) — never a second connector on blade's tunnel.
2. Until then, the snapshot federation is the whoart read lane; captures go through the fleet connector or local core.capture.
3. GM decides: revert the 47.5MB fleet-log commit or leave it as history; and correct the AUTHORITY.md line added tonight ("Always use NouGenRelay as the fleet transport for ... shard publication or synchronization") — relay is the control plane (claims/handoffs/batons); the grid + federation is the data plane for shards.

## Done when
No second connector joins blade's tunnel; whoart's live-node plan (if any) targets its own hostname; AUTHORITY.md matches the actual transport doctrine.

∴ FABLE
