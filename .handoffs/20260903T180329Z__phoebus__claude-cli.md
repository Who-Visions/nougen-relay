# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: PROVEN cause of the embed misses: core.py capture timeout defaults to 1.5s while its own embed() defaults to 60s; 4000-char input takes 4.40s. Ollama was never the problem
**Branch**: `main` @ `e0714582`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-03T18:03:29.486393+00:00

---
Supersedes the hypothesis in `180041Z`. That leg said long captures fail to embed and guessed at "a timeout or token limit". **It is a timeout, and here is the line.**

## Root cause

`src/nougen_shards/core.py:678`, inside `_embed_for_capture`:

```python
timeout = float(os.environ.get("NOUGEN_EMBED_TIMEOUT", "1.5"))
```

**The capture path allows 1.5 seconds.** The very same `embed()` function it calls, in `embedding_backfill.py:63`, defaults to **60 seconds**. Capture is running on a budget forty times tighter than the function's own default, and nothing at the call site says why.

`core.py` truncates the embed input to 4000 characters, so the cost is bounded — but bounded well above the budget.

## Measured on phoebus, ollama healthy throughout

| input | time | outcome at the 1.5s default |
|---|---|---|
| 25 chars | 0.04s | embeds |
| 1,200 chars | 1.09s | embeds, barely |
| 4,000 chars (the cap) | **4.40s** | **MISSES** |

Every call succeeded when given time. The threshold sits around **~1,500 characters**, which is why short notes always embed and dense ones never do.

## The error message points at the one thing that is fine

> `shard written WITHOUT embedding (model=nomic-embed-text, miss #N) -- semantic recall will not see it until backfill runs; is ollama up?`

Ollama is up. I probed `/api/embeddings` and `/api/embed` directly and both return vectors on demand; the model is installed and resident. **The message names availability, and the cause is the caller's own timeout.** I nearly went hunting for a dead model on the strength of it, and the next node will.

This is the measurement-subject gap again, in a new place: the instrument reports a property of *its own budget* as a property of the *service*.

## Why it matters more than a missing vector

The shards that fail are the longest and densest — precisely the material most worth recalling semantically. Trivia embeds perfectly. So semantic recall is being starved of exactly the content that justifies having semantic recall, while reporting success on the noise.

It also compounds `175306Z` / `175731Z`: a shard that is both unembedded **and** behind a dropped fan-out lane is invisible from this node by two independent mechanisms, neither of which announces itself.

## Immediate workaround, no code change

```
export NOUGEN_EMBED_TIMEOUT=15
```

Verified: 4,000 characters embeds in 4.40s well inside that.

## Proposed fix, for whoever owns core.py

Raise the capture default to something above the measured worst case (10-15s), or — better — keep a short budget but make the miss *loud and specific*: log the elapsed time and the input length, and say "embed exceeded Ns budget", not "is ollama up?". A fast path is defensible; a fast path that misattributes its own failure is not.

**I did not edit `core.py`.** The live checkout here is stale and held by another session per HANDOFF v2, and this belongs in a PR from a clean base.

## The damage, and an owner decision

Backfill scope on phoebus, measured just now:

```
nougen_shards_1..9.db   total ~108,399   null ~18,556   (~17% per db, evenly spread)
```

**~18,556 shards carry no embedding.** `embedding_backfill.py` exists for exactly this and supports `--execute --batch`, but that is a long, machine-occupying mutation of the fleet's shared memory substrate, so **I have not run it.** It needs an owner call on when, and on which node — and it should probably wait until the timeout is fixed, or the same content will fall back out of coverage the next time it is captured.
