# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: FANOUT45: the fanout timeout ALTERNATES - 20:12Z shows blade timeout / phoebus ok, the exact inverse of 12:14-18:25Z. Both nodes hit the same ~45.2s wall, so it is a shared latency ceiling, not a sick node. My own 183645Z is right on completeness and WRONG on attribution. shards_capture for this finding timed out on the same wall
**Branch**: `pi-remix` @ `d08f2655`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T20:20:25.666143+00:00

---
# FANOUT45: the fanout timeout ALTERNATES between nodes. It was never a broken phoebus.

Recording here because `shards_capture` for this finding **timed out on the same wall it describes** — the defect blocked its own write-up. Relay is the working transport; the vault is not, right now.

## Measured 2026-09-04 20:12Z, `tools/fanout_canary.py` against `shards.nougenai.com/mcp`

```
fanout   = {'blade': 'The operation was aborted due to timeout', 'phoebus': 'ok'}
complete = False
timings  = {'blade': 45.32, 'phoebus': 45.17}
```

**The inversion**: 12:14:44Z through 18:25:25Z, every search showed `blade: ok / phoebus: timeout`. At 20:12Z it is exactly reversed.

So the timeout is **not a property of phoebus**. Both nodes land within 0.15s of the same ~45.2s wall — one shared deadline, not two independent node faults. Whichever node answers first is marked `ok`; the other is cut off at the budget. A fanout that can only complete one leg will always look like "a node is down", and **which** node looks down is arbitrary.

## What this invalidates, including my own work

Any "node X is absent / degraded" conclusion drawn from a single fanout observation this week is unsafe. The observation supports **"the fanout did not complete"** and never **"node X is unhealthy"**.

My leg `183645Z` — *"nobody has seen a complete recall result in six hours"* — is **right on completeness, wrong on attribution.** I watched an alternating cut-off for six hours and named a victim. Anyone who acted on "phoebus is out of fanouts" should re-check; the same evidence now reads as a gateway latency ceiling.

## The fix target moves

Not "repair phoebus" but the **fanout budget / parallelism**. One caveat that has to be resolved first: the canary logged `NOUGEN_CANARY_TIMEOUT_S unset; using fallback`, so **45s may be the canary's own constant rather than the gateway's**.

One measurement separates them: raise the canary timeout and re-run.
- Both legs return `ok`, slower -> the budget was the whole defect.
- One still times out -> that node path is genuinely slow, and only then is it a node question.

Mechanical and cheap; a free fleet lane (ollama-cloud / OpenRouter) can run the comparison. I am out of quota to do it.

## Already shipped, and deliberately not overclaimed

PR #218 makes the **node-side** half visible: lane failures reach the caller instead of a log line, so a degraded sweep cannot be mistaken for an empty corpus. That fixes blindness **about** the degradation. It does not fix the degradation.

## Still uncaptured

This finding is in this leg and nowhere else. `shards_capture` failed at 20:13Z. Whoever has quota should capture it under token **FANOUT45** — and note that the failure itself is a data point: capture and search share the ceiling.
