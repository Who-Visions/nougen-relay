# Supersedes legs 20260815T122214Z and 20260815T125028Z

Both are stale. This is the current state. Filed via git rather than the fleet
connector, whose auth was invalidated mid-session — **GM needs to reconnect the
NouGen fleet connector**; `relay_*`, `tracker_*` and `shards_*` are all down
from the Claude side until then.

## Three bugs, not one — all on the same path, all fixed on `main`

Each failed in a way the recall path renders as **an empty vault** rather than
an error. Any one alone would have made the first VeilVerse recall look like
the grid was empty.

| commit | bug |
|---|---|
| `50b73fe` | worker sent `Authorization: Bearer`; blade's `_TokenGatedMCP` reads **only** `x-ngs-token` or `?token=` (`app.py:436`) → 401 |
| `5f3b144` | `SHARD_GATEWAY_STYLE` was `sse`, so the worker GET `/sse`; blade mounts **only** `/mcp` (`app.py:513`) and defines no `/sse` route → 404 |
| `828aaf5` | `SHARD_TOOL_SEARCH` was `search_context`, which lives on the **stdio** instance in `src/nougen_shards/mcp.py`, not on `node_mcp`. The node exposes only `recall_memory`, `capture_experience`, `mark_utility`, `node_status` (`app.py:63-93`) → "unknown tool" |

Verified compatible, no further change needed:

- `stateless_http=True` — the worker's separate `initialize` + `tools/call`
  round trips need no session id.
- `json_response=True` — handled by `shardRpcHttp`'s SSE/JSON sniff.
- `recall_memory(query, limit)` matches the `{query, limit}` the worker sends.

`NouGenShards` main is at `5d3b14f` (nougen.bat venv fallback, ported from the
July tree on mondy).

## mondy is now a valid deploy lane

Portable node **v22.14.0** at `C:\Users\Mondy\.local\node`, on the user PATH.
`wrangler 4.123.0` runs. `node --check worker.js` passes and `wrangler.jsonc`
parses with all nine vars correct. **whoart is no longer required for the
deploy** — the "whoart has the toolchain" note in wrangler.jsonc is now stale.

## What is left — all interactive, no lane can do these

1. **blade:** `cloudflared tunnel login` → named tunnel on `mcp.nougenai.com`.
   Pin `NGS_PORT` first; see leg `20260815T123023Z` for why the dynamic port
   silently breaks the tunnel across reboots.
2. **GM:** `wrangler login` on the deploying machine — browser OAuth, and
   mondy is not authenticated.
3. **GM:** `wrangler secret put SHARD_GATEWAY_TOKEN`, set to blade's
   `NGS_NODE_TOKEN` byte-exact. Compare SHA-256 fingerprints rather than
   moving the value; `hmac.compare_digest` fails on a trailing newline and
   reports it as a plain 401.

Then `wrangler deploy` from mondy, and the recall runs.

## Hazard closed

`C:\Users\Mondy\NouGen\NouGenShards` is a stale 2026-07-02 snapshot. A marker
file `_STALE_DO_NOT_PUSH.md` now sits in it documenting that committing that
tree would delete 48 files — including `tools/ngs_node_serve.py`, blade's own
node server — and revert 55 more by six weeks. Its only unique work is already
on main. Clean clone for real work: `NouGenShards-push-main`.
