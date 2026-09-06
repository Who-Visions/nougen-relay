# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: IMPLEMENTED + TESTED: source-grounded IRS evidence ledger MVP; live ingestion/export still gated
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T02:38:50.152Z

---
## Active Incidents
- None caused by this change.
- Pre-existing dirty `src/nougen_shards/core.py` breaks adjacent graph/original-timestamp tests: temporary schemas lack `temporal_meta`, then the retry path raises `NameError: time`. Left untouched.

## Ongoing Investigations
- Production `(ledger_path)` remains deliberately unresolved.
- Encryption/access policy is required before ingesting real financial records.
- Tax ruleset/export layer remains separate and unimplemented.

## Recent Changes
- Added `src/nougen_shards/evidence_ledger.py`: explicit-path isolated SQLite store; SHA-256 original fingerprints; sources, events, claims, transactions, source edges, corrections, conflicts, review flags; event/transaction backward traversal.
- Added `tests/test_evidence_ledger.py`: 10 adversarial tests.
- Invariants: primary source required for SOURCE_VERIFIED; two independent root sources for CORROBORATED; derivative summaries cannot inflate corroboration; UNKNOWN stays null/UNKNOWN; own-account transfers get no automatic tax treatment; event promotion appends correction history.
- Focused verification: `pytest tests/test_evidence_ledger.py -q` = 10 passed; `py_compile` and `git diff --check` pass.
- No live vault, schema migration, or original financial records touched.

## Known Issues & Workarounds
- Kaedra review failed with gateway 530.
- Dav1d connector failed because live roster exposes DavOs, not Dav1d. No external review was performed; rely on local tests until fleet routing is repaired.
- Wargame is at `wargames/irs-evidence-ledger.md` (directory is gitignored by existing policy).

## Upcoming Events
- Select encrypted production storage/access policy.
- Add source scanners/import adapters and annual human-reviewable exports.
- Add query/API surface for uncertain items, conflicts, missing documents, payer/vendor/project summaries.
- Integrate with shard recall only after the isolated model is reviewed; do not point it at the live vault implicitly.
