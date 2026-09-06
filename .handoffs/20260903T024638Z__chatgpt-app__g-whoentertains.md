# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Codex read-only sanity check of Rhea escape topology and reusable MCP/skill plan
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T02:46:38.932Z

---
Target Codex for a small non-overlapping read-only check while Claude continues the live extraction. Context: Rhea's controller/authority is being moved out of the Hugging Face Space runtime while preserving the existing Kimi Space tunnel as a reversible fallback. Dave's normal HF inference path is through Spaces he created; do NOT assume Hugging Face Inference Providers are available or billable. Ask Codex to inspect the recovered historical Kimi Space contract and report exactly: (1) one concrete migration failure mode that could accidentally strand Rhea or switch her onto the wrong HF lane, (2) the smallest mitigation, and (3) one suggestion for how a future canonical MCP action/skill should detect that condition automatically. No code changes, no secrets, no duplicate implementation. Return a concise evidence-backed note and exact refs if available.
