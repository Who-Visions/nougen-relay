# 🤝 Git Handoff — claude-app / gm-phone

**Goal**: blade NGS node is UP (10.0.0.87:4444) but /search takes 50s vs the connector's 5s timeout — fix bm25 hot path before peers can federate
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-14T22:30:29.517Z

---
## Situation

Acked and executed `20260814T172450Z__mondy__claude-cli` on blade (BLADE1TB). **The node is serving**, but federation will not actually work yet — read the blocker below before linking it from a peer.

### What is up

- `tools/ngs_node_serve.py` (new, in `NouGenShards-push-main`) launches `uvicorn app:app` with every env-shaped value probed at run time: bind host, port (first free of `NGS_PORT_CANDIDATES`), advertised IP (UDP default-route probe), token (env → keymaker).
- Live at **`http://10.0.0.87:4444`**, serving **151,144 shards** across the 9-DB vault at `C:\Users\super\Watchtower\vault`.
- `/health` → `status: ignited`, `node_token_configured: true`.
- `NGS_NODE_TOKEN` minted and stored DPAPI-encrypted in keymaker (fp `9c67af03a9da`). It did not previously exist — every data endpoint was 503 deny-by-default.
- Token gate verified live over the LAN: `POST /search` without the header → **401**; with it → **200**.
- HUD deliberately NOT mounted. `app.py` fails closed when the bind is network-exposed and `NGS_HUD_USER`/`NGS_HUD_PASSWORD` are unset. Federation only needs the token-gated REST surface + `/mcp`; do not set HUD creds just to silence the warning — that publishes an unauthenticated vault UI to the LAN.

### Blocker: /search is 10x slower than the client timeout

Measured on blade:

| call | time |
|---|---|
| `POST /search` over LAN, limit=3 | **50.7s** |
| `core.retrieve` (full) | 43.5s |
| `core._keyword_retrieve` | 40.3s |

`connectors/cloud.py::query_cloud_shards` calls `_open_cloud(req, url, 5.0)` — a **5 second** timeout. So every peer will time out, log `cloud node skipped`, and silently contribute nothing. Federation degrades to exactly the same empty result as having no node at all.

### Root cause (measured, not guessed)

The FTS5 index is present and healthy on all 9 DBs — it is not missing and does not need rebuilding:

- bare `shards_fts MATCH ... LIMIT 3` → **0.013s per DB** (~0.12s for all 9)
- `content LIKE '%...%'` → 0.7s per DB

But `_keyword_retrieve` (core.py:685) does not run the bare match. Its FTS branch is:

```sql
SELECT s.*, bm25(shards_fts) AS bm25_score
FROM shards s JOIN shards_fts ON s.id = shards_fts.rowid
WHERE shards_fts MATCH ? ORDER BY bm25_score ASC, s.id ASC LIMIT ?
```

`ORDER BY bm25()` forces SQLite to score **every matching row** before LIMIT can apply — the LIMIT never prunes. With a multi-term query expanded by `_build_fts_match_query`, the match set is a large fraction of each 16.7k-shard DB, so it scores ~150k rows and hauls `content` + `embedding` blobs for all of them across 2.5 GB.

Suspected secondary costs, not yet isolated: `_process_fts_result` per row, and `history.log_event(..., "ACCESSED")` writing once per returned row inside the scan loop.

## Ask

Fix the hot path so a federated `/search` lands well under 5s. Suggested order:

1. Confirm the `ORDER BY bm25()` fanout with `EXPLAIN QUERY PLAN` and by logging the pre-LIMIT match count.
2. Prune before scoring — rank inside an FTS-only subquery (`SELECT rowid FROM shards_fts WHERE MATCH ? ORDER BY rank LIMIT ?`), then join `shards` on the surviving rowids. Keeps blob reads proportional to `limit`, not to the match set.
3. Check `_build_fts_match_query` term expansion — if it ORs terms, the match set is far wider than intended.
4. Re-time `_keyword_retrieve` and the live `POST /search`. Done when the LAN call is under 5s with the same top-3 results.
5. Consider raising the connector's hardcoded `5.0` to an env-resolved timeout (Rule 0.2 — it is a bare magic number in a shipped line), but treat that as a seatbelt, not the fix.

## Done when

- `POST http://10.0.0.87:4444/search` with `X-NGS-Token` returns in **< 5s**.
- A peer with `NGS_ALLOW_INSECURE_CLOUD=1` runs `nougen node link http://10.0.0.87:4444` and a federated recall actually returns blade shards.

## Gotcha for whoever links this node

`_is_safe_cloud_url` **rejects plaintext http to any non-loopback host** unless `NGS_ALLOW_INSECURE_CLOUD=1`. Peers hitting `http://10.0.0.87:4444` need that set or the URL is refused before a request is ever sent — it will look like the node is down.

## Not done on this leg

- The other blade leg (`20260814T174745Z` — rotate both per-lane gateway tokens) is untouched, pending GM ruling: standing doctrine is keys stay in place, so "rotate for hygiene" needs an explicit order.
- The node is a foreground process, not a service. It dies with the session. Making it boot-persistent is a separate leg.
