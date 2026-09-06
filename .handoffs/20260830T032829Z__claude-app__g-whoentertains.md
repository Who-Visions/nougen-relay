# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Added relay, fleet and shards-memory skills to NouGen/skills + ~/.claude/skills; CLAUDE.md prose for Rules 0.0.1/0.5.1/0.0 is now duplicated and should be slimmed to pointers
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T03:28:29.650Z

---
## Situation

Three new skills authored and installed on both surfaces (identical `<name>/SKILL.md` format, so one source serves both):

- `relay` — Rule 0.0.1 baton protocol
- `fleet` — Rule 0.5.1 parallel dispatch
- `shards-memory` — Rules 0.0/0.6 shard memory

Source of truth: `Outpost\NouGen\skills\<name>\SKILL.md`, mirrored byte-identical to `C:\Users\super\.claude\skills\<name>\SKILL.md`. Verified: NouGen `skills.discover()` finds all 8 skills; YAML frontmatter parses; Claude Code Skill tool picked all three up live.

Drafted by `gemma4:e2b-qat` per Rule 0.7, then substantially rewritten as coach — the drafts inverted several facts (claimed `relay_create` publishes, that `relay_ack` means "acknowledge completion", and emitted invalid Python for `Fleet()` init).

## Facts corrected against the source while writing these

1. **`git_handoff.py` is NOT at `NouGen/tools/`.** CLAUDE.md Rule 0.0.1 gives that path; it does not exist. The script lives in each consuming repo: `Outpost\NouGenQ\tools\`, `Outpost\NouGenTv\tools\`. **CLAUDE.md should be corrected.**
2. **`Fleet._call` defaults to `max_tokens=800`** — below the ~1400 E-series floor CLAUDE.md itself mandates. So `f.map(prompts)` without an explicit `max_tokens` silently starves E-series routes (empty content at HTTP 200). Callers must pass `max_tokens=2048`.
3. **CLAUDE.md's Rule 0.5 priority list omits `vertex` (rank 6, BILLED, gated behind `NOUGEN_VERTEX=1`)**, and omits `diversify()` / `by_vendor()`, which are the only way to get genuine model diversity rather than account diversity.
4. **Vault cwd trap confirmed concretely**: `Outpost\NouGen\.vault` EXISTS, and `core.py` resolves `./.vault` ahead of `~/.nougen/shards` when `NOUGEN_VAULT_DIR` is unset. Any capture run from that directory silently lands in the stray vault.
5. **`relay_create` publish semantics differ by surface**: CLAUDE.md's "create does not publish" is a `git_handoff` CLI behaviour; the MCP `relay_create` states its legs land open for other lanes. Scoped accordingly in the skill.

## Ask

1. Slim CLAUDE.md Rules 0.0.1 / 0.5.1 / 0.0+0.6 down to one-line pointers at these skills, so the protocol has one home instead of two that can drift.
2. Fix the `git_handoff.py` path in Rule 0.0.1 (item 1 above).
3. Consider raising `Fleet._call`'s default `max_tokens` from 800 to 1400+ (item 2) — the current default contradicts the documented floor.

## Done when

CLAUDE.md points at the skills rather than restating them, the git_handoff path is accurate, and the fleet default no longer starves the routes it is most often used with.
