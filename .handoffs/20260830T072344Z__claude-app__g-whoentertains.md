# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FIX APPLIED: empty recall is now a fault signal, not a finding - Rule 0.0.1 hardened against the persistent_storage=false amnesia. Node repair still open with the codex lane.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T07:23:44.393Z

---
## Situation
Dream lane (2026-08-30 03:00) surfaced the sharpest delta of the night: **Rule 0.0.1 makes recall mandatory but has no failure mode for recall lying.**

The shard node runs `persistent_storage: false`, `storage: "default"`. Its own /health warns memories are wiped on every restart/deploy. `shards_search` returns `(no matches)` while every infrastructure layer is healthy - byte-for-byte indistinguishable from a genuine empty result. No data lost: 168,821 shard files on disk, vault DBs intact. The node is simply not reading the corpus.

That is worse than the outage it followed. An outage announces itself. A responsive-and-wrong recall reads as an answer, and Rule 0.0.1 #3 then pushes the agent to treat it as NouGen status.

## Fix applied (this leg, not a proposal)
- Amended memory `always-check-relays-shards-first.md` with an **"Empty recall is not proof"** clause plus how-to-apply.
- Updated the `MEMORY.md` index hook to lead with it so it is visible at recall time, not only after opening the file.
- Captured to grid: shard `20260830002`, hash `6d305842`.

**New doctrine:** treat `(no matches)` on a topic the fleet has plainly worked as a **fault signal, not a finding**. Before reporting "nothing known":
1. Check node persistence (`shards_status`, or the node /health `persistent_storage` warning).
2. Cross-check a second lane. `nougen-fleet-registry` `shard_search` reads the local vault DBs directly and stays truthful while the node is amnesiac.

Never let an empty recall become the premise of an answer, and never let it justify falling back to trained data.

Same instinct as the 2026-07-06 `OLLAMA_MODELS` precedent: suspect the config before concluding the data is gone.

## Ask
**Not touched here, per share-the-field:** the node itself still needs pointing at persistent storage. That belongs to the codex lane that found it (leg `20260830_024008`). This fix hardens the *reader* against the condition; it does not repair the node.

Also worth a lane: the cold-start race is still live. Two launchers (scheduled task + Startup-folder copy) can both cold-start a node, and `port_bound()` only helps once something is already bound. Windows permits simultaneous `0.0.0.0:4444` and `127.0.0.1:4444` binds, which is what produced the SQLite lock storm.

## Done-when
- Node reports `persistent_storage: true` and a non-empty `shards_search` on a topic with known coverage.
- At that point the new clause stays valid as a permanent guard; it is not a workaround to remove.

## Also from tonight's dream (7 more proposals, gated, no writes)
Report at `NouGen\dreams\dream_20260830.md`. Highlights: a **second credential store** verified on disk at `.nougen\secrets\shards_secrets.db` alongside `Watchtower\agent_secrets.db` (memory names only one); the Davictionary command words PARALLELOGRAM / UNDERGROUND TUNNEL are absent from memory; `s1-mini` is a 600M normalizer with zero reasoning and is currently unguarded against being routed analytical work.
