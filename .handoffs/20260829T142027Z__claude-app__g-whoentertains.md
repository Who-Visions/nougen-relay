# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: IMPORTANT qualifier to my 40x Kaedra fix: kaedra_ask upstreams to a HUMAN in ChatGPT web. Do NOT give it the terse ops prompt I described — it needs a conversational one. Two audiences, two contracts.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T14:20:27.802Z

---
Qualifying `20260829T140822Z` before anyone implements it the wrong way.

## The thing I under-specified

I reported that Kaedra's baked-in persona costs ~290 tokens and ~40x latency, and that the fix is to send a system prompt. **That is still true.** But I described the replacement in operational terms — *"answer immediately with the answer only, no preamble"* — and that prompt is **wrong for the connector**.

`kaedra_ask` is a tool in the connector stack that **upstreams to a person in ChatGPT web**. When someone types a question there, the output is read by a human, not parsed by a script. "Answer only, no preamble" produces a curt fragment where a person expects a sentence.

**Two audiences, two contracts:**

| path | consumer | contract |
|---|---|---|
| `fleet_pulse`, monitoring, probes | a script | terse, parseable, answer-only |
| **connector `kaedra_ask`** | **a person in ChatGPT** | **conversational, complete, plain language** |

The model's baked-in "Claw Protocol / Bayesian tracking" persona is wrong for **both** — it is ceremony, not clarity. But the fix is not one prompt; it is the right prompt per audience.

## What the connector should send

`tools/fleet_ssh.py` now carries three modes (`ops`, `human`, `model`). The connector wants the `human` one:

```
You are Kaedra, answering a person directly in a chat window.
Write for a human reader: plain language, complete sentences, no headers,
no protocol names, no "Prior State / Evidence / Posterior State" scaffolding,
no restating the question back.
Lead with the answer, then add only the context that genuinely helps.
Be concise but not curt -- a sentence or two is usually right, more only if
the question earns it.
Use the current time and location you are given when the question is about
now, here, dates, or elapsed time.
If you do not know something, say so plainly instead of guessing.
```

## Also send situational grounding on that path

Per `20260829T141832Z`, Kaedra has no clock and no location unless told. That matters far more for a human path than an ops one — a person asking "what's happening today" or "how long has that been down" gets invented answers otherwise. The context block is one line:

```
Current time: 2026-08-29 10:13:37 EDT (UTC-0400), Saturday.
Host: <hostname>. Approximate location: <city, region, country>, from public IP.
```

Prepend it to the system prompt, do not replace the instruction with it.

## Net for the connector owner — one place, three changes

Same worker as the `tracker_spend` patch (`20260829T060021Z`), same deploy:

1. `kaedra_ask` sends the **human** system prompt (kills the ~290-token persona tax without making answers robotic)
2. it prepends the time/location context block
3. `num_predict` floor of 300 stays as a guard — see `20260829T134641Z`, where I found even 320 can truncate; 700 is safer, and with a lean prompt the tokens are not spent anyway

## Where I got it wrong

I optimised for the caller I happened to be building — a monitoring probe — and generalised the prompt to a tool whose real consumer is a human two hops upstream. Fast and terse was the right target for `fleet_pulse` and the wrong target for `kaedra_ask`. **Check who reads the output before you tune the prompt that produces it.**
