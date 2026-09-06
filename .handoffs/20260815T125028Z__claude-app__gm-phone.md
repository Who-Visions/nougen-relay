# 🤝 Git Handoff — claude-app / gm-phone

**Goal**: whoart: both fixes are on main now — deploy nougen-fleet-mcp from main, but ONLY after blade's tunnel answers on mcp.nougenai.com
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T12:50:28.986Z

---
## Update to leg 20260815T122214Z — the branch step is obsolete
Both branches fast-forwarded into main and pushed. Nothing to merge or check out.

- `nougen-fleet-mcp` main → **50b73fe** — bearer→`x-ngs-token` fix + `SHARD_GATEWAY_URL=https://mcp.nougenai.com`
- `NouGenShards` main → **5d3b14f** — `nougen.bat` venv fallback

## Live consequence of the merge — read before deploying
`nougen-fleet-mcp` main now points `SHARD_GATEWAY_URL` at `mcp.nougenai.com`, which **does not resolve until blade's named tunnel is up**. Deploying main right now would replace a worker that fails with a clear "gateway not configured" message with one that fails on DNS instead. Not worse in effect, but noisier to diagnose.

**So: do not deploy until blade posts that the tunnel answers.** Order is unchanged.

## Deploy steps (whoart — mondy has no node/npm/npx/wrangler, git only)
1. `git pull` on main.
2. `wrangler secret put SHARD_GATEWAY_TOKEN` — GM runs this. Value must equal blade's `NGS_NODE_TOKEN` byte-for-byte; verify by SHA-256 fingerprint against what blade reports (see leg `20260815T123023Z`).
3. `wrangler deploy`.

## Done when
`shards_status` green, and a `VeilVerse` recall returns non-empty. Thin result → raise `NGS_CLOUD_SEARCH_TIMEOUT` before drawing any conclusion; search runs 4.1s against a 5s default.
