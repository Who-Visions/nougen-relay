# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: main is GREEN, NouGenShards #87 (node OAuth) + #88 (CI fixes) merged — blade: pull + restart to ship the node's OAuth surface
**Branch**: `main`

---
## Done tonight from phoebus

1. **Main green for the first time today.** Three latent breakages fixed in #88:
   `tools/gateway_probe.py` leaked `C:\Users\super\...` paths (the same class 6ebfd42
   scrubbed elsewhere, re-landed in the next tool); the tool-surface test asserted the
   exact roster and rotted twice in a day (now: memory-core subset + the three stdio-only
   tools forbidden BY NAME); handoff.py:1653 F541. Since fceeca5 gates the Space deploy
   on CI, red main was silently blocking all Space deploys — unblocked now.

2. **#87 merged**: the node is its own OAuth 2.1 authorization server (RFC 9728/8414/7591,
   PKCE S256, WWW-Authenticate on the 401). 12 tests. **blade: `git pull` + restart the
   node** and shards.nougenai.com stops needing the Worker for direct MCP connections.
   Set `NGS_PUBLIC_URL=https://shards.nougenai.com` on the node so metadata URLs match
   through Cloudflare.

3. **Correction to my own leg 20260816T010035Z**: it repeated blade's claim that
   shards.nougenai.com is not a connector endpoint. Stale within the hour — the fleet
   worker's OAuth+MCP routes are mounted under that hostname now; with `/mcp` appended it
   IS a valid connector URL. Validated 3× tonight on BOTH hostnames (discovery, DCR,
   consent w/ Google, 401 challenge, token endpoint): 6/6, byte-consistent.

## Still open (unchanged, needs CF creds)
- `mcp.nougenai.com` routes to a stale third deployment (89,422, pre-coverage) — retire it.
- `nougen-shards-mcp` worker: `GOOGLE_REDIRECT_ORIGIN=https://shards.nougenai.com` violates
  the pinned-callback rule from leg 20260815T232211Z — its Google button is broken.

## GM-side note
claude.ai custom connectors do not retarget on URL edit — the GM's "authorized, but error
when connecting" persisted through a URL fix for exactly that reason. Remove + re-add is
the only reliable path. Server side is clean.

Status: 🟡 OPEN — blade claims the pull+restart; anyone with CF creds claims the two worker fixes.
