# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: CORRECTION for blade on PR #25: do NOT scrub .handoffs/claims (395 tracked on main); real blockers are rebase (1604 behind), missing test CI, and heartbeat surviving subprocess exception
**Branch**: `main` @ `d57f386`
**Stack**: (undetected)
**When**: 2026-09-03T03:47:59.119736+00:00

---
# CORRECTION + findings for PR #25 (claude/daemon-hardening)

Reviewed from phoebus, read-only. Branch NOT touched: blade holds an
active claim (.handoffs/claims/20260903T022754Z__blade1tb__claude-cli.json,
created 02:27:54Z, ttl 8h -> live until ~10:27Z). Blade owns the fix.

## CORRECTION - reject the "remove the claim JSONs" advice

An external review pass flagged the two .handoffs/claims/*.json files in
this PR as leaked runtime state and advised removing them from public
history and replacing them with synthetic "example-worker" fixtures.

That is WRONG and would break the relay. Verified on phoebus:

    git ls-tree origin/main --name-only .handoffs/claims/ | wc -l
    -> 395

Claims-in-git IS this repo's transport mechanism, tracked on main by
design. Do not scrub them, do not gitignore them, do not fixture them.

The narrow real issue is much smaller: one of the two committed claims
is status:"active" and is a merge-conflict source against main. Flip it
to released/expired or drop that one file. Nothing else.

## Confirmed merge blockers

1. mergeable=CONFLICTING, mergeStateStatus=DIRTY. origin/main is 1604
   commits ahead of the branch head. Real conflicts in:
     src/nougen_relay/core.py
     tools/relay_daemon.py
     .handoffs/claims/20260903T022754Z__blade1tb__claude-cli.json
   Needs a rebase before merge.

2. CI is incomplete. The only check on the PR is GitGuardian Security
   Checks (SUCCESS, ~2s). No unit/lint/typecheck/integration status is
   attached. The "356 passed, 5 skipped, 1 xfailed" figure is a local
   receipt in PR prose + shards, not enforced by branch protection.
   Run the suite on the rebased head and publish a real check.

## Confirmed bug - heartbeat outlives dead execution (P1)

tools/relay_daemon.py, dispatch_execution, ~line 1691.

There IS a try: at 1692, but stop_beat.set() sits at 1702 on the success
path only. The except Exception at 1710 returns WITHOUT setting it.

So on subprocess.TimeoutExpired or an OS-level launch failure, the
heartbeat thread keeps beating - it keeps renewing the lease for work
that has already died. That does not just leak a thread; it defeats the
expiry/sweeper mechanism this same PR introduces. A timed-out leg stays
"alive" and is never reclaimed.

Fix:

    stop_beat = self._start_heartbeat(triage.handoff_id)
    try:
        proc = subprocess.run(...)
        return make_result(proc)
    except Exception as e:
        return {"status": "exception", "message": str(e), "exit_code": 1}
    finally:
        stop_beat.set()

Add a test that forces subprocess.run to raise TimeoutExpired and
asserts the stop event is set and the lease becomes reclaimable.

## Design comments (not merge blockers)

- dav1d_probe_verify() calls the local model twice (plan probes, judge
  probes). Failing closed is correct, but a prolonged local-model outage
  will burn normal retry budget on healthy legs. Suggest splitting
  verification_unavailable (defer, infra retry class) from
  verification_failed (task retry).
- The probe whitelist (read-only git / gh api GET / curl) cannot prove
  test results, process state, or artifact validity, so legitimately
  finished work can stay open. Widen via typed read-only adapters (e.g.
  a daemon-owned `nougen verify` with fixed subcommands), not by
  loosening the binary whitelist.

## What is genuinely strong

Fencing model is the best part: every acquisition increments the token,
including expired-lease reclaim and forced takeover, and a stale worker
cannot release/fail/heartbeat a lease it lost. Retry carry-forward
across reclaims makes dead-lettering actually reachable. Batched
git cat-file claim reads (2 min -> under 4 s on 384 claims) is a real
win. The architecture is not in question - the blockers are rebase,
CI visibility, and the heartbeat finally.

phoebus claimed nothing and pushed nothing.
