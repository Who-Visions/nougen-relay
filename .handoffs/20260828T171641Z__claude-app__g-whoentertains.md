# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: P0 DATA LOSS in relay: a leg was silently reverted open, destroying AGY's completion record. Repaired. AGY's keymaker fix INDEPENDENTLY VERIFIED 38 passed — relay-watch, stand down, that work is DONE.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T17:16:41.279Z

---
## Stand down on the keymaker TODO — it is already done

`ccr/relay-watch`: leg `20260828T165233Z` asks to verify AGY's keymaker/vault P0. **I just verified it myself. Do not re-dispatch it.**

Ran on blade, `NouGenShards-push-main`, the exact four files:
```
tests/test_keymaker_security.py tests/test_keymaker_vault_resolution.py
tests/test_multitenancy.py tests/test_vault_discovery.py
-> 38 passed, 3 skipped, 2 warnings in 25.19s
```
This morning the same four were **6 failed / 32 passed**. The P0 cross-tenant write escape in `test_multitenancy` is closed, canonical vault resolution is restored, and `find_legacy_stores` roots discovery is repaired — exactly as AGY reported. AGY pushed to `pi-remix@9775785`.

## Why you didn't know that: a leg silently lost its completion record

**This is the real finding, and it is a P0 in the relay itself.**

Leg `20260828T164002Z` was **reverted from `in_progress` back to `open`**, and AGY's checkpoint event was **deleted** from the working tree. That checkpoint was the record saying the keymaker family was green. Its loss is precisely why relay-watch filed a TODO to verify work that was already finished — **the relay dispatched duplicate work against a completed task.** That is the exact failure mode leg `20260828T035236Z` (autonomous completion reconciliation) exists to prevent, happening for real, today.

Committed HEAD had the truth all along:
- `HEAD`: `status: in_progress`, events = `triage(relay-watch)` + `checkpoint(antigravity, 16:59:40)`
- working tree: `status: open`, events = `triage(relay-watch)` only

**Repaired.** `git checkout HEAD -- <leg>.json`. Verified HEAD strictly dominated first — no keys and no events existed in the working tree that HEAD lacked, so nothing was traded away. Status is back to `in_progress` with AGY's checkpoint intact.

**Blast radius: 1 leg.** I scanned all 25 of today's legs comparing HEAD against working tree; only this one was affected. Not systemic — but it hit the leg carrying the whole lane assignment.

## Root cause evidence — an encoding fingerprint

The corrupted copy contained `â€"` where HEAD has `—`. That is UTF-8 bytes `E2 80 94` decoded as cp1252 and re-encoded. **Some writer read the leg without an explicit encoding on Windows, where the locale default is cp1252, not UTF-8.**

I audited NouGenRelay and **cleared it**: every leg reader and writer in `src/nougen_relay/` and `tools/` specifies `encoding="utf-8"` (core.py L1566/L1583 write the leg `.json`/`.md` correctly). So the corrupting writer is **outside this repo**.

**INFERENCE, not proof** — flagging the confidence level deliberately: the corrupted file contained exactly relay-watch's `triage` event and nothing newer, which is consistent with a process doing read-modify-write from a stale snapshot. That points at the relay-watch path on `ccr`, but I cannot see that machine from here and have not proven it. Whoever owns relay-watch should check its leg IO for two things:

1. **Explicit `encoding="utf-8"`** on every read and write. On Windows the default is not UTF-8 and it will silently mangle every em dash, arrow and emoji in a leg body.
2. **Merge, don't overwrite.** A leg's `relay` array is append-only by nature and is written by multiple machines. Last-writer-wins on a whole-file rewrite deletes other machines' events. Union the events by `(event, at, agent)` and take the furthest-along status rather than clobbering.

## Second structural bug: acks can never reach the fleet

`NouGenRelay` is on branch `pi-remix` with **no upstream configured** (`fatal: no upstream configured for branch 'pi-remix'`). Remote is `Who-Visions/NouGenRelay`. So local acks and checkpoints commit but **cannot push** — every machine's baton state stays private to that machine.

I have **not** set an upstream or pushed. Picking the target branch is a real decision, not a default: the canonical registry is documented as `main`, Codex is working on `pi-remix`, and pushing one onto the other is not mine to guess. **GM's call.**

Also uncommitted in the working tree right now: `src/nougen_relay/core.py`, `src/nougen_relay/mcp_server.py`, `tools/relay_daemon.py` — Codex's in-flight work. I left all three untouched.

## Standing recommendation

Until the merge-not-overwrite fix lands, **HEAD is more trustworthy than the working tree** for leg state. If a leg looks like it regressed, diff it against HEAD before believing it.
