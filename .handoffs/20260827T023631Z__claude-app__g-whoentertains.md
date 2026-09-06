# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DONE: recall timeouts fixed - 56s serialized 9-DB scan now parallel, 2-3s end to end
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T02:36:31.573Z

---
## Done
- Profiled recall in the venv: keyword lane serially ran ~21 one-second FTS statements across the 9-DB cluster, and retrieve() ran that twice (scoped + whole-brain) = 56s warm - past the worker's 30/45s timeouts, and the likely load behind the node's mid-/search deaths.
- core.py: per-DB scans now run on a thread pool (NOUGEN_RECALL_DB_WORKERS env-first, DB-order collection keeps ranking deterministic, ContextVars propagated); scoped + whole-brain passes overlap. 56.3s -> 2.2-3.5s measured, instant through the gateway.
- No regressions: retrieval test subset compares strictly no-worse vs unmodified baseline (all failures pre-existing history.db teardown races).
- Node restarted serving the fix (Google sign-in still configured, gateway green).

## Open
- Node silent-death forensics leg: keep open until a week of no /search deaths confirms load was the killer.
- core.py change uncommitted with the rest of today's diffs (tenants/agents/mcp_oauth/app/tests) pending GM review.
