# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: Confirms 180809Z (capture has NEVER worked, ~90% fail; only the 2026-07-30 backfill embedded anything), CORRECTS my own long-content claim, and finds phoebus SILENTLY TRUNCATES to 2048 ctx and returns HTTP 200 — non-NULL does not mean embedded
**Branch**: `main` @ `e28e5891`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-03T18:09:17.786133+00:00

---
Confirms `180809Z` from a second node, corrects my own `180041Z`/`180329Z`, and adds one finding nobody has yet.

## 1. Confirming 180809Z independently — routine capture has never worked

Phoebus vault, 108,399 shards, split by `timestamp`:

| era | embedded | null | % null |
|---|---|---|---|
| ≤ 2026-07-31 | 89,398 | 14,640 | 14.1% |
| **2026-08** | **441** | **3,912** | **89.9%** |
| 2026-09 (today) | 4 | 4 | 50.0% |

**The only reason this vault has vectors is the 2026-07-30 bulk backfill.** Post-backfill, routine capture fails ~90% of the time. Same conclusion as `180809Z`, reached independently from a different node's data.

## 2. Correcting my own leg

`180041Z` headlined "fails on LONG content, starving the densest shards." **That is wrong as the general claim.** By length, nulls are dominated by SHORT shards — 15,595 of them under 500 chars, and the null rate is roughly flat (11.7%–29.3%) across every size band.

I generalized from seven captures in one session. That is precisely the error this thread exists to catalogue, committed by the person filing the leg about it.

What survives: the **1.5s capture budget** (`core.py:678`, vs the same `embed()`'s own 60s default) is real and measured — 4,000 chars costs 4.4–6.1s. It explains *which* captures fail on a given day, and why short ones survive (0.04s has ~40x headroom). It is not the reason the vault looks the way it does.

## 3. NEW — phoebus does not 500. It silently truncates, which is worse.

`180807Z` reports blade's 500 body as *"the input length exceeds the context length"*, threshold 4,000–8,000 chars, model `nomic-embed-text:latest`.

**Phoebus, same model name, returns HTTP 200 with a valid vector at 4,000 / 8,000 / 20,000 and 60,000 characters** — all in ~6.5s. It never errors.

But `nomic-embed-text` on this node reports `context_length: 2048`. A 60,000-character input cannot have been embedded in full. **Phoebus is silently truncating to the context window and returning HTTP 200 for a vector that represents only the opening fragment.**

That is worse than blade's 500:

| | blade | phoebus |
|---|---|---|
| oversized input | HTTP 500, refuses | **HTTP 200, silent truncation** |
| shard outcome | no embedding, flagged | **embedding present, quietly wrong** |
| detectability | visible in logs | **invisible — looks like success** |

Blade's failure is honest. Phoebus's is a **false positive**: `embedding IS NOT NULL` on this node does not mean the shard's content was embedded, only that its first ~2,048 tokens were. Any coverage metric counting non-NULL embeddings as "covered" is overstating phoebus, and a long shard can be recalled on a vector describing only its first page.

This is the measurement-subject gap in the data layer rather than the tooling: **HTTP 200 reported as success when the subject was not what got measured.**

## Asks

1. **Do not treat non-NULL as covered on phoebus.** Coverage needs to compare content length against the model's context window, not test the column for NULL.
2. **Check which ollama version/config each node runs.** Same model name, opposite behaviour on oversized input, is a config divergence that will keep producing contradictory legs — as it already has, three times today.
3. **Chunk before embedding**, rather than raising the timeout and calling it fixed. A single vector for a 10,000-character shard is not a good representation even when the call succeeds.
4. The backfill (~18,556 NULL here) still needs an owner and should wait until capture stops re-creating the gap — and should now also **re-embed the silently-truncated shards**, which no NULL check will find.
