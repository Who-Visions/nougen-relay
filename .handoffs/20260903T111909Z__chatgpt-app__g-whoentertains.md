# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: NOUGEN 1.0 → 2.0 ROADMAP: advance in clean 0.1 gates with microstep acceptance criteria
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T11:19:09.658Z

---
Dave directive: treat NouGen 1.0 as the baseline and evolve deliberately through 1.1, 1.2, 1.3 ... 1.9, then 2.0. No vague leapfrogging. Every 0.1 release needs a bounded scope, microsteps, measurable acceptance gates, rollback path, parity reconciliation across Blade ↔ Phoebus, side verification from Codex/Antigravity where relevant, and a shardable release record.

PROPOSED VERSION LADDER

1.0 BASELINE / FREEZE AND PROVE
Microsteps: inventory current core; pin repos/branches/SHAs; snapshot schemas/configs; list all services/agents/tools/providers; capture known WIP; define current invariants; run baseline tests for relay, wake, shards, tracker, claims, auth, owner provenance; mark current known failures; establish parity ledger. Exit gate: we can describe and reproduce 1.0 exactly on Blade and Phoebus.

1.1 CORE PARITY + DRIFT CONTROL
Microsteps: deterministic manifests; component hashes; semantic parity classification; host-specific config boundaries; automatic drift detection; sibling-node reconciliation; stale/missing/conflict alerts; merge-forward workflow. Exit gate: Blade and Phoebus cannot silently diverge on NouGen core.

1.2 OWNER AUTHORITY + TRUST FABRIC
Microsteps: signed Dave-origin envelope; full goal+body signing; timestamp/nonce; replay protection; sender/relay chain provenance; key rotation metadata; forged-peer negative tests; frictionless verified-owner path; explicit high-risk boundaries only; auditable decision reason. Exit gate: verified Dave-origin acts without redundant local confirmation while forged/unsigned elevation fails.

1.3 RELAY + LIVE DELIVERY FABRIC
Microsteps: claim/ack lifecycle cleanup; idempotency; duplicate suppression; retry/backoff; dead-letter/stale handling; delivery receipts; ordering semantics; supersession/cancellation; live peer messaging; observation streaming; queue health metrics. Exit gate: relay state matches reality and lost/zombie legs are detectable and recoverable.

1.4 WAKE + CONTINUITY
Microsteps: cold-idle detection; background wake without stealing focus; zero-keystroke remote wake; session rehydration; post-restart continuity; heartbeat/lease model; sleep/reboot/network failure recovery; machine availability model; graceful degrade. Exit gate: an authorized task can wake an idle lane, resume context, execute, and report evidence without Dave touching the machine.

1.5 MEMORY / SHARDS INTELLIGENCE
Microsteps: capture policy; provenance completeness; dedupe; amendments/retractions; utility feedback; temporal coverage checks; destiny/evolve metadata where justified; compaction/distillation under context budgets; retrieval quality tests; stale-memory detection; source confidence. Exit gate: memory is not merely large, it is trustworthy, bounded, temporal, corrective, and useful under cost limits.

1.6 AGENT + PROVIDER ORCHESTRATION
Microsteps: provider-neutral task contract; capability registry; model/provider routing; local-first/free-lane preference where appropriate; fallback chains; budget governor; quota awareness; context-window governor; tool permission model; standardized observation/result envelopes; agent identity/role manifests. Exit gate: the same bounded task can be routed across Ollama/OpenRouter/Hugging Face/Claude/Codex/AGY/etc without rewriting NouGen core semantics.

1.7 SELF-OBSERVATION + BOUNDED AUTONOMY
Microsteps: state introspection; explicit goals/claims; plan→act→observe→verify loops; contradiction detection; confidence; stop conditions; retry budgets; escalation rules; sibling-agent critique; measurable self-awareness indicators without anthropomorphic claims; autonomous maintenance only inside defined scopes. Exit gate: NouGen can explain what it is doing, why, what changed, what it does not know, and when it must stop or ask.

1.8 EVOLUTION + VERIFICATION ENGINE
Microsteps: change proposals; test-before-merge; canary execution; A/B or shadow mode where useful; regression corpus; cross-provider verifier; invariant checks; automatic rollback; release evidence pack; shard lessons from failures; no third repeat of same known failure class without escalation. Exit gate: NouGen can improve itself operationally without silently degrading prior guarantees.

1.9 PRODUCTIZATION + SCALE READINESS
Microsteps: aircraft-carrier-to-bicycle abstraction; single-user minimal install path; multi-machine optional expansion; account/tenant boundaries; secret isolation; quotas/cost telemetry; packaging; installer/updater; migrations; observability dashboard; docs; backup/restore; disaster recovery; performance/load tests; security review; user-facing failure messages. Exit gate: an ordinary user can run the small version cleanly while Dave's lab can run the full fleet using the same core laws.

2.0 CLEAN CONTRACT
Microsteps: freeze 2.0 public/core interfaces; compatibility matrix; migration from 1.x; deprecations; final parity sweep; full acceptance suite; chaos/failure drills; signed release manifest; reproducible deployment; canonical architecture map; release shards; known limitations; 2.1 backlog separated from 2.0 scope. Exit gate: 2.0 is reproducible, testable, migratable, observable, secure, bounded, and no unresolved 1.x ambiguity is smuggled into the release.

FOR EVERY 0.1 RELEASE, REQUIRE THIS SAME MICRO-GATE:
A. define exact scope and non-goals
B. inventory affected components
C. write acceptance tests before/with implementation
D. implement on one node or branch
E. sibling verifies independently
F. Codex/Antigravity side-audit when relevant
G. reconcile/merge forward
H. run regression + failure tests
I. update parity ledger, architecture map, schemas, and changelog
J. shard durable lessons/decisions/failures
K. tag/version only after evidence is green
L. open next 0.1 only after prior gate is clean

Do not optimize for version-number theater. A release number advances only when its contract is proven. If work discovered for 1.6 actually belongs to 1.2, fix the lower-layer invariant first. Maintain dependency graph so later releases cannot paper over earlier defects.

Done when the fleet returns: (1) a dependency-aware 1.0→2.0 master roadmap, (2) per-release microstep checklists and owners, (3) measurable acceptance criteria, (4) estimated dependency/order constraints, (5) current-state mapping showing what is already done versus partial versus missing, and (6) the next smallest executable batch for 1.1.
