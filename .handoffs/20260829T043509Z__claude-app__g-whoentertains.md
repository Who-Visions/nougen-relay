# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Codify NouGen as a capability layer that unlocks user owned infrastructure
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T04:35:09.710Z

---
Architecture doctrine: NouGen is not the compute. NouGen is the capability layer that discovers, connects, routes, remembers, measures, and coordinates the compute and services the user already has access to.

The public repo must NOT encode Dave's private infrastructure. It should encode the grammar for unlocking whatever infrastructure exists on the user's side: local AI, provider AI, cloud AI, remote machines, storage, databases, email, calendars, APIs, and future capabilities.

Canonical mental model:
User infrastructure -> NouGen discovery/configuration -> capability registry -> routing -> agents -> shards/relay/ledger -> any connected AI interface.

Key behavior: degrade according to available capabilities rather than fail because the user lacks Dave's stack.

Examples:
* No GPU -> route cloud.
* No cloud API -> route local.
* One machine -> operate locally.
* Multiple machines -> discover/federate.
* One AI provider -> give it the grid.
* Five providers -> give all five the same substrate while preserving identity in the ledger.

Dave's current setup is the proof instance, not the hardcoded product target. A stranger with one laptop and Ollama should get a smaller version of the same organism. A user with servers, multiple providers, and multiple machines should unlock a larger one.

Public positioning candidate: 'Bring the infrastructure you already have. NouGen turns it into one AI fleet.'

This doctrine should shape README, onboarding, capability discovery, routing policy, health checks, and public reproducibility tests.
