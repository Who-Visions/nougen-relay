# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Agy: apply and verify Dav1d VRAM-gate fix on Blade
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T16:13:11.410Z

---
## Root cause (live-measured on Blade, 2026-08-27)

`ask_dav1d` is advertised and MCP transport is healthy, but default Dav1d inference returns `[Dav1d] local and cloud runs failed` or hits the connector deadline. `dav1d:e2b` is installed. While loaded, `ollama ps` measured it at **2.7 GB, 100% GPU**. The mandatory VRAM admission map does not contain `dav1d:e2b`, so `check_vram()` refuses it as an unknown model before inference.

## Exact scoped fix

File:
`C:\Users\super\Watchtower\NouGen\NouGenShards-push-main\src\nougen_shards\vram_gate.py`

Inside `MEASURED_LOAD_GB`, add exactly:

```python
    # Measured live on Blade 2026-08-27 via `ollama ps` while Dav1d was loaded.
    "dav1d:e2b": 2.7,
```

Do not disable or bypass the VRAM gate. Do not route Dav1d to `gemma4:e2b-qat`; that model is not installed on this Blade. Preserve the env-first model route `NOUGEN_AGENT_MODEL_DAV1D`, currently restored to `dav1d:e2b`.

## Runtime setting already applied

User env `NOUGEN_NUM_PREDICT=256` was set to keep local agent generation below the connector deadline. Confirm it resolves in the restarted node; change only if live timing proves necessary.

## Verification

1. Run the relevant VRAM-gate/agent tests.
2. Restart only the verified `start_grid.py --watch` / `uvicorn app:app --host 127.0.0.1 --port 4444` tree so the source change loads.
3. Confirm `shards_status`: health 200 and MCP RPC OK.
4. Call `ask_dav1d` with prompt `Reply exactly DAV1D_OK` and no model override. Done only when it returns successfully inside the connector deadline.
5. Capture a durable fix shard and ack/close this relay with commit/diff and runtime evidence.

## Why Codex did not apply it

Both parent and fleet-worker `apply_patch` attempts failed before touching the file because the Windows filesystem sandbox helper cannot spawn: `SetTokenInformation(TokenDefaultDacl) failed: 1344`. No source file was changed.
