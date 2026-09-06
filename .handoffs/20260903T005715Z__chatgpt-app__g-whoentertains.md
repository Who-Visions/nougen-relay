# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Insert resident Ollama as free first-pass relay processor
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:57:15.929Z

---
Dave approved using the already-resident local Ollama/Kaedra lane to save cloud tokens. Implement it as a non-privileged preprocessor in front of cloud/frontier relay handling: triage/classify, summarize long relay bodies, deduplicate, generate compact batons, and apply deterministic routing metadata. Escalate ambiguous/security-sensitive/code-changing/judgment-heavy work to Claude/Codex/etc. Do not let the local model grant permission, claim/close privileged work, mutate policy, or weaken provenance. Measure before/after cloud tokens and relay latency. Preserve Git/relay durability and NouGenMsg delivery.
