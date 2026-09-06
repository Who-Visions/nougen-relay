# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Make open relay legs advance autonomously instead of waiting for manual pickup
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T03:03:11.282Z

---
SITUATION
The relay registry is correctly receiving open legs, but relay_claim_list currently shows zero active claims while multiple actionable legs accumulate. This turns the relay into a passive queue instead of an autonomous handoff system.

ASK
Implement autonomous forward triggering in relay-watch / CCR so newly created or discovered open relay legs are actively advanced without requiring Dave or another lane to manually prompt the fleet.

REQUIRED BEHAVIOR
1. On relay_create, emit or enqueue a wake signal for relay-watch.
2. relay-watch polls or receives the signal, reads relay_open, and atomically leases one eligible leg.
3. Use a lease/claim TTL so crashes or dead agents do not strand work permanently.
4. Route by capability/tag/goal where possible; otherwise assign to the healthiest available execution lane.
5. Prevent duplicate execution with idempotency keys based on relay leg id.
6. Retry transient failures with bounded exponential backoff plus jitter.
7. After max retries, move the leg into an explicit failed/dead-letter state and emit a new diagnostic relay instead of silently looping.
8. If no worker is available, keep the leg open and reattempt automatically on the next watcher cycle.
9. A successful worker pickup must immediately register a claim/ack so relay_claim_list reflects active ownership.
10. Worker completion must write a follow-up relay containing result, evidence, changed files/commit if applicable, and any remaining work.
11. The watcher itself must be supervised so it restarts after crash/redeploy.
12. Add observability: queue depth, oldest-open age, claim latency, retry count, dead-letter count, watcher heartbeat, and last successful autonomous handoff.

IMPORTANT ARCHITECTURE RULE
Do not create a new relay URL, MCP URL, provider-specific ingress, or parallel queue. Fix this inside the existing canonical NouGen relay/fleet architecture. The public MCP ingress remains https://shards.nougenai.com/mcp.

SUGGESTED EXECUTION MODEL
Treat open legs as a durable work queue with leases, not merely markdown notifications. relay_create -> wake -> select -> lease -> execute -> report -> next. A periodic sweep should remain as a recovery path in case an event wake is missed.

DONE WHEN
A test relay can be created from ChatGPT, then without any manual follow-up: relay-watch notices it, an execution lane claims it, relay_claim_list shows ownership, the worker performs the task, and a completion relay is written. Also prove recovery by killing or timing out a worker and showing the lease expires and the leg is reassigned exactly once.
