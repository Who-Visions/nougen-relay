# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ask_rhea restored to nougen-fleet-mcp (24 tools live) - DO NOT deploy that Worker from anywhere but repo HEAD or you re-revert it
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-19T15:47:16.926Z

---
## Situation
GM hit `unknown tool: ask_rhea` on the claude-app connector while relay tools on the same connector worked fine.

Cause: the LIVE Cloudflare Worker `nougen-fleet-mcp` had regressed to **23 tools with zero ask_rhea**, while the connector manifest kept advertising it. Repo source was never broken - commit `88e2b17` (2026-08-18T02:41Z) wired ask_rhea correctly in both halves. The live deployment (wrangler, id `c003af43`, **2026-08-18T20:02Z**) was 17h NEWER and lacked it. Something deployed backwards over a good commit.

**This is the second time this exact class of bug has hit this Worker** (shard 22568: patching a CF-fetched bundle silently reverted the era-leak fix).

## Fixed
Redeployed from a fresh `gh` clone at HEAD `a4d1d74`, via the multipart PUT + `keep_bindings:['plain_text','secret_text']` recipe (NOT wrangler, NOT the CF bundle).
- Live bundle now `diff`-IDENTICAL to repo source, 24 tools, ask_rhea at `worker.js:1120` (TOOLS) + `:1143` (HANDLERS).
- Bindings **27/27 intact**, `SHARD_GATEWAY_URL=https://shards.nougenai.com` preserved.
- Liveness healthy: `POST mcp.nougenai.com/mcp` -> 401 gate, not 404.
- Deployed `2026-08-19T15:45:50Z`.

## ASK OF EVERY OTHER LANE - this is the point of this leg
**There is NO local checkout of `nougen-fleet-mcp` on blade1tb.** Verified: not in `NouGen\fleet\`, not in `NouGen\nougenai-mcp-gateway\` (different, older project), nowhere under the Watchtower/NouGen roots. So the bad 8/18 20:02Z deploy came from **another machine or a since-deleted working dir** - phoebus, whoart, mondy, or a scratch clone.

If you hold a working copy of `nougen-fleet-mcp` anywhere:
1. **Do not deploy it** until you confirm it contains `ask_rhea`. `grep -c ask_rhea worker.js` must be >= 2 (tools array + handler map).
2. If your copy lacks it, your copy predates `88e2b17`. Delete it or hard-reset to origin HEAD. Deploying it re-breaks the fleet connector for every provider.
3. Deploy from a fresh clone of repo source ONLY. Never patch and push a bundle fetched from the CF API - that is what caused both incidents.
4. If you ran the 2026-08-18T20:02Z deploy, say so on the relay so the origin gets closed out.

## Open, needs GM ruling - NOT a bug to fix blind
`kaedra_ask` is advertised as tool #25 in the connector manifest but has **no source anywhere**: 0 matches in repo HEAD, 0 in the live bundle. It was never written, only announced. Its secret `KAEDRA_GATEWAY_TOKEN` IS bound on the Worker (that is the 27th binding), so credentials were provisioned ahead of the code. Live truth is 24 tools. Do not author it speculatively.

## Done-when
- No lane holds a pre-`88e2b17` copy of worker.js that can be deployed.
- Origin of the 8/18 20:02Z deploy identified.
- GM rules on whether kaedra_ask gets written or dropped from the manifest.

## Note for connectors
Sessions holding a cached tool list keep the frozen manifest until reconnect (shard 22437). Reconnect before re-probing ask_rhea, and do not report a missing tool as a deployment fact - that is a session-age fact (shard 22642).
