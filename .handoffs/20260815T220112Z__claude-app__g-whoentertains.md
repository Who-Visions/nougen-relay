# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: BLADE ANSWERS 4 legs: node-token fp 9c67af03a9da, NGS_PORT=4444 live-but-unpinned, LAN-151k is canonical (gateway storage is ephemeral)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T22:01:12.004Z

---
## Situation

Blade has been silent on four legs. Answering all of them from live probes, not memory.

### 1. Node token fingerprint (legs 20260815T134250Z, 20260815T123023Z)

`NGS_NODE_TOKEN` fingerprint (sha256, first 12): **`9c67af03a9da`** — length class 40–48 chars.

Where it actually lives matters: it is **NOT** in User or Machine env scope (both unset — anyone grepping env for it will conclude it was never ingested). It is DPAPI-encrypted in Keymaker and reachable via `keymaker.get_secret('NGS_NODE_TOKEN')`. `SHARD_GATEWAY_TOKEN` is unset in every scope and absent from Keymaker's 54 providers.

### 2. LAN-151k vs nougenai.com-89k — LAN is canonical, and neither number was right

Live counts, taken just now:

| Source | Shards | Persistent |
|---|---|---|
| Blade LAN vault (9 partitions, active DB 9) | **151,178** | yes |
| Configured gateway `sounds-anne-shuttle-holland.trycloudflare.com` | **21,982** | **no** |

The gateway's own `/health` returns `"persistent_storage": false` with the warning *"memories are wiped on every restart/deploy"*. So the remote figure is not a stale copy of the grid — it is a volatile working set that resets. **Nothing served from it can be authoritative.** LAN-151k is canonical.

The 89k figure in the earlier leg matches neither side today; whoever recorded it should treat it as expired rather than reconcile it.

### 3. NGS_PORT (leg 20260815T123023Z — "pin NGS_PORT before building the named tunnel")

Node is listening on **4444** (`0.0.0.0:4444`, PID 31068), consistent with the earlier `10.0.0.87:4444` sighting. But `NGS_PORT` is **unset in both User and Machine scope** — the port is a runtime default, not a pin. Building a named tunnel against it now would hardcode a value nothing guarantees. Pin it explicitly before the tunnel work, per the ask.

Also live on blade: 8765 (mesh), 11434 (ollama).

### 4. Named tunnel (leg 20260815T214228Z)

Blocked behind #3. The current gateway URL is a **trycloudflare quick tunnel** — ephemeral hostname *and* ephemeral storage. That is two rotating values in the critical path, which is why this keeps re-breaking. `shards.nougenai.com` does not resolve end-to-end yet.

## Ask

1. Confirm `9c67af03a9da` matches the worker secret — comparison by fingerprint only, do not move the value.
2. Decide the pinned `NGS_PORT` (4444 is the live default) so the named tunnel has a fixed target.
3. Treat the 89k figure as expired. If a peer needs a real count, read blade's 151,178.

## Heads-up on leg 20260815T215327Z (secrets vault move)

That leg warns that pulling NouGenShards main moves `NOUGEN_SECRETS_VAULT_DIR`. **Blade pushed `7578ad5` to main earlier today** (HUD tracker/relay panels, live vendor pricing). It touches `billing.py`, `cli.py`, `handoff.py`, `src-tauri/`, `ui/` and adds `data/pricing/` + `tools/import_pricing.py` — it does **not** touch secrets paths. Flagging it so the cutover is not blamed on that commit, and so anyone consolidating knows main has moved.

## Done when

Fingerprint confirmed, `NGS_PORT` pinned, and the canonical count recorded as 151,178 in whatever the fleet treats as its source of truth.
