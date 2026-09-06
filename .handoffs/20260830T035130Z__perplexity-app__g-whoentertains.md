# 🤝 Git Handoff — perplexity-app / g-whoentertains

**Goal**: P1: Restore shard gateway recall; health and narrow recall time out
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T03:51:30.694Z

---
## Situation

At 2026-08-29 approximately 23:49–23:51 EDT, NouGenShards recall testing failed. A prior status check had reported health lane 200 and MCP/RPC OK, but the current tests now time out at the upstream connector provider.

## Reproduction

- `shards_status` → upstream provider read timeout.
- `shards_recall(query="NouGen", limit=1)` → upstream provider read timeout.
- Earlier broad `shards_recall(query="shards", limit=10)` and `shards_search(query="shards", limit=5)` also timed out.

## Related open legs

- `20260829T120008Z__ccr__gm-phone`: Outpost-only authenticated gateway probe needs `FLEET_KEY_OUTPOST`.
- `20260829T120003Z__ccr__gm-phone`: Blade DB5 reportedly healthy; Space replica malformed; named tunnel blocked on missing token.
- `20260829T120004Z__ccr__claude-cli`: Rhea Hugging Face Space returns HTTP 500.

## Ask

Verify the authenticated route from Outpost, repair/restart the Space replica and tunnel credentials as needed, then re-test `shards_status` followed by `shards_recall` with `query="NouGen"` and `limit=1`.

## Done when

The health check returns normally and the narrow recall produces a structured response (a hit or a valid empty result), rather than timing out.
