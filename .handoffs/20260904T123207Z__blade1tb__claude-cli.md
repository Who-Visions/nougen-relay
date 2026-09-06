# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: Apollo evolve on blade: _SAFE_IDENT fullmatch + 17 regression tests, and the arXiv lane un-darkened (stale env pin removed, probe reads a cached marker; 0.44h old, probe 1.1s faster)
**Branch**: `pi-remix` @ `d08f2655`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T12:32:07.729364+00:00

---
# Blade / claude-cli - Apollo evolve pass

Two Blade-side defects that both traced to the same root: a value that was true once and stale since.

## 1. `_SAFE_IDENT` newline hole - CLOSED (phoebus 115317Z)

`src/nougen_shards/nougenmsg.py:424` now uses `fullmatch()`. Only one copy of `_SAFE_IDENT` exists on blade; the other paths phoebus named are phoebus-side.

phoebus was right not to patch behind the rollout, and right that it is not RCE. Added the coverage that did not exist: `tests/test_nougenmsg_ident_validation.py`, 17 cases. Proof it bites - reverted to `.match()`, exactly the two newline cases failed; restored, 17/17 pass.

## 2. arXiv lane reported dead for weeks while it was healthy

`NOUGEN_ARXIV_VAULT_DIR` (User scope) pinned `C:\Users\super\Watchtower\vault` - 300 files, one arxiv-named. The writers land in `C:\Users\super\.nougen\shards`: **88,192 arXiv shards, newest 0.4h old**. The env pin sat at the TOP of `arxiv_lane_config.resolve_vault_root()`, so it beat the already-correct `config.json`.

Fix: removed the pin rather than repointing it. The chain now resolves to the writers' dir on its own, and `arxiv_gap_backfill.py` no longer needs the dir passed explicitly (closes the standing known-issue).

`sol_hi_probe.ps1` was dark for a second reason - it scanned the constitution vault_dir, not the writers' dir. Globbing the writers' dir inline is not viable (3-30s measured against 88k files; fast-greeting budget is ~7s), so `tools/arxiv_lane_marker.py` caches it out of band and the probe reads a 200-byte JSON, refreshing detached when the marker ages past `SOL_ARXIV_MARKER_MAX_AGE_H` (6h default). Missing marker heals itself.

**Probe now: `arXiv Lane: 0.44 hours old`, and 6602ms vs 7698ms before.** Every new value resolves env -> config -> logged fallback.

## Not mine, left alone
`tests/test_harness_gills_scale.py` fails collection. Untouched - another lane's in-flight work.
