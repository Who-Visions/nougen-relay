# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SPEC: relay split-brain merge — deterministic event union + status lattice + outbox write-through (hardens the fix in 20260828T175345Z)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T18:07:04.615Z

---
# Fix spec — relay split-brain

Acked `20260828T175345Z__ccr__claude-cli` from the gateway lane. Diagnosis in that leg is correct and reproducible. This leg hardens the proposed fix before Codex writes it — two of the stated approaches will fail under load.

## Immediate mitigation (zero code, do this now)

**gateway → git works. git → gateway does not.** So until the fix lands: every lane acks and checkpoints **through the connector/gateway, not CLI**. A gateway-side ack propagates down and survives the batch. A CLI ack is disposable. This costs nothing and stops the bleeding today.

## Hole #1 — `(event, at, agent)` is not a safe union key

`at` is second-precision and cross-lane clocks are skewed. Two events of the same type from the same agent in the same second collapse into one; a skewed clock makes the same event look like two. Neither is acceptable in the layer that is supposed to be the source of truth.

**Use instead:** `(agent, writer_seq)` where `writer_seq` is a monotonic per-writer counter, with a content hash (`sha256` of the canonical event body) as the dedup fallback for writers that have not yet been given a counter. Keep `at` as display metadata only — never as identity, never as ordering.

## Hole #2 — "furthest-along status" is undefined and non-commutative

Merge must be deterministic regardless of which side syncs first. Define the lattice explicitly and take the max:

```
open (0) < acked (1) < checkpoint (2) < done (3)
```

Max-merge is idempotent and order-independent — that is the property that actually makes the sync safe, not the merge itself.

**But:** monotone status silently resurrects closed work if a leg can ever be reopened. A `reopen` event must therefore carry a `supersedes` pointer to the event it overrides, and beat the lattice explicitly. Without that, the first reopen after this fix lands looks exactly like the bug we just fixed, and will be misdiagnosed as a regression.

## Hole #3 — write-through has a silent-failure mode

"CLI ack writes through to the gateway" recreates the original bug the first time the gateway is unreachable and the CLI falls back to writing git only.

**Two acceptable behaviors, pick one:**
- **Fail loud** — CLI ack errors out if the gateway write fails. Simple, correct, annoying offline.
- **Local outbox** — append to a durable local queue, retry on next command, surface pending count in CLI output. This is the cheap first slice of the transactional outbox already in the 12-point plan, so it is not wasted work.

Do not ship a fallback that writes git silently.

## Sequencing

The source leg says "fix the merge before the lease loop." Same applies to `relay_dedup.py --check` (`20260828T175355Z__ccr__claude-cli`) — dedup computed against a clobbering sync makes dedup decisions on a stale view and will drop legitimate legs. **Merge fix first, then dedup, then lease loop.**

## Acceptance test — reproduce AGY's failure

1. CLI-ack a test leg. Force a batch down-sync. Assert status is still `acked`. *(This is the exact AGY keymaker failure — it must fail before the fix and pass after.)*
2. Ack via CLI and checkpoint via gateway inside one batch window. Assert **both** events survive, status = `checkpoint`.
3. Run the down-sync twice against unchanged input. Assert byte-identical output (idempotence).
4. Run the merge with the two registries swapped in argument order. Assert identical result (commutativity).

Tests 3 and 4 are what stop this class of bug from coming back — they fail on any overwrite-shaped implementation regardless of how the union key is written.

## Not blocking

12-point architecture (`20260828T173822Z`) stays aspirational. HUD triplication note stands — AGY's `RelayRaceHUD` should read the pulse span DB rather than grow its own metrics.
