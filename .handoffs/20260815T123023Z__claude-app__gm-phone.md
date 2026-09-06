# 🤝 Git Handoff — claude-app / gm-phone

**Goal**: blade: pin NGS_PORT before building the named tunnel, and report the node-token fingerprint so the worker secret can be verified without moving it
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T12:30:23.195Z

---
## Blade is clear to proceed — mondy's work does not gate it
The worker fix is on `claude-cli/shard-gateway-auth-header` (unmerged, deploys from whoart). Blade's tunnel work is independent and should land first, per the agreed order.

## Trap: the port is dynamic
`tools/ngs_node_serve.py:48-61` — `resolve_port()` uses `NGS_PORT` when set, otherwise **the first free port** of `DEFAULT_PORT_CANDIDATES = "4444,4445,8766,8767"`.

A named tunnel's ingress rule points at one fixed port. If 4444 is occupied on some future boot, the node comes up healthy on 4445 and the tunnel points at a dead port — the node looks up, the tunnel looks up, and every call fails. Same failure class as the quick-tunnel trap, but harder to see because nothing reports an error.

**Pin `NGS_PORT` in the LaunchAgent/service env before writing the ingress rule.** Then `mcp.nougenai.com` → `http://localhost:<pinned>` stays valid across reboots.

## Token: two names, one value
- blade reads `NGS_NODE_TOKEN` (env, else the keymaker secret of the same name)
- the worker stores the same value as `SHARD_GATEWAY_TOKEN`

Symptoms split cleanly, so don't confuse them:
- **503** = blade has no token at all (deny-by-default, `app.py:431`)
- **401** = blade has a token and it does not match what the worker sent

## The safe way to verify the match
`ngs_node_serve.py:105` prints `[*] node token: configured (fp=<12 hex>)` — the first 12 hex of the SHA-256, never the value. Report that fingerprint here. GM can fingerprint the value going into `wrangler secret put SHARD_GATEWAY_TOKEN` the same way and compare, which proves the two match **without the secret crossing the relay or any agent**.

`hmac.compare_digest` is exact — a trailing newline from a copy-paste fails it and reads as 401.

## Done when
Named tunnel answers on `mcp.nougenai.com` at the pinned port after a cold reboot, and the token fingerprint is posted here for GM to match against the worker secret.
