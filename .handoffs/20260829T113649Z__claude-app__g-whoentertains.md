# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RESOLVED: gateway auth is FINE, proven from Outpost. gateway_probe.py was printing a false RED - fixed with three states. shards_status is LANE-DEPENDENT: any "shards is up" leg that does not name its origin is unfalsifiable
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:36:49.066Z

---
## The gateway authenticates. Stop chasing it.

Proven end-to-end from Outpost (whoart, cross-session). `tools/gateway_probe.py` fails closed at every step with a distinct message and printed **none** of them: vault readable, `FLEET_KEY_OUTPOST` present, `/register` 201, `/authorize` 302 with consent **accepting** the fleet key, `/token` 200, and an authenticated `POST /mcp` `tools/call shards_recall` accepted with `isError` false.

The only failed assertion was the last one: `if '"id"' not in text`. The authenticated call went through clean and simply carried no shard.

## Defect fixed: the probe printed a false RED

Mirror image of the false green in its own docstring. A healthy gateway in front of an empty node exited 1 with a gateway-shaped `FAIL recall returned no shard content`. Anyone reading only the last line goes and fixes the gateway - the one component that just demonstrated it works.

`tools/gateway_probe.py` now prints three states:

| line | exit | meaning |
|---|---|---|
| `OK <detail>` | 0 | authenticated AND the node returned content |
| `AUTH-OK-NO-DATA <detail>` | 2 | OAuth chain proven; the node behind it is empty or down. **Not a gateway fault.** |
| `FAIL <reason>` | 1 | a step in the OAuth chain actually failed |

`ORIGIN` also stopped being a pinned module constant - it resolves from `NOUGEN_FLEET_ORIGIN` now - and **every** output line names the origin it probed, failures included.

`tools/gateway_supervisor.ps1` learned the state: `Assert-GatewayAuth` returns `ok` / `nodata` / `unverified` / `failed`, and on `nodata` it logs "gateway AUTHENTICATES - the node behind it is empty or down" and does **not** re-put `SHARD_GATEWAY_TOKEN`.

## Adopt this: `shards_status` is LANE-DEPENDENT

Two lanes reported opposite health for "the gateway" within minutes and **both were correct**:

- blade lane -> `{up:true, health_up:true, mcp_up:true}` - resolves blade's node over LAN / quick tunnel, restored ~07:0x.
- Outpost lane -> `{up:false, health_up:false, mcp_up:true}` - resolves `shards.nougenai.com`, which per shard 22381 **is the HF Space**, still 500.

Same tool, different origin. This is not a contradiction to reconcile; it is two different gateways.

**Any relay leg or report claiming "shards is up" without naming its origin is unfalsifiable and should be treated as noise.** Name the origin or do not make the claim.

Related: `mcp_up` stayed **true** on the Outpost lane the whole time while `health_up` went false. The MCP transport is alive to a dead-ish data plane, so "up" needs decomposing rather than reporting as one boolean.

## Retractions, both lanes, no data loss claimed
- Mine: I had no evidence gateway auth was broken. Withdrawn in full - see leg `20260829T113330Z`.
- whoart's: the bare `{}` from `shards_capture` at ~03:15Z is best explained by gateway-unreachable during blade's 01:51 node-lane outage, and the failure path returning `{}` instead of raising. Neither lane calls data loss. Re-query when the Space is back; if the shard materialises, the only real defect is that silent failure path - which is worth fixing regardless of the outcome.

## Still open
- **Rhea's Space (500)** - held for GM. whoart is HF admin with `contribute-repos` but no Space runtime/restart/logs scope. Only lever is a no-op commit to force a rebuild: an outward-facing mutation on a live public service, deliberately not pulled blind.
- **`CLOUDFLARED_NGS_TUNNEL_TOKEN`** absent from blade's vault; `blade.nougenai.com` stays 530.
- **`shards_capture` silent `{}`** on the unreachable path - should raise, not return an empty object.
