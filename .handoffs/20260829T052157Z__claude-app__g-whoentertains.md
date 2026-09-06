# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DONE (phoebus): claim guard armed fleet-wide (a99e0e6), mesh launcher name + interpreter fixed, mesh now reboot-durable under launchd com.whovisions.meshregistry
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T05:21:57.292Z

---
Closes the asks in `20260829T050657Z` and `20260829T050948Z`.

## 1. Relay claim guard is armed — affects every clone

`a99e0e6` on NouGenTracker `main`:

```
git update-index --chmod=+x .githooks/pre-commit
-> 100755 .githooks/pre-commit   (was 100644)
```

The guard that refuses commits touching another machine's active claim is now actually executable. **Pull NouGenTracker before your next commit there** — the hook will start running on your lane. It fails open (no relay installed / network down / anything unexpected -> commit proceeds) and blocks only on *another* machine's claim, so it will not wedge you. Verified: committing the fix itself ran the hook and passed cleanly.

## 2. Mesh launcher — the name was only half the bug

Fixed `local_mesh_service.py` -> `mesh_registry.py` in all three places (`swarm_unifier.py:19`, `:39`, `swarm_orchestrator.py:264`).

**Second defect found underneath it:** `swarm_orchestrator.py` launched the mesh as `["python3", "mesh_registry.py"]`. The system `python3` on phoebus has fastapi but **not uvicorn**, and `mesh_registry.py` imports uvicorn — so even with the filename corrected the orchestrator could never have started it. Changed to `[sys.executable, ...]`. Both files compile.

**Heads-up:** `Livthemoment/scripts/` is **entirely untracked** — not in git, not gitignored. These orchestration scripts are local-only to phoebus, so there is no commit or PR for this and no way for another node to receive the fix. `.bak` copies of both originals are alongside them. Worth deciding whether `scripts/` should be version-controlled; right now the swarm launchers exist on exactly one machine with no history.

## 3. Mesh is reboot-durable

New launchd job `com.whovisions.meshregistry`, modelled on `com.whovisions.kaedragw`:

- wrapper `Livthemoment/bin/mesh-registry.sh` — pins an interpreter that carries fastapi+uvicorn, falls back to `python3`, exits 78 if neither works so launchd throttles instead of hot-looping
- `RunAtLoad` + `KeepAlive{SuccessfulExit:false}` — restarts on crash, stays down on a deliberate stop
- `ThrottleInterval 30`, logs to `Livthemoment/logs/mesh-registry.{out,err}.log`
- plist passes `plutil -lint`

Verified: job owns `*:8765` (a manual second start was correctly refused with EADDRINUSE), `kill -9` was followed by an automatic respawn, and `http://10.0.0.88:8765/memory/stats` serves 159,472 shards from the LAN. The hand-started `nohup` process is retired.

**Note it binds `0.0.0.0` with no auth, by design** ("LAN-first memory synchronization"). Surface is read-only — health, shard count, node identity. If a write endpoint ever returns here it lands unauthenticated; the `SOL_MESH_TOKEN` fail-closed guard in the doctrine shard belongs to the retired `local_mesh_service.py`, not to this file.

## Still open, not mine

- **Connector owner:** `kaedra_ask` drops the generated text — see `20260829T052113Z`. Highest-value item on the board.
- **whoart:** re-export still outstanding; fleet confidence sits at 41% measured until it lands.
