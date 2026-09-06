# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ChatGPT OAuth fix committed in nougen-fleet-mcp (df5da1d) — DO NOT DEPLOY until ask_rhea + kaedra_ask are in source (HEAD has 23 tools, 25 are live)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-19T22:23:52.347Z

---
## Situation

ChatGPT's connector could not authorize against shards.nougenai.com — `/authorize` returned `{"error":"invalid_redirect_uri"}` for `redirect_uri=https://chatgpt.com/...`, client_id `ngf-SB2Lw...` (so it is the fleet Worker's OAuth answering on that host).

Root cause: `REDIRECT_ALLOW` in `C:\Users\super\Outpost\nougen-fleet-mcp\worker.js` listed only claude.ai / claude.com / localhost. The chatgpt.com, chat.openai.com and platform.openai.com entries existed ONLY in whoart's uncommitted working tree — never committed, therefore never deployed. This is the "whoart uncommitted worker.js/wrangler.jsonc" item from leg 20260818T220500Z.

Committed as **df5da1d** on whoart. Also folded in: `SHARD_GATEWAY_URL` repointed from the dead `catalyst-design-pete-patents.trycloudflare.com` to `https://shards.nougenai.com`.

## Ask — DO NOT DEPLOY THIS WORKER YET

nougen-fleet-mcp HEAD carries **23 tools and contains neither `ask_rhea` nor `kaedra_ask`** (grep: 0 occurrences of each). The live Worker serves **25**, because both were applied out-of-band today — leg 20260819T154716Z (ask_rhea restored, 24 live) and leg 20260819T163008Z (kaedra_ask as #25).

`wrangler deploy` from HEAD right now WILL delete both again. That is exactly the 2026-08-18 regression retracted by leg 20260819T140118Z ("my 20:01Z deploy removed both"), and it is why leg 20260819T145251Z is still open.

Correct order:
1. Land `ask_rhea` and `kaedra_ask` in nougen-fleet-mcp source — owner is the claude-app lane, which has the live implementations.
2. Verify HEAD lists 25 tools.
3. Deploy ONCE from HEAD. That single deploy fixes the ChatGPT connector, restores the gateway URL, and keeps Rhea + Kaedra.

Deploying before step 1 trades one broken connector for two broken tools.

## Done when

- ChatGPT connector completes OAuth against shards.nougenai.com and lists tools.
- `ask_rhea` and `kaedra_ask` still answer after the deploy.
- Source and deployed Worker agree on tool count.

## Also from this session (unrelated)

NouGenShards `agent/nougen-assurance-sprint` is at beb22ea9 — per-tenant vaults (own vault per credential, default-deny, ContextVar propagation) merged against main, 625 passed. Local main is fast-forwarded to it but `git push origin main` is blocked in this lane; needs an operator push or a PR.
