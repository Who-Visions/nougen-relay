# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ask_dav1d now routes to the dav1d:e2b persona (node /dav1d/ask + Worker 1869fe5f216c); VRAM gate learns sizes from /api/ps; blade node needs one elevated restart to go live
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T00:54:03.505Z

---
## Dav1d = persona, AGY = tool (blade1tb, claude-cli, 2026-09-01 20:55 EDT)

Dave corrected the routing: "ask Dav1d" must reach dav1d:e2b on blade's ollama lane, not the AGY CLI. Done and verified in-process; one elevated node restart away from live.

- **Node**: new `POST /dav1d/ask` + MCP `ask_dav1d(prompt, model="")` -> `ask_dav1d_persona()` via `OllamaClient.chat`. Envelope matches `/dav1d/exec` so `engine: ollama` (persona) vs `engine: agy-cli` (execution layer) is explicit. In-process: "DAV1D_OK. dav1d:e2b on the local ollama lane answered this query." in 18s.
- **VRAM gate**: was refusing dav1d:e2b ("no measured load size", static table only). Now learns sizes from `/api/ps` into `~/.nougen/vram_measured.json` (env `NOUGEN_VRAM_MEASURED_PATH`), records fully-on-GPU residents on every check, admits residents first. Strict refusal for unmeasured models kept. dav1d:e2b measured 2.67 GB on an empty card. 18/18 tests.
- **Worker**: etag `1869fe5f216c` (00:46Z), 32 bindings. `ask_dav1d` -> `/dav1d/ask`; on 404 it falls back to AGY with a visible "[fallback: ...]" prefix. Verified through the door against the pre-route node: labelled fallback came back exactly as designed.
- **AGY lane** still quota-locked until ~2026-09-05 00:25 EDT (leg 20260902T003755Z).

**Owed (Dave, elevated PowerShell in NouGenShards-push-main)**: `.\tools\node_lane.ps1 -Action stop; .\tools\node_lane.ps1 -Action start`, then `ask_dav1d` from any reconnected connector should answer with `engine: ollama`.

All node changes remain uncommitted on `codex/shards-capture-main` (app.py, core.py, vram_gate.py) beside other lanes' WIP. Scripts and pre/post copies in `nougen-worker-backups\griot-20260901\`.
