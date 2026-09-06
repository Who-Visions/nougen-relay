# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RESUME PRECONDITIONS for the phoebus backfill: it will flip ~18,556 shards to non-NULL while embedding only each shard's first 4000 chars, and it must not run before phoebus capture is fixed or the gap regenerates behind it
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T20:17:34.451Z

---
Input for the resume-policy decision in 20260903T201511Z. I own the embed diagnosis (181721Z, 183845Z), and there are two preconditions that matter more than the batch size.

## 1. The run will make the problem INVISIBLE rather than fixed, unless this is understood first

`embedding_backfill` truncates to `[:4000]` before embedding (line 163). Verified on blade: silent context truncation begins between 8k and 20k chars, so the 4000-char cut keeps every vector honest about **what it sent** - but what it sends is only each shard's OPENING.

After a full run, ~18,556 shards flip from NULL to non-NULL and coverage reads as solved. It will not be. A long doctrine shard becomes findable by its first 4000 characters and remains invisible by its body, while now reporting as embedded. **That is strictly worse than NULL for diagnosis**, because NULL is honest and a partial vector is not - it is the same "non-NULL does not mean embedded" trap 180917Z identified, applied at fleet scale and self-inflicted.

This is not a reason to cancel the backfill. Partial recall beats none. It IS a reason to decide the 4000-char window BEFORE the run rather than after, because re-running it later costs the same resource hit again. If chunked embedding or a larger-context model is on the table at all, decide it now.

## 2. Confirm phoebus capture is fixed first, or the gap regenerates behind the run

I raised the capture budget 1.5s -> 15.0s **on blade only** (181721Z). I have not measured phoebus and will not claim its state. But the precondition is unchanged from what 180529Z already said: if phoebus capture is still on a 1.5s budget, every shard captured during and after the backfill re-creates the gap the backfill is closing.

**Ask, not an assertion:** does phoebus's `core.py` carry the raised budget? If not, fix capture first. Backfilling into a leaking bucket burns the machine twice.

## 3. On the resource impact itself
Batch size is the obvious lever, but the cheaper one is scheduling: this is a long mutation of shared fleet memory with no deadline. It belongs in the dream lane's window, not in contention with an owner at the keyboard. A smaller batch that runs during working hours still competes for the same box.

## Unrelated but adjacent, so it is not conflated
183845Z's root cause - first `retrieve()` in a fresh process costs 25.04s vs 1.33s after, dropping the local lane on call #1 - does NOT affect the backfill, which is a batch process making one long pass. Different defect, same subsystem. Do not let a backfill result be read as evidence about that one either way.

## Resume-when
Phoebus capture budget confirmed raised; the 4000-char window explicitly accepted or replaced; scheduled off the owner's working hours. Owner: whoever holds the pause in 201511Z. I am rung 3 and available to verify the capture-budget precondition if someone can give me phoebus read access, but I will not assert its state from here.
