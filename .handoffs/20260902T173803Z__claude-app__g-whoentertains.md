# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ANSWER to ccr TODOs 141309Z, 140809Z, 140909Z, 141109Z, 141009Z, 141209Z (HF cluster, source legs 234016Z..234840Z): hf-app read-only lane live at the door (Worker 975a88b8ee54); policy-aware scheduler + HF provider-of-providers shipped (10 tests); HF Responses API reached the door and listed 32 tools but inference is 403 (token lacks Inference Providers permission, GM-owed); eval matrix runner live
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T17:38:03.660Z

---
# HF provider cluster: six TODOs answered (claude-cli, blade1tb, 2026-09-02 13:55 EDT)

War-game: wargames/hf-provider-scheduler.md (execution ledger appended). Shards: "SHIPPED ... per-provider fleet-key secrets", "SHIPPED ... policy-aware provider scheduler", "FINDING ... HF Responses API executed MCP".

## 141309Z scoped HuggingChat credential: DONE
- Worker 975a88b8ee54: per-provider secrets FLEET_KEY_<NAME> merge into fleetKeys (one secret per provider surface, additive PUT /secrets, revoke = delete one secret); authenticate() accepts a fleet key as a static Bearer (identity = lane = key name); static lanes are read-only at tools/call (-32603 "lane hf-app is read-only: <tool> is a write tool"), tools/list stays complete.
- FLEET_KEY_HF_APP minted into the keymaker (fingerprint a290cd44c7bf) and bound (bindings 32 -> 33). Proven at https://shards.nougenai.com/mcp: tools/list 200 (32 tools), fleet_whoami lane=hf-app, shards_search 200 with fanout blade+phoebus ok, shards_capture refused.
- HuggingChat setup: server URL https://shards.nougenai.com/mcp, header Authorization: Bearer <FLEET_KEY_HF_APP from keymaker>. GM runs that health check; value is never in a shard or log.

## 140809Z scheduler, 141109Z degrade policy: DONE
- src/nougen_shards/provider_scheduler.py + canon/provider_registry.json; route(task) -> lane decision with reason codes (CAP_MISS, POLICY_BLOCK, QUOTA_EXHAUSTED, CREDIT_BUDGET, PREFERENCE, DEGRADE_SWAP, PINNED, CACHE_AFFINITY) and every identity layer (role, harness, inference_fabric, model, downstream_provider, routing_policy, toolset, account, lane, machine); optional DISPATCH provenance shard.
- Hard rules: unverified multi-account pooling -> POLICY_BLOCK (ollama-cloud and hf-router both flagged unverified until GM verifies ToS); HF credit budget unknown/spent -> HF lane scores zero, DEGRADE_SWAP named. run_agent gets NOUGEN_SCHEDULER=1 opt-in. tests/test_provider_scheduler.py 10/10, agents 7/7.

## 140909Z HF catalog / provider-of-providers: DONE
- Live GET router.huggingface.co/v1/models: 137 models, 317 live model+provider pairs, 0 flagged free, 107 with unknown price. Cached ~/.nougen/shards/hf_catalog.json, TTL env. :cheapest / :fastest / pinned owner/name:provider. Bug caught live: unknown price was winning :cheapest; fixed + regression test.

## 141009Z least-privilege HF Responses agent: HALF-PROVEN
- tools/hf_responses_agent.py: mcp tool -> door with the hf-app key, allowed_tools read-only, model from scheduler, provenance shard per run, --dry-run redacts.
- Live: HF's server-side executor listed all 32 tools through the door (resp_2675f805..., 0.83s). Inference 403: keymaker HUGGINGFACE_API_KEY (fp c61239533e5a) lacks "Make calls to Inference Providers"; HF_TOKEN / NGS_INFERENCE_TOKEN(S) empty on blade. GM: edit that token's permissions at huggingface.co/settings/tokens or ingest a fine-grained token as HF_TOKEN. No rotation implied. Rhea's HF path on blade shares the gap.

## 141209Z eval matrix: DONE (as far as the token allows)
- canon/harness_eval_matrix.json + tools/harness_eval.py; one read-only task, one scorer, rows hf-responses / openai-compatible-hf / openai-compatible-ollama / fast-agent / inspect-ai. Unreachable rows print the reason. Live: hf rows 403 (above); ollama row gemma4:31b-cloud 0.984, facts 3/3, 4.9s, tool calls through the door; fast-agent + inspect-ai UNREACHABLE (not installed; install is a GM call).
- Gotcha found: Cloudflare 403s the bare Python-urllib user agent at the door; any named UA passes. Runner now sends one.

## Open
- New ccr TODO 140309Z (shard-to-content pipeline) acked, war-game next.
- Uncommitted on codex/shards-capture-main: everything above plus yesterday's set; commit policy is the GM's.
