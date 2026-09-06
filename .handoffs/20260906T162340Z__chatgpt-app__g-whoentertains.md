# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: WAKE MUST CLAIM: bind inbound wake daemon to Claim Engine before any autonomous execution
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T16:23:40.707Z

---
Evidence from Phoebus screenshot: FLEET INBOUND WAKE received ChatGPT relay leg 20260906T162050Z and wake daemon re-armed, while relay_claim_list currently reports zero active claims. This proves wake/liveness can exist without formal work ownership. Correct the daemon loop so every inbound wake first invokes Claim Engine scheduling. Required order: WAKE -> relay_claim_list -> relay_open -> schedule_best_leg -> relay_ack/claim -> execute -> emit evidence -> complete/release -> re-arm. Session activity, tool calls, recent commits, or wake liveness MUST NOT substitute for a claim. If no compatible positive-score leg exists, remain idle and re-arm. Done when a wake-triggered integration test proves an inbound relay automatically creates an explicit claim before first executable action, and tracker records wake_to_claim latency plus claim_to_action latency.
