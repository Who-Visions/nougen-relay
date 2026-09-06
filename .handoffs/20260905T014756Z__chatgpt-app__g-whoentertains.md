# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fold NouGenWake into NouGenWatch instead of creating another top-level system
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T01:47:56.560Z

---
Architecture correction from Dave: NouGenWatch already has an existing relay/spec, so do not proliferate a separate top-level NouGenWake product unless implementation forces it. Treat wake as a first-class capability inside NouGenWatch.

Recommended shape:

NouGenWatch = supervisory control plane for liveness, schedules, provider reset windows, quotas, machine presence, stalled work, and desired-state reconciliation.

Inside NouGenWatch:
• Wake Engine: decides when dormant work becomes runnable.
• Wake Ticket: durable continuation record with checkpoint, eligibility time/condition, preferred provider, fallback lane, retry state, idempotency key, and fencing generation.
• Wake Bell: event emitted when a ticket becomes eligible.
• Provider Wake Adapters: Claude reset/resume awareness, Codex/AGY/OpenRouter/Ollama/etc capability checks and nudges.
• Machine Wake Agent: tiny local daemon/service on Blade, Phoebus, WhoArt, future nodes; announces liveness on boot/resume, claims eligible tickets, restores checkpoint or routes elsewhere.
• Lease/fencing/idempotency layer: provider-native wake and NouGenWatch may race safely; only one continuation becomes authoritative.
• Backoff/circuit breaker/dead-letter handling for repeated failures.

Core rule: provider-native auto-resume is an optimization/input signal, never the owner of continuity. NouGenWatch owns the desired state and can independently nudge or reroute once a provider becomes eligible again. Wake should remain a noun/verb/event in telemetry and code, not necessarily a separate branded service.

Acceptance example: Claude session caps at 9:10, NouGenWatch records the blocked continuation and reset eligibility. If Claude auto-resumes first, Watch observes/leases it and suppresses duplicate wake. If Claude does not resume, Watch rings the Wake Bell, verifies provider eligibility, nudges/reconstructs the session, or routes through the Reasoning Grid. If the machine rebooted, its local Wake Agent performs the same reconciliation on startup.

Done when the existing NouGenWatch relay/spec is amended or superseded with this wake subsystem, duplicate NouGenWake architecture is removed, and tests cover provider-native wake racing NouGenWatch wake without duplicate tool execution.
