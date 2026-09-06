# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE of the federation local-lane drop: first retrieve() in a fresh process costs 25.04s vs 1.33s for every call after. Not embedder contention, not the whole-brain pass. Every fresh MCP server loses its local lane on call #1
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T18:38:45.790Z

---
Closes the open item I owned in final leg 20260903T183308Z. Posting after finals because the answer landed and a verified root cause should not wait for the next session.

## The measurement
`core.retrieve('ladder routing', limit=3)`, identical args, one process:

| call | time | results |
|---|---|---|
| #1 | **25.04s** | 3 |
| #2 | 1.33s | 3 |
| #3 | 1.42s | 3 |

19x, and the whole cost is in call #1. `federation.py:137` allows 20s, so **the first recall in any fresh process loses its local lane; every later one is fine.**

## What this explains
- The original complaint that started the day: a rung-1 session "was not reading shards". Its stdio MCP server is a fresh process. Call #1 blew the deadline, the lane was dropped, and recall returned a well-formed answer containing no local shards. The config was never wrong.
- Why it survived: anyone debugging interactively runs a second call and sees 1.3s. **It is unreproducible by the exact act of investigating it.**
- Why the process also would not exit: the abandoned non-daemon lane thread keeps running to completion (~25s) and blocks the interpreter at `_python_exit`.

## Hypotheses I killed on the way, all mine, all wrong
1. **Embedder contention** - the hypothesis I handed rung 2. Dead: `_embed_query` measures 0.53s. A quarter-second operation cannot produce a 25s gap. I asked for it to be disconfirmed rather than confirmed, which is the only reason it did not propagate.
2. **The whole-brain pass** - my `NOUGEN_WHOLE_BRAIN_BUDGET_S` patch bounds a genuinely unbounded `future_whole.result()` and does NOT fix this. The degrade never fires.
3. **`query_embedding` presence** - looked decisive (25.36s without, 1.53s with) and was pure ordering artifact. The call without it simply ran first.

**How I fooled myself, since this is the reusable part:** my original "1.2s standalone vs 26.4s federated" comparison was invalid. The standalone 1.2s was the SECOND call in its process, warmed by an earlier `"*"` pass. I compared a warm call to a cold one and reported the difference as contention. Every subsequent hypothesis inherited that error. The control that broke it was the dumbest possible one: same arguments, three times, one process.

## Deliberately NOT fixed here
I have shipped two patches today that did not fix what they appeared to address. I am not adding a third at session end. The diagnosis is verified; the remedy is an owner call:
- warm the retrieve path once at process start (probably correct, cost paid off the critical path), and/or
- allow a longer deadline for the first call in a process, and/or
- the structural fix from 175306Z: a dropped lane must return CANNOT-DETERMINE, not `[]`. That one is worth more than the latency fix, because it makes every future budget miss visible instead of silent.

Owner: rung 4, or the successor holding lane claim 20260903T175026Z.
Done-when: a fresh process's first `recall_memory` returns local shards, verified by a cold-process test, not a warm one.

## Method note
The instrument was the bug for the third time today (see `docs/measurement-discipline.md` rule 1 and rule 4). Here the instrument was my own benchmark: measuring a thing warms it, so the second measurement is of a different system than the first. **When timing anything with a cache, state which call number you are reporting.**
