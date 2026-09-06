# 🤝 Git Handoff — claude-app / gm-phone

**Goal**: whoart: deploy nougen-fleet-mcp branch claude-cli/shard-gateway-auth-header — bearer→x-ngs-token fix must land BEFORE the recall, or the gate 401s and reads as an empty vault
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T12:22:14.316Z

---
## Situation
mondy picked up leg `20260815T120557Z` (set SHARD_GATEWAY_URL + redeploy). Found a blocker that would have faked a failure.

**The bug.** `worker.js:shardHeaders` sent `Authorization: Bearer ${SHARD_GATEWAY_TOKEN}`. blade's `_TokenGatedMCP` (NouGenShards `app.py:418-444`) reads **only** `x-ngs-token` header or `?token=` query param — it never inspects `Authorization`. So every `shards_*` call would 401 no matter how correctly the secret was minted, and the recall path surfaces a 401 as an *empty vault*. The green light would have looked like "the grid is empty."

Fixed on branch `claude-cli/shard-gateway-auth-header`:
- `worker.js` — sends `x-ngs-token`
- `wrangler.jsonc` — `SHARD_GATEWAY_URL` → `https://mcp.nougenai.com` (the hostname line 25 already reserves for blade)

## Ask (whoart — mondy has no node/npm/npx/wrangler, only git)
1. Merge or check out `claude-cli/shard-gateway-auth-header`.
2. `wrangler secret put SHARD_GATEWAY_TOKEN` — GM runs this; the value must equal blade's `NODE_TOKEN` exactly (`hmac.compare_digest`, no trimming).
3. `wrangler deploy` — **only after** blade's named tunnel answers on `mcp.nougenai.com`. Until then the var points at a dead host.

## Done when
`shards_status` reads green and a `VeilVerse` recall returns non-empty. If it comes back thin, raise `NGS_CLOUD_SEARCH_TIMEOUT` before concluding anything — search runs 4.1s against a 5s default.

## Warning for any lane touching NouGenShards
`C:\Users\Mondy\NouGen\NouGenShards` on mondy is a **stale July snapshot**, not live work — files date 2026-07-02/07-23 against a remote HEAD of 2026-08-14. Committing that tree would delete 48 files (including `tools/ngs_node_serve.py`, blade's own node server) and revert 55 more by six weeks. Do not push it. A clean clone is now at `NouGenShards-push-main`.
