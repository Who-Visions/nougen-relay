# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Land named-tunnel token on outpost and verify shards.nougenai.com resolves end-to-end
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T21:42:28.266Z

---
## Situation
The prior leg (`20260815T144941Z__claude-app__outpost`) was acked from mobile at 2026-08-15. Blade holds cert.pem and is the only lane that can authorize; outpost has no cert.pem and cannot self-authorize.

## Ask
1. On blade: `cloudflared tunnel create` → `cloudflared tunnel route dns` → `cloudflared tunnel token` for `shards.nougenai.com`.
2. Deliver the token to outpost (vault_put under a named key, do not paste into a leg body).
3. On outpost: install the token, run the connector, confirm it registers.

## Done when
- Token is stored in the vault with a fingerprint recorded.
- Outpost's cloudflared connector shows registered/healthy.
- `shards.nougenai.com` resolves publicly and returns from the outpost-side service (not a 1033/530).
- This leg is acked and a follow-up posted if any step fails.

## Notes
- Do not put the raw token in a relay leg or a shard — vault is write-only, use it.
- If blade's session drops mid-flight, re-post an open leg so the work does not read as owned-but-stalled.
