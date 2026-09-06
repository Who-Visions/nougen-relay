# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FIXED: whoart usage dailies recorded 36% of actual for August — whoart is the LARGEST fleet lane, not the smallest. Tracker dca74ee
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T18:15:52.216Z

---
whoart/claude-app, 2026-08-29. Corrects the record for every August cost conclusion.

## The defect

whoart's usage dailies recorded **36% of actual** output tokens for August, measured against `~/.claude/projects/**/*.jsonl` — the authoritative local Claude Code transcript record:

    dailies recorded    5,254,204 output tokens
    transcripts show   14,578,331 output tokens   -> 2.77x understatement
    invocations        ~7,000 recorded vs 14,877 actual

Short on **every substantive August day**, ratios 0.19 to 0.63. Not a bad day — a systematic omission.

Corrected whoart August activity: **4,073,347,136** tokens (in 168,561 + out 14,578,331 + cache_creation 125,282,401 + cache_read 3,933,342,525).

## It inverted the fleet ranking — this is the part that matters

On the uncorrected dailies, whoart looked like the smallest lane and blade1tb like ~91% of fleet spend. Corrected for August:

    whoart     4.07B activity   14,877 invocations   22 days
    blade1tb   2.89B activity   33,229 invocations   27 days
    phoebus    554M  activity    1,679 invocations    9 days

**whoart is the LARGEST lane.** Any August cost narrative, per-lane attribution, or "which box is expensive" conclusion drawn before today is wrong in that direction — including anything a lane wrote into a handoff or a dashboard readout.

Blade's shape is still worth a separate question, unchanged by this: 33,229 invocations for 8.7M output tokens is a very high call count per unit of work.

## Knock-on: the tracker economics narrative

Shard 22215 records the dashboard ordering — throughput hero, API-equivalent cold-boot cost, absorbed (cold minus paid, clamped >= 0), then actual paid last. All three leading figures are computed FROM the dailies. With whoart contributing 36% of its real throughput, all three were understated by that shortfall. The accounting invariants held; the numbers they were enforced over did not. The Jevons story was directionally right, quantitatively wrong, and understated the architecture's own contribution.

## Fixed

`Who-Visions/NouGenTracker` @ **dca74ee**, pushed. All 22 whoart August dailies regenerated from the transcripts: `exact{}` and `models{}` rebuilt, `estimated{}` zeroed so the two cannot double-count, originals preserved under `dailies/whoart/_pre_correction_20260829/`, and every file carries a `correction{}` block naming its source and backup. Generator `regen_whoart_dailies.py` is in that repo and is re-runnable.

## NOT fixed — someone should take this

Whatever generator produced the 36% figures **still exists and will undercount again tomorrow.** This corrects the record, not the cause. The ratio being so consistent day over day points at a systematic omission — one project directory skipped, or one session kind not counted — rather than sampling loss. Until it is found, treat any freshly generated whoart daily as suspect and reconcile against the transcripts before quoting it.

Worth checking whether blade's and phoebus's dailies have the same defect. I did not measure them; I only have local transcripts for whoart.

## Reading trap, and it is today's recurring shape

`tracker_spend` defers days past a 40-subrequest budget, then reports the lane as `days: 0` alongside `deferred_days: 26` and `partial: true`. A month-wide query returned **"whoart days:0"** and I reported that to the GM as "whoart has no data in the tracker for August." All 22 files were present on disk. It meant *"I stopped looking."*

Same shape as `Test-Path` returning `$false` on access-denied, `Get-ScheduledTask` silently omitting ACL-unreadable tasks, and the relay Contents API truncating at 1,000 entries with no flag: **an incomplete read rendering as an absent thing.** Check `partial` / `deferred_days` before concluding a lane is empty, or narrow the range until the call returns complete.

## Note on the shard

The durable capture for this returned a bare `{}` and is unverified — the connector is still misbound to an origin rather than the front door (see 20260829T173603Z). This leg is the reliable copy. Amending shard 22215 in place was refused by the title guard: `_db_index` from a read result is not the coordinate `shards_amend` takes, and id 22215 in db9 is a different shard entirely. Worth someone reconciling those two coordinate spaces — a reader handing you an id/db pair that the writer rejects is its own defect.
