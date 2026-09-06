# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE FIXED: NouGen/.mcp.json set NOUGEN_VAULT_DIR=".vault" (relative), routing every project-scoped capture incl. nightly dream-lane into a stray vault. 154 shards recovered; 5 stale worktrees pruned
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T05:23:59.895Z

---
## Root cause — it was never the cwd trap

`Outpost\NouGen\.mcp.json` **explicitly** set `"NOUGEN_VAULT_DIR": ".vault"` — a *relative* path. The project-scoped `nougen-shards` MCP server therefore wrote every capture into `Outpost\NouGen\.vault` instead of `~\.nougen\shards`. This was not an accidental cwd fallback; it was configuration.

The nightly **`dream-lane` scheduled task** (cron `0 3 * * *`) captures via that MCP server, so every night's findings landed in the stray vault, invisible fleet-wide. Confirmed by timestamps: task `lastRunAt` `2026-08-30T03:02:07`, newest stray shard `2026-08-30T03:01:12`.

The stray vault was **live and growing** — 16 MB, 9 shard DBs, last written yesterday 23:01. Not a leftover.

## Fixed

- **`.mcp.json`** now uses absolute paths for both `NOUGEN_VAULT_DIR` (`C:\Users\super\.nougen\shards`) and `PYTHONPATH`. Backup: `.mcp.json.bak-20260830`. Valid JSON verified.
- **154 orphaned shards recovered**: 149 newly written to the real vault (185,827 → 185,976), and 5 confirmed **already present by content hash** — the `return False` at `core.py:637` is the dedup guard, not a failure. Nothing was lost. Migrated shards carry tag `migrated-from-stray-vault` and preserve their original timestamps.
  Recovered material includes: gateway 502/524 root cause (08-18), several dream-lane runs, the corrected multi-source fleet token ledger, blade + WhoArt disk recoveries, voice-to-NouGen parity fix, the 36% generator-ratio root cause.
- **Stray vault retired** to `.vault.orphaned-20260830` (16 MB preserved, not deleted). With it gone, `core.py`'s fallback now resolves correctly: running from `Outpost\NouGen` with **no** env var resolves to `~\.nougen\shards` — verified live. The trap is closed at the source.
- **Real vault backed up** first to `~\.nougen\shards.bak-20260830` (**4.2 GB** — delete once satisfied; the box has disk pressure).
- **5 stale worktrees pruned**: `busy-euclid-e483a6`, `busy-sanderson-6defde`, `gracious-shirley-fd2f39` (all clean, HEAD `bc73a539` contained in 40 refs) plus two already-prunable registrations. This removed the last `metameric_*.py` files on the box — **zero drift filenames remain in NouGen**.
- CLAUDE.md Rule 0.6 updated: the old note claimed `.vault` exists, which is no longer true.

## Note for whoever audits vaults next

`src/nougen_shards/connectors/local_vault.py:155-158` already carried a comment describing exactly this failure — a relative `.vault` shadowing the canonical substrate. The knowledge existed; the config still had the bug. Worth checking whether other repos' `.mcp.json` files carry the same relative setting.

## Still open

1. **GEMINI.md Rule 0.7 collision** — CLAUDE.md 0.7 = E2B Delegation, GEMINI.md 0.7 = Parallel Agent Orchestration. Cross-references are ambiguous fleet-wide and GEMINI.md still has no FLEET IS PLURAL rule. Needs a decision on which file renumbers.
2. **Valerion purge is still uncommitted** on `agent/nougen-assurance-sprint` — commit it as its own changeset so it does not strand like `71f598a` did.
3. Embedding backfill: a few migrated shards were written without vectors (`nomic-embed-text` misses during the run) and will not surface in semantic recall until `embedding_backfill.py` runs.
