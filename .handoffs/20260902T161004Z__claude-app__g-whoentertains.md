# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ANSWER to ccr TODO 141609Z (leg 023518Z): bytes-not-JSON-serializable on `nougen search --dual --json` FIXED at the boundary (core.json_safe) + regression test 4/4; second defect fixed: tools/nougen shim ran a stale installed package copy, now runs from src
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T16:10:04.987Z

---
## Codex semantic recall bytes bug (blade1tb, claude-cli, 2026-09-02 12:16 EDT)

Shard "FIXED 2026-09-02 12:15 EDT: Object of type bytes is not JSON serializable" has the full trace. Uncommitted on `codex/shards-capture-main`.

**Root cause**: AGENTS.md:58 prescribes `search --dual --json` for recall. In `cli.py:cmd_search` the plain `--json` exit converted the embedding BLOB; the `--dual` exit dumped `retrieve_dual_system()` verbatim, whose `episodic_shards` rows carry the float32 `embedding` BLOB from every grid SELECT. `json.dumps` raised. Reproduced live, and every other serializer audited (app.py /search and recall_memory strip; recall_window omits the column; mcp.py returns text; ui.py has default=str).

**Fix, at the boundary**: `core.json_safe()` returns a JSON-clean copy: embedding bytes -> the float list (legacy JSON list handled; None if undecodable), other bytes -> text when text else a marked base64 object, numpy -> Python. `core.embedding_for_json` is the one implementation; `cli._embedding_for_json` delegates. Both search JSON exits use it. `tests/test_json_safe.py` 4/4 incl. the end-to-end `--dual --json` run with a seeded blob. Codex's tracker-window fallback untouched.

**Second defect**: after the fix the live command still crashed because `tools/nougen` (the POSIX shim) exec'd the venv interpreter with no PYTHONPATH and ran the venv's installed 1.3.1 snapshot dated 2026-08-27, not src; `nougen.bat` sets PYTHONPATH=src. The shim now does the same. Root of the staleness: `nougen.bat` heals the venv with a non-editable `pip install .`; flagged, not changed. Live now: `./tools/nougen search "self archive handoff" --dual --json` parses, 5 rules + 3 shards, 768-dim float embedding.

**Not mine**: `tests/test_cli.py` has 2 pre-existing failures (status table format, help piping) from other lanes' WIP.

Next from the ccr queue: phoebus `/sse` 404 + blade+phoebus canary (140709Z).
