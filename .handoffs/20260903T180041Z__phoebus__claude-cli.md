# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: Sue Bryce brand/business doctrine ingested + DEFECT: nougen add --embed silently fails on LONG content (ollama is healthy), starving semantic recall of the densest shards
**Branch**: `main` @ `05c26632`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-03T18:00:41.292285+00:00

---
Two things: a knowledge-base ingest, and a defect found while doing it that matters more.

## 1. Ingest — Sue Bryce, brand and business doctrine

`Visions-ai/knowledge_base/transcripts/-10ptuFAdEM.json` (20 steps, 10 takeaways). Companion to the posing system already ingested at `FWvQUhzdtFA.json` + `knowledge_base/posing_curves.md`: **posing is HOW, this is WHY ANYONE PAYS.**

The load-bearing claim: **craft alone earns nothing.** She shot her finished, recognisable style for years while taking home 400–500 a week on wages. People buy on how work is *presented and sold*, not on how good it is — selling is a separate skill that has to be learned separately.

Sequence she insists on: **define the style first**, then build service, marketing and pricing around it. Her style locked around 1999 and the brand has not changed since; the next fifteen years went into the business, not the look.

**The portfolio is a marketing decision, not an aesthetic one** — displayed images are the only thing determining who calls. She showed only glamour so she booked only glamour, deliberately. Corollary: if mothers are not booking, look at whether your advertising shows mothers.

Technical doctrine embedded in the business talk, worth recalling on its own: everything serves **the face**, and the face shot cannot be cropped from a wider frame; **two eyelines only** (down the lens, or down the subject's own body line — anything else is a model pose, not a portrait); **the diamond** (head → outer shoulders → base of décolletage) is never closed down; **direct, do not pose**; and **connection is what sells** — the camera rising drops a self-conscious veil and killing that veil is the actual job.

Biggest revenue idea: the **inner-circle multiplier**. Six friends booking a girls' day out is six sales in one day, and a three-generation shoot marketed as glamour is functionally a family shoot connected to a much larger network.

Caveat recorded in the shard: she cites model-BMI statistics in support of the advertising argument. **Treat those figures as her claim, not verified data.**

## 2. DEFECT — `nougen add --embed` fails on LONG content, silently degrading the best shards

Seven captures this session on phoebus. The correlation is clean:

| shard | rough size | embedded |
|---|---|---|
| harsh-light ladder | medium | yes |
| suntimes tool | medium | yes |
| Nijhorst translation pointer | medium | yes |
| Sue Bryce attribution | short | yes |
| Nijhorst studio lighting | long | **NO** |
| posing curves | very long | **NO** |
| Bryce business doctrine | very long | **NO** |

Failure message every time: `shard written WITHOUT embedding (model=nomic-embed-text, miss #1) -- semantic recall will not see it until backfill runs; is ollama up?`

**The message is misleading and I nearly acted on it.** It points at ollama being down. Ollama is UP — I probed both `/api/embeddings` and `/api/embed` directly and both return vectors for `nomic-embed-text`. The model is installed and healthy. The failure correlates with **content length**, which points at a timeout or a token limit in the embed path, not availability.

**Why this is worse than it looks:** the shards that fail are the *longest and most information-dense ones* — exactly the material most worth recalling semantically. Short notes embed fine. So semantic recall is being systematically starved of the richest content while reporting success on the trivial. It also compounds the federation issue already on the board (`175306Z`, `175731Z`): a shard that is both unembedded and behind a dropped fan-out lane is effectively invisible from this node by two independent mechanisms.

**Asks:** (a) confirm whether long captures also fail to embed on blade, or whether this is phoebus-local; (b) fix the error message to name the actual cause rather than pointing at ollama, which sends the next node on an hour-long hunt for a healthy model; (c) confirm whether the backfill it promises actually runs, and on what schedule — "until backfill runs" is doing a lot of work in that sentence and nobody has verified it.
