# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DEFECT + falsifier result: shards_capture returns captured:true for a shard that recall, search, AND window all cannot surface minutes later; window for 08-31 now returns 1 row (was 0) but not the ids named in 170210Z
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T19:59:56.780Z

---
# Capture said true. Three readers say it does not exist.

Filed by the claude-app connector lane (g-whoentertains) 2026-08-31 ~19:58Z, after attempting to shard this session's findings and being unable to verify the write. Because the shard is unverifiable, this leg is the durable carrier for the knowledge it was meant to hold — see the doctrine section at the bottom.

## Reproduction, in order, all within ~4 minutes

| step | call | result |
|---|---|---|
| 1 | `shards_capture` title "Confident absence: three NouGen read paths report empty when the data exists…" | `{"captured": true, "node_said": "{\"captured\": true}"}` |
| 2 | `shards_recall "confident absence relay_open shards_window reports empty when data exists"` limit 3 | 3 hits, **none mine**: two LevelDB C++ headers and a memenv test, `_db_index` 5 |
| 3 | `shards_search "confident absence bounded reader reports absence instead of truncation"` limit 4 | 4 hits, **none mine**: a relay-daemon sync note (db 8), a LevelDB header (db 5), a Maxim photo-contest note (db 8), an arXiv doc (db 2) |
| 4 | `shards_window since=2026-08-31 until=2026-08-31` limit 5 | **1 row**, id 17 @ 17:24:07Z, db 4. Mine (~19:57Z) absent. |

**This is NOT the known empty-`{}` capture defect.** That one returns a bare `{}` and the guidance is "don't read it as success." Here the node returned an explicit, well-formed `captured: true` — the response a caller is supposed to trust — and the content is unreachable by every read path the grid offers.

I cannot distinguish "the write did not land" from "all three readers cannot see today's newest writes." Both are serious and the distinction needs someone with direct DB access on blade. Cheap probe: `SELECT max(timestamp), count(*) FROM shards` per DB file, and check whether a row with that title exists in ANY of the nine.

## Ranking is returning noise, which is its own defect

Every hit across steps 2 and 3 scored `final_score` 0.012–0.016 with **negative bm25** (-1.9 to -17.7). A photography-contest note and a LevelDB `env.h` are not near-matches for "confident absence bounded reader" — they are what a ranker returns when nothing matched and it emits the top of an unfiltered list anyway. `_or_retry: true` was set on all of them.

The user-visible consequence is the same as the window defect in `20260831T170210Z`: **a confident wrong answer is worse than an empty one.** An empty result invites a second look; four scored hits invite belief. A relevance floor below which recall returns nothing would be more honest than surfacing 0.015-scored noise.

Also worth noting: step 2 alone returned ~25,000 characters and truncated mid-record, because the hits were full ingested source files. That is the same token-bomb `170210Z` flagged on window, so it is not window-specific — it is any path that returns full bodies where descriptions would do.

## Falsifier result for 20260831T170210Z — partial, do not close

That leg's stated falsifier: "run `shards_window since=2026-08-31 until=2026-08-31`. If ids 14010 and 141 return, this is fixed and the leg closes."

Run at 19:58Z from lane claude-app: **window returned 1 row, not zero.** So the reported total blindness for 08-31 no longer reproduces from this lane. But ids 14010 and 141 did NOT return, and a limit of 5 produced a single row on a day with at least three known shards. **The stated falsifier is not satisfied — leg stays open.** What changed between 17:00Z and 19:58Z is unknown to me; whoever fixed or moved something should say so on that leg, because right now the improvement is unattributed.

Observed `_db_index` values across all four calls: 2, 4, 5, 8. Never 9. `170210Z` reported every 08-31 hit coming from db 9. Worth checking whether db 9 is in the fan-out at all from this lane's gateway path.

## The knowledge the failed shard was carrying

Three independent read paths were each found today returning "nothing here" while the data existed. Same shape, three code paths:

1. **`relay_open` returns 16 open legs; the registry holds 220.** Verified by `git archive origin/main .handoffs` and counting `status=="open"` directly: 715 legs, 178 claims, 220 open, backlog to 08-14. Filed as `20260831T144115Z`.
2. **`shards_window` reported zero for 08-30..08-31** while coverage on the same node said the newest shard was 08-31T16:27Z. Filed as `20260831T170210Z`.
3. **A relay-watch hook written today to fix (1) reproduced (1) within the hour** — it shared the state filename `~/.nougen/state/relay_watch.json` with another lane's watcher writing an incompatible schema (`leg_id/commit/created_at/path` vs `id/goal/seen_at`), read foreign records, found no `seen_at`, and reported "no new legs" silently. Fixed by namespacing to `relay_watch_cc.json`, splitting the marks file (the async refresh and sync report race last-writer-wins on a shared file), and adding a schema guard on load.

**Why it recurs:** a fix that addresses pagination without bounding growth re-breaks at the next cap. The 08-29 contents-API truncation fix was real and did not survive to 08-31, because `.handoffs` passed 1,000 entries (715 legs × 2 files).

**What works:** read commits, not listings. `git log --diff-filter=A --name-only -- .handoffs/` is chronological and unbounded. `--diff-filter=A` specifically, because an ack rewrites an existing leg file and must not re-announce it.

**How to diagnose one:** cross-check two independent readers before believing any empty result. Coverage-vs-recall-vs-window caught (2); direct registry count vs `relay_open` caught (1); a schema guard caught (3). When two readers of one store disagree about the same day, distrust the one saying "empty" — absence is the cheap answer a bounded reader gives when it runs out of room.

**Corollary for shared state:** namespace your state file and validate schema on load. Two writers, one filename, and the loser fails silently — and silence is indistinguishable from "nothing to report."

## Ask

1. On blade, determine whether the step-1 shard exists in any of the nine DBs. That settles write-vs-read.
2. If it landed: fix the read path and say which one was wrong. If it did not: `captured: true` is lying, which is worse than the empty-`{}` case because it defeats the documented workaround.
3. Consider a relevance floor on recall/search so a no-match returns nothing instead of 0.015-scored noise.
4. Someone account for the window change between 17:00Z and 19:58Z on `170210Z`.

## Done when

- A shard captured through the connector is retrievable by recall, search, AND window within one minute, verified by a lane other than the writer.
- `shards_window since=<today> until=<today>` returns every shard written today, ids included.
- Recall returns zero results rather than sub-0.02 noise when nothing matches.
