# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Generalize AGY idle-wake into provider-agnostic NouGen wake fabric
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T04:13:27.827Z

---
Dave identified the product-level requirement: every user will face the same wake problem across different runtimes. Do not solve this as an AGY-only hook. Build a provider adapter layer that detects runtime/lifecycle capabilities, discovers wake mechanisms, provisions an always-on watcher when needed, and verifies idle-to-active execution with a canary. User-facing API should be one concept: when an eligible baton arrives, wake/resume the target agent and deliver the baton. Provider-specific mechanics such as PreInvocation, named pipes, inbox polling, webhooks, scheduled tasks, or local daemons stay hidden behind adapters. Done when a fresh install can self-diagnose 'streaming works but idle wake missing' and either configure the bridge automatically or return one actionable setup step.
