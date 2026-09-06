# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Valerion naming purge COMPLETED on agent/nougen-assurance-sprint (uncommitted); fleet_reminder hook corrected; GEMINI.md Rule 0.7 collision still open and needs a decision
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T04:49:08.837Z

---
## Situation

The 2026-07-29 purge (commit `71f598a`, "Valerion is the canonical architecture name") **never merged into the working line**. It is reachable only from `origin/claude-cli/cli-colour-theme` and `origin/feat/private-vault-encryption`, not from `agent/nougen-assurance-sprint`. Its GM review gate stayed open for a month, so drift regrew from 16 occurrences to 26.

Completed it in place today. **Changes are UNCOMMITTED in the working tree** — 13 tracked changes, cleanly isolated (the 35 other items on the branch are all untracked and were not touched).

### Applied — 19 edits across 12 files + 1 deletion
Mapping follows `71f598a`: "The Metameric Memory Engine" → "The Memory Engine"; "Autonomous Metameric Evolution" → "Autonomous Memory Evolution"; Module 1 "Metamers" → "Convergent Traces". `TMEM` untouched (7 occurrences, genuine acronym).

- `tools/metameric_deep_sweep.py` **deleted** — it was a byte-identical 7,776-byte duplicate of `tools/valerion_deep_sweep.py`. The 2026-07-29 "rename" had actually been a copy; the original was never removed. Nothing referenced it except a historical handoff.
- Files renamed *to* Valerion still carried drift **internally** — `valerion_longform.py` (7 hits) and `valerion_deep_sweep.py` (3). The old purge fixed filenames, not contents. Now fixed.
- TS banner `cli.ts:178` and assertion `cli.test.ts:68` kept in sync, verified programmatically.
- Verified: `py_compile` clean on all 6 changed Python files; `pytest tests/test_cli.py tests/test_skills.py` → 32 passed; diff is 19 insertions / 19 deletions (surgical, no line-ending churn).

### Deliberately PRESERVED — do not "fix" these
1. `docs/handoffs/2026-06-27_cloud-repo-session.md:63` — a dated handoff referring to `metameric_deep_sweep` by its name at that time. Rewriting a historical record falsifies it (same principle as the append-only dossier rule).
2. `tools/valerion_longform.py:30-31,37` — a comment explaining the drift plus the `METAMERIC_LONGFORM_OUT` back-compat env fallback. Removing it breaks existing shells.

### Also fixed
`Outpost\.claude\hooks\fleet_reminder.py` (backup: `.bak-20260830`) was telling **every agent on every fleet-related prompt** to route to `iris-ai:e4b`, `sol-ai:e4b`, `Yukiai`, `solai` — all 404 since 2026-08-08 — and blamed empty output on the API path rather than the real cause. Replaced with the correct gotchas: max_tokens=2048 floor, dead tags, 429-is-per-model, vendor-vs-key diversity, billed vertex lane, NOUGEN_VAULT_DIR. Hook is conditional (0 bytes on non-fleet prompts, 2941 when triggered), so the added length is free.

## Ask

1. **Decide the GEMINI.md Rule 0.7 collision.** CLAUDE.md 0.7 = "E2B Delegation Default"; GEMINI.md 0.7 = "Parallel Agent Orchestration". Every `(Rule 0.7)` cross-reference is ambiguous fleet-wide, and GEMINI.md has **no FLEET IS PLURAL rule at all**. Not renumbered here — that is destructive to references I cannot see from this lane.
2. **Veto window on "Convergent Traces"** for Module 1. Worth noting: "metamer" is arguably a genuine technical term for what Module 1 does (distinct inputs that resolve to the same underlying phenomenon) — the same reasoning that kept TMEM. This is the one rename most defensible to reverse. One `sed` either way.
3. Commit the purge as its own changeset — do not fold in the 35 untracked WIP items.

## Done when

The purge is committed on the working line (not stranded on an unmerged branch again), Rule 0.7 means one thing fleet-wide, and Module 1's concept name is settled.
