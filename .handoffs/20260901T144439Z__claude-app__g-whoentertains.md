# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Retrieval RCA: hits were only in MCP text, structuredContent was a bare stub - fixed in fleet worker (withHits) + /mcp bare path 404 fixed (PR #172); worker deploy awaits GM
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T14:44:39.863Z

---
# Retrieval fix - blade1tb / Claude Cli, 2026-09-01 14:5xZ

## Verified: the grid is innocent
All 9 blade DBs: 235,203 rows, `temporal_meta` present on every one, FTS indexes 1:1 with rows. Direct MCP calls to blade answer correctly and fast: `recall_memory` 2.2s with real hits, `recall_window since=2026-04 until=2026-04` returns a 2026-04-30 shard in 4.6s. **The node is fine. The code around it was not.**

## Root cause of "shards refuse to be retrieved"
The node's shard tools answer in MCP `content` **text**; they return no `structuredContent`. The fleet worker published `withFreshness(result.structuredContent, env)` - i.e. a bare `{gateway_url, checked_utc}` stub. Connectors that render structuredContent therefore showed **"gateway metadata with no hit payload"** (ChatGPT's exact words, leg 20260901T084247Z) for queries that DID return shards. Indistinguishable from an empty vault.

## Fixes made
1. **fleet worker** `C:\Users\super\Watchtower\NouGen\nougen-fleet-mcp\src\worker.js`:
   - new `withHits()` carries the rows in BOTH fields (`hits[]` + `count`, `raw` only when nothing parsed). The node concatenates JSON objects with no separator (`}{`), so it uses a string-aware brace-depth scanner, not a whitespace split. Validated against a real 3-hit blade body: count=3, correct ids/titles; braces-inside-strings safe; true-empty stays a stub.
   - `shards_recall`/`shards_search` now check `result.isError` (they laundered node errors into "(no matches)") and fall back to `recall_memory` when `SHARD_TOOL_RECALL`/`SEARCH` are unset. `shards_coverage` already had both guards - which is exactly why coverage was the ONE shard tool that kept working.
2. **node** PR #172: `/mcp` answered **404** while `/mcp/` served fine - Starlette's Mount hands the inner app an empty path. Fixed with a pre-router middleware rewrite (normalizing inside the token gate cannot work; routing 404s first). Bad token still 401 on both paths. 3 tests.

## Deploy state
- Worker: patched, `node --check` clean, `deploy.py --dry-run` OK (2,288 lines, account resolved). **PUT is gated for agent lanes - GM runs `python deploy.py` in `nougen-fleet-mcp`.** New `deploy.py` ships only that dir's `src/worker.js`; note `NouGenShards-push-main\fleet\worker\worker.js` is a STALE 1,922-line duplicate and its `deploy_worker.py` would REVERT production - do not use it.
- Backup of the pre-patch bundle is in this session's scratchpad.
- PRs open: #169 (sync guards), #171 (boot quarantine), #172 (/mcp bare path).

## Also observed
`state/gateway_probe.json` has been timing out at 45s every 5 min, and a grid_watch tick runs ~80s - that is phoebus's "something rescans the grid every ~90s". Unresolved; separate from this fix.
