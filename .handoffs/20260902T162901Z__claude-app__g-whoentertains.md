# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: VERIFIED END TO END: Codex itself ran `nougen search --dual --json` per AGENTS.md:58 and reported no exception, valid JSON, 768-dim embedding; same via nougen.bat and the shim (closes TODO 141609Z / leg 023518Z)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T16:29:01.735Z

---
## Codex bytes bug: closed by Codex's own run (blade1tb, claude-cli, 2026-09-02 12:28 EDT)

Follow-up to leg `20260902T161004Z`. Dave asked for end to end, so the fix was proven on the three surfaces that matter:
- **Git Bash shim** `bash tools/nougen search "self archive handoff" --dual --json`: valid JSON, 5 rules, 3 shards, 768-float embedding.
- **Windows** `nougen.bat` (full path via PowerShell, NOUGEN_NO_PAUSE=1): same, 0 TypeError.
- **A real Codex session** (`codex exec --skip-git-repo-check --approve-for-me -C <push-main>`, codex-cli 0.152.0) running exactly that command reported: no exception, exit 0; valid JSON with semantic_rules and episodic_shards; first embedding length 768.

Scripting notes for whoever drives Codex next: 0.152 has no `--full-auto`; `--sandbox` and `--approve-for-me` are mutually exclusive; Codex runs the prompt's command literally (a stray trailing period became "unrecognized arguments: ." on my first try). From Git Bash, call `nougen.bat` by full path through PowerShell; `cmd //c "cd /d ..."` gets its `/d` mangled by MSYS path conversion.

Shard "VERIFIED END TO END 2026-09-02 12:27 EDT" captured. Fix set still uncommitted on `codex/shards-capture-main` (core.py, cli.py, tools/nougen, tests/test_json_safe.py). Next from the ccr queue unless redirected: phoebus `/sse` 404 + blade+phoebus canary (140709Z).
