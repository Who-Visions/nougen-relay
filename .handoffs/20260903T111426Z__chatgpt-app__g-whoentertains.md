# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: BLADE ↔ PHOEBUS CORE PARITY: maintain 1:1 NouGen state and evolve forward cleanly
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T11:14:26.115Z

---
Dave directive: Blade and Phoebus must become reciprocal core witnesses for NouGen. Do not merely exchange summaries. Establish continuous 1:1 parity on everything that materially defines NouGen core, then update, evolve, and merge forward without silent divergence.

WORK AS A TWO NODE RECONCILIATION LOOP:
1. Each side inventories its current NouGen core: repos/branches/SHAs, relay/wake fabric, NouGenMsg, shard gateway, auth + owner provenance, Keymaker interfaces/fingerprints only, tracker, claims, agent/tool maps, provider adapters, config/schema versions, tests, launchers/services, hooks, rules/laws, and known WIP.
2. Exchange manifests Blade → Phoebus and Phoebus → Blade. For every component classify EXACT MATCH / INTENTIONAL MACHINE DIFFERENCE / STALE / MISSING / CONFLICTING / UNKNOWN.
3. Hash or otherwise deterministically compare code/config artifacts where practical. Do not call two things equivalent because their prose sounds similar.
4. For each mismatch, message the other node immediately with evidence and proposed resolution. The receiver verifies independently before accepting it. Keep the back-and-forth alive during work, not only at completion.
5. Determine canonical direction per change from evidence, recency, tests, and architecture. Never blindly overwrite the newer/better implementation merely to force equality.
6. Merge cleanly forward. Preserve intentional host-specific differences behind explicit config/adapters rather than forks of core behavior.
7. Run shared acceptance tests after reconciliation: relay delivery, signed Dave-origin provenance, forged-peer rejection, wake/cold-idle behavior, shard read/write, claims, tracker publication, provider/tool routing, and any other core invariants discovered during inventory.
8. Any newly discovered invariant, failure, architectural improvement, or machine-specific exception must be relayed to the other node and captured/sharded where durable.
9. Produce a parity ledger showing component, Blade state, Phoebus state, canonical state, evidence, action taken, test result, and remaining divergence.
10. Establish a forward rule: material NouGen core changes are not considered fleet-complete until the sibling node can observe/reconcile them and the parity ledger is updated.

IMPORTANT: 1:1 means semantic/core parity, not blindly identical machines. Secrets stay secret, only fingerprints/metadata compare. Host-specific paths, hardware, credentials, and provider availability may differ intentionally but must be explicit and testable.

Done when Blade and Phoebus independently agree, with evidence, on the current canonical NouGen core; required changes are merged forward cleanly; shared acceptance gates pass; intentional differences are documented; and a repeatable reconciliation mechanism exists so they cannot silently drift apart again.
