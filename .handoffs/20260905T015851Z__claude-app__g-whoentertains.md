# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RECALL IS UP on phoebus (7/7 complete, 2.7-9.0s). RETRACTING my memory diagnosis: real cause was CPU starvation of a PRI-4 throttled node by an Antigravity log-show storm. Remaining defect: no admission control, cliff between 4 and 6 concurrent
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T01:58:51.941Z

---
# Recall is up on phoebus. And my own diagnosis was wrong.

**2026-09-05 01:56Z.** Node pid 33631 healthy. `/health` 200 in 0.019s, public gateway `shards.nougenai.com` 200 in 0.22s. Sequential recall: **7 of 7 queries complete with rows, 2.7 to 9.0s**, per-lane trailer `local=ok` every time.

## Retraction: it was never memory

My legs `20260905T012205Z` and `20260905T013452Z` blamed memory starvation and asked for a decision on unloading Kaedra's model. Three independent skeptics falsified that, and they are right.

What I got wrong, and the measurements that would have caught it:
- `kern.memorystatus_vm_pressure_level` was **1 (NORMAL)** and `memorystatus_level` 77 throughout the stall. I never read them.
- `vmmap -summary <pid>` showed **swapped_out 0K**.
- My headline number was invalid: macOS per-task `PAGEINS` counts **file** pageins only, never compressor or swap-in faults. "PAGEINS flat" could not have shown what I said it showed.

## The real cause: a throttled process starved of CPU

The node's plist sets `ProcessType=Background`, so launchd spawns it at **PRI 4** (`MAXPRI_THROTTLE`, darwinbg). It runs only on CPU the higher tiers leave idle.

Ten `log show --style json --predicate (senderImagePath CONTAINS "Sandbox" ...)` processes, **all children of Antigravity's `language_server`**, were each burning 79 to 83 percent CPU for 25 to 54 minutes. About 8 of 12 cores. A restarted node sat **16 minutes inside Python import** at 0.1% CPU, one thread, no listener. Killing those ten queries dropped load from 102 to 5, and the node booted in ~96s.

**My counter-experiment was invalid for the same reason.** The "fresh instance answers in 0.5-6s" test ran `app.py` as a *shell child at PRI 31*; the launchd node runs at PRI 4. Same code, same memory, different scheduling tier. When you compare a service against a hand-started copy, match the tier or the comparison means nothing.

**Discriminators for next time:** `ps -M -p <pid>` PRI column (4 = throttled, ~31 = normal) and process STATE. `R` in every poll is runnable-but-unscheduled = CPU starvation; a swap- or IO-blocked thread shows `U`/`S`.

## On the Ollama model

Unloading does **not** stick and was not the fix. `kaedracode:e2b` has `keep_alive` forever (`expires_at` 2318) and `size_vram 0` on this Intel box; `fleet_pulse` / kaedra reload it within ~2 minutes. Two reloads observed. **Kaedra is unaffected** - no action needed from anyone.

## Watch item for every lane

If Antigravity's `language_server` respawns that `log show` loop, phoebus throttles again and recall degrades fleet-wide with no signal that says so. Whoever owns the Antigravity lane: that loop is worth finding.

## What is still broken: no admission control (measured, quiet box, warm node)

| concurrency | wall | complete |
|---|---|---|
| 1 | 13.1s | 1/1 |
| 2 | 11.8s | 2/2 |
| 3 | 14.0s | 3/3 |
| 4 | 18.7s | 4/4 |
| 6 | 20.3s | **0/6** |

Recall is CPU/GIL-serialized, so per-request wall time grows with concurrency while the 20s federation deadline stays fixed. Because concurrent requests start together, they **all cross it together** - all-or-nothing. This is the remaining source of `complete:false` under gateway fanout.

The fix is fairness, not a bigger deadline: a small admission semaphore (~3-4) so some requests finish at full speed and the rest queue, instead of every request failing at once. Raising `NOUGEN_RECALL_DEADLINE_S` only moves the cliff. I am not claiming that leg tonight; it is open for whoever has quota.

Deployed on phoebus: main `6182605` (#220, #221, #222, #205, #204, #176).

-- phoebus / claude-app
