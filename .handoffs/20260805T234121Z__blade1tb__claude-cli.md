# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: mcp.nougenai.com gateway hardened on blade: auth + scope filter verified locally, not exposed yet
**Branch**: `main` @ `f5b74b1`
**Stack**: (undetected)
**When**: 2026-08-05T23:41:21.918284+00:00

---
# mcp.nougenai.com gateway: auth + scoping landed on blade, local-verified, NOT yet exposed

- `Watchtower/local_search_mcp.py` gateway mode now has bearer-token auth (env `NOUGEN_GATEWAY_TOKEN` or ACL-locked `.gateway_token`, fingerprint `d51ae2fe329d`) and a server-side scope filter (`gateway_scopes.json`: denies personal/private/secrets/finance categories + credential-ish tag substrings) applied at one choke point across all 16 read tools. Write tools remain unregistered in gateway mode.
- Gateway port resolves env `NOUGEN_GATEWAY_PORT` → 8766 (8765 stays APOLLO mesh). `Sol-Ai/tools/cf_tunnel_bringup.py` ingress + next-step corrected to the gateway; tunnel NOT brought up.
- Verified: `/health` 200; no token → 401; Bearer and `?token=` → 200; real MCP client saw 16 tools, 0 write tools; filter unit-proven against 5 synthetic denied records. Server stopped after tests.
- Go-live remains a GM call: run the tunnel, confirm scopes file, paste token into the Claude custom connector.
- Known gaps: `?token=` fallback fails on `/messages` POST for header-incapable clients (prefer header auth); FTS misses 3 deny-tagged shards (33131/33133/33158) — the choke-point filter catches them anyway, but FTS coverage deserves a look.
