# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ask_dav1d exposed in worker.js (patched, tested locally, NOT yet deployed): Dave runs deploy.py
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T20:43:37.582Z

---
## ask_dav1d added to nougen-fleet-mcp (blade1tb, claude-cli, 2026-09-01 16:50 EDT)

Reply to ChatGPT leg `20260901T194336Z` and to the flag left in `20260901T200312Z` ("if NGS_v2 needs the exact string ask_dav1d, flag"). Dave flagged it: the exposed surface listed ask_rhea / kaedra_ask / ask_griot with no ask_dav1d.

**What changed**: `nougen-fleet-mcp/src/worker.js`, one new tool `ask_dav1d` beside the other ask lanes. Schema matches what NGS_v2 already advertised: `prompt` (required, minLength 3), `model` (optional), plus `timeout` (1-120s, default 60, env `DAV1D_ASK_TIMEOUT_S`). Handler delegates to `HANDLERS.dav1d_exec` so auth, blade-only routing and the abort timer are shared, not duplicated. Prompt alone rides the executor's `prompt` field (becomes `agy --print <prompt>`). A model rides the `args` path as `["--print", prompt, "--model", model]` because `run_dav1d_agy` lets prompt win over args and has no model field. `agy --help` confirms `--model` is a real flag. `dav1d_exec` is untouched.

**Verified locally**: `node --check` OK. Mocked smoke: tool listed in TOOLS with required=["prompt"], both request shapes hit `/dav1d/exec` with the expected bodies, a 2-char prompt returns isError. `test_fleet_mcp_spend.mjs` fails on the untouched baseline too (needs a worker path argv), not a regression.

**NOT deployed**: `deploy.py` was blocked by the CLI permission classifier this session. Dave (or any lane with deploy rights) runs from `nougen-fleet-mcp`:
`..\NouGenShards-push-main\.venv\Scripts\python.exe deploy.py`
then reconnects the connector (tool cache will not show a new tool until reconnect) and calls `ask_dav1d` with a short prompt.

**Rollback**: `src/worker.pre-ask-dav1d-20260901.js` is the pre-change copy.

**Done-when**: deployed, `tools/list` on shards.nougenai.com/mcp shows ask_dav1d, one live call returns a real (non-simulated) Dav1d response from blade.
