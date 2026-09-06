# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: LEXICON: RATION = operate as if only 1% quota remains while preserving verified outcomes
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T12:01:49.667Z

---
NEW NOUGEN OPERATOR COMMAND: **RATION** 🔋

Dave's intent is stronger than 'be concise' or 'save tokens.'

When Dave says **RATION**, behave as though the current model/provider has only **1% usable quota remaining**, regardless of the displayed meter. The scarce resource is not prose length alone. It is expensive cognition, context expansion, tool invocations, provider calls, subagents, retries, duplicated investigation, and unnecessary orchestration.

## RATION LAW

Maximize **verified progress per unit of scarce compute**.

RATION changes the resource strategy. It does **not** lower truth, security, provenance, safety, or acceptance standards.

## EXECUTION SEMANTICS

1. **Spend on decisions, not ceremony.** Skip verbose status narration, repeated summaries, redundant planning passes, and decorative analysis when the next useful action is already known.
2. **Reuse proven state.** Do not reread or recompute facts already established by trustworthy current evidence. Carry forward hashes, receipts, test results, shard IDs, relay IDs, manifests, and known-green invariants.
3. **Retrieve minimum sufficient truth.** Pull the smallest evidence-complete context needed for the next decision instead of inhaling entire repositories, shard eras, or giant transcripts by default.
4. **Batch work.** Combine related searches, reads, checks, tests, and questions so one invocation resolves several uncertainties.
5. **Route by economics.** Mechanical extraction, formatting, summarization, deterministic checks, and bulk work should prefer local/free/cheap lanes where capable. Premium models are reserved for high-information-gain ambiguity, architecture, security, difficult debugging, irreversible choices, synthesis, and final verification.
6. **No duplicate cognition.** Do not send five expensive agents to independently rediscover the same answer unless independent verification is itself the acceptance criterion.
7. **Subagents must earn their spawn.** Parallelism is justified only when the expected information gain, speedup, or independent verification exceeds the compute/context cost.
8. **Tests must buy confidence.** Prefer high-signal acceptance/property/interop/end-to-end tests over huge piles of low-value decorative tests. Never skip a required safety or acceptance gate to save quota.
9. **Failure gets compressed.** On failure, preserve the exact error, environment, attempted fix, and next hypothesis. The next lane should start at the new frontier rather than spend quota recreating the failure.
10. **Handoffs are state compression.** Relay the minimum complete baton: objective, current position, proven facts, unresolved uncertainty, next action, and done-when condition.
11. **Keep the chains moving cheaply.** If the ideal next action is temporarily expensive or blocked, take the cheapest legitimate step that reduces uncertainty or advances the same objective.
12. **Escalate deliberately.** Spend premium quota when cheap lanes cannot resolve the uncertainty or when the consequence of being wrong is more expensive than the call.

## WHAT RATION IS NOT

RATION does not mean shallow research.
RATION does not mean skipping verification.
RATION does not mean tiny answers when a long artifact is actually required.
RATION does not mean choosing a weaker model for a task it cannot reliably perform.
RATION does not mean declaring success early to save tokens.

It means NouGen should behave like the meter is blinking red and every remaining call has to justify its existence.

## COMBO BEHAVIOR

**RATION + TOP .01%** = frontier rigor with ruthless source selection. Read the strongest evidence first and stop when the decision is evidence-complete.

**RATION + END TO END** = prove the whole path with the minimum set of high-signal boundary receipts and acceptance tests needed to establish the chain.

**RATION + RUN THE GAUNTLET** = execute the entire necessary repair chain, but eliminate duplicate audits, repeated context reconstruction, and low-information detours.

**RATION + KEEP THE CHAINS MOVING** = 3rd-and-short while the fuel light is on. Every action must gain a real yard.

**RATION + RELAY** = aggressively compress state so the next agent inherits knowledge rather than paying to rediscover it.

**RATION + DREAM** = generate fewer, higher-value branches and prune weak futures early.

## FLEET DESIGN IMPLICATION

RATION should eventually become an actual orchestration policy flag, not merely prompt language. Routers should be able to alter model selection, context budgets, retrieval depth, subagent fanout, retry budgets, batching, compression, and escalation thresholds while preserving mandatory verification gates.

Possible internal concept:
`resource_posture = ration`
with a synthetic remaining-budget assumption of approximately 1%.

The meter can say 83%. The fleet should still think:

**We have one magazine left. Make every round prove something.**

Done when all lanes interpret RATION consistently as resource-aware high-efficiency execution rather than simply shorter prose.
