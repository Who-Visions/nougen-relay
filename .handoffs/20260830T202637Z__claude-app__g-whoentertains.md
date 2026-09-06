# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Tracker + Relay pushed; NouGenRelay pi-remix merge REFUSED on measurement (139 legs diverge both ways)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T20:26:37.446Z

---
## NouGenTracker (PUBLIC repo)
`dashboard.html` regenerated through 2026-08-29, committed and pushed to `main` (`5d20b2f`). Headline now leads with tokens plus cold-boot list price, absorbed-vs-paid split, and a stale-peer warning: phoebus stopped publishing 588h ago. Note for the GM: this repo is public and the dashboard carries per-machine spend (blade1tb $6,367 / whoart $2,197 / phoebus $542) and a daily cost chart. The previous committed version already did, so this is an established public artifact, not a new exposure.

## NouGenRelay (PRIVATE)
`pi-remix` pushed: `026cc63..481614d`, 6 legs including the 1000-file listing cap root cause.

**PR #15 (whole-branch merge to main) closed unmerged, deliberately.** Measured before merging instead of trusting the 525-file diff:
- Files on `pi-remix` and NOT on `main`: **1** (`20260823T041100Z__blade1tb__apollo-antigravity.md`, a sidecar whose `.json` was already there).
- Files on `main` and not on pi-remix: 176.
- The other 139 differences are the SAME legs with divergent state, diverging in BOTH directions: 6 `done`->`open`, 2 `completed`->`open`, 1 `acked`->`open`, 3 `open`->`acked`, 3 `released`->`active`, plus `retry_count`/`failures`/`relay` bookkeeping on ~45. 42 more were pure `\uXXXX` vs raw UTF-8 encoding noise.

Merging either direction silently rewrites other lanes' leg state, including reopening finished legs. No machine gets to make that call, so I did not. If someone wants those states reconciled, it needs a per-leg decision by the owning lanes.

**PR #16 merged instead** (`35bc1e5`): the one genuinely missing sidecar, verified present on `main`.

## Note
Encoding split is worth a look on its own: one writer emits `\uXXXX`-escaped JSON, the current one emits raw UTF-8. Same legs, different bytes, guaranteed future conflicts.
