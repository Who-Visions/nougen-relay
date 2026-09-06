# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Enforce Claude coach mode and free-fleet-first routing
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T01:15:59.081Z

---
GM directive: Claude should operate as a concise coach/orchestrator, not spend Fable/Opus tokens doing work that resident/free lanes can safely handle. Route bulk reasoning, triage, summarization, search/distillation, recon, repetitive analysis, and other low-risk heavy work first to resident Ollama/Kaedra and policy-approved free providers such as OpenRouter free lanes, Hugging Face/provider routes, Arly, and any currently healthy free fleet lanes. Keep Claude for integration judgment, code review, evidence synthesis, permissions, and tasks that fail local/free quality gates. Preserve provenance, tests, relay ownership, and permission boundaries. Do not route privileged decisions to local models. Make this explicit and measurable: record provider chosen, reason, fallback reason, and cloud tokens avoided where feasible. Inspect existing provider_scheduler / routing code before adding anything redundant. Done when coach mode is represented in the routing policy and a live task demonstrates free-first delegation with Claude returning only a compact supervisory result.
