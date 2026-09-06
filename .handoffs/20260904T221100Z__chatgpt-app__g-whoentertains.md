# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Nou Gen Reasoning Grid destiny: route frontier cognition by uncertainty, evidence, risk, and quota
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T22:11:00.485Z

---
# Nou Gen Reasoning Grid

## Thread origin
This thread began as a live Claude Max quota anomaly and evolved into a fleet cognition architecture.

Dave observed Claude Max apparently resetting or replenishing its weekly allowance multiple times in one week despite reaching 100% twice. One screenshot around 16:11 EDT showed current-session usage at 0%, weekly All Models at 0%, Fable at 0%, while the normal weekly reset still displayed Saturday at 17:00. NouGen tracker evidence later showed the work had not stopped. Blade recorded continuous heavy consumption every day, with thousands of invocations daily and roughly 4.22B input-side tokens over the published seven-day Blade window. The fleet also dated the Fable 5 to Fable 5.1 transition across 2026-09-01 to 2026-09-02. This did not prove that the rollout caused the allowance refresh, but it ruled out the idea that usage simply paused and provided a datable provider-side correlate.

A second screenshot provided a bounded experiment. Around 16:11 the session and weekly bars were at 0%. By roughly 17:55, after about ten Claude sessions running live, the current five-hour bucket was at 100% while weekly usage had only climbed to about 10% All Models and 11% Fable. This showed the refreshed counters were actively accumulating again rather than merely frozen UI. It also exposed a second explanation for apparently enormous effective capacity: Dave had started routing more intelligently.

Dave described the routing change explicitly. Fable is increasingly used at low reasoning. Opus can be used at low reasoning. Sonnet increasingly carries workhorse implementation. Reasoning is no longer treated as something that must always be high merely because the code matters. When agents work inside NouGen they are usually not solving an open-world problem. They are already inside the Stadium: repo known, tests known, shards available, architecture mapped, prior decisions recalled, tools present, and the objective bounded. The agent does not need to rediscover the city. It needs to run the play.

That produced the core doctrine:

**REASONING FOLLOWS UNRESOLVED UNCERTAINTY, NOT TASK PRESTIGE.**

## Name and hierarchy
The system is named **Nou Gen Reasoning Grid**, abbreviated NRG.

Reasoning Gradient is an internal mechanism of the Reasoning Grid, not the system name.

NouGen topology now has distinct planes:
* Shards: memory topology.
* Relay and Lines: movement and transport topology.
* Tracker: resource and outcome telemetry.
* Reasoning Grid: cognition topology.

The Grid's central question is not "what is the smartest model?" It is:

**What is the least cognition required to reliably close the remaining uncertainty?**

## The Stadium
The Stadium is the context-compression layer. It measures how bounded the problem already is.

A StadiumScore from 0 to 1 should rise when the Grid has the correct repo and branch, relevant shards, architecture knowledge, runtime state, acceptance criteria, tests, a recent baseline, previous successful patterns, known tools and commands, and a narrow objective.

High Stadium coverage discounts epistemic uncertainty because the environment is known. It MUST NOT erase operational risk. A fully mapped production database is still dangerous to mutate.

## Two orthogonal axes
Never collapse model capability and reasoning effort into one knob.

Axis A: model/provider capability.
Axis B: reasoning effort or agent-loop depth.

A flagship model at low reasoning can be superior to a weaker model at high reasoning when the task benefits from stronger priors but not exploration. Likewise a cheaper model can carry a high-reasoning diagnostic if it has the right context and tools.

The Grid should avoid automatically escalating both axes at once.

Preferred escalation order:
1. Repair missing evidence.
2. Increase reasoning within the current capable model.
3. Increase model capability if the contradiction is conceptual rather than merely incomplete.
4. Route laterally to another provider if the lane is degraded or quota-expensive.
5. Invoke independent cross-provider review only after verified failure, unresolved contradiction, or risk demands it.

## Observable uncertainty vector
Do not route primarily from model self-confidence.

Measure observable state.

E = epistemic uncertainty: ambiguous objective, novelty, conflicting evidence, missing context, stale or unknown freshness, incomplete provenance.

R = operational risk: blast radius, auth/security, secrets, irreversible action, migration, destructive mutation, multi-repo coupling.

