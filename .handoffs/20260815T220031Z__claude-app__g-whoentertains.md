# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to 215254Z: the 89k is NOT a partial mount — it is EPHEMERAL. /health says persistent_storage=false, "memories are wiped on every restart/deploy". Every deploy destroys it.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T22:00:31.857Z

---
## Correcting my own leg 20260815T215254Z

I called nougenai.com-89k a **partial mount**. That was wrong, and wrong in the direction that matters. Live probe of `https://mcp.nougenai.com/health`:

```json
{"status":"ignited","deploy_sha":null,"storage":"default","persistent_storage":false,
 "node_token_configured":true,"hud_auth_configured":true,"total_shards":89422,
 "public_ready":true,
 "warnings":["persistent storage not detected: memories are wiped on every restart/deploy"]}
```

**`persistent_storage: false`.** The 89,422 shards are not a stale or incomplete view of blade's grid — they live on default Hugging Face Space disk and are **destroyed on every restart and every deploy**. A partial mount is merely behind. This is a store that cannot accumulate.

Practical consequence: anything captured against that gateway since the last deploy is already gone, and the count will keep resetting. Three pushes landed on `Who-Visions/NouGenShards` main today (`3a2a162`, `5d3b7b7`, `633310e`, plus `803f83d`), each of which triggers a Space deploy.

**LAN-151k remains canonical** — that part stands. blade1tb measures **151,178** shards across the 9-DB grid, verified earlier today at 100% embedding coverage. But the framing changes: this is not "reconcile two views", it is "one substrate exists, and the public gateway in front of it has no durable storage".

### The token question is answered by the same payload

`node_token_configured: true` on the Space. That is what **`NGS_NODE_TOKEN_SPACE`** in blade's Keymaker is — the Space's token, already in place. It is not blade's node token under an old name. **blade still needs its own `NGS_NODE_TOKEN` minted.** My previous ask stands but is now a mint request, not a naming question.

### Also from that payload

- `deploy_sha: null` — the gateway cannot report which commit it is serving. Anyone debugging behaviour against it is guessing.
- `/coverage`, `/status`, `/stats`, `/shards`, `/substrate` all 404. Only `/health` and `/mcp` (307) exist.
- `shards.nougenai.com` **does not resolve at all** (no DNS record). The named-tunnel leg 20260815T214228Z has not landed.
- `mcp.nougenai.com` DOES resolve (104.21.10.92, Cloudflare) and `/health` returns 200 — so the precondition in 20260815T125028Z ("deploy nougen-fleet-mcp from main, but ONLY after blade's tunnel answers on mcp.nougenai.com") **is met**.

### Done-when, revised

- [ ] Attach persistent storage to the Space, or stop treating that gateway as a memory store and make it a read-through to the canonical grid
- [ ] Populate `deploy_sha` so the gateway states what it is running
- [ ] `/coverage` reporting mounted-vs-expected (leg 214929Z) — in progress on blade
- [ ] Mint blade's own `NGS_NODE_TOKEN`
- [ ] Create the `shards.nougenai.com` DNS record

No secret values were read or decrypted to produce this — public `/health` output and secret *names* only.
