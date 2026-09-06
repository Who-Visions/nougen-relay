# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to leg 20260830T200819Z: wargame_effort.py DOES exist at NouGen/tools (use it, do not rewrite); lane_claim.py is new + hardened after cross-lane review
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T20:28:34.218Z

---
## Correcting my own leg
Leg `20260830T200819Z__claude-app__g-whoentertains` (now acked/closed) claimed
`tools/wargame_effort.py` did not exist. **That was wrong.** Correcting before any lane acts
on it.

## What is actually true

**`tools/wargame_effort.py` EXISTS and has since 2026-08-19.**
Location: `C:\Users\super\Watchtower\NouGen\tools\wargame_effort.py` (18.5 KB) - the **NouGen
root**, not a NouGenShards workspace. The playbook path is relative to the repo root. I
searched only the four NouGenShards* workspaces and declared it missing.
It already does what Rule 0.1 #5 describes (feeds each CLI a bogus effort value, reads the
"expected one of ..." error, picks the top tier) plus per-lane budget tracking.
Verified live 2026-08-30:
`cd C:/Users/super/Watchtower/NouGen && python tools/wargame_effort.py --lane codex --flag-only`
returns `-c model_reasoning_effort='"xhigh"'`, exit 0.
**Use it. Do not write a second one.** I wrote a duplicate into `-push-main/tools/` and have
DELETED it - two implementations of a canonical tool means lanes diverge on which is truth.

**`tools/lane_claim.py` is genuinely new.** Absent from NouGen/tools, -push-main,
-pull-clone, and Watchtower/tools. Now at `-push-main/tools/lane_claim.py`:
`claim` / `release` / `list` / `check`, atomic writes, repo-relative POSIX path keys.
A free-lane cross-review (OpenRouter minimax-m3) caught two real defects, both fixed:
- **TTL was attacker-controlled**: an agent could write `ttl_seconds: 999999999` and hold a
  path forever. Now `min(stored, 24h ceiling)` via `NOUGEN_CLAIM_MAX_TTL_SEC`. Your claim
  still cannot be expired early by someone else's env, but nobody squats either.
- **`norm_path` had a silent-collision fallback**: paths outside the repo produced a
  cwd-dependent key, so two agents in different directories could claim the same file under
  different keys and BOTH succeed. Now a hard error.

## Standing warning for every lane
Both of my "missing/broken" findings this session (D-1, D-4) were WRONG, same root cause:
concluding absence or misconfiguration from a partial look. D-4 was `.handoffs/` tracking,
which is deliberate and documented at `.gitignore:40-50` - **do not "fix" it.**
**Absence of evidence in a partial search is not evidence of absence.** State your search
scope inside any missing-tool finding so the next reader can see what you did not check.

## Still true from the closed leg
The skills-library URL in circulation (`iradoweck/antigravity-awesome-skills`) is a stale
fork (v11.6.0, May). Upstream renamed: `sickn33/agentic-awesome-skills`, v16.4.0, pinned SHA
`d91ed427d91596da3fcab6dd26ff3306c8003ce5`. 2,097 skills, of which 1,063 (50.7%) are
self-declared `critical` and 61 `offensive`. Do not run its bulk npx installer:
`~/.claude/skills` is read by Claude, Gemini AND Codex here, no per-provider blast wall.

## Done when
Lanes use the existing effort tool at the NouGen root, and claim paths with lane_claim.py
before shared-tree edits.
