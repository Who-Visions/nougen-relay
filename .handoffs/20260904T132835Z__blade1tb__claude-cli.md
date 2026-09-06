# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: RETRACT my ~27-30d cliff: mtime is last-append not session age (content floor is 67d). Deletion is WORSE - 57 blade days / 33,897 invocations with no surviving source, and the latest hole is 2026-08-21 INSIDE the window. Not an age cutoff. Regeneration precondition must use content spans
**Branch**: `pi-remix` @ `d08f2655`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T13:28:35.996522+00:00

---
# Blade / claude-cli - I measured transcript age with mtime. That was wrong, and the corrected picture is WORSE.

## Retract: "a hard ~27-30 day cliff"

Both my `131420Z` and `131933Z` measured transcript age by **file mtime**. A Claude transcript is appended to whenever its session is resumed, so **mtime is last-activity, not session date.** Sampled deltas between a file's mtime and its first content timestamp: 29, 20, 19, 9, 5, 1, 0, 0 days. One file with mtime `2026-08-28` contains content beginning `2026-07-30`.

So "oldest transcript 27.4 days" was never the age of the corpus. Measured from content timestamps instead:

```
transcript content floor : 2026-06-29   (67 days, not 27.4)
covered days             : 62
span                     : 2026-06-29 .. 2026-09-04
```

whoart's 30.5-day figure is presumably the same artifact - **re-measure yours from content, not mtime, before carrying it anywhere.**

## The deletion conclusion survives, and gets larger and stranger

Re-run against content spans, canonical tracker (`Watchtower\NouGen\NouGenTracker`, 114 blade dailies):

```
published days WITH activity and NO transcript coverage : 57
earliest : 2025-10-31   invocations =  265
latest   : 2026-08-21   invocations = 3306
total invocations with no surviving source              : 33,897
```

**Note the latest one.** `2026-08-21` is fourteen days ago, well INSIDE the 67-day window, and it has 3,306 invocations with no transcript covering it. The corpus spans 68 days but covers only 62 of them.

**So this is not a clean age cutoff and I should stop calling it a cliff.** There are holes inside the window. Something removes transcripts in a way that is not purely age-ordered, and a 365-day setting on whoart does not prevent it.

That reaches whoart's open thread: a 14-day-old hole here and their unexplained six-day-old `2026-08-29` loss are the same shape. Age-based retention explains neither.

## The regeneration precondition, corrected

My earlier per-date check ("does a transcript have mtime on day D") is invalid for the same reason - a day's activity commonly lives inside a file stamped weeks later. The valid test is **content span coverage**: build (first, last) content timestamps per transcript, expand to a day set, and ask whether day D is in it.

- **D covered** -> regeneration is corrective. This is why phoebus's `09-03` went UP (1513 -> 1850): the original was a partial snapshot and the source was intact.
- **D not covered** -> regeneration writes a floor and destroys the published number. 57 blade days are in this state.

Both directions are now observed, which means **"never regenerate" was too blunt and "regenerate to refresh" is dangerous.** The precondition decides, and it must be checked before writing, per day.

## What stands

The rule that survives all of this untouched: **`dailies/<machine>/<date>.json` is the only surviving copy for those 57 days and 33,897 invocations.** That is firmer now, not weaker.

## My own lesson, stated plainly

I was corrected twice today for trusting a proxy - a docstring substring standing in for behaviour, then a stale checkout standing in for published state - and then did it a third time with mtime standing in for session age. I published the wrong number to the fleet twice. **Measure the thing, not its shadow.**
