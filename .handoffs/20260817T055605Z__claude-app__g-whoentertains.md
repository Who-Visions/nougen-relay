# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Node perf fixed: /search 52.7s -> 6.8s, /health <0.1s (commit f140747, tiered federation + timeouts + FTS)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T05:56:05.918Z

---
## Situation
Live node (4444) measured /health 7.07s and POST /search limit-3 at 52.7s. Diagnosis with per-store timings: three registered vaults had no *_ngsfts index, so every federated query ran a LIKE full scan — veilverse_canon_vault alone (1.07 GB) cost 46.2s, and the concurrent sweep's wall-clock is its slowest store. Grid lanes ~6s. The 7s /health was disk contention from concurrent sweeps.

## Done
- FTS5 indexes built on veilverse_canon_vault, whoart_grid_vault, sol_ai_vault (tools/build_vault_fts.py, ~220 MB, droppable).
- Two-tier sweep (war-game legacy-federation Move 5 fork fired): hot = pinned/small/FTS-indexed inline; cold (large+unindexed) behind NOUGEN_FEDERATE_TIER2. Cold set is currently empty.
- Per-store budget NOUGEN_LOCAL_VAULT_TIMEOUT_S=2s via sqlite progress handler; timed-out stores surface as a FEDERATION_STATUS trailer in the /search response — never silent.
- /health + coverage aggregates cached NOUGEN_HEALTH_CACHE_S=30.
- Suite green (584 passed / 4 skipped, test_mcp_endpoint.py excluded per ledger). Commit f140747 rebased over PR #90 (its local_vault.py stub superseded) and pushed to origin/main; privacy guard PASS.
- Node restarted via start_grid; re-measured: /health 0.01-0.08s, /search 6.75s, same top-3 provenance. Public health 200.

## Ask
None blocking. Watch item: any NEW large unindexed vault registration lands in the cold tier (invisible to default recall) until tools/build_vault_fts.py is run on it — run the builder after registering big stores.

## Done-when
Already done; this leg is the brief.
