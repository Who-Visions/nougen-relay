# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Exploit HF as nested provider router for NouGen agents
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T23:42:14.178Z

---
Current Hugging Face Inference Providers docs change our provider-specialization model. HF is not just a specialist API; it is a provider-of-providers with one token, automatic/provider-pinned routing, :fastest/:cheapest/:preferred policies, automatic failover, and GET /v1/models exposing pricing/context/latency/throughput when available. Official integrations also let both Claude Code and Codex use HF as their backing inference fabric while preserving their agent harness UX.

ASK:
1. Add an HF capability/catalog adapter that periodically ingests /v1/models and normalizes model, downstream provider, task support, context, price, latency, throughput, availability.
2. Keep HARNESS identity separate from BACKING MODEL and DOWNSTREAM PROVIDER in provenance. Example: harness=claude-code, fabric=huggingface, model=GLM-5.1, downstream_provider=together/fireworks/etc.
3. Extend scheduler scoring so NouGen chooses task/role first, then optionally delegates provider selection to HF via fastest/cheapest/preferred or pins a provider for deterministic evals.
4. Prototype at least two agent shells: Claude Code over HF and Codex over HF. Use different backing models/roles and record success, latency, cost/credit burn, tool behavior, and quality into Shards.
5. Preserve policy/account compliance. Current HF docs confirm $0.10/mo credits for free users and BYOK vs routed billing, but do NOT establish permission for multi-account quota pooling; do not build that assumption.

DONE-WHEN: one NouGen task can be assigned to a role, routed through HF to a chosen/open model, execute inside Claude Code or Codex harness, and return telemetry naming all layers. Run a repeatable eval comparing fastest vs cheapest vs pinned-provider routing and shard the outcome.
