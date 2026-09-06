# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: WAR GAME: shadow-migrate NouGenRelay into hosted Hugging Face relay fabric
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T02:21:18.079Z

---
Dave approved a long-form Destiny war game for evolving NouGenRelay from his GitHub repo into a relay system any NouGenShards user can use. Treat this as architecture + staged implementation planning, not permission for destructive cutover.

FIRST PRINCIPLE: GitHub is excellent as provenance/audit/dev history, but it should not remain the hot-path multi-tenant coordination database if the Destiny is 100 users then 100M. The first safe step is a hosted Hugging Face relay SHADOW MIRROR using the already-designed Space/service surface.

WAR GAME / STAGES:
0) Separate control plane and data plane. Control: Google/OIDC identity, tenant/member/role mapping, quotas/billing/provider policy. Data: relay append/read/claim/ack/event stream.
1) HF SHADOW MIRROR: add hosted relay API. Dual-write Dave's new legs to GitHub + HF. Consumers may compare/read HF, but Git remains current authority initially. Immutable event IDs + idempotency keys. Instrument parity: counts, hashes, order, lifecycle, latency, duplicates.
2) Define tenant-ready event schema now even single-tenant: tenant_id, relay_id, root/parent chain, sender lane, goal, body/content_ref, created_at, status event, lease, provenance, idempotency_key, schema_version. No secrets in relay body.
3) READ CUTOVER after sustained parity: hosted state becomes primary read path; Git remains audit/fallback/export.
4) WRITE CUTOVER after read proof: authenticated clients append to hosted service directly. Append-only event log becomes source of truth. Git export becomes async snapshot/audit, not a commit per claim/ack/status mutation. This should eliminate branch/working-tree drift and high-frequency claim commit churn.
5) TENANT ISOLATION: Google subject resolves server-side to tenant/member/role. Never trust caller tenant override. Dave and Spas must be mutually unreadable. Test guessed IDs, cross-tenant search, claim/ack, logs, exports, deletion, and credential boundaries.
6) REALTIME: push/subscribe path (SSE/WebSocket/long-poll/durable notification) to relay_live adapter -> NouGenMsg -> active CLI. Goal healthy p50 <2s, p95 <5s create-to-visible. Git export latency is decoupled.
7) FREE-FIRST COMPUTE: relay core stays deterministic. Ollama/Kaedra/free providers can summarize, triage, dedupe, compress batons only. They never authorize. Preserve canonical body hash and transformation provenance.
8) BILLING: keep transport/basic quota cheap/free where possible; charge for hosted retention, volume, premium inference, storage, team/SLA as evidence supports. Provider inference metering separate from relay semantics.
9) 100-TENANT GATE: load 100 concurrent isolated tenants with retries, reconnects, claims, rollover, local receivers offline, and service restarts. Record p50/p95/p99, throughput, queue lag, storage/user/day, cost/user/day. Gate is ZERO cross-tenant leakage and deterministic replay/idempotency.
10) FUTURE SCALE: only after 100-user evidence, move state behind stable API into managed DB/queue/object-store/cache and stateless replicas as needed. Partition by tenant hash. HF is first hosted step, not a forever constraint. 100M is a Destiny, not a present capacity claim.

FAILURE WAR GAME: HF Space sleep/restart/ephemeral filesystem; provider or auth outage; duplicate writes; out-of-order events; split-brain Git vs hosted; stale claim leases; clock skew; network partition; oversized payload; tenant flood/noisy neighbor; schema migration; account transfer/deletion/export; billing exhaustion. Required mechanisms: idempotency, append-only lifecycle events, replay cursor, leases, dead-letter quarantine, bounded payload + content refs, reconciliation, per-tenant rate limits, backups/export, explicit degraded mode.

CURRENT EVIDENCE TO INCORPORATE:
- relay_live was recently moved off the stale local working-tree path and measured about 9s create-to-visible.
- current origin census shard reports 997 legs / 42 open, and claim-state discrepancies between connector and origin. Use that as evidence that repo/local-checkout state is already straining as runtime truth.
- stale/open bookkeeping debt must be cleaned independently so it is not blindly imported into hosted truth.
- Dave = Case Study 1. Spas Jamaica = Case Study 2 and should become first external tenant migration from Dave's Google-family context to his own Google-auth tenant with zero cross-user leakage and preserved legitimate continuity.

FIRST DELIVERABLE: inspect the already-designed HF relay Space/service assets and return an evidence-backed migration plan naming repo/paths/components that already exist, what is missing, and the smallest reversible shadow-mirror implementation. If safe and non-destructive within current permission, implement only the shadow-mirror seam + tests. Do NOT cut over authority or delete Git history. Capture a Destiny/shard and relay back concrete before/after evidence.
