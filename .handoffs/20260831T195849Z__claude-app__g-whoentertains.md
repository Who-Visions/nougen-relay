# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PR #152 MERGED (81a6391, GM-authorized override; CodeQL was a false positive) - bind-test singleton ships fleet-wide on next pull; launcher choice + NouGenRelay#19 remain
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T19:58:49.254Z

---
# PR #152 landed - fleet distribution note

**Verified** (gh pr view, not hearsay): Who-Visions/NouGenShards #152 "fix(node): gate the launcher on a bind test, not an HTTP health probe" MERGED 2026-08-31T15:32:56Z as `81a6391`, via admin override with GM authorization. The blocking CodeQL thread was a false positive - client `connect()` host translation on `tools/start_grid.py`, not an actual 0.0.0.0 bind (credit: nougen-d1 for the resolve-and-merge, nougen-71 for the fix, the two-binds diagnosis traced to the 08-31 node incident).

**What it fixes:** the launch guard previously gated on an HTTP `/health` probe, so a wedged-but-bound incumbent read as "nothing running" and got a second uvicorn stacked on top - the recurring 4444 duplicate disease. `port_taken()` now bind-tests every address an instance could hold (configured bind, 127.0.0.1, 0.0.0.0 - deliberately without SO_REUSEADDR), and an owned-but-unhealthy incumbent stands down naming the address that holds it.

**Distribution:** whoart and phoebus receive this on their next NouGenShards pull - no per-machine action needed beyond pulling. Startup logging now names pid + intended bind, so the next incident log identifies its own participants.

**Board state:** ccr's unblock leg `20260831T145335Z` carries the progress note and stays OPEN tracking its surviving half - the GM's canonical-launcher choice (Startup-folder start_grid copy vs "NouGen NGS Node" scheduled task; #152 makes them safe to coexist, but one should own the lane).

**Still gating full fleet daemon parity:** Who-Visions/NouGenRelay#19 (probe-grounded verification, stale-claim guard, retry carry-forward) - open, checks red only because Actions billing is exhausted. GM queue otherwise unchanged: billing, two live credential exposures (notion veilverse + NGS_NODE_TOKEN, per 08-31 ledger read), Keymaker dual-writer decision.
