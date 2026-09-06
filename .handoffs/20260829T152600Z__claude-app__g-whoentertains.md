# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CONNECTOR FIX 1/4 (kaedra_ask): send a default system prompt + situational grounding — exact patch at worker line 1271. Kills a ~40x tax and the metadata-only answers ChatGPT sees.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T15:26:00.717Z

---
One of four independent connector fixes, dispatched in parallel. **This one is self-contained — it touches only `kaedra_ask` and can ship without waiting on the other three.**

## Exact patch site

`nougen-fleet-mcp`, `kaedra_ask`, line 1271:

```js
const body = { prompt: args.prompt };
for (const k of ["model", "system"]) if (args[k]) body[k] = args[k];
```

`system` is forwarded **only if the caller supplies one**. The connector never supplies a default, so every call inherits `kaedracode:e2b`'s baked-in 1,489-char persona ("Claw Protocol… Plan -> Execute -> Test -> Fix", "Bayesian tracking: Prior State -> Evidence -> Posterior State"), which burns ~250-290 tokens **before any visible output**.

## Patch

```js
const body = { prompt: args.prompt };
for (const k of ["model"]) if (args[k]) body[k] = args[k];

// Ollama replaces a model's baked-in SYSTEM when a request supplies one.
// Without this every call pays the persona's ~290-token preamble, and any
// num_predict under ~300 returns an EMPTY string — which is exactly what
// ChatGPT has been seeing as "metadata only" (leg 20260829T143257Z).
const GROUNDING =
  `Current time: ${new Date().toISOString()} (UTC). ` +
  `You are Kaedra, running on phoebus in the NouGen fleet.`;
const HUMAN_SYSTEM =
  "You are Kaedra, answering a person directly in a chat window. " +
  "Write for a human reader: plain language, complete sentences, no headers, " +
  "no protocol names, no 'Prior State / Evidence / Posterior State' scaffolding, " +
  "no restating the question back. Lead with the answer, then add only the " +
  "context that genuinely helps. Be concise but not curt. Use the current time " +
  "you are given when the question is about now, dates or elapsed time. " +
  "If you do not know something, say so plainly instead of guessing.";
body.system = args.system || (GROUNDING + "\\n\\n" + HUMAN_SYSTEM);
```

## Why the HUMAN prompt and not a terse one

`kaedra_ask` upstreams to a **person in ChatGPT**. An operations-style "answer only, no preamble" prompt is right for a monitoring probe and wrong here — see `20260829T142027Z`, where I made exactly that mistake and corrected it.

## Measured

Identical prompt, identical model, only the system prompt differs:

| | baked persona | with system prompt |
|---|---|---|
| "reply OK" | 37.5s, 291 tok | **1.9s, 2 tok** |
| "what is SSH" | 39.0s, 302 tok | **2.4s, 6 tok** |
| hard diagnosis | 45.2s, 348 tok | 35.1s, 315 tok — **same correct answer** |

~20-40x on short calls, and **no quality loss on hard ones** — the saving is pure ceremony, not thinking.

## Done when

A ChatGPT `kaedra_ask` returns prose. Verify with an `eval_count` under 300: under the old behaviour that guaranteed an empty answer, under the new one it should be a complete sentence.

**Note for whoever deploys:** the worker reads `env.RELAY_BRANCH`, `env.KAEDRA_GATEWAY_TOKEN`, `env.SHARD_GATEWAY_TOKEN` and more. I did **not** deploy this myself — `workers_get_worker_code` returns a *bundled* artifact, not the source project, and pushing a hand-edited bundle risks dropping bindings on the connector the whole fleet depends on. **Apply this to the real source.** If no source project exists, that is the finding to escalate before any of these four ship.
