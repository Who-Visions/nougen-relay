# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: MCP consolidation: creds vaulted + Cloudinary secret out of config, 8 duplicate MCP entries removed, TWO Keymaker stores found that cannot see each other. Cloudflare route work BLOCKED on permission.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T23:32:05.620Z

---
War-gamed to `wargames/mcp-consolidation.md`, ledger updated, then fanned out three lanes in parallel while I held the credential and Cloudflare streams (secrets must never enter a worker's context).

## The finding that matters most: two Keymaker stores

This machine carries **two keymaker databases, identical schema, different contents**, and they cannot see each other:

| store | rows | who reads it |
|---|---|---|
| `~\Watchtower\agent_secrets.db` | 205 | `keymaker_peel.py` default, so every one-key launcher (`exa_mcp_launch`, `ollama_mcp_launch`) - and the path the constitution names |
| `~\.nougen\secrets\shards_secrets.db` | 89 | `keymaker.resolve_secrets_store()`, so the repo's `get_secret` / `ingest_secret` |

I hit it live: ingested three credentials with `ingest_secret`, verified each round-tripped through `get_secret`, then a peel-based launcher reported `CLOUDINARY_URL not in keymaker` for a slot just written and verified. Nothing was broken - the write and the read addressed different databases.

**This is precisely the failure Rule 0.3 exists to prevent.** A lane could read that as "the credential is missing" and go ask the GM to re-paste a secret that is safely vaulted. Note `keymaker.py` already exports `VaultDivergenceError` and `candidate_stores`, so divergence is modelled - the peel launchers just do not consult it.

Fixed without picking a winner: `~/.nougen/bin/nougen_secret_exec.py` probes candidate stores and uses the first holding the slot, reporting which store answered (name and path only, never a value). **Which store is canonical is a GM decision. Do not delete either.**

## Credentials (done)

Three were sitting inline in `~/.codex/config.toml`: a Cloudinary URL across 4 servers (`fp f2854dee63ed` - worst of the three, a `cloudinary://key:secret@cloud` URL embeds an API secret), a Stitch key (`fp b725c7986f75`), a Ref apiKey in a query string (`fp 68c79bf762f0`). All vaulted DPAPI-wrapped, round-trips verified. The four Cloudinary servers now launch through the new launcher - the secret is peeled at spawn and passed via env only, and the config file is **clear of it**. Launcher fails closed: missing slot prints the slot NAME and refuses to start the child.

**Not fixed, deliberately**: Stitch and Ref are HTTP servers Codex dials directly, so no launcher can intercept. Codex's config uses **no env-reference syntax anywhere**, so `${VAR}` expansion is unverified for that client and guessing would break two working tools. Both are vaulted, so the fix is staged. Also found untouched: **a GitHub token in antigravity's `mcpServersParked`**.

## Config dedupe (done)

Eight entries removed or renamed, every file backed up and re-parsed, no caller broken:
- `local_search_mcp.py` was declared under three names. Worst case: antigravity called it **`nougen-shards`**, a name that means the remote gateway in every other client. Now `nougen-fleet-registry` everywhere.
- Codex's `nougenai-fleet-registry` dropped (same URL as its `nougen-shards`), with 11 tool-approval subsections that were attached to the wrong server anyway - they listed the LOCAL script's tools.
- `context-mode` dropped (same `start.mjs` as `nougen-ctx`); `vault-intelligence` dropped (script verified absent); `cua_repl` dropped (verified `enabled:false`).
- `NOUGENTRACKER_DIR` unified on `~\.nougen\tracker`. **Both tracker dirs are live and neither was touched**: `NouGenTracker` holds 1959 files / 6.64MB including a `reports\daily\` git history; `.nougen\tracker` holds 164 / 1.07MB. A daily-reports merge is likely wanted - flagging, not acting.

## BLOCKED - needs GM permission

The Cloudflare consolidation is written and gated but **could not execute**: the permission classifier blocked the production routing mutation, correctly. I did not route around it.

Ready to run the moment it is approved, in this order:
1. Deploy a `http_request_dynamic_redirect` rule folding `mcp.nougenai.com` and `ngs.nougenai.com` into `shards.nougenai.com` with a 308 preserving path and query. **Verified safe**: I grepped all 7 readable config sources - 5 references to `shards.`, **zero** to `mcp.` or `ngs.`, so no client gets repointed out from under a running session.
2. Only then delete the 22 clone routes (`mcp.` and `ngs.` are route-for-route copies of `shards.`; the full route table is recorded in the war-game so they can be re-created).
3. Stand up `fleet.nougenai.com/mcp` as the admin door. It is already a proxied `AAAA 100::` placeholder with **zero routes**, which is why today's 405 there is Cloudflare's default and proves nothing. It must be shown to fail closed on a missing token BEFORE being routed.

Three MCP workers have no route at all (`nougen-fleet-mcp-chatgpt`, `nougen-shard-gateway`, `nougen-shards-mcp`). Per the war-game these get their workers.dev subdomain disabled (reversible), not deleted.

## Still running

Two fanned-out lanes: hardcoded paths + private IP (`claude-cli/derive-paths-and-endpoints`), and the silent-failure pair - `shards_capture` returning `{}` regardless of outcome, and `NOUGEN_VECTOR_CACHE=0` silently killing the vector lane (`claude-cli/no-silent-failures`). Both open PRs against main, neither merges itself.

## Done-when

- [x] credentials vaulted, Cloudinary secret out of the config
- [x] duplicate MCP entries removed across all clients
- [x] launcher survives the two-store divergence
- [ ] **GM: approve the Cloudflare routing change** (steps 1-3 above)
- [ ] GM: which keymaker store is canonical
- [ ] GM: tracker daily-reports merge
- [ ] Stitch/Ref env-expansion confirmed, or fronted via `mcp-remote`
