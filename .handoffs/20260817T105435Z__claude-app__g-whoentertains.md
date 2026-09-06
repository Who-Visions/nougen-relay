# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ask_griot recovered into source + era leak fixed at the connector (2b9ffdd) — needs one deploy, operator holds the token
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T10:54:35.312Z

---
## Situation
`ask_griot` was serving live traffic from a tree nobody committed. `nougen-fleet-mcp` `main` and `origin` both sat at `2accf5a`; the string "griot" appeared nowhere in the repo; the deployed worker advertised the tool anyway. Its era leak was unreviewable because there was nothing to review.

The repo's 22 tools were otherwise identical to the live surface, so `ask_griot` was the **only** uncommitted delta — a rewrite could land without losing anything else.

## Landed on `nougen-fleet-mcp` main
- **`2b9ffdd`** — `ask_griot` in source, era bounds enforced on every arm:
  - a row that can't be proven inside the window is **held back and counted**, including **undated** rows (vault lanes return memories with no timestamp — those were the leak). An undated memory is not evidence for a bounded question.
  - bounded questions also fan out to `recall_window`, which filters on timestamp in SQL before scoring, so a quiet era keeps its own shards.
  - arms dedupe by tool name: `SHARD_TOOL_SEARCH` is pinned to `recall_memory`, so recall and search were the same call twice — a wasted round trip against a cold Space.
  - shards reached by two arms merge into one memory, so `held_back`'s denominator is the archive, not the fan-out.
  - each arm degrades alone and names itself in `failures`; incomplete packets say so.
  - **18 tests** (`npm test`, `node --test`) pinning era predicates, undated hold-back, arm selection, dedupe, ordering, degradation, advertised schema.
- **`f2ce3fa`** — `SHARD_GATEWAY_URL` synced to the live quick tunnel (`catalyst-design-pete-patents`). The repo still named the previous hostname; a deploy would have silently reverted the gateway.

## Second bug found on the way: the deploy path itself
`tools/deploy.sh` kept a hand-maintained copy of `wrangler.jsonc`'s vars and had drifted. It still carried `SHARD_GATEWAY_URL: ""` and `SHARD_GATEWAY_STYLE: "sse"`, and had lost `SHARD_TOOL_WINDOW/COVERAGE/AMEND/RETRACT/FORGET/VAULT_*` plus the entire Google Sign-In block. **Running it would have deployed a connector with no gateway and an SSE style blade does not serve** — every `shards_*` tool dead.

Now derives all 21 bindings from `wrangler.jsonc` through a string-aware JSONC reader (a naive `//` strip eats the `https://` in the tunnel URL), preserves secrets via `keep_bindings`, and refuses to deploy an empty gateway or with failing tests. Dry-run verified: 21 bindings, gateway and style intact.

## Ask — operator, one command
The connector vault has `CLOUDFLARE_API_TOKEN_NOUGEN_FULL` (`655061650c12`) and `CLOUDFLARE_ACCOUNT_ID` (`5b3062d17ab4`), but there is deliberately no `vault_get`, so no lane can read them. Deploy is yours:

```
CLOUDFLARE_API_TOKEN=… CLOUDFLARE_ACCOUNT_ID=… tools/deploy.sh
```

## Done when
After deploy, `ask_griot(question="shard highway", since="2025-01", until="2025-03")` returns **zero** 2026-08 rows and a non-zero `held_back` — today it returns 8 memories, all out of era, `held_back: 0`.

## Still open
The node half (`18ea86b6`, `/search` era bounds) is in NouGenShards PR #89 and is a separate merge. The connector fix stands on its own; both together close the leak end to end.
