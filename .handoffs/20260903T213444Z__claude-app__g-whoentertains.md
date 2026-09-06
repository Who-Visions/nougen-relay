# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Phoebus backfill RUNNING since 17:31 EDT by GM order (blade super-65 holds the SSH session); ~1 shard/s, load 20, ETA ~4h; do not start a second one
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T21:34:44.270Z

---
# Phoebus backfill launch record, 2026-09-03 17:31 EDT

Launched by blade super-65 on Dave's explicit "end to end do it" (17:31 EDT), superseding the hand-to-GM in leg 210855Z. Precondition from 201734Z was already met (ngsnode pid 8489 with NOUGEN_EMBED_TIMEOUT=15; zshenv line 2 now also sets it for CLI captures).

Command (running in the foreground of a held SSH session from blade, so it dies if that session drops; commits per row, so a restart resumes the remaining backlog with no loss):
```
cd ~/.nougen/src/nougenshards; PYTHONPATH=src NOUGEN_EMBED_TIMEOUT=15 nice -n 15 python3 -u -m nougen_shards.embedding_backfill --vault ~/.nougen/shards --model nomic-embed-text --batch 32 --execute
```

First-minute measurements (17:32 EDT): 1 backfill process, llama-server pid 96766 at 810% CPU, db2 1456 -> 1392 unembedded, load 20.13 / 7.96 / 4.56. nice on the Python driver does not throttle ollama; the load is the embedder, and the 201511Z resource concern is real but accepted by GM order. Rate ~1 shard/s -> ~4.4 h for 15,927.

Rules while it runs: do NOT launch a second backfill (two drivers double the ollama load and race on the same rows). If the process is gone and counts are still nonzero, relaunch the same command once, from ~/.nougen/src/nougenshards.

Done-when unchanged: all nine vaults at 0 unembedded AND one fresh capture through 127.0.0.1:4444 with a non-NULL embedding. Blade super-65 will post the closing numbers.
