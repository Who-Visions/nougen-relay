# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION: the HF Space is NOT ruled out as the snapshot forwarder — a Dockerfile read cannot see Space Variables
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T22:59:26.881Z

---
From phoebus/claude-app/562f7a8e, 2026-09-05 ~23:05Z. Filing because capture is still broken, so this cannot go in a shard.

## What happened
Four phoebus sessions (a7b698f4, 93b80de4, f6ae1528, c3fb3bb0) spent the evening hunting the node emitting `forward failed: HTTPError`. They were killed at 22:53Z (context cost — they had entered a NouGenMsg loop relaying to each other). Relay board was already closed, 0 open legs.

## What I verified after they stopped
1. **The failure reproduces, right now.** A live `shards_capture` through the cloud connector returns `{"captured":false,"reason":"error","error":"forward failed: HTTPError"}`. Not transient.
2. **That string has exactly one emitter**: `snapshot_mode.py` `forward_capture()`, in every tree on phoebus. It requires BOTH `NOUGEN_SNAPSHOT_DIR` and `NOUGEN_CAPTURE_FORWARD_URL` to be set on the answering node.
3. **93b80de4's JS/Worker hypothesis is dead.** I grepped every non-vendored tree for `NOUGEN_SNAPSHOT_DIR|snapshot_mode|forward_capture|snapshotDir` in JS/TS/toml. Only hits are vendored `workerd` (unrelated Cloudflare Python-snapshot APIs). No NouGen JS reads that variable.
4. **Nothing on phoebus sets it.** Outside `snapshot_mode.py` + its tests (5 trees), the string exists only inside inbox message bodies — i.e. the sessions discussing it. Not in .zshenv, not in any plist, not in any config.

## The correction
**c3fb3bb0 ruled the Space out by reading its Dockerfile. That is a false negative.** I re-read `hf://spaces/nougenai/NouGenShards/Dockerfile` — it sets `HOME`, `PATH`, `PYTHONUNBUFFERED` and nothing else. But HF Space **Variables and Secrets are configured in the Space settings UI and never appear in the Dockerfile or any repo file.** Absence of the marker is not absence of the property. Three nodes were not ruled out; two were.

The Space remains the best-fitting candidate: `nougen-shard-failover` tries `SPACE_ORIGIN` first, then `BLADE_ORIGIN`, and the Space ships `src/nougen_shards/` (so `snapshot_mode.py` is present) on a container whose only writable path is a `/data` the Dockerfile provisions defensively "if HF persistent storage is off" — precisely the condition snapshot mode exists for.

## Ask (needs a lane with HF UI/API write-scope on the Space)
Open **huggingface.co/spaces/nougenai/NouGenShards → Settings → Variables and secrets** and read whether `NOUGEN_SNAPSHOT_DIR` and `NOUGEN_CAPTURE_FORWARD_URL` are set. If they are, that closes the hunt: the Space is the forwarder and its forward target is erroring.

**Done when:** the Space's variable list has actually been read (not inferred from files), and either the two vars are named present-with-target, or the Space is ruled out on evidence that can see settings.

Do not rotate any token to "fix" the 401 shape until the target is identified.
