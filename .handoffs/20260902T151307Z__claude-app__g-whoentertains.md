# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CLOSED: Shadow Xoah stack live end to end through the door after elevated restart (node PID 238356, Worker e4f8d35b9514); ask_xoah 10.9s; destiny #1 fulfilled; /xoah/ask 500 root-caused (missing lane key in node env), Rhea's /agent has the same exposure
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T15:13:07.073Z

---
## Xoah stack live (blade1tb, claude-cli, 2026-09-02 11:14 EDT)

Dave asked for the elevated restart; done from the CLI via `Start-Process -Verb RunAs` (UAC approved on screen), three times as fixes landed: 388592 -> 154480 -> 172504 -> 238356. Node serves 28 MCP tools incl. ask_xoah, xoah_pressure/override/self/throne/throne_decide, destiny_*, unfinished_destinies, evolve_report, ask_dav1d.

**Through the door** (Worker `e4f8d35b9514`): `unfinished_destinies` 0.3s, `xoah_throne` 0.4s (Jaru on Prime -> FORBIDDEN, BRANCH_AWAY), `ask_xoah` **10.9s**: destiny #1 named, branch U0, provenance destiny:1 + legs 010902Z/011226Z/011422Z, brain free:nemotron-3-super. That was destiny #1's own verification, so it is now **fulfilled** via `POST /destiny/1/status` with the call as evidence; unfinished = 0; `evolve_report` shows the transition.

**Two defects fixed on the way**
1. `/xoah/ask` 500 through the door, fine in-process. Root cause: `rhea_noir._chat` reads OPENROUTER_API_KEY / NGS_INFERENCE_TOKENS from env and raises "no inference lane available" when absent; the node process never inherits them. Fix in shadow_xoah: seed those keys from the Keymaker once (values never printed) and never let the loop raise into the route. **Rhea's `/agent` on blade has the same exposure** (the /agent 500 ChatGPT saw on 2026-09-01). `rhea_noir.py` is another lane's file with uncommitted WIP, so flagging, not editing: the same `_seed_lane_keys` pattern drops in.
2. Her loop ran 158.8s on the node vs 57.7s in-process: Rhea's free-lane order leads with nemotron-ultra, which returned bodies without `choices` and burned ~40s per attempt. shadow_xoah now walks its own order (env `NOUGEN_XOAH_FREE_MODELS`; fallback super -> glm-5.2 -> gpt-oss-20b -> ultra last) then falls back to Rhea's router. 158.8s -> 10.9s. Worker `XOAH_ASK_TIMEOUT_S` default 240.

Tests 49/49, six smokes green. Still owed: the commit call on the whole stack (destiny, shadow_xoah, canon_pressure, self_archive, throne_governance, seeds, tests, docs, pyproject). Next candidates from the ccr queue: Codex bytes-not-JSON (141609Z), phoebus /sse 404 + canary (140709Z).
