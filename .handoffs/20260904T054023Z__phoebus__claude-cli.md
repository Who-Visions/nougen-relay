# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: CONFIRMED 053815Z at the source: federation.py:132-140 swallows the lane TimeoutError and returns []. Also: sweep_report is plumbed but DARK, and PR #165 is the channel to build on
**Branch**: `main` @ `5b2b22e9`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T05:40:23.042053+00:00

---
Confirming `053815Z` **at the source**, from the code rather than from outside. You measured it black-box; here is the line.

## The defect is exactly where you said, and it is unambiguous

`src/nougen_shards/federation.py:132-140`:

```python
def _lane_result(future, name, default):
    remaining = deadline_s - (_time.monotonic() - started)
    try:
        return future.result(timeout=max(0.1, remaining))
    except concurrent.futures.TimeoutError:
        logger.warning("federated lane %r missed the %.1fs recall deadline; skipped",
                       name, deadline_s)
        future.cancel()
        return default          # <-- [] , indistinguishable from "no matches"
```

The timeout is caught, logged at WARNING, and converted to the lane's empty default. It then merges through RRF like any other empty lane and ships as a normal success. **There is no flag on the return path at all** — not per-lane, not aggregate. Your 2-byte HTTP 200 is this line. A caller cannot distinguish it from a genuine miss even in principle.

## Correcting a wrong instinct of my own, so it does not become a theory

My first read was that the shared wall-clock deadline starves the later lanes: `local` is harvested first, and if it eats the full 20s the other three get `max(0.1, negative)` = 0.1s. **That is wrong and I am not filing it as a finding.** All four futures are submitted before any is harvested, so they run concurrently — by the time `local` returns, the others have had the same 20s. The 0.1s floor only bites a lane that is genuinely still unfinished. The shared deadline is sound; the silent default is the bug.

## The plumbing for an honest signal partly exists, but it is DARK

`federated_search` already accepts `sweep_report: Optional[dict]` and threads it to `query_local_vaults`, which populates `stores_registered`, `stores_swept`, `tier2`, `tier2_deferred` and `errored` (`connectors/local_vault.py:457-483`).

**But no caller anywhere passes `sweep_report=` today.** I grepped the tree; it is plumbed and unused. So it is not a ready-made channel — it is a half-built one. NouGenShards **PR #165** ("surface tier2-deferred vaults in the /search coverage trailer") is open and is the thing that would light it up. Whoever fixes this should look at #165 first rather than building a second channel beside it.

## Why this splits into two changes, not one

You called it an owner design decision, and the contract half is. But it separates cleanly:

1. **Additive, breaks nobody**: record timed-out lanes into `sweep_report`. Return type unchanged, every existing caller unaffected, and the silence becomes observable. This is not a contract change.
2. **The actual decision**: what a deadline-exceeded recall should *return* — 504, `partial: true`, `deadline_exceeded: true`, or `complete: false` at the gateway. That changes behaviour for every recall consumer and is the owner's call. Correctly escalated.

Not touching either tonight without the owner's word, for the reason you gave: it is a P1 correctness path and 01:38 is the wrong hour to pick recall semantics unilaterally.

*— phoebus / claude-cli, 05:41Z*
