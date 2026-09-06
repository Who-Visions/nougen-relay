# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build HF harness integration eval matrix for NouGen
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T23:45:35.410Z

---
2026-09-01 follow-up from HF Inference Providers integrations overview. Official HF docs show Inference Providers works not only with Claude Code/Codex but with a broad harness/framework layer: Pi, OpenCode, Hermes Agent, CrewAI, GitHub Copilot Chat, fast-agent, Inspect, LangChain, LiteLLM, LlamaIndex, PydanticAI, Roo Code, smolagents, Vision Agents, NeMo Data Designer and others. HF also says non-explicit integrations may still work via its OpenAI-compatible API if they accept custom endpoints.

ASK: build a small integration/eval matrix for NouGen rather than hard-wiring one harness. Columns should include: harness, HF integration method, MCP/ACP/tool support, custom endpoint support, agent/team abstraction, structured/typed output support, coding strength, eval support, latency overhead, setup friction, and provenance fields emitted. Prioritize first-wave prototypes: (1) fast-agent because it is explicitly MCP/ACP powered and eval-oriented, (2) Inspect for repeatable agent/model evaluation, (3) LiteLLM as a unified gateway, (4) CrewAI for multi-agent team semantics, (5) PydanticAI or smolagents for lightweight typed agents, (6) OpenCode/Pi/Hermes/Roo as alternate coding bodies.

Architecture rule: preserve role != harness != inference_fabric != model != downstream_provider != routing_policy != toolset. NouGenShards/Relay must remain the persistent continuity layer so changing the harness or HF-routed model does not restart the project.

Done-when: at least two non-Claude/Codex harnesses can execute the same read-only NouGen task through HF or an HF-compatible endpoint, results are scored with one common eval, and telemetry proves which harness/model/provider/toolset actually produced each result.
