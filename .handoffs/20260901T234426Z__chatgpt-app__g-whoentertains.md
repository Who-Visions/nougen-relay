# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Design NouGen for permanent HF-free survivability
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T23:44:26.587Z

---
Strategic design exercise from Dave: assume Hugging Face's free inference access remains available indefinitely, but do NOT depend on today's exact credit amount or pricing surviving. Build the scheduler so HF free capacity is treated as opportunistic specialist compute, not a foundational dependency. Local Ollama should absorb bulk; HF should be reserved for high-value routed specialists, Responses API/MCP agents, embeddings, modality access, and provider breadth; premium first-party lanes remain optional promotion targets. Done-when: a provider free-tier reduction degrades throughput but never breaks continuity, agent identity, Shards, Relay, or project state; routing policy can explicitly budget scarce HF credits and switch to local/premium alternatives without losing provenance.
