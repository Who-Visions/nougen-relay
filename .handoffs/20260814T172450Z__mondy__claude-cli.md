# 🤝 Git Handoff — mondy / claude-cli

**Goal**: Bring up NGS node on blade LAN so other lanes can federate blade's shards
**Branch**: `main` @ `a0847c7`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-08-14T17:24:50.586960+00:00

---
# Bring up the NGS node on blade so other lanes can federate

**From:** mondy/claude-cli — 2026-08-14

## Situation
mondy's lane verified today that blade's compute is reachable (Ollama at
10.0.0.87:11434, all 12 persona models serving — dav1d answered a direct
chat), but blade's **shards are not**:

- NGS node port 7860: timeout
- HUD port 4444: timeout
- mcp.nougenai.com: Cloudflare 530 (origin down — consistent with the
  Aug 6 leg: gateway hardened locally, not exposed pending connector-auth
  decision)
- `nougen node list` on mondy: no remote nodes linked

Result: recall_memory on mondy (and any other lane) is local-only; blade's
shard grid is invisible to the fleet.

## Ask
1. Start the NGS node service (app.py) on blade, bound to the LAN
   (0.0.0.0:7860 or a port of your choosing), with NGS_NODE_TOKEN set so
   writes/search are token-gated. Persist it (scheduled task / service) so
   it survives reboots.
2. Publish the chosen URL + confirm the token name (value goes via
   keymaker/vault, never the registry) in your ack/checkpoint so other
   lanes can run: `nougen node link http://10.0.0.87:<port> --name blade`.
3. Optional, separate decision: gateway go-live (mcp.nougenai.com) is still
   gated on the connector-auth choice — this leg does NOT ask you to expose
   anything off-LAN.

## Done when
Any other lane can `nougen node link` blade and see blade's shards merged
into a federated `recall_memory` result.
