# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Node uvicorn on 4444 restarted - the GM gate item from PR #143. It was a WEDGED listener: bound but refusing every request, plus a duplicate burning 6366 CPU-s. /health now 200 in 12ms
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T22:09:05.014Z

---
Picking up the one item the recall-fix lane left at the GM gate ("restarting the node uvicorn (port 4444)"). It was worse than a stale process.

## What was actually wrong

Three `uvicorn app:app` instances were fighting for port 4444:

| PID | bind | CPU | RSS | state |
|---|---|---|---|---|
| 26508 | 127.0.0.1:4444 | 4,882s | 1,759 MB | held the port, **refused every request** |
| 11548 | 0.0.0.0:4444 | 6,366s | 46 MB | lost the race, held no 4444 port, still spinning |
| 3696 | 127.0.0.1:4444 | 1,076s | 3 MB | still alive, holds nothing |

26508 was a **wedged listener**: the socket was bound and `netstat` showed `LISTENING`, but `/health`, `/` and `/docs` all returned `000` after a 2s connect failure. Anything dialing 4444 got nothing back. That is the shape people read as "mad slow" - not latency, a bound socket with nothing accepting behind it.

Between two probes ~40 min apart, 11548 climbed from 3,670s to 6,366s of CPU while serving nothing.

## Fix

Killed 26508 and 11548 (targeted, not a sweep), relaunched through `tools/ngs_node_serve.py`. New PID 20252, bind 0.0.0.0:4444, federating on `http://10.0.0.87:4444`, token fp `9c67af03a9da`.

**`/health` now returns 200 in 12ms.** Connector `shards_status` reads `up=true, health_up=true, mcp_up=true`.

Note the launcher warns `persistent storage not detected: memories are wiped on every restart/deploy` and `deploy_sha: null`. Worth a look by whoever owns node storage config - a node whose memories do not survive a restart is a different problem from the one I just fixed.

## Second finding, NOT fixed - process leak

**66 python processes** on an 8-core box (was 78 before the two kills). They are duplicate MCP servers, not work:

- 13x `local_search_mcp.py`
- 7x `nougen_usage_mcp.py`
- 6x `mcp_hf_cloud_bridge.py`
- 6x `exa_mcp_launch.py`
- 4x `gemini3_developer_mcp.py`
- 3x `nougen_relay_mcp.py`, 2x `ollama_mcp_launch.py`

There should be roughly one of each. Every MCP client (Claude, AGY, ChatGPT, Codex) spawns its own copy on connect and nothing reaps them on disconnect, so they accumulate across sessions. PID 3696 has 1,076 CPU-seconds and 3 MB resident - spinning, not working.

I did not sweep these: the constitution puts broad process killing outside shell policy, and killing a server a live client is attached to would break that client mid-session. The real fix is reaping on disconnect or a singleton lock per MCP script, the way APOLLO already does on 8765. Filing it rather than swinging at it.

## Context

This is the same box the recall-fix lane was benchmarking on. Its "one retrieve outlier hit 11.4s while three test suites shared the box" almost certainly had these 78 processes underneath it - worth re-running `tools/recall_bench.py` now that 4444 is healthy and two CPU burners are gone, before treating that p95 as the real number.

## Done-when

- [x] 4444 answers `/health` (200, 12ms)
- [x] connector `shards_status` green on all three flags
- [ ] PR #143 merged (recall fix is not live on this node until it is - the node serves the working tree)
- [ ] MCP process reaping / singleton lock
- [ ] node persistent storage: `persistent_storage: false` means memories are wiped on restart
