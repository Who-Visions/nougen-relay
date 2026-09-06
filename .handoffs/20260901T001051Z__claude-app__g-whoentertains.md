# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: relay_open truncation FIXED and deployed — fleet can see real open-leg state again
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T00:10:51.685Z

---
## 🔴 Active Incidents
- **relay_open truncation is FIXED.** Root cause: nougen-fleet-mcp's listLegs() had a bare `catch (_) {}` around its trees-API call that silently fell back to the 1000-entry-capped contents API on ANY failure — no logging. `.handoffs` has 1540 flat entries (767 json + 773 md), well over that cap, so the fallback (when it silently triggered) always surfaced ~08-29-era legs as "newest." The repo/GitHub API itself was never the problem — confirmed truncated:false with correct data using an independent token.
- Fix (deployed, version 688a43b6): replaced the whole-repo recursive tree walk with two non-recursive calls (root tree → `.handoffs`' own tree object directly) — smaller, cheaper, avoids whatever was tripping the old path — plus error logging on every failure branch so a recurrence is visible in `wrangler tail` instead of vanishing silently again. Verified live: relay_open now returns today's actual newest legs (23:59Z down through 15:53Z), including several of mine that had been invisible for ~5 hours despite landing successfully.
- **New P1 now visible** (was hidden by the truncation bug): `20260831T235318Z__ccr__gm-phone` — "Space sqlite grid keeps corrupting under write load — GM decision needed on thin gateway vs snapshot artifacts." Flagging to Dave, not investigating myself yet.

## 🟡 Ongoing Investigations
- Full open-leg backlog is now actually visible (25+ shown, was capped at 15 stale ones) — worth someone doing a real triage pass now that reads are trustworthy again.

## 📋 Recent Changes
- See shard: "relay_open truncation FIXED — root cause was a silently-swallowed error in the trees-API path, not the trees API itself" for full technical detail.

## ⚠️ Known Issues & Workarounds
- Doctrine reinforced: a silent fallback to a known-bad path is worse than no fallback — always log the trigger, not just the existence of the fallback.

## 📅 Upcoming Events
- None.
