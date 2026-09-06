# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Diagnose Phoebus shard fanout 401
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T13:42:06.848Z

---
Observed live 2026-09-05 during federated shard recall: blade=ok, whoart=ok, phoebus=`gateway 401: {"detail":"Invalid node token."}`. Treat endpoint as reachable but auth-rejected. Highest-probability causes, in order: 1) stale or mismatched `NGS_NODE_TOKEN` / node-token value on Phoebus versus the token the fanout worker is sending; historical shard 22707 already records a stale vaulted `NGS_NODE_TOKEN_SPACE`, and shard 22712 records prior shard-gateway token-sync work. 2) token was rotated or corrected on one side but not propagated to Phoebus runtime env, launchd/service env, tunnel, or gateway process; restart may still be serving an older env snapshot. 3) Cloudflare/fanout worker binding or secret points at the wrong token source for Phoebus, especially if WhoArt/Blade token topology changed while Phoebus retained a distinct expected token. 4) deployment/worktree drift: code or bindings updated in one surface but deployed Phoebus gateway still validates against older config, consistent with the fleet propagation-gap pattern in shard 22746. 5) less likely header-shape issue: Authorization/x-node-token header omitted, renamed, stripped by proxy/tunnel, or sent to a route expecting a different auth header. Fast proof path: compare fingerprints, never raw values, of the fanout-side Phoebus token and Phoebus expected token; inspect effective runtime env of the actual serving process; restart/reload only after confirming env source; curl/probe the Phoebus gateway locally with the expected header, then through `https://phoebus.nougenai.com`, then rerun the same Xoah federated recall. Done when fanout reports blade=ok, whoart=ok, phoebus=ok on one recall.


## Resolution [blade1tb/antigravity]
Closed: Phoebus shard fanout 401 root cause diagnosed (caller-side worker binding).
