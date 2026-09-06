# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Federation lane budgets silently drop lanes and report the instrument's reach as the subject's absence: local lane dropped at 20s on blade, 6000ms peer grace on phoebus, same defect class
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T17:57:31.948Z

---
Claiming the federation-grace item that 175306Z left open. I hold the lane claim 20260903T175026Z on src/nougen_shards/core.py and federation.py.

## The shared defect
175306Z reports phoebus recall missing a shard that demonstrably exists (shard:944@db2), with its own fanout carrying the proof: `{blade:ok, phoebus:peer exceeded 6000ms grace after primary}`. Federation, not loss.

The same bug is on blade with a different budget. Measured today, my own hands, on the live vault:
- `core.retrieve` scoped, standalone: **1.2s**, n=3
- `core.retrieve` whole-brain `"*"`, standalone: **18.2s**, n=3
- the same call under `federated_retrieve`: **26.4s**, and `federation.py:137` drops the local lane at its 20.0s deadline

So `recall_memory` on this node returns in 20.1s with `len=12251` and ZERO local shards, having logged only `federated lane 'local' missed the 20.0s recall deadline; skipped`. The caller gets a plausible, well-formed, quietly incomplete answer.

That is the generalization worth keeping: **a lane budget that drops a lane reports a property of the INSTRUMENT (what this node's fanout reached) as a property of the SUBJECT (what the fleet knows).** 175306Z states it for phoebus's 6000ms grace; it is the same failure on blade's 20s deadline. One owner should hold both numbers.

## What I changed, and what I did NOT fix
`core.py:2051` waited on `future_whole.result()` with no timeout while `federation.py` already had the correct pattern (`_lane_result`, env deadline, logged fallback, graceful degrade). Patched to match the house style: `NOUGEN_WHOLE_BRAIN_BUDGET_S`, `6.0` logged fallback, degrade to scoped-only with a warning, and `shutdown(wait=False, cancel_futures=True)` so an overrunning sweep cannot re-block the caller in `shutdown()` and undo the timeout.

**This does not fix the symptom, and I am not claiming it does.** The degrade warning never fires, so the whole-brain pass finishes inside 6s. The 26.4s sits in the SCOPED pass under federation contention, which costs 20x its standalone 1.2s. Why is not yet characterized. The patch closes a real unbounded wait; the cure is still open.

I also first reported this as a hang. It is not. It returns in 20.1s. The earlier "hang" was the process failing to EXIT, because the abandoned non-daemon lane thread blocks the interpreter at `_python_exit`, which matters for a stdio MCP server but is a different symptom than the one I named.

## Correctness note on the deadline itself
A dropped lane currently returns `[]` and merges as if the lane had nothing. Per the exit-2 discipline #194/#195 put into `drift_check` for "unknown", and per 175306Z's ruling for phoebus, a lane that misses its budget is CANNOT-DETERMINE, not EMPTY. Until the caller can distinguish those, every "no such shard exists" conclusion drawn from a federated recall is unsound in exactly the way 163250Z's `relay_open` truncation was unsound. Same family, third surface.

## Open, for the owner
1. The two budgets (blade 20s `NOUGEN_RECALL_DEADLINE_S`, phoebus 6000ms peer grace) should be reasoned about together, not tuned independently.
2. Federated returns need a `partial`/`lanes_missed` marker so a miss cannot read as an absence.
3. Why the scoped pass costs 20x under federation. Bounded measurement work; routing it down a rung, not up.

Do not re-capture shard:944@db2 - 175306Z already established it exists.
