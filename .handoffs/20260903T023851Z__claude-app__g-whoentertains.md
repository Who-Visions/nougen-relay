# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Leg 015748Z Phase B DONE (NouGenRelay-main, branch claude/daemon-hardening): fencing token + heartbeat + sweeper + history in core.py leases, admit() before acquisition in guard.py, daemon wired; 83 tests. Relay-live daemon shielded after a Ctrl+C death
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T02:38:51.457Z

---
## Phase B shipped (NouGenRelay-main, branch claude/daemon-hardening, GM go at 02:14Z)
Elevated the existing lease store (.relay/leases), no new subsystem.
- core.py: acquire_lease issues lease_id, monotonic fencing_token per leg (increments across expiry reclaim and force; prior tokens never reused), heartbeat_utc + heartbeat_count, attempt_count, state (LEASED/RUNNING/RETRY_WAIT/DEAD_LETTER/COMPLETE/RELEASED/CLAIMABLE), history[] {utc, actor, from, to, evidence} capped by NOUGEN_LEASE_HISTORY_MAX (50). lease_is_active ages against the newest heartbeat.
- fencing: release_lease(fencing_token=), record_leg_failure(fencing_token=), heartbeat_lease() reject a stale token, append to rejected[], and leave the record untouched. Legacy callers with no token still work.
- heartbeat_interval_seconds = TTL / NOUGEN_LEASE_HEARTBEAT_DIVISOR (3). sweep_expired_leases marks expired active leases CLAIMABLE with "sweeper: expired after N min" evidence (idempotent). lease_metrics = live index: by_state, by_status, active, expired_swept, reclaimed, dead_letter, fencing_rejections, oldest_active_min.
- guard.py: admit(root, leg, lane) -> (ALLOW|DEFER|DENY, reason). DENY: terminal leg status, dead_letter, closed lease, capability miss. DEFER: blocked, leased by another holder (names holder + token + ttl), retry window open. ALLOW: claimable or re-entry by the same holder. No model in the loop. CLI: `relay admit <leg_id> [--lane]`, exit 0/2/1.
- relay_daemon.py: admit before acquire (verdict printed), tokens kept per leg and presented on every release/failure (FENCED lines when stale), heartbeat thread at TTL/3 wraps the agy subprocess (UTF-8, CREATE_NO_WINDOW), sweeper + metrics at the top of run_cycle.
Tests: tests/test_lease_control_plane.py 10 new (token monotonic across reclaim/force; stale token cannot release/fail/heartbeat; heartbeat extends liveness; sweeper + visible reclaim + metrics; dead-letter history; admission verdicts incl. retry window; history cap). Full suite 345 passed, 1 fixed (test double without the new kwarg), 6 skipped, 1 xfail.
Not done: the running "NouGen Relay Watcher" task still runs the old daemon code until restarted (Dave's task, 5-min trigger; restart = next trigger after a stop). C (Worker-side relay_claim_list) and D (push wake into run_cycle) remain per the war-game.

## Correction, relay-live (push-main commit 2080155)
The notifier died at 02:06Z to a console Ctrl+C (0xC000013A); legs 021127Z and 022118Z sat unseen until 02:31Z. Now: SIGINT ignored + SetConsoleCtrlHandler(None) on Windows, pid + interrupt mode in the banner. Task settings (RestartCount 0, ExecutionTimeLimit PT72H) need an elevated Set-ScheduledTask; one-liner in the correction shard.

## Open legs seen, not taken
021127Z (vibes.py persona stream), 022118Z (HF relay shadow-mirror war-game), 023538Z (Fleet Expression Protocol), 023600Z (Xoah hidden challenger). Session at 1.9 h; handoff-and-reset is the right next move for those.
