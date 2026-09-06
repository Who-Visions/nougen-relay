# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: nougen-mcp-server: MCP server source under version control, private, files NOT moved (external git-dir)
**Branch**: `main` @ `b4d8794`
**Stack**: (undetected)
**When**: 2026-08-12T17:28:01.889793+00:00

---
# nougen-mcp-server: MCP server source now under version control (private)

## What landed

`Who-Visions/nougen-mcp-server` — **private**, created 2026-08-12, first commit
pushed. Tracks the `nougen-fleet-registry` MCP server source, which had been
sitting untracked at Watchtower root.

Tracked set is the verified import closure, 8 files:
`local_search_mcp.py`, `search_service.py`, `models.py`, `helpers.py`,
`query_planner.py`, `search_strategies.py`, `infrastructure.py`, `fleetman.py`.

Includes the `write_memory` provenance fix: `DEFAULT_MEMORY_SOURCE` resolves
from env `NOUGEN_MEMORY_SOURCE` with an `"unattributed"` fallback, instead of
defaulting to the literal `"codex"` and misattributing every unlabelled write.

## The unusual part — read before running git in that directory

**The files did NOT move.** `.git` lives at
`Watchtower\nougen-mcp-server\.git`, but `core.worktree` points at
`C:/Users/super/Watchtower`.

Why: a full walk of 1,841,551 files found **15 executable/config references**
hardcoding `C:/Users/super/Watchtower/local_search_mcp.py` —
`elevation_audit_daemon.py`, both Iris daemons,
`Sol-Ai/tools/cf_tunnel_bringup.py`, `mesh_acceptance_test.ps1`,
`mesh_smoke_test_fast.ps1`,
`NouGen/NouGenShards-push-main/tools/nougenai_fleet_registry_mcp.py`,
seven `.mcp.json` / `mcp_config.json` files, and `C:\Users\super\.claude.json`.
Relocating would have broken all of them, several silently at logon. So
`.claude.json` needed no edit and nothing had to be re-pointed.

Consequences other machines should know:

- **Watchtower root is still NOT a git repository.** `git status` there reports
  "not a repository". Only commands run from `nougen-mcp-server/` see the repo.
  This is deliberate: no agent can stumble into staging the vault.
- **⚠️ NEVER run `git clean` from `nougen-mcp-server/`.** The worktree is all of
  Watchtower and nearly everything is ignored, so `-fdx` would wipe the tree.
  `clean.requireForce` is set. `git checkout .` / `reset --hard` are safe —
  tracked files only.
- **The allowlist is `.git/info/exclude`, NOT a root `.gitignore`.** ripgrep
  honours `.gitignore`, so a `/*` deny-all at Watchtower root would make every
  agent's code search silently return nothing. Do not "fix" this by moving the
  rules into a `.gitignore`.

Rules: deny `/*`, un-ignore the 8 files, then hard-deny `*.db`, `*.jsonl`,
`*.csv`, `*.env`, `secrets/`, `vault/`, `backups/`, `.gateway_tokens/`,
`agent_secrets*`, keys and tokens. Last match wins. Verified via
`git check-ignore`: `agent_secrets.db`, `vault/nougenai_memory_vault.db`,
`.env`, `.gateway_tokens/*` all ignored. Remote tree confirmed to hold exactly
9 blobs — the 8 sources plus the README.

`nougen_registry_ext.py` is **excluded on purpose** — its own docstring says it
lives outside the public repo; it is operator-private and loaded via
`NOUGEN_REGISTRY_EXT`. It still imports `models` / `search_service` from
Watchtower root, unchanged.

## Pre-commit secret scan: clean

Anchored patterns for OpenAI/Anthropic/Google/AWS/GitHub/Slack/HF/OpenRouter key
shapes, private-key blocks, assigned secret literals, the operator's home
address and name, emails, SSN/card/phone shapes, absolute user paths.

Result: no keys, no PII, no address. Only five `C:\Users\super\...` path
literals — all env-overridable except two `argparse` defaults in `fleetman.py`
(~L418, ~L424) that affect only its standalone CLI, not the MCP server.

## ⚠️ Open finding for whoever owns the mesh work

**Something other than this session edited four of these files mid-session.**
`local_search_mcp.py`, `search_service.py`, `helpers.py` and `search_strategies.py`
grew **+265 lines between 12:49 and 13:10 EDT on 2026-08-12** while the repo was
being built.

The diff is coherent feature work, not corruption: per-port gateway lock files
(`gateway_lock_file(port)`), lock records with liveness checks
(`read_lock_record`, `_holder_is_alive`, signal handler), `acquire_lock` retry
attempts, an FTS tokenizer (`tokenize`, `fts_query`), and `_mirror_after_write`
/ `_shard_row`.

I re-scanned the **current** content (clean) and compile-checked all 8 modules
before pushing, so the pushed snapshot is valid — but it is a snapshot of
in-flight work by another session or process. If that was you, pull before you
continue or you will diverge from the commit.

## Verification

- `mesh_health` → `PASS` both before and after; vault/registry/journal present.
- All 8 modules `py_compile` clean.
- `git status` in the scoped repo: 0.29s (deny-all stops the tree walk).
- Remote confirmed `visibility=PRIVATE`, `isPrivate=true`.

## Next

Nothing blocking. If the mesh work above is ongoing, commit it into this repo
rather than leaving it untracked at Watchtower root — that is the whole point of
the repo existing now.
