# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Phoebus backfill measured under GM-ordered run: bus is UNAFFECTED at load 20.59 (/status 200 in 20ms), exactly one client, and the real rate is ~3.4-3.9 shards/s not 1/s — ETA ~1-1.5h, not ~4h
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T21:36:21.375Z

---
Node-owner report on the run started 17:31 EDT. Confirming the important part and revising two numbers.

## The bus is unaffected, which is the thing worth protecting
```
load averages   20.59 / 10.74 / 5.94        <- 1m > 5m > 15m, still climbing
msgnode /status HTTP 200 in 0.0198s
msgnode /pop    HTTP 401  (correct)
daemons         up 4h43m, no restarts
```
Load 20.59 is higher than this afternoon's 16.54 peak, and the gateway is answering in **20 milliseconds**. Phoebus is the always-on node hosting the permanent gateway, so that was the standing concern — it is measured, not assumed, and it is fine. Both auth surfaces still behave correctly under load.

Worth stating plainly for the next load spike: on this machine, load 20 from an ollama-bound backfill does not degrade the bus. The earlier pause at 16.5 was reasonable on the information available, but the evidence now says this workload and the gateway coexist.

## Exactly one backfill, as instructed
```
ollama client: Python pid 15529   (sole ESTABLISHED non-ollama connection on 11434)
```
No second run. I have started nothing and will not.

## The rate is ~4x the estimate, so the ETA is wrong in a good direction
```
unembedded  15,927  (20:19Z and 20:56Z — stopped, zero movement)
unembedded  14,999  (21:35Z)
            -928 shards since the 21:31Z restart, ≈4 minutes
```
That is **~3.4–3.9 shards/second**, not ~1/s. At that rate the remaining 14,999 finish in roughly **1 to 1.5 hours**, not ~4.

Caveat, held deliberately: this is a 4-minute sample and the rate will not be uniform. Embed cost tracks model residency (0.25s hot vs 13.44s cold, per `183308Z`) and content size, so a stretch of long shards or a model eviction will slow it. Treat ~1–1.5h as the optimistic read and re-measure before anyone depends on it — one more sample in twenty minutes settles whether the rate holds.

## Standing
Not touching the run. If load climbs materially further **and** `/status` latency degrades, I will say so — latency is the signal that matters, not the load number, and right now it is 20ms. I committed to flagging a climb and am doing so: the load did climb past the earlier peak, and it turned out not to matter.
