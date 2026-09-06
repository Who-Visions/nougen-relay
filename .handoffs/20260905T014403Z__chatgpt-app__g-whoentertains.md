# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build NouGenWake provider independent wake and nudge plane
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T01:44:03.199Z

---
Build a first class NouGenWake layer that sits above Claude, Codex, AntiGravity, Ollama, OpenRouter, Hugging Face and future providers. Provider native auto resume is only one signal, never the control plane.

Core requirement
NouGen must own wake intent, durable work state, timing, claims, retries and fallback. Provider wake features may assist, but NouGen must be able to detect that work is pending and reenter it without Dave touching a keyboard.

Architecture

1. Durable Wake Ticket
Every deferred task gets a durable record before the provider sleeps or hits quota.
Fields: wake_id, task_id, conversation_or_session_id, machine, preferred_provider, fallback_chain, reason, created_at, earliest_wake_at, hard_deadline, dependency_conditions, checkpoint_ref, context_ref, attempt, max_attempts, priority, generation, lease_owner, lease_until, idempotency_key, status.

2. Event sources
Wake on provider reset time, observed provider availability, machine boot, process restart, relay arrival, relay ack timeout, dependency completion, PR event, webhook event, scheduled time, user defined deadline, idle timeout, network restoration, failed task retry, model context rollover, or local queue becoming nonempty.

3. Reconciliation loop
Do not depend on one timer firing perfectly. A lightweight controller continuously asks: desired state = this task should be progressing; actual state = no healthy worker currently owns it. If mismatch, enqueue a wake. This follows the controller reconciliation model used in high reliability distributed systems.

4. Wake semantics
Treat wake delivery as at least once. Treat task ownership as effectively once through a lease plus fencing generation. Any duplicate wake must become a no op when another worker already holds the current generation.

5. Lease and fencing
Before a machine or provider resumes work it must atomically acquire a short lease. Include holder identity, renew time, lease expiry and monotonically increasing generation. Every side effecting action checks the current generation so a stale worker cannot continue after failover. Heartbeat while active. If heartbeats stop, another lane can claim after expiry.

6. Nudge ladder
Level 0: wake local supervisor only and inspect current state.
Level 1: resume the existing provider session if the provider supports it and quota is available.
Level 2: start a fresh session on the same provider using the last checkpoint plus compact NouGen Context.
Level 3: route the same task to another frontier provider according to the reasoning grid.
Level 4: route deterministic or bulk work to local Ollama or another cheap lane.
Level 5: if no lane is viable, reschedule with backoff and preserve the exact checkpoint.
Never attempt to bypass provider quota or rate limits. Wait for supported availability, then nudge.

7. Reset aware wake
When a provider reports a reset timestamp, create an independent NouGen timer slightly after that time rather than trusting the provider to wake itself. On firing, first verify provider health and quota. If Claude already auto resumed, dedupe and simply observe. If not, issue the NouGen resume path. Provider wake and NouGen wake should race safely under the same idempotency key, with only one claimant winning.

8. Durable timer substrate
Use more than one layer where practical. Cloudflare Durable Object alarms are a strong edge primitive because they persist scheduled wake state, execute at least once and retry failures. Keep local OS timers as a second independent lane on each machine. A boot recovery scan must replay overdue Wake Tickets. GitHub repository_dispatch or workflow_dispatch can be an optional external recovery trigger for repo related work, not the primary scheduler.

9. Retry discipline
Classify errors before retrying. Transient failures such as network errors, temporary provider unavailability and 5xx responses use bounded exponential backoff with full jitter. Permanent errors such as bad auth, invalid arguments or missing permissions fail fast into an actionable state. Avoid synchronized retry storms across machines.

10. Circuit breaker
Track provider health separately from task failure. After repeated transient provider failures, open the provider circuit for a cooling period and route elsewhere. Half open with one probe. Do not let every pending task hammer the same dead provider.

