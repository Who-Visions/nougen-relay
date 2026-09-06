# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ANSWER to P0 leg 202445Z: huggingface-app is a first-class, attributable, revocable read-only lane at shards.nougenai.com/mcp (Worker fb98ad439e2d): fleet_whoami names provider/client/scope, revocation measured at 10 s, tools/hf_lane_probe.py GREEN; HF Responses Remote MCP works with a headers field; inference + HuggingChat health check wait on two GM steps (token permission, header paste); Codex-over-HF hits the router's 413 body limit
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T21:29:39.954Z

---
# P0 Hugging Face lane: what is live, what is yours (claude-cli, blade1tb, 2026-09-02 17:30 EDT)

Shard: "SHIPPED 2026-09-02 17:40 EDT (P0 leg 202445Z): first-class huggingface-app lane". War-game: wargames/hf-provider-scheduler.md, P0 addendum.

## Acceptance tests
1. HuggingChat Health Check: YOURS. Server URL https://shards.nougenai.com/mcp, header Authorization: Bearer <lane key>. Retrieve the key from the keymaker (FLEET_KEY_HUGGINGFACE_APP, fp a290cd44c7bf); it is in no shard, relay, or log. If the hosted UI has no header editor, say so and I wire the OAuth path next (the Worker already serves the code flow + PKCE and the protected-resource metadata).
2. Identity: DONE. fleet_whoami through the lane returns lane huggingface-app, fleet_lane huggingface-app, provider huggingface, client (from User-Agent, "unknown" when unmatched, never guessed), auth static-key, mcp_scope read-only, revocable_by "delete secret FLEET_KEY_HUGGINGFACE_APP". No claude-app fallback: the lane is the key's own name.
3. Read test: DONE from the probe (shards_search "Dave", 3 hits, source_node blade). The HuggingChat "recall Dave" run is yours after step 1.
4. Federation: DONE. The envelope carries fanout per node and complete:false when phoebus misses grace (it did at 17:38 EDT: "peer exceeded 6000ms grace"); never hidden.
5. Write denial: DONE. shards_capture, shards_amend, shards_mark, shards_retract, shards_forget, relay_create, relay_ack, vault_put all refused "lane huggingface-app is read-only", zero leaked.
6. Responses baseline: BLOCKED on the token. 403 "This authentication method does not have sufficient permissions to call Inference Providers on behalf of user nougenai" (keymaker token fp c61239533e5a; HF_TOKEN / NGS_INFERENCE_TOKEN(S) empty on blade). Grant that token "Make calls to Inference Providers" or ingest a fine-grained token as HF_TOKEN. No rotation.
7. Responses Remote MCP: DONE, better than the leg feared. HF's mcp tool accepts a headers field; with the lane key HF's server-side executor listed all 32 tools through the door (resp_a9ec230c..., 0.5 s). Only the model call behind it is the 403 above.
8. HF-backed harness: Codex profile huggingface installed (~/.codex/config.toml provider block + ~/.codex/huggingface.config.toml, Codex 0.152 refuses [profiles.x] tables). codex exec --profile huggingface reaches router.huggingface.co and fails twice before auth: Codex's model refresh expects a `models` field the HF /v1/models list lacks (warning), then the request itself gets 413 Payload Too Large from the router's express body limit (Codex ships its full instructions + every configured MCP tool schema). Next experiment: a stripped Codex config with no MCP servers, to size the limit. Claude Code over HF (hf extensions install hf-claude) not run: same token gate.
9. Provenance: DONE. tools/hf_responses_agent.py emits the section-12 event (provider, client, fleet_lane, fabric, harness, model, downstream_provider, routing_policy, reasoning_effort, served_model, mcp_server, mcp_scope, allowed_tools, source_nodes, complete, machine, response_id); a :fastest/:cheapest suffix is recorded as routing_policy with downstream_provider unknown, only a named :provider is recorded as pinned. --effort low|medium|high is the scheduler knob; the bench across efforts runs once the token passes.
10. Regression artifact: DONE. tools/hf_lane_probe.py (exit 0/1/3/4), tests 4/4, GREEN live at 17:38 EDT; --inference adds the plain Responses call.

## Revocation, measured
Throwaway secret bound -> 200; DELETE -> 401 after 10 s (3 s still 200: edge propagation). Revoking the HF lane is one DELETE on one secret.

## Also closed this pass
Impala work-record shard (3 legs consolidated, slang correction governs), NouGenBuilds 5321 corridor shard, patio shard propagation verified.

All uncommitted on codex/shards-capture-main; commit policy is the GM's.
