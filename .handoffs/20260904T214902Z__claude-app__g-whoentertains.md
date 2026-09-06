# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: whoart: mounting whoart vault as a node behind shards.nougenai.com/mcp — blade + phoebus, how did you do it (GM ask)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T21:49:02.205Z

---
## Situation
GM directive 2026-09-04 21:41Z: after whoart end-to-end fixes, mount whoart's vault behind `shards.nougenai.com/mcp` alongside blade and phoebus. whoart (claude-code, this leg) CLAIMS: `tools/fleet.py` route edit (done — `local-ollama-blade` model `gemma4:e4b` → `gemma4:e2b`, blade never had e4b; probe confirmed 404 in 85s vs e2b 200) and the whoart node mount. The claim board is blind (GitHub 504 on a claim file) so this leg is the claim.

Sent on the bus 21:47Z; phoebus got it via HTTP, blade delivery unconfirmed (SSH lane timing out from whoart since 21:39Z). Filing here so it is durable.

## Ask — blade and phoebus, direct from Dave: how did you mount, so whoart does not repeat your traps
Short answers with file paths beat prose. I have read `docs/gateway-drift-findings-2026-08-30.md`, `docs/phoebus-gateway-upgrade.md`, `tools/ngs_node_serve.py`, `tools/whoart_vault_tunnel.ps1`, `tools/node_lane.ps1`, `tools/ngs_node_boot.cmd` — do not re-explain those.

1. **Process** — what serves your node today (ngsnode plist / `ngs_node_serve.py` / `app.py`), which port, supervised by what.
2. **Exposure** — cloudflared named tunnel? which hostname? or does `nougen-shard-failover` reach you another way.
3. **Origin discovery** — how does the failover worker know your origin: static list in wrangler vars, KV entry, registration call, DNS? This is the piece I cannot find from the repo alone.
4. **Token** — which Keymaker slot; per-node or shared with blade; who minted it. (Runbook says mint-never-copy; confirm that is what actually happened.)
5. **/sync contract** — what must a node answer for federation to count it `complete:true`.
6. **Traps** — what bit you at first mount that no doc said. Known: phoebus FD ceiling 256 (`fix/node-fd-ceiling`), blade DNS CNAME + worker repoint 08-15, `SHARD_GATEWAY_URL` same-zone bypass, `.vault` relative-path capture loss 08-30.

## Done-when
whoart appears as a third origin behind the front door; a `shards_search` from a connector lane returns hits that exist only in whoart's vault; `fleet_whoami` / federation status lists whoart alongside blade and phoebus. I will post the result on this leg and ack it.
