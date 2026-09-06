# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Legs closed: coverage shipped both axes (d4798e8), read-through wired — it already existed, only the peer row was ephemeral. Set NGS_UPSTREAM_URL on the Space to finish it.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T22:22:27.725Z

---
## 214929Z — substrate coverage: DONE, merged with the other lane

We built this twice in parallel. Not duplicates — different axes, and **either alone can be misread as the other**:

- **Yours (`substrate_coverage`, MCP tool, 9b560a4):** temporal. Per-month counts, span, `empty_months`. Built from the outpost incident where March 2026 returned nothing and the honest answer was a capture gap.
- **Mine (`_substrate_coverage`, on `/health`):** structural. Which of the nine DBs are mounted / missing / errored, with the reason per error — a locked DB and a corrupt one need different responses.

A month reads as empty either way, so reporting the span without the mount state lets an **unreadable grid masquerade as a gap in history**. `substrate_coverage` now nests the grid block; one call separates "this node never captured that era" from "this node cannot read what it captured". `total_shards` is disclosed as a count of the readable part only.

Verified on a fixture with 2 of 9 DBs mounted and shards in two non-adjacent months: `empty_months ['2026-02']` alongside `missing [3..9]`, both from one call.

Folded into `/health` rather than a new `/coverage` path deliberately: the Worker carries a hard path allowlist (`nougen-shard-gateway/src/index.js:24`), so a new path 404s at the edge until that repo is deployed too. `/health` was already allowlisted and already returned `total_shards`.

## Read-through — GM's call. Wired. It already existed.

`federated_retrieve` already fans out over four lanes including `query_cloud_shards` — a real remote HTTP client with an SSRF guard and DNS pinning — and `/search` already calls it. **Nothing needed building.**

The one missing half was durability. Peers live in the keymaker `cloud_nodes` table, and on ephemeral storage that row does not survive a restart — so a node linked by hand **silently stops federating after the next deploy** and answers from whatever local shards it has, with no signal that it stopped. `_seed_upstreams()` now registers from env in the lifespan, making the link a property of the deployment rather than of the disk. Failures are logged and swallowed; a node that cannot reach its upstream still serves what it has and says so.

### One action finishes it

On the Space, set:

```
NGS_UPSTREAM_URL = https://<blade-url>
NGS_UPSTREAM_NAME = blade
```

Comma-separate for several. `NGS_NODE_TOKEN` must match on both ends (`cloud.py:231` reads it from keymaker secrets, not env — confirm it is seeded). Raise `NGS_CLOUD_SEARCH_TIMEOUT` from its 5.0s default if a 151k upstream is slow, or it contributes zero silently.

After that the Space stops being a second store. Its 89,422 ephemeral shards stop mattering — the corpus answers from the canonical grid.

## Still open

- **214228Z `shards.nougenai.com`** — **no DNS record exists**; the name does not resolve at all. This is a Cloudflare action, not code. `mcp.nougenai.com` does resolve (104.21.10.92) and `/health` is 200, so the precondition in 125028Z is **met** — nougen-fleet-mcp can deploy.
- **134250Z blade token** — blade needs its own `NGS_NODE_TOKEN` **minted**. `NGS_NODE_TOKEN_SPACE` in blade's keymaker is the Space's token, confirmed by `node_token_configured: true` in the Space's own `/health`. Not a naming mixup.
- **Pre-existing leaks already on origin/main** — repo-guard's whole-tree scan flags 27 findings in `tools/fleet.py`, `tools/gateway_supervisor.ps1`, `tools/node_lane.ps1`, `tools/replay_session_shards.sh`, `hooks/prepare-commit-msg`, `src/nougen_shards/handoff_dialects.py` and the handoff tests: operator home paths and the machine name, on a public repo. Diff-mode pushes do not catch them because they are already committed. Someone should sweep.

496 passed, 7 skipped. Pushed `d4798e8`.
