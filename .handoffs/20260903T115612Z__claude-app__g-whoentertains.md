# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PARITY LEDGER v5: #188 merged (main@6015d43) — canonical manifest generator on main with SALTED fingerprints; two CodeQL alerts dismissed on the record; 1.1 batch steps 1+2 complete on phoebus
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T11:56:12.465Z

---
Ledger v5 for directive `111426Z`, superseding v4 (`115143Z`).

## Merged
PR #188 → `main@6015d43` (11:55Z), squash, branch deleted. `tools/parity_manifest.py` is now canonical: one script every node runs, contract rows (`contract:origin_signing_bytes` = sha256[:16] of the shared worked example = `cb955f7584fe7ca3`, `contract:origin_limits`, `contract:gate_policy`), secret rows as `HMAC-SHA256(NOUGEN_MANIFEST_SALT, value)[:12]` — SALT-REQUIRED without a salt, never a bare hash. Verified before merge: no-salt refuses; two salts give two different 12-hex values (unlinkable).

## On the record: two CodeQL alerts dismissed
`py/clear-text-logging-sensitive-data` ×2 (high) on the manifest's row printing. Dismissed as false positive with the reason written into the alert: the printed value is a keyed one-way fingerprint computed in a child process; the secret value is never read into the parent nor emitted; the taint is the name heuristic (`get_secret`/`secrets`) surviving the HMAC. Rationale lives in `secret_fingerprint`'s docstring. The security workflow was re-run after dismissal and the PR was ALL GREEN at merge — not "mergeable with a red umbrella". CodeQL remains non-required on `main`; noted again so nobody equates the two.

## 1.1 batch status (from `112420Z` item 6)
1. Merge #187 + repoint both nodes at merged `tools/` — phoebus DONE (argv + hash acceptance, ledger v2); blade blocked by design on the wake-adapter PR (option 2, ledger v3).
2. Land the manifest generator — DONE (#188).
3. Drift alert on each poll — blade's `drift_check.py` built and running on both nodes (map-override fixed); landing as `tools/drift_check.py` with the wake PR. Phoebus to wire it into relay-watch's poll after, plus a RELAY-STALE self-announcement when pull != ok.
4. Baseline the missing suites (shards/claims/tracker/wake) — other lanes' subsystems; untouched.

## Deployment state, phoebus
Deployment clone at `main@6015d43`; this merge touched no daemon file (hashes of the three bus files unchanged vs the running processes — no reload performed, none needed). Worktrees retired.

## Still open
Owner token asymmetry (owner's step). Blade convergence (wake PR). Bare fingerprints of two high-entropy tokens remain in earlier ledgers — noted, not rotated.
