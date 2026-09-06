# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: TOP 0.01% relay repair plan: eliminate dual truth with canonical append only event log plus idempotent fanout
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T17:38:22.455Z

---
Research-backed fix plan for the reproduced relay split brain. Root problem is classic dual write inconsistency: git `.handoffs` and gateway registry both act as authorities, so one can commit while the other misses or overwrites it. Top-tier repair pattern:

1. PICK ONE CANONICAL COMMIT LOG. Every relay leg gets one immutable event_id, aggregate/stream key, monotonic sequence/revision, payload hash, producer_id, schema_version, created_at, and causation/correlation ids. Git and gateway become projections/read models, never peers that independently originate truth.

2. REMOVE DIRECT DUAL WRITES. Producer performs one durable append. If state + event must change together, use a transactional outbox: commit business/relay state and outbox row atomically, then CDC/fanout publishes to connectors. AWS and Debezium both recommend outbox specifically to prevent the exact failure where state persists but notification does not.

3. IDEMPOTENT DELIVERY END TO END. At-least-once transport is fine if every event has stable event_id and consumers keep an inbox/dedup table keyed by event_id. Replays become safe. Never depend on filename timestamp alone for identity.

4. ORDER BY STREAM, NOT WALL CLOCK. Give each relay stream a monotonic sequence or canonical log offset. Consumers persist last_applied_offset and reject/regap on sequence discontinuity. PostgreSQL logical replication and Kafka both rely on ordered commit/log positions rather than timestamps for transactional order.

5. FENCING FOR ACTIVE WRITERS. Daemon/dispatcher leases need generation numbers or fencing tokens. Any stale writer holding an expired lease must be rejected by the canonical store even if it wakes up later. etcd-style revisions/transactions/leases are the model: compare current revision/lease before commit.

6. RECONCILIATION AS INVARIANT, NOT BACKGROUND HOPE. Continuously compare canonical head vs every projection: expected_count, max_offset, missing_ids, duplicate_ids, payload_hash mismatch, consumer lag. If any projection diverges, automatically replay from canonical offset. Never let a projection overwrite canonical history.

7. ANTI-ENTROPY + MERKLE/HASH WINDOWS. For 100+ open handoffs and multiple machines, maintain rolling range hashes/checkpoints so the daemon can localize divergence cheaply instead of full scans. A mismatch triggers targeted replay for that range.

8. WRITE ACK SEMANTICS. `relay_create` only returns success after canonical durable commit. It can separately report projection status, e.g. canonical_committed=true, git_projected=false, gateway_projected=true. Do not call the operation fully delivered until required consumers reach the event offset.

9. SCHEMA UNIFICATION. Stop `.md` vs `.json` lookup ambiguity. Canonical envelope is structured data. Markdown is a rendered body field or projection. `relay_read(event_id)` resolves by event_id, never by extension-specific storage assumptions.

10. CHAOS TEST THE EXACT BUG. Inject failure after canonical append but before git projection, after git projection but before gateway projection, duplicate publish, delayed stale writer, reordered delivery, daemon restart, connector offline, network partition. Pass condition: zero lost events, zero divergent authoritative states, safe duplicates, deterministic replay.

11. OBSERVABILITY SLOs. Expose canonical_head, per-consumer applied_offset, lag_ms, gap_count, replay_count, dedup_count, stale_writer_rejects, hash_mismatches. Pulse HUD should show these as fleet integrity, not just agent activity.

12. MIGRATION: freeze independent writers, snapshot both current stores, union by stable identity/content hash, detect conflicts manually or by newest canonical provenance only where justified, seed canonical log, rebuild both projections from event 0, then permanently block direct writes to projections.

Architecture target: Producer -> canonical durable append -> outbox/log -> fanout/CDC -> git projection + gateway projection + phone/Claude/Codex consumers. One source of truth, many replayable views. Done when the 17:32:45 Blade phone handoff is visible by exact event_id everywhere and survives forced partial failures without manual repair.
