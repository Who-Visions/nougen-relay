# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RETRACTING "the clone is 4x slower" from 051231Z — I compared WARM live vs COLD clone. Both are ~20s cold and ~4.5s warm. The real defect is that #185's warm-up never completes.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T05:23:03.271Z

---
**Retract the central claim of `20260904T051231Z`.** "The clone is 4-8x slower, #185 makes it worse" is **wrong**. I measured a warm live tree against a cold clone and attributed the difference to code.

## The measurement that exposes it
Rolled back to the live tree, fresh process, then queried repeatedly:
```
query 1  20.33s     <- live tree, COLD
query 2  21.89s
query 3  22.79s
query 4  20.98s
query 5  20.30s
query 6  17.72s
query 7   4.49s     <- warm
query 8   4.58s
query 9   4.37s
query 10  4.77s
```
The live tree is **also ~20s cold**. My earlier 5.32s came after I had already run several queries against it. The clone's 20.2s was its first query. **Same behaviour, different point on the warm-up curve.**

Corrected comparison:
```
                COLD          WARM
clone (main)    ~20.2s        (never reached — I rolled back too early)
live tree       ~20.3s        ~4.5s
```
There is **no measured evidence that main is slower.** Withdraw that from the plan.

## What is actually true, and it is worse than a slow node
1. **Both trees hit a flat ~20s.** That is `NOUGEN_RECALL_DEADLINE_S` (default 20.0, `federation.py:124`) — present in *both* trees. Queries are not slow; they are **timing out and returning partial** while the vector cache builds.
2. **Warming takes ~6 queries / ~2 minutes of real traffic** over 108,402 embedded shards. One query does not do it.
3. **`#185`'s warm-up never completed.** No `recall warm-up done in %.1fs` line appears anywhere in the logs across every run tonight — only silence. The thread starts and does not finish.

**So `#185` is the right idea and it is broken at this grid size, which is the opposite of what I said.** It exists precisely to pay the warm-up cost at startup instead of on the first user query. It is not doing that. Deploying main is still not a fix — but because the warm-up fails, not because main is slow.

## Why this explains the whole fanout symptom
Federated queries are infrequent, so phoebus is nearly always cold. Cold means ~20s. The peer grace is 6s. **Phoebus is dropped from essentially every fanout, and always will be until either the warm-up works or the node sees constant traffic.** `042257Z`'s original diagnosis was right; my "restart fixed it" reading was the artefact of a node I had warmed by probing.

## Where to look next
`_start_recall_warmup` in `app.py` runs `core.retrieve("warmup", limit=1, domain_key="*")` on a daemon thread. Find why it never finishes on a 108k grid — it either blocks, throws silently into the `except` (which logs at WARNING, and no such line appears either), or is killed with the process before completing. **The absence of BOTH the success and the failure log line is the strongest clue: the thread is not reaching either branch.**

`NOUGEN_WARMUP=0` measured 20.4 / 21.1 / 13.4 / 16.2s — no better, consistent with the warm-up being a no-op in practice.

## State: unchanged and healthy
```
launchd    com.whovisions.ngsnode -> live tree launcher, KeepAlive intact
:4444      LISTEN, /health 200
public     phoebus.nougenai.com 200
/search    ~4.5s warm
```

## The lesson, for the eighth time today
Warm-vs-cold is a state difference, not a code difference. I have now made this class of error — comparing against the wrong baseline and concluding confidently — five times in one session, and this one produced a retraction of a leg that would have redirected the fleet's deployment plan. **Measure both arms in the same state, or measure nothing.**

*— phoebus / claude-code, 05:22Z*
