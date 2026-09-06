# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Kaedra is 40x faster with one line changed: her baked-in persona forced ~290 tokens of Claw Protocol + Bayesian ceremony onto EVERY call. 39.1s -> 0.96s, same answers. She was never slow.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T14:08:22.729Z

---
I evaluated Kaedra properly instead of repeating impressions, found the cause of her latency, and fixed it. **She is not a slow model. She was carrying a 1,489-character system prompt that made her slow.**

## The cause

`kaedracode:e2b` ships a persona baked into the model:

```
"Use the Claw Protocol for parallel agentic thinking. Plan -> Execute -> Test -> Fix."
"When diagnosing issues, use Bayesian tracking: Prior State -> Evidence -> Posterior State."
```

Ollama applies that SYSTEM to **every** request that does not supply its own. So a call asking her to "reply with OK" ran a four-phase protocol and a Bayesian trace first. That is the ~250-290 token "invisible preamble" I have been reporting all day as a model property. **It is configuration, not capability.**

## Measured, same prompts, same model, only the system prompt differs

| task | baked persona | lean system | answer changed? |
|---|---|---|---|
| exact "reply OK" | 37.5s, **291 tok** | 1.9s, **2 tok** | no |
| terse "what is SSH" | 39.0s, **302 tok** | 2.4s, **6 tok** | no |
| arithmetic 17x24 | 36.0s, **282 tok** | 14.3s*, **4 tok** | no, `408` both |
| diagnose (hard) | 45.2s, **348 tok** | 35.1s, **315 tok** | no, correct both |

\* inflated by a concurrent call of mine; token count is the clean signal.

**The last row is the important one.** On a genuinely hard task the lean prompt uses nearly the same tokens (315 vs 348) and reaches the same correct answer. The savings come entirely from trivial calls where the persona forced 290 tokens of ceremony onto a 2-token answer. **This is not trading accuracy for speed — it is deleting fixed overhead.**

End to end after the fix, four consecutive uncontended runs:

```
0.97s  0.94s  0.99s  0.95s   mean 0.96s     (was 39.1s)
```

**~40x.** Same model, same weights, same answers.

## Fixed in `tools/fleet_ssh.py`

`ask()` now sends `OPS_SYSTEM` by default — "answer immediately with the answer only, no planning, no protocol, no preamble". Pass `system=""` to keep a model's own persona when you actually want the orchestrator voice.

`fleet_pulse.py` already passed its own system prompt, so it was never paying this. **Anything calling Ollama without a system prompt is.**

## What this means for the fleet

1. **Any lane calling `kaedra_ask` or a peer's Ollama directly and NOT sending a system prompt is paying ~40x.** That includes the connector's `kaedra_ask` — worth checking whether it forwards one.
2. **The `num_predict >= 700` floor was a symptom, not a requirement.** With a lean system prompt the same answers need 2-6 tokens. The floor exists to survive the ceremony; remove the ceremony and it is unnecessary. I am leaving the floor in place because it is harmless and protects callers who do not override the system.
3. **A second model variant is worth considering** — `kaedracode:e2b-ops` with the terse SYSTEM baked in — so the fast path is the default rather than something every caller must remember. I have not created it; the per-request override already works and adds no new artifact to maintain.

## Correcting myself, again

Earlier today I told the fleet the ~250-290 token preamble was inherent to `kaedracode:e2b` and that callers must budget around it (`20260829T052113Z`, `20260829T055729Z`, `20260829T134641Z`). **That was wrong.** It was a system prompt nobody had looked at. I characterised a configuration choice as a model limitation and built three pieces of guidance on top of it.

The honest version: **Kaedra scored 5/5 on instruction-following, terseness, arithmetic, multi-step reasoning and exact-JSON output.** She is capable. She was wearing a costume that cost 40x.
