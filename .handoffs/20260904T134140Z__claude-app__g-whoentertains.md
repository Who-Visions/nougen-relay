# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PUSHED + PR #213: arxiv resolver + 2 more _SAFE_IDENT-class fixes + allowed_roots revert, all with tests. Luna can fetch now. Env pin cleared, run_daily.py rewritten for the catch-up-only-fires-on-app-start finding.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T13:41:40.515Z

---
# whoart / Hyperion — pushed, PR open, all four operator items done

Branch `hyperion/evolve-2026-09-04`, commit `3a176be5`, PR
https://github.com/Who-Visions/NouGenShards/pull/213 — **Luna can fetch now**, blade's
earlier attempt found nothing because this did not exist yet.

## 1. Adversarial review before push

Ran a 6-route fleet panel (Rule 0.5.1) against the diff cold. 3 routes returned real analysis
(3 failed/rate-limited). All 3 that answered converged on the same three points:

- **TOCTOU `isdir`→`scandir`** — checked against the actual code, not a bug: `scandir`'s
  `OSError` is already caught and demotes the candidate to rank 1. Verified, not fixed
  (nothing to fix).
- **Case-sensitivity of `startswith` on Windows** — real. NTFS is case-preserving but
  lookup-insensitive; a plain string compare doesn't know that. **Fixed**: prefix match is
  now case-insensitive both directions, +2 tests.
- **`min(ranked)` fragility** — `index` is `len(ranked)` at append time so it's always
  unique today, meaning the tuple never actually ties past `(rank, index)` — but a bare
  `min()` would fall through to comparing `value`/`note` (a list) if that ever stopped
  holding. **Hardened**: `min(ranked, key=lambda r: r[:2])`, +2 tests including a direct
  unit test of the selector with a constructed tie.

## 2. Public-repo leak scan before push

`NouGenShards` is public. My new files carried 47 hostname literals (blade/whoart/phoebus)
and one account path (`C:\Users\super\...` in a comment). The repo's own
`test_published_surface.py::test_no_account_names_or_machine_paths_are_published` caught the
path leak in CI-equivalent local run — exactly what it exists for. Neutralized all of it to
`node-a`/`node-b`/`node-c` (still valid identifiers, so they work as test data too) before
committing. Final diff scanned clean; guard test passes.

Also: this confirms blade's `PublicRepoGuard` finding is a live, present risk — my own
uncommitted work would have added to the exact class of leak it flagged at 32 sites,
if I'd pushed before scanning.

## 3. All four operator items

1. **`_allowed_roots()`** reverted to the committed single-tenant-root form + 13 new tests
   pinning the guarantee (parent not allowed, sibling tenant not readable, secrets store not
   readable, traversal blocked, env override replaces not extends).
2. **`NOUGEN_ARXIV_VAULT_DIR`** cleared at User scope. Verified in a genuinely fresh
   environment after my first check was contaminated by an inherited stale value. A new
   session now resolves `derived:~/Watchtower (MISSING...)` with the loud warning — correct,
   whoart has no arXiv corpus.
3. **Pushed + PR** (this leg).
4. **`run_daily.py` + `SKILL.md` rewritten** around the catch-up-only-fires-on-app-start
   finding: backfills every CLOSED day owed, oldest first, via `--publish`, using
   `git ls-files` not a directory listing. Never today; never regenerates a published day.
   Added an idle-day marker (`readouts/.idle-days-<machine>.json`, local, gitignored) so the
   four genuinely-zero-invocation days in whoart's window don't get rescanned every single
   run forever — a gap the backfill pattern itself doesn't cover for free.

## Not done, still open

- The 32-site public-repo leak sweep (blade's finding) — needs its own claim and war-game,
  explicitly not a same-turn edit, per blade.
- Whether whoart's wake-listener (`tools/antigravity_wake_daemon.py`, found untracked on any
  ref, 2s poll loop, no supervision) should be reconciled with blade's `agy_msg_listen.py`
  lineage — separate thread, separate owners.
EOF
