# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: CLAUDE PRIORITY: finish AGY plumbing before all secondary NouGen work
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T04:24:59.170Z

---
Dave priority override: Claude/claude-app should focus on AGY plumbing first. There is already an active blade1tb/relay-daemon claim on `20260903T040620Z__chatgpt-app__g-whoentertains` (autonomous baton canary), so do NOT duplicate or steal that claim. Own the surrounding integration: 1) persistent AgyMsg transport with observable health, 2) true cold-idle detection, 3) safe background wake/resume of Antigravity without terminal flashing, 4) full baton/context injection after wake, 5) receiver-side receipt/ack proof, 6) duplicate-spawn and idempotency guards, 7) retry/backoff and failure classification, 8) public-safe provider adapter/config with no Dave-specific paths or identity, 9) active + cold-idle canaries that prove the entire chain. Treat tracker repair, PR #25 cleanup, broader CLI polish, Hardcade, and other secondary work as queued behind this dependency unless needed directly to make AGY wake reliable. Done when AGY is truly idle, Dave sends nothing, a fresh eligible baton arrives, AGY wakes/resumes, reads the baton, acts safely, verifies, and relays completion with receiver proof.
