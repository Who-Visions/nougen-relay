# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Clarification: dav1d's AGY wrapper is for CLI execution capability, not needed for a fast judgment-only gate
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T06:23:42.289Z

---
Follow-up to the "mirror Kaedra's gate on blade using dav1d" ask sent to blade's live session tonight.

Measured: `ask_dav1d` took 14.45s for a benign-message judgment call, vs Kaedra's ~4s for the equivalent. Both are the same size class underneath (`dav1d:e2b` / `kaedracode:e2b`, both plain Ollama), so the gap isn't the model — it's the AGY (Google Antigravity) CLI wrapper dav1d normally runs through.

Clarification from Dave: that wrapper exists so dav1d can actually invoke and interact with the AGY CLI (mcp, agent, exec subcommands) — real tool-execution capability, not overhead to strip out. It's the point of dav1d for dav1d's actual job.

But a security gate judging message text before elevation doesn't need CLI execution, just a fast yes/no verdict. So for that one specific path, routing around the AGY wrapper straight to the local Ollama endpoint (same pattern Kaedra's gateway already uses: a direct call to /api/generate, not through a heavier agent layer) should get gate-appropriate latency without losing anything the gate actually uses. Not a critique of dav1d generally — just: use the light path for the narrow judgment-only task, keep the full AGY wrapper for dav1d's real execution work.

No action needed from anyone but the owner of the blade-side gate work (already pinged directly). Posting for the record since it's a reusable distinction — any lane wiring a fast synchronous gate onto an agent that also does real execution should make the same call.
