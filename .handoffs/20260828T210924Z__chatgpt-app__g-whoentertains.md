# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: DIRECTOR PLAN: convert fleet backlog into owned execution and closed evidence loops
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T21:09:24.143Z

---
Dave approved relay of the execution plan. Current diagnosis: fleet has accumulated open work faster than it is claiming and closing it. Priority is ownership + validation, not more planning/spec multiplication.

EXECUTION ORDER

P0 — OWNERSHIP / RECONCILE
1. Every capable lane checks relay_open + relay_claim_list before starting.
2. Claim one non-overlapping executable leg. Do not create a new planning leg when an equivalent TODO/spec already exists.
3. Completion requires tests/runtime evidence/commit where applicable, then a concise handoff.
4. Highest leverage deliverable: daemon-driven autonomous claim/relay/shard/reconcile loop so Dave no longer has to manually trigger fleet coordination.

P0 — SPLIT-BRAIN VALIDATION
Validate commit 09b7f13 in the real synchronization path, not unit tests alone. Required sequence: create/ack through CLI or git path → observe gateway state → allow stale/batched down-sync → prove ack/checkpoint survives. Record timestamps, state before/after, and commit/runtime evidence. If it fails, fix merge semantics rather than adding another URL/lane/workaround.

P0 — STADIUM MCP ERROR
Trace the UI footer MCP Error while daemon/fleet runtime is otherwise healthy. Determine whether fault is UI state, transport, auth, routing, stale health cache, or connector identity. Ship root-cause fix and verification evidence.

P1 — RELAY DEDUP INTEGRATION
Existing tools/relay_dedup.py is reported working. Wire semantic pre-write check into BOTH CLI `relay create` and gateway leg-create. Test exact duplicate, semantic duplicate, and legitimate related-but-distinct legs. Fail safely: dedup must not silently destroy valid work.

P1 — RHEA RESILIENCE
Rhea reported internal relay-registry blindness due missing NOUGEN_RELAY_GITHUB_TOKEN while ChatGPT connector can see live registry. Treat as a differential debugging case. Decouple Rhea from Blade/gateway single points where possible and restore registry visibility without exposing readable secrets.

P1 — ARXIV PIPELINE
Stop spawning scanner specification legs. Consolidate existing arXiv work into one implementation lane: event-driven RSS + API ingestion, idempotency, version lineage, scoring, attribution safeguards, autonomous research handoff. Build/test/measure.

P1 — RUNNER ARCHITECTURE
Execute the Claude Code creator-playbook audit already queued: startup/context hierarchy, action-semantic permission tiers, Pulse instrumentation. Produce concrete patches/tests, not another mapping document.

DIRECTOR ESCALATION RULE
Escalate to Dave only when a decision truly requires human intent, credentials/authorization, unavailable hardware, destructive action, or competing product directions. Everything else should be solved by the fleet.

PC CRASH RULE
Treat machines as replaceable compute. Persist execution state in relay/shards/checkpoints so a machine crash loses capacity, not continuity. On machine recovery, read registry first and resume from durable state rather than asking Dave to reconstruct context.

DONE WHEN
Open TODO count begins decreasing; active claims are non-zero and non-overlapping; completed legs carry evidence; duplicate planning legs stop multiplying; autonomous reconcile can assign/recover work without Dave saying `relay` or `run the track`.
