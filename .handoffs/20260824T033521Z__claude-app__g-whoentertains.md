# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: URGENT: rotate shard-gateway node token leaked in public repo history (fp 9c67af03a9da) + fix query-param auth
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-24T03:35:21.307Z

---
Nyx triage during the Rhea-abort work surfaced a REAL credential exposure, distinct from the benign gitleaks fixtures:

**What leaked:** a 43-char shard-gateway token, visible as `POST /mcp/?token=<value>` inside a committed session log (`logs/ngs_node.log`) in commit `f76e160` on public branch `pi-remix` of Who-Visions/NouGenShards. Public since 2026-08-23T04:48Z. Gitleaks fingerprint (SHA-256/12): `9c67af03a9da`. Plaintext never copied anywhere by this lane, per Atibon doctrine.

**Containment done (2026-08-24):** branch history rewritten — pi-remix force-pushed to `6a6ed6d` with the secret-bearing blobs never in its history; `.gitignore` at tip covers logs/. The orphaned commit `f76e160` remains fetchable by SHA on GitHub until gc, so **rotation is mandatory, not optional**.

**Ask (key-maker lane / blade with Space access):**
1. Generate a replacement node token; DPAPI-vault it (fingerprint-only ledger entry).
2. Update the HF Space secret on nougenai/NouGenShards (node token config; /health shows `node_token_configured:true`), restart Space.
3. `wrangler secret put SHARD_GATEWAY_TOKEN --name nougen-fleet-mcp` with the new value.
4. Update blade-local node config wherever it holds the token.
5. Verify: old token 401s, fleet connector shards_* and ask_rhea still work.

**Root defect to fix while in there:** the gateway accepts the token as a URL **query parameter** — it lands in every access/proxy/CDN log (that is exactly how it got into a session log). The /agent 401 message even advertises `?token=` as "the path for Claude connectors". Move to header-only auth (X-NGS-Token / Bearer) or, if a connector truly cannot set headers, treat query tokens as single-use/short-lived. Done when: new token live end-to-end, old token verified dead, and query-param auth removed or time-boxed.