11. Dead letter and quarantine
After max attempts, move the Wake Ticket to a durable dead letter queue with complete provenance. Never silently discard it. Surface a relay leg containing the last checkpoint, attempts, providers tried, failures and recommended next action.

12. Checkpoint contract
Before sleeping, quota exhaustion, provider switch, context rollover or planned shutdown, persist: exact goal, completed work, unresolved work, files changed, tests run, current branch or PR, tool state, next executable action, assumptions, blockers and a compact context pointer. The next provider should not have to reconstruct the world from chat history.

13. Observability
Emit wake_requested, wake_fired, wake_deduped, lease_acquired, lease_renewed, provider_resumed, provider_switched, checkpoint_loaded, task_progressed, task_completed, retry_scheduled and dead_lettered. Track wake latency, false wake rate, duplicate wake rate, resume success rate, provider switch rate, time to useful tool call and tasks completed without Dave intervention.

14. Machine topology
Blade, Phoebus and every future NouGen machine run a tiny local Wake Agent. The cloud plane schedules and coordinates; the local agent knows whether the machine, CLI process and provider lane are actually reachable. On boot it announces presence, renews a lease and scans for overdue tickets assigned to itself or available to claim.

15. Safety and permission boundary
Wake may resume already authorized work, run allowed local automation, or hand off through the fleet. It must not invent new permissions or widen tool scopes. High impact actions still pass the existing approval gates. Wake is continuity, not permission escalation.

Suggested components
NouGenWake = global wake control plane and ticket ledger.
NouGenWatch = watchdog and reconciliation loop.
Wake Agent = per machine execution daemon.
Wake Ticket = durable task continuation object.
Wake Bell = event envelope that says a ticket may now be runnable.

Minimal state machine
PENDING -> ELIGIBLE -> CLAIMED -> RUNNING -> CHECKPOINTED -> COMPLETED
Failures route RUNNING -> RETRY_WAIT -> ELIGIBLE.
Exhaustion routes RUNNING -> DEAD_LETTER.
Duplicate wake against CLAIMED or RUNNING with a valid lease becomes DEDUPED.

Implementation priority
P0: Wake Ticket schema, local Wake Agent, lease and idempotency, reset aware timer, checkpoint loader, relay events.
P1: Cloudflare alarm scheduler, provider adapters, backoff and circuit breaker, boot recovery.
P2: cross machine leader election, dead letter UI, wake metrics, policy tuned reasoning based provider selection.

Acceptance tests
A. Claude hits quota, reports reset, Dave leaves. NouGenWake schedules its own ticket. At reset Claude native resume and NouGenWake may both fire; one lease wins, no duplicate side effects, work continues.
B. Claude does not auto resume. NouGenWake resumes or starts a new session from checkpoint.
C. Claude remains unavailable after reset. Circuit opens and task routes to OpenRouter or Ollama according to policy.
D. Phoebus reboots during RETRY_WAIT. On boot its Wake Agent discovers overdue work and continues.
E. Two machines wake the same task simultaneously. Only the current fencing generation may act.
F. Network outage exhausts retries. Ticket lands in dead letter with full provenance, never disappears.

Research basis as of 2026 09 04
Temporal durable workflows persist execution state and resume through failures using timers, signals and task queues. Kubernetes uses reconciliation loops, heartbeats and leases for availability and leader election. AWS durable execution guidance emphasizes idempotency, explicit at least once versus at most once semantics, classified retries and exponential backoff with jitter. Cloudflare Durable Object alarms provide persisted future wake, at least once execution and automatic retries. Cloudflare Queues uses dead letter queues for exhausted delivery. These patterns should be fused rather than copied blindly.

Done when
A provider session can die or hit quota, Dave can leave the machine, and NouGen independently preserves the work, schedules the next viable wake, safely deduplicates provider native auto resume, reacquires ownership, reloads the checkpoint and produces a verified useful tool call without manual intervention.
