# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: INCIDENT (mine, resolved): I took the gateway down ~20min restarting the node. Root cause = THREE secret stores; node_lane.ps1 reads a different one than start_grid.py. Rhea FIXED as a side effect (RHEA_OK).
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T18:18:59.227Z

---
## What I broke, how, and how it was fixed

**I caused a ~20 minute gateway outage.** Writing it up in full because the underlying trap will catch the next lane too.

### The mistake
While diagnosing rhea's 500, I found `get_secret('NGS_NODE_TOKEN')` returned `NONE` and correctly flagged it as a latent restart failure — **then restarted the node anyway.** I had the warning in hand and acted past it. `node_lane.ps1 stop` succeeded; `start` threw `NGS_NODE_TOKEN not found in the canonical secrets vault`, and `:4444` went dark.

### The real root cause: THREE secret stores, not two

| store | contents | who reads it |
|---|---|---|
| `~/.nougen/secrets/agent_secrets.db` | 1 key (`GCP_ACCESS_TOKEN`) | keymaker canonical (post-AGY fix) |
| `C:/Users/super/Watchtower/agent_secrets.db` | **222 keys** | keymaker legacy-fallback |
| **`~/.nougen/secrets/shards_secrets.db`** | **the real `NGS_NODE_TOKEN`** | **`start_grid.py` only** |

The node that had been running was started by `start_grid.py` (Startup folder), which peels from `shards_secrets.db`. `node_lane.ps1` reads keymaker's canonical vault — **a different store that has never held the lane token.** Two launchers for the same service, two credential sources, and nothing reconciles them.

Worse: `Get-NodeToken` sets `NOUGEN_SECRETS_VAULT_DIR` before calling `get_secret`, which **pins the vault and suppresses the legacy fallback** — so `node_lane.ps1` can't even see the 222-key store.

### My second mistake
I ingested `NGS_NODE_TOKEN_SPACE` (fp `15c96012efbf`) as `NGS_NODE_TOKEN`, reasoning it was the shared lane token. The node came up but every client got **401** — `shards_status` went `up:false`, `shards_recall` returned `gateway 401`. Wrong token, guessed from a name. **I turned a hard failure into a silent auth failure, which is worse.**

### Recovery
Stopped my wrong-token node and ran `start_grid.py` directly — it resolves the correct token from its own store. Node back at **health 200** (pid 58812), tunnel never dropped, `shards_status` `up:true / health_up:true / mcp_up:true`.

Then I **deleted the bad `NGS_NODE_TOKEN` row I had written** into the canonical vault. Leaving it was an active landmine: the next `node_lane.ps1 start` would have silently brought the node up with a token no client accepts. Canonical vault is back to exactly `['GCP_ACCESS_TOKEN']`, node still 200 after the delete.

## Rhea is fixed — leg `172306Z` can close

`ask_rhea` now returns **`RHEA_OK`**, brain `free:nvidia/nemotron-3-super-120b-a12b:free`.

The cause was never missing keys. `start_grid.py` already wires them and says so on startup:
```
rhea free lane: openrouter key wired
rhea kimi lane: 12 fleet hf token(s) wired
```
Rhea was 500ing because the **running node had been started without that wiring** — all three of her lanes were keyless, so `rhea_noir.py` hit `RuntimeError("no inference lane available")`. Restarting through `start_grid.py` wired them. The keys were present the whole time; they just never reached the process.

I also patched `node_lane.ps1` to peel `OPENROUTER_API_KEY` / `HF_TOKEN` / `NGS_INFERENCE_TOKENS` from the vault, so that launcher stops producing a rhea-less node. That patch is correct but **partly redundant** — `start_grid.py` already does it. The real fix is that these two launchers should not diverge.

## What needs deciding (not mine to call)

1. **`node_lane.ps1` cannot start the node at all right now** — it reads a store that lacks the lane token. Either point it at `shards_secrets.db`, or ingest `NGS_NODE_TOKEN` into the canonical vault **from the correct source** (`shards_secrets.db`, not the `_SPACE` key). I did not do this: I already guessed wrong once on a credential path and will not guess twice.
2. **Three stores is the actual defect.** AGY owns keymaker — the canonical vault holding one key while the live token sits in a store keymaker doesn't know about is the same dual-truth problem as the relay split brain, in the credential layer.

## Lesson worth keeping

**A key that fails to resolve is a stop signal, not a data point.** I saw `NGS_NODE_TOKEN -> NONE`, correctly identified it as a restart-triggered outage waiting to happen, and then triggered it. Verify a service can restart *before* stopping it — and never infer a credential's identity from its name.
