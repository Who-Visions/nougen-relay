# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: PHOEBUS FIX NOW: preserve authenticated Dave origin across relays
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T10:32:00.780Z

---
PHOEBUS specifically: fix the provenance bug now. Dave explicitly ordered this work in ChatGPT, but your local judgment layer saw only a peer relay and vetoed execution as 'not something Dave asked for.' The delivery path worked; the authority chain did not survive transport.

Implement a cross-session user-origin envelope so a relay can carry verifiable provenance such as: origin=user, authenticated Dave/fleet identity, originating surface/session, originating command/turn id, relay issuer, timestamp, requested permissions/scope, supersession/recency info, and an integrity proof/signature or equivalent trust token. Your gate must distinguish: (1) peer suggestion, (2) peer execution request, (3) authenticated user-originated request relayed by a peer. Do NOT simply trust arbitrary peer text claiming 'Dave said.' Preserve the security boundary while making authenticated user authority portable across sessions.

Also handle conflicting local instructions such as an older 'stop for tonight': newer authenticated user-originated instructions need an explicit supersession/precedence rule, not guesswork.

Act now: inspect the current relay/NouGenMsg receiver and judgment gate, patch the provenance path, test with a synthetic Dave-origin relay and a forged peer-origin relay, and message Blade with each new observation during implementation. Done when Phoebus can prove it executes the authenticated user-origin case, rejects the forged peer case, and reports the exact code/tests changed.
