# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: NOUGEN_BUS_DIR now persisted in both phoebus plists (5/5 MATCH) — but drift_check STILL exits 1 under the real daemon env, via the SAME feature-branch bug that produced the false blade incident 120029Z. Do not wire it into the watcher yet
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T15:48:06.066Z

---
Follow-up to `153746Z`, executed on phoebus 2026-09-03 15:46-15:48Z.

## Done
`NOUGEN_BUS_DIR=/Users/kushboygroup/.nougen/src/nougenshards/tools` added to both `com.nougen.msgnode.plist` and `com.nougen.relaywatch.plist`. Plists backed up as `*.bak-20260903T1546Z`, both `plutil -lint` OK, `NOUGEN_WAKE_DISABLED=1` verified intact after the edit.

**Reload used `bootout` + `bootstrap`, not `kickstart -k`.** `kickstart -k` restarts the process but does NOT re-read the plist, so it will not pick up a new `EnvironmentVariables` entry — you get a fresh PID and the old env, which looks like success. Worth knowing on every node.

New PIDs 14389 / 14400, both exit status 0, argv inside the deployment clone. Confirmed **in-process** via `ps eww`: both carry `NOUGEN_BUS_DIR` and `NOUGEN_WAKE_DISABLED=1`. `GET /status` online; `POST /msg` → `delivered: true`.

## The BUS_DIR fix worked — and uncovered the next layer
Run with the EXACT env the daemons now carry, `drift_check` gives 5/5 MATCH on the bus files, and then this:

```
PULL-BLOCKED /Users/.../The Observatory/NouGen/nougenshards
  HEAD is not an ancestor of origin/main; no fast-forward is possible
  and a polling watcher here has already stopped learning
exit 1
```

**This is a false alarm, and it is the SAME BUG that produced incident `120029Z` about blade.** That checkout is on branch `node-tool-concurrency`, upstream `origin/node-tool-concurrency`, 2 ahead / 4 behind `origin/main`. A feature branch. `drift_check` compares HEAD against `origin/main` regardless of what the branch actually tracks, so any node whose `NOUGEN_SHARDS_REPO` sits on a feature branch reports PULL-BLOCKED with that "already stopped learning" text while nothing is wrong.

That is now **twice in one day**, on two different nodes, from one comparison: it cost an escalated owner ruling on blade (withdrawn in `152445Z`) and it fires on phoebus today. The rule it violates is the one already captured in shards: prove the reference is current before believing any comparison.

## Two defects, both must be fixed before the watcher wiring
1. **Wrong reference branch.** `drift_check` must resolve the repo's own upstream (`@{u}`), not assume `origin/main`. A branch that tracks something else is not pull-blocked; it is on a branch.
2. **`NOUGEN_SHARDS_REPO` double duty.** On phoebus it names the live checkout ONLY because the keymaker venv lives there — it was never meant to be the canonical reference, and it cannot simply be repointed without breaking keymaker for the daemons. `drift_check` needs its own variable (`NOUGEN_CANONICAL_REPO`) or must default to the bus dir's own clone. This is the split already listed as a sequenced next step in handoff `151443Z`; the PULL-BLOCKED row above is the concrete evidence for why.

Also still recommended from `153746Z`: drop the `.nougen/bin/` fallback map and fail loudly when `NOUGEN_BUS_DIR` is unset, rather than silently guessing a runtime location.

## Blast radius today: none
`drift_check` is not yet invoked by any daemon — the wiring into `relay_watch_node.py`'s poll is still a deferred step. So exit 1 has no runtime effect right now. **But it is a hard blocker for that wiring**: branch on this exit code today and a fully healthy phoebus alarms on every poll. Whoever picks up that step should land defects 1 and 2 first.

Not fixed here — a code change to canonical belongs in a PR, not a live edit on a node.
