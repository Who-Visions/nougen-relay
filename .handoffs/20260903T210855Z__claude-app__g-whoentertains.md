# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Rung 4 ruling on phoebus backfill: capture precondition MET at 17:08 EDT (ngsnode pid 8489 runs NOUGEN_EMBED_TIMEOUT=15); backfill launch handed to GM, exact command inside
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T21:08:55.767Z

---
# Phoebus backfill - end-to-end pass by blade super-65, 2026-09-03 16:48-17:10 EDT

## Measured (all via SSH, phoebus = KushBoyGroups-Mac-mini.local)
- Backfill was NOT running at 16:52 EDT. pid 4265 cited in 201920Z is `The Observatory/heartbeat.py --run` (5 days old). llama-server pid 96766 at 0% CPU. Unembedded counts identical to the 20:16Z figures.
- Nine vaults confirmed: 108,399 total / 15,927 unembedded (db1 0, db2 1456, db3 2144, db4 2072, db5 2101, db6 2027, db7 2104, db8 2027, db9 1996).
- Live capture node is `com.whovisions.ngsnode` -> `~/The Observatory/NouGen/nougenshards/bin/ngs-node.sh` -> `app.py` on 127.0.0.1:4444. That checkout is 0043dd3 (Sep 1, 10 behind origin/main). `~/.nougen/src/nougenshards` (d7d7d6b = origin/main) is NOT what serves captures.
- `core.py:677` in both checkouts already reads `NOUGEN_EMBED_TIMEOUT` with a 1.5 fallback. No code change needed to meet the precondition. The 291-line blade patch on branch `codex/shards-capture-main` (45 behind origin) was NOT deployed.

## Changed on phoebus (backups taken beside each file)
1. `~/Library/LaunchAgents/com.whovisions.ngsnode.plist`: added EnvironmentVariables.NOUGEN_EMBED_TIMEOUT=15 (bak-20260903T2057Z). NOTE: `launchctl kickstart -k` does not reload plist env; this only takes effect after a future bootout/bootstrap.
2. `bin/ngs-node.sh` line 23: env-file case now `NGS_*=*|NOUGEN_*=*)` so NOUGEN_* keys pass through (bak beside it).
3. `~/The Observatory/.env` line 89: `NOUGEN_EMBED_TIMEOUT=15`.
4. `launchctl setenv NOUGEN_EMBED_TIMEOUT 15` (user domain, harmless).
5. ngsnode restarted 3x; final pid 8489 verified with `NOUGEN_EMBED_TIMEOUT=15` in its environment via `ps -E`. Node startup takes ~5 min (lifespan runs `core.quarantine_malformed_dbs()` over 9 DBs before binding 4444).

## Rulings (Rung 4, standing authority)
- 183835Z token claim ACCEPTED; rotation from 183716Z cancelled.
- 201734Z precondition (capture budget on phoebus) is MET for node-path captures. CLI-path captures on phoebus still fall back to 1.5s until `export NOUGEN_EMBED_TIMEOUT=15` lands in `~/.zshenv` (blocked from blade; one-line manual add).
- 4000-char embed window ACCEPTED as interim; "backfill complete" != "fully searchable" and every completion claim must say so.
- Resume NOW at reduced impact (nice 15, batch 32) rather than waiting for dream-lane window: load is 2.8, owner requested end-to-end today.

## Launch (blocked by blade auto-mode classifier; GM or phoebus lane on GM say-so runs it)
```
ssh phoebus 'cd ~/.nougen/src/nougenshards && PYTHONPATH=src NOUGEN_EMBED_TIMEOUT=15 nohup nice -n 15 python3 -u -m nougen_shards.embedding_backfill --vault ~/.nougen/shards --model nomic-embed-text --batch 32 --execute > ~/.nougen/embedding_backfill_20260903b.log 2>&1 < /dev/null &'
```
Progress: `sqlite3 ~/.nougen/shards/nougen_shards_N.db "select sum(embedding is null) from shards"` per vault; log is unbuffered (-u).

## Done-when
All nine vaults report 0 unembedded AND a fresh capture through port 4444 lands with a non-NULL embedding (proves the gap does not regenerate). Report both numbers, not one.
