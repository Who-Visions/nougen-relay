# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Add autonomous completion reconciliation so fleet closes finished legs and advances only unfinished work
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T03:21:28.238Z

---
## Finding
Desktop fleet execution is now parallel, but relay state lags reality. Claude observed that some Rhea upgrade legs appear already fulfilled by Gemini, yet remain open because the executor did not ack/close them. This creates stale work, duplicate effort, and ambiguity about what should run next.

## Required fix
Implement an autonomous completion-reconciliation layer in NouGenRelay / relay-watch.

### Core loop
1. Inspect open legs plus active claims.
2. Gather completion evidence from executor output, shards, relay events, commits, tests, deploy status, and explicit agent completion notifications.
3. Match evidence to open legs by goal fingerprint, dependency graph, referenced source leg ids, touched files/services, and acceptance criteria.
4. If completion is verifiable, atomically mark the leg fulfilled/acked with structured evidence and executor identity.
5. Collapse equivalent duplicate legs into the canonical completed leg rather than leaving stale copies open.
6. Release dependent legs whose prerequisites are now satisfied.
7. Select the highest-priority unfinished compatible leg and dispatch/claim it automatically.
8. Never re-execute work merely because registry state is stale.

## State model
Use explicit states instead of open/acked only where possible: OPEN, CLAIMED, RUNNING, VERIFYING, COMPLETED, BLOCKED, FAILED_RETRYABLE, DEAD_LETTER, SUPERSEDED. If storage compatibility requires existing status fields, encode the richer state in relay events first and migrate safely.

## Completion evidence
A leg is closable only with evidence, for example:
* test suite or targeted tests green
* deployed artifact or service health verified
* commit/file diff matches requested change
* shard captures durable completion detail
* agent completion notification references the leg or a deterministic goal fingerprint
* external verification from a second lane when risk is high

Store: completed_by, completed_at, evidence_refs, verification_method, canonical_goal_hash, supersedes/superseded_by, dependent_leg_ids, retry_count.

## Deduplication
Canonicalize goals and compute a stable semantic/structural fingerprint. Detect duplicate TODOs created by ChatGPT, CCR relay-watch, Claude, Gemini, or future lanes. If A and B ask for the same fix, one execution should satisfy both when acceptance criteria overlap. Preserve provenance: do not delete duplicates, mark them SUPERSEDED or SATISFIED_BY=<canonical leg>.

## Dependency release
Allow legs to declare or infer prerequisites. When a prerequisite completes, downstream work should become eligible automatically. The scheduler must prefer genuinely unfinished work over already-satisfied siblings.

## Lease safety
Claims need TTL/heartbeat. If a worker dies, lease expires and the leg returns to eligible state. Completion write must be idempotent and compare-and-set to prevent double closure.

## Evidence grading
LOW: agent says done with no artifact.
MEDIUM: artifact/diff exists.
HIGH: artifact + tests/health checks.
CRITICAL path: require HIGH or independent verification before closure.

## Scheduler rule
Before any worker starts work, run reconcile(). The invariant is: `reconcile reality -> close/supersede satisfied work -> release dependencies -> claim only unfinished work`.

## Acceptance tests
1. Gemini completes Rhea relay_create fix but forgets to ack. Claude/relay-watch detects completion evidence and closes/satisfies the stale Rhea legs automatically.
2. ChatGPT and CCR create duplicate timeout-hardening legs. One successful implementation satisfies both without rerunning the fix.
3. Worker crashes after claiming. Lease expires and another eligible worker resumes.
4. Two workers race to close one leg. Only one canonical completion commits; second sees idempotent success.
5. Completed prerequisite automatically releases next temporal-provenance migration phase.
6. Registry retains full audit trail showing who did work, who verified it, and why a duplicate was superseded.

## Architectural constraint
Do not build a second relay system or new ingress. Extend the existing NouGenRelay / relay-watch control plane. Preserve current relay registry compatibility and one-grid provenance.

## Done when
The fleet can receive several overlapping relay legs, execute them across Gemini/Claude/ChatGPT/desktop agents, autonomously reconcile what was actually completed, close or supersede stale legs, release dependencies, and continue into the next unfinished task without Dave manually telling each lane `do what hasn't been done yet`.
