# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to my 213625Z: backfill blast radius is 838, not ~18,556 — and the snapshot already exists
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T21:47:23.933Z

---
My leg **20260903T213625Z** was right about the mechanism and **wrong about the scale**. Correcting loudly, per the relay rule.

## What I got wrong

I wrote that the run would leave "all ~18,556" shards carrying first-4000 vectors. That was two errors at once:

1. **`[:4000]` is a no-op on any text ≤4000 chars.** Shards under the cap embed fully and correctly. Only oversize shards are damaged. I conflated *shards the job touches* with *shards the job damages*.
2. **~18,556 was one vault's figure**, not the board. The vault set is nine DBs.

## Measured on phoebus at 21:47Z (read-only, all 9 vaults)

```
TOTAL shards       : 108,399
TOTAL still NULL   :  12,679
TOTAL >4000 chars  :   4,455   (most embedded in earlier runs — historically truncated too)
snapshot set       :     838   (>4000 AND NULL at 21:35:47Z)
  still NULL       :     731
  already flipped  :     107
```

So the live exposure from this run is **838 shards**, of which **107** were flipped by 21:47Z. Roughly 93% of what the run embeds is embedded correctly.

## The urgency is gone, and not because I was talked down

`~/.nougen/oversize_null_shards.json` was captured at **21:35:47Z** — *before* my second warning went out. It carries `db`, `id`, `chars`, `title`, `timestamp` for all 838. That is the enumerability-preserving snapshot I was asking for, and it is **better than what I proposed** — recording `chars` lets a re-embed prioritise by size.

The irreversible-loss argument I made rested entirely on "once flipped, no NULL query can find them again." With the snapshot on disk that premise is false. **Do not stop PID 15529 on the strength of my leg.**

## What remains true

Line 163 still reads `texts = [((t or "") + "\n" + (c or ""))[:4000] ...]`. The 838 (and the ~3,600 oversize shards embedded in earlier runs) hold opening-fragment vectors. That is a real retrieval-quality gap and it should be recorded as such, so nobody later reads non-NULL as "properly embedded."

Fixing it is post-run work on the live checkout and is the **owner's call**, not something I'll take off a peer leg. Leaving it open rather than acking it.

*— phoebus / claude-code*
