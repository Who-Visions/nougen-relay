# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: blade1tb: arXiv fix 904a773f is NOT on main — pull after PR #89 merges, then set NOUGEN_ARXIV_VAULT_DIR and rerun the scan
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T06:11:08.348Z

---
## Situation
The standing TODO (`20260817T015226Z`) told blade1tb to pull `904a773f` and rerun `arxiv-daily-scan`. **That pull would have failed silently.** Verified from whoart:

- `904a773f` (arxiv lane: dedicated vault override + fix dead derived fallback) is contained **only** in `origin/agent/nougen-assurance-sprint`.
- `origin/main` is still at `f1407472`. `db251c13` (shard highway + e2b routes) is in the same position.
- `bf133eb` (vault discovery — the trap the phoebus note cleared) **is** on main.

GM decided 2026-08-17: bring it through `main` rather than have machines track an agent branch. Branch pushed; it rides **PR #89** (`Who-Visions/NouGenShards`), which now carries 13 commits including:
- `904a773f` arXiv vault override
- `db251c13` shard highway + local e2b routes
- `18ea86b6` `/search` era bounds (fixes the ask_griot leak — see below)
- `afc18c80` phoebus gateway checklist

## Ask — blade1tb lane, in this order
1. Wait for PR #89 to merge to `main`. Do **not** pull the agent branch.
2. `git pull --ff-only` on `main`; confirm `904a773f` present.
3. Set `NOUGEN_ARXIV_VAULT_DIR` (resolution order is env → config `arxiv_vault_dir` → derived; the override exists because the derived fallback was dead).
4. Rerun `arxiv-daily-scan` and report the vault path it actually resolved, not just success.

## Done when
The scan writes into the dedicated arXiv vault dir on blade1tb and the resolved path is reported back on this leg.

## Landed alongside (whoart, this session)
- **ask_griot era-bounds leak — root-caused and fixed at the node.** `SearchRequest` had no `since`/`until` at all, so bounds never reached any arm. Reproduced live: `2025-01..2025-03` returned 2026-08 shards + undated vault rows with `held_back: 0`. `18ea86b6` filters the federated arm, holds back undated rows, counts them in `X-NouGen-Held-Back`, and unions the timestamp-filtered SQL sweep. 5 new tests; suite 565 passed / 4 skipped.
- **Tracker dailies re-scoped.** blade1tb was never stale — it had published 08-03..08-15; the local clone was 3 commits behind and is now fast-forwarded. whoart exported 08-16 + 08-17 locally (unpushed). **phoebus is the only stale lane**, still at 2026-08-02.
- **Phoebus = gateway** (GM). Checklist: `docs/phoebus-gateway-upgrade.md`.

## Open, owned by whoever deployed the connector
`ask_griot` does not exist in `nougen-fleet-mcp` source — `main` and `origin` both sit at `2accf5a` with no `griot` string anywhere. The live worker serves it regardless, so it was deployed from an uncommitted tree. The node-side leak is fixed, but the connector's own `held_back` accounting cannot be reviewed until that source is recovered and pushed.
