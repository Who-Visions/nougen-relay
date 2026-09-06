# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CLI gap: relay_open/create/ack/etc have no local CLI client, need OAuth
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T16:33:52.107Z

---
## Finding (blade1tb, claude-cli, 2026-09-01 16:33 EDT)

Dave flagged: "the relay_open etc tools aren't listed in the cli or wired right." Investigated — this is real, not a misconfiguration.

**Root cause**: `shards.nougenai.com/mcp` (the tools you're reading this through) is Cloudflare-proxied to Worker `nougen-fleet-mcp` via a dashboard Custom Domain (not visible in wrangler.jsonc, which only omits Wrangler Route config). It requires full OAuth 2.0 — `GET /.well-known/oauth-protected-resource` returns `{"authorization_servers":["https://shards.nougenai.com"],"scopes_supported":["fleet"]}`. That's the same flow the Claude Code MCP connector completes silently (browser consent + refreshed token) — NOT the simpler `?token=` connector path CLAUDE.md documents for the Gradio `app.py` `/mcp` endpoint (different, local deployment).

**Gap**: `NouGenShards-push-main/src/nougen_shards/cli.py` has zero client code for this API (confirmed via grep: 0 hits for relay_open/create/ack/claim_list/shards.nougenai.com anywhere in src/). The CLI's `handoff` subcommand is a totally separate, local-file-based system (`.handoffs/` dir) — not connected to this cloud relay at all. `auth`/`connect` subcommands only manage provider API keys.

**What it would take**: a real OAuth 2.0 authorization-code + refresh client built into cli.py, plus a token store. Non-trivial — worth its own task, not a quick patch. Flagging here in case Phoebus or another lane is already touching cli.py/auth this session (temporal-provenance work is in flight per the latest legs) so nobody duplicates.

**Interim reality**: these tools already work fine through any MCP-connected session (this leg was written through them). The actual gap is only for standalone scripts/headless callers that aren't MCP clients.

Done-when: Dave decides whether to greenlight an OAuth client build for cli.py, or accept MCP-connector-only access as the standing design.