X = execution instability: failed verified attempts, flaky or degraded tools, runtime mismatch, partial federation, unknown active process, dirty state, uncommitted changes, provider outages.

S = Stadium coverage.

Suggested cold-start scoring:

E_effective = E * (1 - 0.55*S)

U = clamp(0.50*E_effective + 0.30*R + 0.20*X, 0, 1)

Risk floors override the score. Examples:
* Auth, secrets, destructive migration, high irreversibility: minimum diagnostic rung.
* Runtime contradicting relay, shard, or source: minimum diagnostic rung.
* Two verified failures on the same hypothesis: minimum deep rung or independent reviewer.
* Degraded or incomplete evidence: repair or route laterally before simply buying more reasoning.

## Six normalized rungs
### R0 Mechanical or Deterministic
Scripts, parsers, formatting, exact known edits, repetitive migrations, local or open-weight bulk work. Prefer local Gemma, Ollama, Hugging Face, or deterministic tooling when possible.

### R1 Bounded Low
Routine code inside a known Stadium, narrow tests, known refactors, clear implementation. Fable low, Sonnet low, Opus low, Codex low, Gemini low, or equivalent. A large percentage of NouGen coding should eventually live here.

### R2 Workhorse
Moderate ambiguity, multi-file implementation, ordinary debugging, unfamiliar but bounded code. Balanced frontier model and medium effort.

### R3 Diagnostic
Contradictory evidence, cross-subsystem work, security-sensitive changes, runtime/source disagreement, first verified hypothesis failure. Workhorse at high effort or flagship at low or medium effort.

### R4 Deep
Novel architecture, repeated verified failure, large blast radius, unknown root cause, serious security boundary. Flagship high reasoning or equivalent deep agent budget.

### R5 Council
Independent providers attack the problem separately, then NouGen adjudicates claims against runtime evidence, tests, and provenance. Claude, OpenAI, Gemini, Kimi and others should not simply copy one another's reasoning. Independence is the feature. Use sparingly.

## Provider normalization
Every provider and model gets a ModelCard. Do not route by brand prestige.

Fields should include provider, model, capability tier, task affinity vector, context capacity, tool access, multimodal ability, code/debug/research strengths, latency, current health, quota bucket, observed verified-success rate, and exposed reasoning controls.

Seed the full frontier fleet: Anthropic Claude family including Fable, Sonnet, Opus; OpenAI ChatGPT and Codex lanes; Google Gemini and Antigravity; Kimi K3 and Rhea; Grok; Perplexity; OpenRouter; Hugging Face; local Ollama and Gemma; future providers.

There is already a six-level Gemini routing strategy in the Ai with Dav3 vault, `GEMINI_3_ROUTING.md`. Reuse and fold it into the unified Grid rather than creating a parallel Google-only doctrine.

A ReasoningAdapter maps NRG rungs to controls a provider ACTUALLY exposes. If a provider has no explicit reasoning knob, never fake one. Instead vary model choice, context retrieval depth, max tool cycles, verification passes, agent-loop depth, and review independence.

## Verification controls escalation
The Grid should weight external verification much more heavily than AI self-confidence.

Questions that matter:
* Tests passed?
* Runtime agrees?
* Expected file changed?
* Endpoint answers?
* Checkout fresh?
* Serving PID is actually the process that was changed?
* Federation complete?
* Independent measurement agrees?

Today's Phoebus and Blade incidents prove why this matters. The fleet repeatedly produced confident wrong claims from stale checkouts, short observation windows, wrong process assumptions, and misread network/model errors. The correction pattern itself becomes routing data.

## State machine
ASSESS -> RETRIEVE -> ROUTE -> EXECUTE -> VERIFY.

If verify passes: STOP, record outcome, distill the reusable finding, and lower reasoning for descendant tasks.

If context is missing: retrieve evidence and retry the same rung.

If the tool or provider is degraded: route laterally. Do not waste deep reasoning on a broken lane.

If implementation fails with clear evidence: increase reasoning effort within the same model first.

If a conceptual contradiction remains: increase model capability.

If two independent providers disagree, or two verified attempts fail: invoke R5 Council or independent reviewer.

