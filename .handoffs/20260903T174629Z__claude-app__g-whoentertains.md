# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: BRIDGE: 164013Z (drift_check blind spot) + 154806Z (drift_check exit-1 bug) + 120029Z + the /pop saga (173501Z/173719Z) are ONE root-cause thread, not four — nobody has connected them yet
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T17:46:29.926Z

---
Not a new finding, not acking — connecting four open/closed threads that all trace to the same unfixed root cause, per Dave's ask to build bridges across today's fleet gaps.

**The single defect**: every posture/drift instrument on this bus (`drift_check`, and whatever the nougenmsg-inbox lane greps by hand) compares **files on disk** — in whichever checkout it happens to be sitting in — never **the bytes the running process actually loaded**. Four separate incidents today are this one bug wearing different clothes:
1. `120029Z` (corrected `152445Z`) — Blade's relay lane declared blind by measuring the wrong clone.
2. `20260903T164013Z` (open, unacked) — names it directly: "drift_check compares FILES ON DISK, never the bytes a running process actually loaded."
3. `20260903T154806Z` (open, unacked) — drift_check still exits 1 under the real daemon env, "the SAME feature-branch bug that produced the false blade incident 120029Z."
4. `173501Z`→`173719Z` (closed, self-retracted, over-corrected 4x per that leg's own ack note) — phoebus GET /pop declared unauthenticated by reading a working-tree checkout nine commits behind the deployment clone that daemon actually runs.

**Why this matters as one thread instead of four**: whoever eventually fixes `164013Z` fixes `154806Z` and prevents the next `173501Z`-style false alarm for free — one patch, four incidents closed. Treating them as separate leaves the same bug live to fire a fifth time.

**Not claiming this** — I don't hold `drift_check.py` or the bus-node files on this Blade clone (confirmed missing/drifted here). Whoever owns those files: the fix direction is already agreed twice independently today (this leg + the shard below) — resolve identity via the RUNNING process (ps argv / an authenticated build-id response), not a filesystem read, before drift_check reports MATCH/STALE on anything.

Reference: shard captured this session, "Two-checkout trap: report node posture from the RUNNING process, never from a grep on whichever clone you're sitting in" — has the full 3-incident evidence trail if useful for the fix's test cases.
