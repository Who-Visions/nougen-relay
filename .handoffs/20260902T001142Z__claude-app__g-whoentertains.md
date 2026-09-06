# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Node concurrency FIXED (PR #176): FastMCP ran sync tool bodies on the event loop — 3 concurrent 63s -> 10.8s, phoebus now makes the fan-out grace
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T00:11:42.936Z

---
The blocker from leg `20260901T234103Z` is fixed and verified.

**Root cause**: FastMCP calls a **sync** tool function directly inside its async handler — `func_metadata.call_fn_with_arg_validation` ends in a bare `return fn(**args)`, no threadpool. A sync tool therefore owns the event loop for its whole duration. **15 of 16 tools were sync.**

**The measurement that named it**: 3 concurrent recalls took **63.0s each through the node**, while the *same three* ran in **0.85s wall as plain threads in-process** — a 74× gap on identical retrieval code. `core.retrieve` was never the bottleneck; 3 concurrent in-process is actually *faster* than 3 serial (0.85s vs 1.31s) because SQLite releases the GIL. Bisecting in-process vs over-HTTP is what separated "the query is slow" from "the server can't answer two at once". Every earlier theory — ollama, federation, uptime degradation — died to a measurement.

That's also why **a restart never fixed it**: a held event loop is invisible in CPU, RSS and `/health`.

**Fix (PR #176)**: `_offloaded` wraps each sync tool so FastMCP registers an async function whose body runs via `run_in_threadpool`. Safe by precedent — the sync-def FastAPI endpoints already run these same bodies in Starlette's threadpool, so nothing newly acquires a thread. Tool schemas byte-identical (`functools.wraps` + `inspect.signature` follows `__wrapped__`).

| | before | after |
|---|---|---|
| 3 concurrent | 63.0 s each | **10.8 s each** |
| single, same load | 20.4 s | **10.6 s** |

Three concurrent now cost what one costs — the exact signature of unblocking an event loop. Verified end to end: `shards_search` returns `fanout={blade:"ok", phoebus:"ok"} complete=true`, phoebus making the 6s grace consistently where it had been missing it.

**Same disease as #161 one layer up** — that fixed sync-def FastAPI endpoints, this fixes sync tool bodies under FastMCP. **Any fleet node registering sync MCP tools has this trap.**

Suite: 737 passed. One pre-existing failure (`test_section_is_additive_in_substrate_coverage`) reproduces on clean `origin/main` — flagged, not mine.

⚠️ **Blocking on #174**: the nightly refresh agent is installed on phoebus and points at `ops/ngs-node-refresh.sh`, which only exists on the unmerged `node-refresh-schedule` branch. **It will fail at 04:15 local unless #174 merges first.** #174 and #176 both want review.
