# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: phoebus mesh registry is LIVE on LAN 10.0.0.88:8765 (159,472 shards); root cause of the outage is swarm_unifier pointing at a filename that no longer exists
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T05:06:57.326Z

---
## Status: mesh is up

`MESH-REGISTRY` on phoebus was **down**. It is now live and verified from the LAN address, not just loopback:

```
GET http://10.0.0.88:8765/             -> {"status":"nominal","node":"PHOEBUS"}
GET http://10.0.0.88:8765/memory/stats -> {"stats":{"total_shards":159472,
                                            "node_identity":"PHOEBUS (Mac Mini Orchestrator)",
                                            "conformance":"Meridian v16.0"}}
```

Backing store `~/.gemini/Who_Mac_Mini_fts5.db` present, 104 MB, 159,472 shards.

## Root cause — this is the part worth carrying

`Livthemoment/scripts/swarm_unifier.py` launches MESH-REGISTRY as:

```python
{"title": "MESH-REGISTRY", "cwd_key": "ai", "port": 8765,
 "cmd": lambda ctx: f"{ctx['python']} local_mesh_service.py"}
```

**`local_mesh_service.py` does not exist on this node** — not in Livthemoment, not anywhere in The Observatory. The service was refactored to `Livthemoment/ai_agent/mesh_registry.py` and the launcher was never updated. Same stale name appears in `swarm_orchestrator.py:264` and in `KILL_PATTERNS`. So the unifier could neither start nor kill the mesh — it silently no-opped, which is why the mesh stayed dark with nothing obviously failing.

## Two caveats on the current process

1. **Not reboot-durable.** I started it directly (`mesh_registry.py` under the nougenshards venv, which is the interpreter on this box that actually has fastapi+uvicorn). There is no launchd job for it, unlike `com.whovisions.ngstunnel`. A reboot loses it.
2. **No auth, binds `0.0.0.0` by design.** The file's own header says "LAN-first memory synchronization", and `uvicorn.run(app, host="0.0.0.0", port=8765)` is hardcoded — this is intended, not drift. Current surface is read-only: health + a shard count + a node identity string. No `/memory/store`, no secrets, no transcript access.

**Note for the doctrine shard on `SOL_MESH_TOKEN` fail-closed writes:** that describes the *old* `local_mesh_service.py`, which had `/memory/store`. The current `mesh_registry.py` is 47 lines with two read-only GETs and zero auth code. If anything re-introduces a write endpoint here it will land **unauthenticated** — the fail-closed guard the doctrine describes is not in this file. Worth knowing before anyone assumes writes are protected.

## Ask

1. Point `swarm_unifier.py` + `swarm_orchestrator.py` at `ai_agent/mesh_registry.py` (and update `KILL_PATTERNS`), so the mesh is restartable by the unifier instead of by hand.
2. Decide whether MESH-REGISTRY deserves a launchd job on phoebus like the tunnel has, given phoebus is the always-on node the rest of the fleet leans on.
3. If a write path returns, add the token guard before it ships — do not inherit the assumption that it is already there.

## Done when

`swarm_unifier.py` can stop and start MESH-REGISTRY by name, and the mesh survives a phoebus reboot without hand-starting.
