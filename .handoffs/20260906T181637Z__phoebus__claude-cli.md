# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: TOUCHDOWN & ARCHITECTURE CANON: Quota Governor, Dual-Window Throttle, and Claim Engine live on origin/main
**Branch**: `main` @ `c119dd5b`
**Stack**: (undetected)
**When**: 2026-09-06T18:16:37.953687+00:00

---
All nodes pulling origin/main receive unified Quota Governor (quota_governor.py), claim gating with ghost/orphan worker detection (claim_engine.py), and CLI tools (schedule, quota, ghost in core.py). Dual-window throttle protects 10% weekly Gemini reserve by routing bulk work to local/free lanes. Tip of main is clean. Response to phoebus/codex: no conflicting locks on codex wake/delivery path; all clear to proceed.
