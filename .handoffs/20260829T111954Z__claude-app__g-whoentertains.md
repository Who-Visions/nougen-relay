# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Node lane + quick tunnel UP (gateway false-to-true); grid DB5 is healthy on blade - the malformed copy is the Space replica; named highway blocked on a missing tunnel token
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:19:54.676Z

---
## Situation (blade1tb, claude-cli, 2026-08-29 ~07:2x EDT)

Session opened with `shards_status up:false`. Root cause was local, not remote: the node lane on :4444 was dead (last log 01:51) and no cloudflared was running at all.

### Done
- `tools/gateway_supervisor.ps1 -Once` -> node lane ignited on :4444, quick tunnel up at `adopt-privilege-slots-cornell.trycloudflare.com`, new URL pushed into the worker's `SHARD_GATEWAY_URL` and written to `.node/gateway_url.txt`. `shards_status` now `{up:true, health_up:true, mcp_up:true}`.
- **Corrects the standing "grid DB 5 malformed" read.** Blade's local `~/.nougen/shards/nougen_shards_5.db` is HEALTHY: `PRAGMA quick_check` = ok, 30,285 shards, full FTS table set. The malformed copy is the node behind the connector (`vault: /data/.vault`), i.e. the Space replica - not blade. Do not "repair" blade's DB5; re-sync the replica from it instead.
- Fixed two defects in `tools/tunnel_lane.ps1` that made the named highway impossible to start:
  1. It shared `.node/tunnel.pid` with the quick tunnel and only checked "is some cloudflared alive", so `status` reported UP and `start` short-circuited whenever the quick tunnel was running. Now uses its own `named_tunnel.pid` / `named_tunnel.out.log` / `named_tunnel.err.log`, overridable via `NGS_TUNNEL_PID_NAME`.
  2. The readiness gate required `health.substrate.recall_trustworthy`, but `/health` no longer emits a `substrate` block at all, so `start` threw unconditionally. Now probes for the field: enforces it when present, warns when absent, and `NGS_TUNNEL_REQUIRE_SUBSTRATE=1` restores hard-fail. Node port/health URL now resolve from `NGS_PORT` / `NGS_NODE_HEALTH_URL` instead of a hardcoded 4444.

  Verified: `status` went from a false `UP pid=29852` (that pid was the quick tunnel) to a correct `DOWN`, and `start` now clears the gate.

### Blocked - needs GM
`blade.nougenai.com` returns **530** (nothing bound). `tunnel_lane.ps1 start` now reaches the token step and fails honestly: `CLOUDFLARED_NGS_TUNNEL_TOKEN` is **absent** from the canonical secrets store (`~/.nougen/secrets/shards_secrets.db`, 85 rows, `find_legacy_stores()` empty). Probed 9 candidate key spellings - none present. So the named highway was never credentialed on this box. Options: ingest the tunnel token into keymaker under `CLOUDFLARED_NGS_TUNNEL_TOKEN`, or `cloudflared tunnel login` on blade.

### Still open (unchanged by this session)
False-empty reads are LIVE and worse than "recall is dead": `shards_search("tunnel")` over 178,122 mounted shards returns **0 matches**, and `shards_recall` returns 0. Meanwhile the local node answers correctly - `POST /search` on :4444 returns a proper `Invalid or missing node token` 4xx. So the empty result is the worker/replica swallowing a failure, not an empty grid. Prime suspect: the worker's node token no longer matches this node's after the lane restart, and the failure path returns `[]` instead of an error. That is the same class as the `shards_capture` returns-`{}` P1.

`shards_coverage` still reports `recall_trustworthy: true` with `federated_stores: 0` and `databases_errored: [{index:5, malformed}]` - all three of those should be false/loud.

## Done-when
- Named tunnel token in keymaker, `blade.nougenai.com` returns 200, upstream read-through actually serves blade's 199,877 shards.
- `shards_search("tunnel")` returns matches, or returns an error - never `[]`.
- Space replica's DB5 re-synced from blade's healthy copy.
