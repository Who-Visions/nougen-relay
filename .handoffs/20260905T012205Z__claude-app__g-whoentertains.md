# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RECALL ROOT CAUSE: phoebus is thrashing (swap 10/11GB, 23MB free, load 49-74); kaedracode:e2b pinned resident at 8GB owns the memory; node cache paged out, /search 66-81s. GM decision: unload the model?
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T01:22:05.496Z

---
# Recall on phoebus is memory-starved, not code-starved

**Measured 2026-09-05 01:10Z to 01:20Z on phoebus (this Mac mini, 16GB).**

## What the node looks like
- `POST /search` single caller, single-token queries: **81.4s, 76.9s, 66.5s**, each returning only the `FEDERATION_STATUS` trailer (local lane missed the 20s deadline).
- Node process (pid 51860, started 17:48 EDT on `b9c2834` = PR #220): **RSS 53 to 87MB**. A warm node holds ~800MB of vector matrices. They are paged out.
- 95 threads, 166 descriptors at idle (so the 256 ceiling from #220 is not what is biting now).
- Warm-up history in the node log: **678s and 622s** at 09:48 and 10:20 EDT, 10.6s at 17:49. Memory pressure has been shaping recall all day.

## What the box looks like
```
vm.swapusage: total = 11264M  used = 9975M  free = 1288M
PhysMem: 16G used (3536M wired, 1290M compressor), 23M unused
Load Avg: 49.54, 60.60, 74.58
```

## Who owns the memory
| process | MEM | compressed | note |
|---|---|---|---|
| llama-server (Ollama, `kaedracode:e2b`) | 8055M | 6316M | 6.4GB model, `expires_at` 2318 = keep_alive forever, up 3d22h, size_vram 0 |
| Comet Helper (Renderer) | 1164M | 790M | |
| Logi Bolt | 770M | 765M | |
| Python (shards node) | 584M | 529M | almost entirely compressed = paged out cache |
| uTorrent Web | 530M | 463M | |

## Why this reads as "recall is broken"
The node's cache is the first thing the kernel compresses when it sits idle between queries; every query then decompresses and pages 800MB back in behind an 8GB resident model on a 16GB box. `/health` stays 200 the whole time, the trailer says `complete:false`, and nothing names memory.

## Ask (GM)
1. **Go / no-go on `ollama stop kaedracode:e2b`.** Reversible: the next `kaedra_ask` reloads it. It is the one-command experiment that separates memory from everything else, and I expect it is the fix. Not pulling it without the owner because the persona lane depends on it.
2. If Kaedra must stay resident here: pick a smaller quant, or move the resident model off the always-on shards node. 8GB pinned plus the shards cache does not fit in 16GB alongside Codex, Comet and Claude.

## Status of the code fixes
- PR #220 (descriptor ceiling) merged and deployed on phoebus at 17:48 EDT. No `soft limit raised` line in the log yet; I am verifying the live limit separately.
- PR #222 (request must not queue behind a matrix build) merged on main, **not yet on the phoebus clone** (clone is 5 behind). A restart now would rebuild the cache into the same starved memory, so I am holding the redeploy until memory is decided.

-- phoebus / claude-app / g-whoentertains lane, acked legs 183645Z 202025Z 200011Z
