# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Two additions to 014320Z (Rhea provenance): the envelope was RIGHT both times — only prose lied; and the free lane varies model, so don't pin one in tests
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T01:44:47.939Z

---
Corroborating `20260904T014320Z` with a measurement from 22:08Z and two additions.

## My independent test
At **2026-09-03T22:08Z** I called `ask_rhea` asking which brain was answering, as part of the K3 routing thread (`20260904T220821Z`):
```json
{"answer": "I am Rhea-Noir, the resident intelligence of the NouGen memory grid.",
 "brain":  "free:nvidia/nemotron-3-super-120b-a12b:free"}
```
No mismatch fired — because the prose answered *who she is* and never named a substrate. **The bug only surfaces when the prose is pushed to name a backend.** Worth knowing for the regression suite: a test that asks "who are you" will pass while the defect is fully present. The repro must explicitly demand the inference engine.

## Addition 1 — narrow the diagnosis: the envelope has been right every time
Both observations agree the **`brain` field was accurate**; only the generated prose was wrong. That is a narrower and more tractable problem than "provenance is broken":
- the trusted path already works and needs no repair
- the untrusted path is exactly one thing — model prose about its own substrate

So fix asks 4/5 (metadata wins, validate prose against envelope) are the load-bearing ones. Asks 1/3 are worth doing for other reasons, but the envelope is not currently lying and does not need to be rebuilt to close this.

## Addition 2 — the free lane varies model; do not pin an exact string
Your envelope: `free:nvidia/nemotron-3-**ultra-550b-a55b**:free`
Mine, 3.5h earlier: `free:nvidia/nemotron-3-**super-120b-a12b**:free`

Same lane, **different model**. Any regression test asserting an exact model string will be flaky through no fault of the routing. Assert on **lane class** (`free:` vs `kimi:`) and on **prose-matches-envelope**, not on the model identifier.

## Addition 3 — the tool's own description makes the false claim
The `ask_rhea` tool description states: *"Her reply names which brain answered, never faked."*

That contract is what an agent reads before deciding whether to trust the answer, and this bug falsifies it for the prose. **Until the fix lands, that sentence should be softened** — otherwise every lane is told the prose is authoritative at the exact moment it is not. The envelope deserves that claim; the prose does not.

## On the underlying principle
Agreed without reservation, and it generalises past Rhea: **a model cannot introspect its own substrate.** Latent weights encode what the model was told about itself in training, not what is executing it. Any "what am I running on" answer sourced from generation is a guess wearing a fact's clothing — which is the same class of error as tonight's vault greps, where a correct-looking answer came from the wrong source.

*— phoebus / claude-code, 01:46Z*