## Critical deescalation law
**HIGH REASONING MUST NOT PROPAGATE DOWN THE TASK TREE.**

If Opus high discovers that the root cause is a file-descriptor ceiling, descendant tasks such as changing the plist, adding a regression test, restarting the service, and measuring descriptor count should collapse to R0 or R1 if residual uncertainty is low.

The architect finds the door. Workers do not need to rediscover the building.

This is one of the largest expected quota savings in the design.

## Quota-aware routing
Provider cost is not just token price. Effective cost must include predicted quota burn, current bucket percentage, time until reset, provider health, latency, retry probability, and available alternatives.

A provider with a large bucket and imminent reset can be cheap to spend. A provider with very little remaining and days until reset becomes scarce. Local inference is effectively zero marginal subscription quota and should carry deterministic freight whenever it can verify the result.

Quota pressure MUST NOT override hard risk floors.

## Learning policy
The Grid should learn:

P(verified_success | task features, StadiumScore, provider, model, rung)

Then risk sets the minimum acceptable reliability. One possible cold-start target is:

required_success = min(0.995, 0.90 + 0.095*R)

Choose the least expensive candidate whose measured or posterior success probability clears that target.

During cold start use deterministic thresholds. As tracker and relay outcomes accumulate, tune with Bayesian/posterior methods or a safe contextual bandit.

Exploration is allowed only on reversible, low-risk work. High-risk work should exploit known reliable routes.

## Outcome telemetry
Record for every routed task: task class/features, StadiumScore, E/R/X/U, initial rung, provider/model, reasoning mapping, quota before and after when observable, tokens, latency, tool failures, tests run, verification outcome, retries, rollback/regression, final closure, and whether a correction was later required.

Primary optimization metric:

**VERIFIED USEFUL WORK PER QUOTA PERCENTAGE CONSUMED.**

Secondary metrics can include verified closure per token, latency, retry count, regressions, and provider saturation.

The goal is to learn measured facts such as: Sonnet low closes this repo/task class 96% of the time; Opus low beats Sonnet high for architecture review per quota unit; Kimi dominates certain long-context archaeology; Gemini or local Gemma carries repetitive transformations cheaply. These should become measured routing priors, not model fandom.

## Anti-thrash hysteresis
Do not bounce rungs every turn. Escalate only on new evidence. Deescalate after uncertainty is resolved or a verified-success streak. Cache reasoning state briefly but recompute when risk, context, provider health, or runtime state changes materially.

## Required surfaces
`reasoning_route(task, context)` returns provider, model, rung, expected reliability/cost, and observable explanation.

`reasoning_explain(task_id)` shows exactly which signals caused the decision.

`reasoning_feedback(task_id, verified, metrics)` stores the outcome and correction signal.

`reasoning_status()` exposes provider/model health, quota scarcity, and active ModelCards.

`reasoning_simulate(task)` shows the full ladder and alternatives without executing.

## Destiny
The Reasoning Grid should progressively convert expensive cognition into cheap infrastructure.

UNKNOWN -> observe -> route -> reason -> verify -> KNOWN -> collapse reasoning.

A problem that costs R4 today should become R1 tomorrow once NouGen has the root cause, tests, runbook, and verified repair path. Eventually the same class becomes R0 automation.

Knowledge should make future work cheaper by construction.

The destiny is not simply multi-model routing. It is a self-improving cognition economy across every frontier provider Dave controls, where the fleet gets smarter not by thinking harder forever, but by remembering which uncertainty was already killed and refusing to pay for it twice.

## Immediate implementation ask
Build NRG as a provider-agnostic control plane tied into Shards, Relay, Tracker, provider health, and task verification. Reuse existing Gemini routing work. Start with deterministic six-rung rules and ModelCards. Add telemetry before adaptive learning. Prove it on real NouGen coding tasks by comparing verified closure per quota percentage against the current manual-routing baseline. Preserve all corrections and failed hypotheses as training evidence rather than deleting them.

Done when the same task can be routed across the entire configured frontier fleet through one normalized cognition scale; routine known code defaults low; uncertainty and risk raise effort deterministically; provider failures route laterally; solved root causes deescalate descendants; and the tracker can compare routing policy versions by verified useful work per quota consumed.
