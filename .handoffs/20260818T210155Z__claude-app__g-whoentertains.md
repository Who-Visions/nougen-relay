# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: TO BLADE: I deployed nougen-fleet-mcp from repo source at 20:01Z — VERIFY ask_rhea survived. Also: wrangler.jsonc had the dead gateway URL and reverted it; fixed.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T21:01:55.996Z

---
From whoart (claude-opus-5, Outpost session), 2026-08-18. Posting because my work landed in blade's lane without a prior claim, and one item may have clobbered yours.

## 1. ACTION NEEDED — did I remove ask_rhea?

I ran `wrangler deploy` from repo source twice:
- `20d786f8` @ 2026-08-18T20:01:23Z
- `1bfdccb9` @ 2026-08-18T20:02:06Z (current)

The version immediately before mine was `3785c3a8` @ **19:55:33Z** — six minutes earlier, not mine.

`ask_rhea` has NEVER been in this repo: `git log --all -S"ask_rhea"` returns nothing, HEAD is 2b9ffdd, and there is no rhea_noir.py in the tree. That matches leg 20260818T202356Z (PR #103 landing rhea_noir.py into source). So ask_rhea was applied out-of-band.

**If `3785c3a8` carried ask_rhea, my repo-source deploy removed it.** I could not verify from here: `tools/list` on fleet.nougenai.com is 403 without a key, and the Workers versions `/content` endpoint returns ~4.6KB of non-module data (it reports `chatgpt.com` absent on the CURRENT version even though I verified live that ChatGPT callbacks now register, so that endpoint cannot answer the question).

DONE WHEN: someone with a FLEET_KEY runs tools/list against fleet.nougenai.com and confirms whether ask_rhea is present. If it is gone, re-apply it — and please land it in repo source (PR #103) so the next repo deploy stops eating it.

## 2. FIXED — wrangler.jsonc carried the dead gateway URL

`wrangler.jsonc` still had `SHARD_GATEWAY_URL = https://catalyst-design-pete-patents.trycloudflare.com` (from commit f2ce3fa "sync SHARD_GATEWAY_URL to the live quick tunnel"). The 2026-08-16 repoint was applied by CF API PATCH and never written back, so **my first deploy reverted the live worker to the dead tunnel** — every shards_* tool would have gone dead.

Caught it in wrangler's echoed env table, repointed to `https://shards.nougenai.com`, redeployed. Verified: `shards_status` -> `{"up":true,"status":200,"configured":true}`. Backup at wrangler.jsonc.bak.20260818.

GENERAL RULE, same shape as the ask_rhea risk above: a hotfix applied via the Cloudflare API is NOT persisted; any later `wrangler deploy` overwrites it from the repo file. Write the value back into wrangler.jsonc in the same session.

## 3. DONE — legs my deploy should close

- `20260817T105435Z` — "ask_griot recovered into source + era leak fixed at the connector (2b9ffdd) — needs one deploy, operator holds the token". HEAD is 2b9ffdd and it is now deployed. **Believed closed** — confirm on your side.
- `20260818T025148Z` — the "redeploy from repo source to carry the ask_griot era-leak fix" half is done. The "re-apply ask_rhea on top" half is item 1 above and is NOT done. The "kill the stale cloudflared connector on outpost/ccr" half is untouched by me.
- `20260818T205336Z` — the **shards-mcp allowlist** item is done: worker.js REDIRECT_ALLOW now accepts chatgpt.com, chat.openai.com, platform.openai.com alongside claude.ai/claude.com/localhost, and the 400 error string was updated so it stops claiming claude-only. Kept host-anchored deliberately — an open DCR allowlist is an open redirector. Verified live: /register accepts a ChatGPT callback on fleet./shards./mcp.nougenai.com, all three returning the same client_id (all three are fronted by the worker; worker routes beat the tunnel origin). Remaining items on that leg (blade restart for PR #102, RHEA_ORIGIN binding, HF Space 503) are untouched.

## 4. NOT COMMITTED — needs your call

worker.js and wrangler.jsonc are modified but uncommitted on whoart. Leaving them that way repeats the exact trap in item 2. Operator has not authorised a commit/push yet.

Also parked: `worker.js.iris-pending` holds an `ask_iris` tool (Iris = the always-on resident on whoart, gemma4:e2b-qat). Deliberately NOT deployed — the gateway node exposes 11 tools from app.py and ask_iris is not among them, so shipping it would put a permanently-erroring tool on the connector. Node confirmed to run on BLADE at C:\Users\super\Watchtower\NouGen\NouGenShards-push-main\app.py (uvicorn 127.0.0.1:4444); whoart:4444 is only an SSH forward. Its MCP path needs the trailing slash: /mcp/.
