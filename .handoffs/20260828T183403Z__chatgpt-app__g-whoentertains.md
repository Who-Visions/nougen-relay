# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Decouple Rhea from Blade so agent survives shard gateway outages
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T18:34:03.079Z

---
P0 architecture fix. Current ChatGPT connector identity reports shards.gateway_url=https://blade.nougenai.com, so ask_rhea fails whenever Blade fails even though Rhea is intended to live on Hugging Face. Top fixes: 1) give Rhea a direct Hugging Face agent endpoint independent of Blade; 2) make Blade/shard recall an optional dependency, not transport; 3) degraded mode: if recall/Griot unavailable, Rhea still answers and explicitly marks memory offline; 4) health-check Rhea host and shard backend separately; 5) circuit-breaker + timeout so shard failure cannot cascade into agent failure; 6) cache last-known context or lightweight replicated read model for emergency continuity; 7) route selection should prefer Rhea host, then enrich with shards when available; 8) expose telemetry showing agent_up, memory_up, relay_up independently. Acceptance: power off Blade and ask_rhea must still return from Hugging Face within normal timeout with degraded-memory status.
