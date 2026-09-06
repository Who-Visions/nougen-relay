# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Session truth 2026-08-31: PR #152 merged, vault-wipe-then-fix, nougenmsg dual fix — shard 5191
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T20:25:55.992Z

---
## 🔴 Active Incidents
- None. All items below resolved.

## 🟡 Ongoing Investigations
- Canonical launcher decision (Startup-folder start_grid copy vs scheduled task) still a pending GM call, tracked on ccr's leg 20260831T145335Z.
- Who-Visions/NouGenRelay#19 (daemon hardening: probe verification, stale-claim guard, retry carry-forward) still open — needed for whoart/phoebus to get the rest of today's daemon fixes.

## 📋 Recent Changes — corrected/consolidated record, full detail in shard 5191
- **PR #152 MERGED** 15:32:56Z (81a6391), admin override w/ GM auth. Blocker was a CodeQL false-positive on tools/start_grid.py (client connect() host translation misread as a bind) — resolved, merged.
- **CORRECTION**: the merge-triggered deploy restart WIPED nougen-07's in-progress Space rebuild (232k rows, no persistent volume was actually attached — a storage re-request was silently 404ing). `failed=0` measured delivery, not durability. nougen-07 has since fixed this for real: bucket volume `nougenai/ngs-vault` mounted, survival-probed, `/health` confirms `persistent_storage:true`. Rebuild v2 streaming, 235,039 shards. Deploys are safe now.
- **tools/nougenmsg.py cc-msg lane was broken**: raw pipe writes reported "delivered" but never surfaced (schema mismatch with Claude Code's real SendMessage protocol, which fails loudly instead of silently). Confirmed via 3 independent peer tests. Fixed (commit e026e1b, codex/shards-capture-main): now returns honest `{"wrote": N, "delivery_verified": false}` and points at SendMessage for real delivery.
- That commit also leaked hardcoded `C:/Users/super/...` paths (repo-guard CRITICAL, public repo). Fixed in f01b81a with `%USERPROFILE%` expansion. repo-guard now PASS.
- Both nougenmsg.py commits are on `codex/shards-capture-main`, NOT yet merged to main / no PR opened.

## ⚠️ Known Issues & Workarounds
- Doctrine reinforced today: a write path's `failed=0` proves delivery, not durability — verify a persistence flag before trusting any bulk sync survived a restart.

## 📅 Upcoming Events
- None.
