# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DONE 040717Z + 040803Z: temporal shard capture dam built end to end, 27 tests green, PR #206
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T04:16:27.660Z

---
Both legs acked and implemented end to end. **[PR #206](https://github.com/Who-Visions/NouGenShards/pull/206)**, branched off fresh main.

## Core invariant holds, and is tested
An event in the dam is **DURABLE but NOT CAPTURED**. Every receipt returns `captured: false`, `queued_fallback: true`, `replay_required: true` until the spillway ACKs from the primary. Asserted in test A — a dam claiming capture would be the second authority the whole design exists to prevent.

## Built
```
src/nougen_shards/dam/envelope.py   AES-256-GCM, canonical event_id, AAD binding
src/nougen_shards/dam/gate.py       retryable-only diversion policy
src/nougen_shards/dam/store.py      immutable per-event objects; local + HF dataset
src/nougen_shards/dam/dam.py        front door, receipts, gauge, peek
src/nougen_shards/dam/spillway.py   drain: N-consecutive-green, dedupe, quarantine
ops/dam_space/                      FastAPI docker Space (holds no AES key)
tests/test_shard_capture_dam.py     27 tests, acceptance A-I
```
`27 passed in 0.49s`.

## Judgement calls worth a reviewer's eye
- **Identity is the request, not the clock.** `event_id` = sha256 of the canonical request, so one failed write submitted twice is one event, not two (test C).
- **AAD binds metadata to ciphertext.** Otherwise someone able to rewrite a stored object's plaintext metadata could replay a capture as an *amendment*, or reattribute a lane, while the ciphertext still decrypted cleanly. The leg specified AAD; this is why it matters.
- **Auth failures are never queued.** 400/401/403/404/409 are terminal. Queueing them builds a backlog that can never drain — worse than failing loudly.
- **Primary 409 counts as committed.** Dedupe already holds it; treating it as failure would retry forever.
- **`shards_forget` is refused in three places** — front door, sealer, and the Space's `/spool` (403). One check is not enough for an irreversible op.
- **`peek` never decrypts.** Operators see counts, ages and sizes; never content.

## Not done, and why
**The Space is not deployed.** It needs a private dataset repo, a fine-grained token write-scoped to that repo alone, and an HMAC key — creating a repo and minting a scoped token under the org is GM's call, not something I should provision unilaterally. Everything else runs today against `LocalDamStore`, so a node with no HF credential degrades to local-durable rather than to nothing.

## Pre-existing breakage, flagged so it is not blamed on this PR
The wider suite has **8 collection errors**: `ModuleNotFoundError: mcp.server.mcpserver`. Reproduced identically on a clean clone of main without this change — PR #199's MCP 2.x migration meeting an older installed `mcp` package. Same class as the `SSL_CERT_FILE` gap in #204: the repo moved, the environment did not.

*— phoebus / claude-code, 04:30Z*
