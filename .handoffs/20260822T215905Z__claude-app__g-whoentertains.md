# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: dav1d_exec now resolves agy version at call time (live probe, verified 1.1.18); uncommitted in push-main alongside other lanes' work
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-22T21:59:05.323Z

---
## What was broken

`src/nougen_shards/dav1d_executor.py` never probed the binary. `get_agy_version()` opened with `if _CACHED_VERSION: return _CACHED_VERSION` against a module constant set to `"1.1.17"`, so the probe branch was unreachable dead code. Blade's actual binary reports **1.1.18**. Every execution receipt the bridge published carried a version nobody had observed.

`tests/test_dav1d_executor.py` asserted `ver == "1.1.17"`, which locked the defect in. A test that asserts the constant cannot catch the constant going stale.

## Fix

Version now resolves `NOUGEN_AGY_VERSION` env override -> live `agy --version` probe -> `"unknown"`. It never returns a version it did not observe, because that string is published to the fleet as runtime evidence and an invented one is worse than no answer.

- `NOUGEN_AGY_VERSION_TIMEOUT_SEC` (default 5) bounds the probe.
- `NOUGEN_AGY_VERSION_CACHE=0` disables the per-process memo; `get_agy_version(path, refresh=True)` forces a re-probe.
- Rejected-subcommand branch reports a resolved version instead of the constant.
- Simulated branch (no binary, e.g. HF Space) now reports `unknown (no agy binary on this host)` instead of claiming `1.1.17 (fleet manifest)`.
- `app.py` tool docstring no longer advertises `agy v1.1.17` to MCP clients; it points at the `version` field in the result.

Tests rewritten to assert behavior: env override wins, no binary yields unknown, a bad path yields unknown rather than an invented version, and where a real binary exists the reported version equals what the binary prints.

## Verified on Blade

```
{'host': 'Blade Node (Stadium)', 'version': '1.1.18', 'status': 'success',
 'exit_code': 0, 'output': '1.1.18',
 'binary_path': 'C:\\Users\\super\\AppData\\Local\\agy\\bin\\agy.exe'}
```

Real process, real exit code, real stdout. That is the local half of the bridge genuinely working, which also sharpens the earlier finding: the gateway path returns `simulated` only because the cloud Space cannot reach this binary, not because the executor is broken.

`pytest tests/test_dav1d_executor.py tests/test_mcp_endpoint.py` -> 14 passed (venv interpreter, since gradio is absent from system 3.11 and those 9 endpoint tests silently skip there).

## State

Changes are **uncommitted** in `NouGenShards-push-main` on `main` at `147cd56`. The tree also holds unrelated uncommitted work from other lanes (`cli.py`, `core.py`, `history.py`, `connectors/*`, `agents.py`, `keymaker.py`), so I did not commit and sweep someone else's in-flight changes into it. Mine are `src/nougen_shards/dav1d_executor.py`, `tests/test_dav1d_executor.py`, and one docstring in `app.py`.
