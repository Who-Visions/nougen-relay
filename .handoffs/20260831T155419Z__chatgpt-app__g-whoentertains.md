# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Prototype VS Code as provider-neutral local NouGen workbench
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T15:54:19.376Z

---
Fresh integration target from Dave: evaluate VS Code as a neutral local NouGen shell rather than another provider-specific client. Desired shape: VS Code owns the workspace/UI, NouGen owns memory, relay, tracker, identity, tool policy, and provenance, while the model behind the editor can be swapped among local Ollama, OpenRouter, Hugging Face, Codex-compatible, or other lanes. Explore the cleanest MCP/local-extension architecture, with explicit lane identity and no hard dependency on one commercial model. Done when: recommend the minimal architecture, identify whether an existing VS Code MCP/agent extension can be configured directly or whether a thin NouGen extension is warranted, define auth/tool-permission boundaries, and report a concrete first prototype path.
