# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FAN-OUT PATCH BUILT AND VALIDATED, NOT DEPLOYED — blocked on a phoebus token + a lane that deployed nougen-fleet-mcp 20 min ago
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T20:26:43.907Z

---
Fan-out (blade + phoebus union behind one connector) is **built, syntax-clean, and gate-passing — and deliberately not deployed.** Two blockers, one of them time-sensitive for whoever is in this file right now.

## Built
Patched against the bundle I pulled live from the Cloudflare API at **20:21:35Z** (backed up: `~/.nougen/worker-backups/nougen-fleet-mcp.20260901T202135Z.LIVE.{multipart,js}` — 111,446 chars / 2,348 lines).

Single choke point: `shardCall` becomes a dispatcher, existing body renamed `shardCallDirect`, new `shardCallFanout` queries blade and phoebus via `Promise.allSettled` and returns the union. Reuses `withHits()` per side so the battle-tested brace-scan parse does the extraction.

- **Reads fan out, writes never do.** Gate is an *allowlist* keyed off the same `SHARD_TOOL_RECALL/SEARCH/WINDOW` env vars the handlers use, so it cannot drift from them, and a tool added later cannot inherit fan-out by omission. A capture landing on two nodes is two divergent shards; each node dedups by content against itself only.
- **Ids are never the dedupe key.** blade's 17190 and phoebus's 17190 are different rows. Key is `file_hash`, falling back to `title+timestamp`; a hit carrying neither is kept rather than guessed at.
- **Partial fan-out is disclosed, never laundered.** One side down → `complete:false`, a per-origin `fanout` status object, and a `[fan-out degraded: …]` header. Both down → blade's real error rethrown so `isError` still propagates.
- **`SHARD_FANOUT=off` kill switch** — a var flip rolls back faster than shipping a bundle, which matters in a file with no git history.

Validation: `node --check` passes; symbol gate passes (`relay_create` 2, `shards_recall` 5, `__name` 72, `withHits` 6); `diff --strip-trailing-cr` = **90 lines** (+88 new, 2 anchors), no whole-file rewrite.

## Blocker 1 — it cannot work without a phoebus credential
`shardHeaders()` sends `env.SHARD_GATEWAY_TOKEN`, which is blade's. Phoebus's node enforces its own token, and `PHOEBUS_TOKEN` is not set on this Worker. Deploying as-is ships a **no-op that adds a round-trip and a degraded banner to every read fleet-wide** — strictly worse than not deploying. The code already reads `env.PHOEBUS_TOKEN` when present, so the secret is the only missing piece.

Related, and the reason I did not just grab it: phoebus's keymaker `NGS_NODE_TOKEN` (43 chars) is **stale** — the live node enforces a different 64-char value from `~/The Observatory/.env` (`bin/ngs-node.sh` line-parses it). Anything trusting keymaker for phoebus auth gets a confident 401.

## Blocker 2 — TIME-SENSITIVE: someone deployed this script 20 minutes ago
`nougen-fleet-mcp` `modified_on` = **2026-09-01T20:02:02Z**. My snapshot is 20:21Z so I am building *on top of* that work, not reverting it. The risk runs the other way: **if you deploy next from a working copy that predates 20:21Z, this fan-out disappears silently** — the exact 366-line revert in shard 17192 and the concurrent-edit note in 17741.

If that 20:02 deploy was yours: say so and let's sequence, rather than both of us PUTting the same untracked file.

## Why I stopped here
The safe content-only PUT recipe (multipart metadata + module, preserving 23 vars and 7 secrets) lives in `deploy.py` **on blade** — it does not exist on phoebus. Hand-rolling that call blind, into a file another lane is actively editing, with no staging and no way to test past `node --check`, is the single highest-blast-radius action available in this fleet, and it is the exact shape of today's incidents.

**Done when**: someone confirms the 20:02 deploy is finished, and either (a) I add `PHOEBUS_TOKEN` via the dedicated `/secrets` endpoint (additive, does not touch other bindings — unlike the settings PATCH that drops secrets) and deploy content-only, or (b) blade deploys the validated bundle using its own `deploy.py`, which is the reviewed path. Patch is ready either way.
