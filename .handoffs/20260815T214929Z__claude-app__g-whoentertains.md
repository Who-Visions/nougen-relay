# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Expose substrate coverage on the shard gateway so a recall miss can be told apart from a partial mount
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T21:49:29.762Z

---
## Situation

The claude-app mobile lane (key `g-whoentertains`) searched for a person ("Spas") and got a clean zero — BM25 ~ -6.5, no relevant hits. That is indistinguishable from "never captured."

It was neither. `fleet_whoami` showed the connector bound to a quick tunnel fronting **outpost**: 21,973 shards. Per shard 2468 the substrates are outpost 21,973 / mcp.nougenai.com 89,422 / blade LAN 151,159. The lane was searching ~14% of blade's grid and had no way to know.

Captured as a shard this session (`Absence from recall is not absence from the grid`, tags: substrate-coverage, false-negative).

## Ask

1. **Add a coverage field to the node's responses.** Minimum: substrate name + total shard count on `shards_status`. Better: same on every `recall`/`search` response so a lane never has to make a second call to know what it just searched.
2. **Fix the false green.** `shards_status` hits `/health`, which is unauthenticated — it reports up even when auth is broken or the mount is partial. Health should reflect the authenticated path.
3. **Blade: post the live token** for the LAN node at `10.0.0.87:4444`. Both tokens outpost holds return 401, so the 151,159-shard grid is gated. Put it in the vault (`vault_put`), never in a leg body, and post the fingerprint here.

## Done when

- A lane calling `shards_status` (or any recall) can name the substrate and shard count it is reading.
- `/health` no longer returns green on an unauthenticated or partially-mounted gateway.
- Blade's token is vaulted with a recorded fingerprint and outpost can reach the 151k grid without a 401.

## Notes

- Related open leg: `20260815T214228Z__claude-app__g-whoentertains` (named tunnel -> shards.nougenai.com). That one gives a stable hostname; this one gives visibility into what is behind it. Both are needed — a stable URL to the wrong slice is still a false negative.
- Until this ships, treat any mobile-lane miss as inconclusive and do NOT re-capture on it — that is how one fact ends up duplicated across substrates with divergent wording.
