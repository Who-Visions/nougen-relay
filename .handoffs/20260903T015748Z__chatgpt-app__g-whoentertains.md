# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Rebuild relay claims as live lease-based control plane, reconcile Git backlog, and eliminate terminal flashes
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T01:57:48.938Z

---
GM directive 2026-09-02 ~21:5x EDT: elevate NouGenRelay claims to production-grade live/accurate semantics and stop all MCP/daemon/helper terminal windows from flashing or stealing focus. Treat this as a control-plane redesign, not a cosmetic patch.

GROUND TRUTH / WHY:
- `relay_claim_list` can show zero active claims while many legs remain open. `relay_open` is only a small window (max 25 in the connector), so it is NOT a census.
- Historical direct-Git census shard 17025 found 721 legs / 217 open on 2026-08-31, with much of the open set bookkeeping debt from a blind read window. Dave suspects the Git registry may now have ~300 open; verify from the registry directly before publishing a number.
- Existing autonomous pickup/reconcile already has Git-visible claims, SHA fencing, local execution leases, stale recovery, retry/backoff (shard 22474 / PR #13 lineage). `nougen_relay/guard.py` claim enforcement exists but is off by default and currently fires at commit time rather than claim-admission time (shard 23238). Do not build a duplicate subsystem; elevate this one.
- relay-live has already moved notification reads toward origin/main and measured ~9s create-to-visible, but a curly-quote/cp1252 subprocess decode bug later broke passes until fixed. Live path must be Unicode-clean and event-first.

TOP-TIER TARGET ARCHITECTURE:
1. Git remains the durable append-only audit/evidence ledger, NOT the hot scheduling queue. Build a live derived claim index / control plane in front of it. Every runtime transition must be asynchronously mirrored to Git; a reconciler proves Git and hot state converge.
2. Separate `open` from `actionable`. Runtime state machine: DISCOVERED -> TRIAGED -> CLAIMABLE -> LEASED -> RUNNING -> {COMPLETE | BLOCKED | RELEASED | RETRY_WAIT | DEAD_LETTER | ARCHIVAL_DEBT | SUPERSEDED}. Historical open bookkeeping debt must never compete with fresh actionable work.
3. Claim record minimum fields: leg_id, source_sha/version, owner/lane, priority, affinity/capabilities, actionability, dedupe_group, lease_id, monotonic fencing_token, lease_expires_at, renewed_at, attempt_count, max_attempts, last_error, blocker, next_action, proof_refs, supersedes/superseded_by, created_at, updated_at. Append transition history with actor + evidence.
4. Claim acquisition must be atomic CAS, not read-then-write. Admission runs BEFORE acquisition. `guard.py` becomes the deterministic admission controller and returns ALLOW/DEFER/DENY with reason. Local Ollama may classify/summarize/score/routing-suggest for free, but it NEVER grants permissions or bypasses policy.
5. Lease semantics: worker atomically acquires {lease_id,fencing_token,expiry}; heartbeat every ~TTL/3; any write/complete must present the current token. Expired tokens are rejected. Graceful shutdown explicitly RELEASE/NACKs work so another worker can pick it up immediately. Sweeper reclaims expired leases. Monotonic fencing prevents a zombie worker from finishing after its lease was reassigned.
6. Idempotency: every side-effecting transition uses stable idempotency key = hash(leg_id, transition/action, relevant source version). Retries must be safe. Duplicate legs collapse into one dedupe group or supersession chain.
7. Retry/dead-letter: bounded attempts + exponential backoff with jitter; poison legs cross a threshold into DEAD_LETTER with the failure evidence preserved so fresh work is never blocked behind one bad leg.
8. Scheduling: priority + age + owner affinity + dependency readiness + capability match. Fresh P0/P1 actionable work first; blocked/dependency legs do not consume worker slots. Fairness aging prevents starvation. A worker should maintain a small bounded in-flight count.
9. Hot-path delivery becomes push-first: `relay_create`/registry write emits a lightweight event immediately to the local control plane; relay-live/NouGenMsg is woken with the specific leg id. Git remains fallback/replay. Use event stream consumer-group semantics (pending list, ack, reclaim) rather than scanning hundreds of JSON files for every decision. Redis Streams or NATS JetStream are acceptable if already available/free; otherwise implement the same lease/CAS semantics in the existing local store first. Do NOT add infrastructure merely for fashion.
10. Reconciler: periodic full Git census compares ledger vs hot index; repairs missed events; identifies stale OPEN records that are actually complete/superseded; produces `total/open/actionable/leased/running/blocked/archival_debt/dead_letter` counts. `relay_claim_list` must read live leases, not infer activity from Git status. `relay_open` should remain a browse API, not the operational truth.
11. Observability: record timestamps for create -> origin -> ingest -> triage -> claim -> first heartbeat -> visible NouGenMsg -> complete -> Git-confirmed. Publish p50/p95/p99 claim latency, queue lag, active leases, expired/reclaimed leases, retries, DLQ size, reconciliation drift, Git-sync lag. Demo target: create-to-visible <=2s p95 on LAN/local path and claim decision <=1s p95 when an eligible resident worker exists; Git durability can follow asynchronously but must converge.
12. Backlog migration: DIRECTLY census the Git registry first. Batch old open legs through local Ollama only for advisory classification, then deterministic evidence rules decide: actionable, already-completed, superseded, blocked, archival debt. Never mass-ack from model opinion alone. Produce before/after census with evidence and preserve every historical leg.

WINDOWS UX HARD REQUIREMENT: Dave does NOT want terminals constantly popping, flashing, or stealing focus on MCP calls/relay ticks.
- All persistent MCP servers, relay-live, claim workers, sync/reconcile daemons should be long-lived background processes/services. Do not spawn a visible cmd.exe/PowerShell window per call.
- On Windows Python subprocesses that must exist, use `shell=False`, explicit argv, redirected stdout/stderr, and `creationflags=subprocess.CREATE_NO_WINDOW`; do not combine it with DETACHED_PROCESS. Prefer direct Python/library APIs over shelling out. Decode child output explicitly as UTF-8 (`encoding='utf-8'`, safe error handling or bytes->UTF-8) so cp1252 cannot sink the daemon again.
- For always-on components, prefer a Windows Service / non-interactive Task Scheduler registration or equivalent resident launcher. `pythonw.exe` is acceptable only for simple user-session helpers with proper file logging. No GUI dependency, no focus stealing, no transient terminal window.
- MCP calls should talk to resident processes over socket/pipe/HTTP, not launch a new terminal process for every invocation.
- Add a regression test that invokes every hot-path helper repeatedly and asserts no console-window creation path is used on Windows.

REFERENCE PATTERNS researched 2026-09-02/03 current docs: Redis Streams consumer groups use append-only events, pending-entry lists, XACK, XAUTOCLAIM/XCLAIM and lag metrics; current Redis docs also emphasize idempotent processing. Kubernetes Lease uses holderIdentity, renewTime, leaseDurationSeconds and optimistic concurrency/fencing concepts for leader failover. GitHub concurrency groups model bounded ownership/queuing but GitHub itself should not be the hot queue. Python 3.14 subprocess exposes CREATE_NO_WINDOW; Microsoft documents CREATE_NO_WINDOW as console-less execution and recommends background/service patterns for non-interactive tasks.

IMPLEMENTATION ORDER:
A) Verify full Git census and current claim/guard code paths, no guessing.
B) Add/activate admission-at-claim + atomic lease/fencing + heartbeats/release/reclaim in existing subsystem.
C) Build live materialized claim index and wire connector `relay_claim_list` to it.
D) Add push wake from relay creation to claim scheduler/relay-live; retain Git replay fallback.
E) Classify/reconcile historical OPEN debt with evidence.
F) Make all Windows processes invisible/background and Unicode-safe.
G) Instrument latency/accuracy and publish before/after proof.

DONE WHEN: full Git census is reported; zero-active-claim with actionable backlog cannot persist while an eligible worker is healthy; duplicate claims are fenced; stale workers are reclaimed; backlog debt is separated from live work; live claim state is queryable with age/owner/expiry; p95 live delivery/claim latency is measured; every persistent Windows component survives reboot without flashing a terminal; and all changes are sharded/relayed with tests and exact code refs.
