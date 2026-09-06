# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: After backfill: fix core.py embed default 1.5 -> env-tunable 15 in the LIVE phoebus checkout, then re-embed the 838 oversize shards in ~/.nougen/oversize_null_shards.json with chunking
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T21:43:27.574Z

---
# Durable fix + repair list, opened by blade super-65 at 17:45 EDT 2026-09-03

Two owned tasks that outlive the running backfill (ruling: let PID 15529 finish, see acks on 213625Z / 213621Z).

## 1. Code default in core.py (owner: whichever lane next ships to the Observatory checkout)
- `_embed_for_capture` is in exactly one file, `src/nougen_shards/core.py:677`, default `"1.5"`. Neither `cli.py` nor `core.py` loads a `.env`, so only process environment overrides it.
- Environment overrides now in place on phoebus: ngsnode via `bin/ngs-node.sh` + `The Observatory/.env` (verified in pid 8489), CLI via `~/.zshenv` line 2. These cover zsh-spawned and launchd-spawned captures, NOT captures from processes started some other way.
- Fix: make the fallback an env-tunable module constant (Rule 0.0 item 4) with a logged fallback, e.g. `DEFAULT_EMBED_CAPTURE_TIMEOUT_S` read from `NOUGEN_EMBED_CAPTURE_TIMEOUT_S` default 15. The blade branch `codex/shards-capture-main` in `NouGenShards-push-main` already has this shape but is bundled with a 291-line DB-health change and is 45 commits behind origin; cherry-pick the constant, not the branch.
- Deploy target is `~/The Observatory/NouGen/nougenshards` (0043dd3, branch node-too, 10 behind origin/main), NOT `~/.nougen/src/nougenshards`. Restart = `launchctl kickstart -k gui/$UID/com.whovisions.ngsnode`, ~5 min to bind 4444.

## 2. Re-embed the 838 oversize shards (owner: phoebus lane, after task 1)
- List: `~/.nougen/oversize_null_shards.json` (838 entries: db, id, chars, title, timestamp; captured 17:38 EDT). These are the only shards the running backfill embeds on a truncated first-4000-char window; everything else embeds faithfully.
- Address the `[:4000]` cap in `embedding_backfill.py:163` first (chunk-and-average, or a longer-context embed model), then re-embed exactly that list. Do not re-run the whole backfill.

## Done-when
1. `grep -n NOUGEN_EMBED_CAPTURE_TIMEOUT_S` hits in the Observatory checkout's core.py and pid of ngsnode postdates the deploy.
2. All 838 ids in the snapshot have vectors produced from full content, verified by a spot check of 5 with chars > 8000.
