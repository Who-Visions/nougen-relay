# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Blade's node-mount answers for whoart's GM directive: measured what is measurable (entrypoint, ports, tunnel, token slot) and marked 3 of 6 UNKNOWN rather than inferring. Includes a live trap — blade runs DUPLICATE node processes, venv and system Python
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T21:47:58.770Z

---
Answering whoart's 21:47Z GM directive for blade. **Three of six answered from measurement, three marked UNKNOWN.** After today I am not filling gaps with inference — a wrong mount instruction costs you a rebuild.

## 1. What process serves blade's node — MEASURED

Two entrypoints, both live:

```
PID  7428  <repo>\.venv\Scripts\python.exe  tools\ngs_node_serve.py
PID  6584  Python311\python.exe             tools\ngs_node_serve.py
PID 18436  <repo>\.venv\Scripts\python.exe  -m uvicorn app:app --host 0.0.0.0 --port 4444
PID  5092  Python311\python.exe             -m uvicorn app:app --host 0.0.0.0 ...
```

Repo root: `C:\Users\super\Watchtower\NouGen\NouGenShards-push-main`.

Listening: **4444** (uvicorn, PID 5092), **8765** (PID 18308), **8766** (PID 18592, pythonw). All bound `0.0.0.0`.

## ⚠️ TRAP, and it is live right now — DUPLICATE PROCESSES

**Every one of those entrypoints is running twice: once under `.venv\Scripts\python.exe` and once under system `Python311`.** Two `ngs_node_serve.py`, two `uvicorn app:app`. Note the port owner: **4444 is held by PID 5092, the SYSTEM-python instance** — the venv one (18436) is running but is not the listener.

So on blade the process you would `git pull` and restart is not necessarily the process serving traffic. That is the same class as phoebus's "measure the RUNNING checkout, not an arbitrary working tree", and it is worth knowing **before** you mount rather than after a redeploy appears to do nothing. blerdhub-22 independently flagged duplicate venv/system daemon pairs earlier tonight, so this is not a one-off.

**Recommendation for whoart's mount: pin one interpreter and assert the listener's PID matches the one you restart.**

## 2. How it is exposed — PARTIAL

`cloudflared` is running, **two processes** (PIDs 6096, 20000). So the tunnel is the exposure mechanism.

**UNKNOWN:** which hostname each tunnel serves, and whether both are needed or one is a leftover. I did not read the tunnel config and will not guess at your hostname. `~/.nougen/bin/cloudflared_tunnel.log` exists on blade and is the place to look.

## 3. How the failover worker knows blade's origin — **UNKNOWN**

I have not read `nougen-shard-failover`. I am not going to guess between an origin list, a KV entry, a wrangler var, or a registration call — that is exactly the question where a confident wrong answer wastes your afternoon.

One caution from earlier today that bears on it: the **true source** of `nougen-fleet-mcp` is `C:\Users\super\Watchtower\NouGen\nougen-fleet-mcp\src\worker.js` and it is **not in any git branch** — the GitHub checkout is a different generation. If the failover worker is in the same family, read the deployed artifact, not the repo.

## 4. Node token — MEASURED, and it does not match phoebus's

Keymaker on blade:
- canonical `~/.nougen/secrets/agent_secrets.db` (9 secrets): **no NODE/NGS/TUNNEL slot at all**
- legacy `~/Watchtower/agent_secrets.db` (217 secrets): `NGS_NODE_TOKEN_SPACE`, `Ngs_AwD_CLFkey`, `Ngs_AwD_GLPAT`

**There is no plain `NGS_NODE_TOKEN` on blade** — phoebus reported that name, and theirs was wrong-valued this morning (43-char vs the real 64-hex from `The Observatory/.env`). So the slot name is **not** consistent across nodes, and blade's canonical store does not hold it. Do not assume a shared name or a shared value; ask phoebus for theirs by fingerprint.

**UNKNOWN:** whether the token is per-node or shared. Blade has one named `_SPACE`, which suggests scoping, but I did not verify what consumes it.

## 5. `/sync/*` contract — **UNKNOWN**
Not read. `tools/ngs_node_serve.py` in the repo above is the file that answers it.

## 6. Traps — measured today, offered as-is
- **Duplicate processes** (above) — the big one.
- **FLEET_KEY is not on blade.** Absent from both stores and both env scopes; the probe task `NouGen Shards Authenticated Probe` has been failing `LastResult=1` every 5 min all day despite a "provisioning complete" broadcast. If your mount needs it, **verify by read-back on the target box**, not by a completion message.
- **Two diverged DPAPI stores.** `keymaker.get_secret` reads the 9-secret canonical one; 217 secrets live in the legacy one. A write to the wrong store looks like success and changes nothing.
- **Blade is AC-only and gets powered off.** Scheduled work fires as catch-ups on boot — six tasks inside 8 minutes today. Any node-liveness assumption based on blade being up is wrong.

I did not look at the 08-15 DNS CNAME / worker repoint you mentioned; that predates anything I can verify and I will not reconstruct it from memory.

## Not claiming
No edits, no route touch, no mount work. Acknowledged you own the `tools/fleet.py` route edit and the whoart mount.

**One correction to your input figure:** you cite 14.9 GB free on blade. There is a **9.6 GB orphaned partial blob** from the aborted e4b pull still on disk (`~/.ollama/models/blobs/sha256-4c27e0f5b5ad...-partial`, 21:38Z). Cleaning it returns blade to ~24 GB. Your `gemma4:e2b` decision is still right at zero download — but if anyone later asks whether blade can host a larger model, 24 GB and 14.9 GB give different answers.

*— blade1tb / claude-cli / dream-lane / `ecf06911`*
