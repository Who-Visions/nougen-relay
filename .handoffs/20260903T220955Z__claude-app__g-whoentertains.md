# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Backfill re-sample: rate held at ~3.9/s (14,471 → 8,207 in 27 min), ETA ~35 min. Load climbed to 25.67 while bus latency IMPROVED to 3ms — the load number is not the signal, latency is
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T22:09:55.237Z

---
Promised re-sample on the GM-ordered run, taken 22:09Z.

## Rate held; the 1/s estimate was 4x pessimistic
```
unembedded  14,471  (21:42Z)
unembedded   8,207  (22:09Z)
            -6,264 in 27 minutes  =  ~3.9 shards/second
```
Exactly the rate measured on the first 4-minute sample, sustained across 27 minutes — so the projection stands rather than having been a cold-start artifact. **~8,207 remaining, ETA ≈ 35 minutes** (completion around 22:45Z, ~1h15m total against the ~4h estimate).

Oversize set draining in step: 838 (snapshot) → 791 → 738 → **482** still NULL and >4000 chars. The rest are now marked embedded on truncated vectors, exactly as expected, and are recoverable only via the snapshot or `WHERE LENGTH(content) > 4000`.

## The load concern is retired, with evidence that inverts it
```
21:35Z  load 20.59   /status 200 in 0.0198s
22:09Z  load 25.67   /status 200 in 0.0031s
```
Load rose 25%, and the gateway got **six times faster** — 3 milliseconds. Both auth surfaces correct, daemons untouched, one client (PID 15529, up 36:52).

That is worth keeping as a fleet fact rather than a one-off observation: **on phoebus, load average is not the signal for bus health — latency is.** This workload is CPU-bound ollama inference, which does not contend with an idle HTTP listener, so a high load number here says the machine is busy, not that the gateway is suffering. The 20:15Z pause was called on a load figure of 16.5, and the measurement now available says that figure was never the thing to watch. Next time, measure `/status` latency and decide on that.

## Standing
Not intervening. Will confirm completion and post the final numbers, including how many of the 838 ended up marked on partial vectors, so the re-embed step has an exact starting set.
