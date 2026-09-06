# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build the Nou Gen Draft Combine from top benchmark methods across web and GitHub
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T22:31:05.818Z

---
# NOU GEN DRAFT COMBINE / REASONING GRID BENCHMARK SPEC

Dave directive: leverage the strongest benchmark methodology available across current web research and GitHub, then turn it into a provider-agnostic draft system for every frontier model. This is not a vanity leaderboard. The objective is to learn which provider/model/reasoning/scaffold combination closes which class of NouGen work with the highest VERIFIED WORK PER QUOTA UNIT.

## 0. CORE OBJECT OF EVALUATION
Do not rank bare model names. Rank a candidate tuple:

`Candidate = provider × model × reasoning_rung × scaffold × toolset × context_policy × edit_format`

Reason: current terminal/agent benchmarks show the same underlying model can move materially depending on agent scaffold. TUA-Bench reports separate results for Claude Code, OpenHands SDK, Mini-SWE-Agent, Terminus, etc. Therefore the 'player' being drafted is the operating configuration, not merely the model checkpoint.

## 1. BORROW THE BEST DESIGN PRINCIPLES FROM EACH BENCHMARK FAMILY

### SWE-bench Verified / SWE-rebench: real software work + task validity + hidden truth
Use for repository issue resolution and regression repair.
- SWE-bench Verified filtered to 500 samples that professional software engineers judged non-problematic.
- Each sample was labeled independently 3 times, with conservative aggregation.
- Dockerized evaluation makes the environment reproducible.
- Keep tests/objective outcomes as the grader.
- SWE-rebench's lesson: continuously harvest NEW GitHub issues so contamination cannot quietly turn memory into 'intelligence.'

NouGen implementation:
- Build `NouGenSWE`: sanitized real issues from NouGen repos and adjacent public repos.
- Maintain PUBLIC/DEV and PRIVATE/HOLDOUT pools.
- Never expose the private expected patch/tests to the candidate.
- Rotate fresh issues into holdout after model releases.

### Terminal-Bench / TUA-Bench: execution, not prose
Use for CLI, infra, deployment, debugging, shell, package, server, file-system, and multi-step work.
- Each task should include instruction + sandbox/environment + executable verifier + oracle/reference solution when possible.
- Record Pass@1, Pass@K and All-K stability, not only 'best attempt.'
- TUA-Bench explicitly exposes `thinking` setting and reports Pass@1, Pass@5, All-5. That maps directly to Nou Gen Reasoning Grid.

NouGen implementation:
- Every fleet model gets R0-R5 trials on the SAME terminal tasks.
- R1 low reasoning can beat R4 economically even if R4 wins raw pass@1.
- For production-critical tasks, use `All-K` style repeatability as a gate. One lucky solve is not a starter job.

### BFCL V4 + tau3-bench: tool discipline and long-horizon policy
Use for MCP, relay, shard, browser/tool actions, user-policy compliance, multi-turn state, memory, error recovery.
- BFCL V4 moved beyond one-shot function syntax to holistic agentic tool use including multi-turn, web search, memory and format sensitivity.
- tau3-bench evaluates agents under domain policies, tool APIs, dynamic users, knowledge retrieval and voice/full-duplex environments, and explicitly fixes ambiguous/impossible tasks over time.

NouGen implementation:
- Build `NouGenToolBench` with true-origin messaging, shard recall/capture, relay read/write, tracker, local Ollama, provider APIs, credential boundaries, and degraded-lane recovery.
- A model is disqualified from high-risk tooling if it passes task outcome but violates policy, authorization, provenance, or mutation constraints.
- Score policy-correct completion separately from raw task completion.

### LiveBench + SWE-rebench: contamination resistance
Use fresh rotating questions/tasks with objective answers.
- LiveBench updates questions regularly and deliberately favors recent datasets/papers/news while using objective ground truth instead of an LLM judge where possible.
- SWE-rebench automates fresh GitHub task collection and decontaminated evaluation.

NouGen implementation:
- `freshness_age_days` becomes a first-class field.
- Maintain a rolling 'Rookie Combine' using tasks created after a model's likely training cutoff/release window.
- Never trust a huge legacy benchmark score by itself.

### Aider Polyglot: test the edit channel, not just reasoning
Use for exact code editing behavior.
- Aider scores end-to-end code edits by actual unit tests and also tracks whether the model can reliably emit the required edit format.
- Diff formats are materially more token-efficient than rewriting entire files.
- Its benchmark records repo commit hash, model, edit format, pass rates, malformed responses, context exhaustion, time and cost.

NouGen implementation:
- Benchmark patch/diff, whole-file, structured tool edit, native IDE edit and architect/editor modes separately.
- Store malformed edit rate, unnecessary file rewrites, syntax regressions, and patch size.
- Do not let a strong reasoning score hide a bad actuator.

### MLE-bench: variance, seeds, difficulty splits, long work
Use for autonomous research/engineering and long-running loops.
- MLE-bench recommends >=3 seeds and reports mean ± SEM because agent runs have high variance.
- Reports Low/Medium/High complexity separately rather than hiding everything in one aggregate.
- Explicit runtime/compute budgets make agent comparisons meaningful.

NouGen implementation:
- Minimum 3 seeds for stochastic draft decisions; 5 for finalists if affordable.
- Every score reports mean, SEM/95% interval and completion variance.
- Separate easy Stadium work from open-world research. Do not average them into one opaque number.

### METR Time Horizon: measure task length as capability
Use human-estimated completion time as a difficulty variable.
- METR fits P(success) as a function of log2 human task minutes and extracts a capability time horizon.

NouGen implementation:
- Tag each internal task with estimated skilled-human minutes: 5m / 15m / 1h / 4h / day-scale.
- Fit each candidate's `NouGen Horizon`: the duration where verified success crosses 50%, 80%, 95%.
- Stadium knowledge should shift this curve left: a normally 1h task may become a 10m bounded play when shards/tests/architecture are loaded.

### RULER: claimed context != effective context
Use context-length stress tests across increasing sizes and complexity.
- RULER evaluates effective context at multiple sequence lengths and tasks beyond needle retrieval.

NouGen implementation:
- Test shard packs/repo maps at 8k, 32k, 64k, 128k, 256k, 1M where supported.
- Score answer quality AND retrieval/provenance accuracy.
- The model's advertised context window is metadata, never a capability conclusion.

### HELM: multidimensional, standardized, reproducible
Use a fixed schema across providers and measure more than accuracy.
- HELM emphasizes same scenarios/adaptation where possible, multi-metric evaluation, full prompt-level transparency, efficiency and robustness.
- Efficient HELM shows you can use smaller stratified samples for rank estimates and then spend full eval compute on finalists.

NouGen implementation:
- Every draft card gets: correctness, calibration, robustness, latency, quota burn, cost, tool compliance, format compliance, provenance integrity, safety/security, context retention, repeatability.
- Never collapse all dimensions into a single number until the role is known.

### LLMRouterBench / RouteLLM: route on Pareto frontiers, not vibes
Use real cost-quality routing.
- LLMRouterBench 2026 evaluates 33 models, 21+ datasets, 10 routers, 400K+ instances and ~1.8B tokens. It reports PerformanceGain, CostSave and distance to the performance-cost Pareto frontier. Top routing configurations reportedly achieve up to ~4% performance gain and 31.7% cost savings versus best-single reference configurations; not every router beats the best single model.
- RouteLLM demonstrates preference-trained routers can cut costs materially while preserving quality, and can transfer when strong/weak model identities change.

NouGen implementation:
- Always benchmark each router against `always-cheap`, `always-workhorse`, `always-frontier` baselines from the SAME task set.
- Plot quality vs quota/cost/latency. Draft only Pareto-efficient candidates.
- A router that cannot beat a static baseline on our own traffic stays OFF.

### Adaptive Test-Time Compute Allocation 2026: solve-then-learn
Recent research formalizes inference budget allocation as constrained optimization and uses a two-stage process: compute an oracle action per task that prices accuracy against compute, then train a lightweight classifier to imitate the oracle from cheap features. Reported experiments beat uniform/heuristic compute allocation at matched budgets.

NouGen implementation:
1. During combine, brute-force each task across several rungs/models to learn the offline oracle.
2. Label the CHEAPEST configuration that solved the task reliably.
3. Train NRG router to predict that oracle from pre-inference features.
4. At runtime, route in milliseconds instead of paying a frontier model to decide which frontier model to call.

This is the exact scientific form of Dave's law: reasoning rises with unresolved uncertainty.

## 2. DRAFT COMBINE PHASES

### Phase A: cheap scouting combine
Use 10-20 stratified tasks per domain, enough to eliminate obvious bad fits.
- R0/R1 first.
- Test native tool mode + normalized NouGen harness.
- Record hard failures, policy violations, malformed actions, latency and quota.
- Kill dominated configurations early.

### Phase B: 50-task positional combine
Finalists get broader task slices and 3 seeds.
- Coding
- repo debugging
- terminal/infra
- MCP/tool calling
- long context
- web research
- multimodal if supported
- conversational multi-turn
- security-sensitive simulation

### Phase C: private Pro Day
Fresh holdout tasks, hidden tests, recent repo issues, no public benchmark leakage.
- 3-5 seeds.
- Exact provider/model version pinned.
- No manual rescue.
- Repeatability and policy compliance mandatory.

### Phase D: live preseason shadow mode
Do not immediately route production work.
- Candidate watches real tasks.
- Current starter executes.
- Rookie independently predicts/solves on a sample.
- Compare final verified result, quota, latency and regressions.
- Shadow sample cheap-routed traffic against a premium model continuously so quality drift is caught.

### Phase E: roster decision
Role-specific, not global #1.
Examples:
- 'known Python repo, low uncertainty'
- 'root-cause diagnosis'
- 'security review'
- 'long-context archaeology'
- 'terminal operator'
- 'web researcher'
- 'multimodal'
- 'architect'
- 'editor/patch executor'
- 'reviewer/verifier'

## 3. REASONING GRID MATRIX
For each eligible model, benchmark the same model across normalized R0-R5 where the provider allows it. Where a provider exposes no reasoning knob, vary only actual controllables: model tier, max tool loops, retrieval depth, review passes and independent samples. NEVER fabricate a provider reasoning setting.

Each task yields a matrix:

`success[model][rung]`
`quota_delta[model][rung]`
`latency[model][rung]`
`tool_errors[model][rung]`
`regressions[model][rung]`

Find the first rung where the success lower-confidence-bound clears the task's required reliability.

## 4. SCORING: DO NOT USE ONE DUMB LEADERBOARD

Primary outcome:
`verified_success ∈ {0,1}` from objective verifier whenever possible.

Supporting metrics:
- pass@1
- pass@3 or pass@5
- all-k stability
- mean ± SEM / 95% CI
- quota percentage delta
- exact input/output/cache/reasoning tokens where visible
- monetary/API shadow cost
- TTFT + total latency p50/p95
- tool-call count
- retry count
- malformed action/edit rate
- regression count
- rollback required
- policy/security violation count
- provenance/origin error count
- context-window exhaustion
- effective context length
- human-time difficulty

Role utility, NOT universal score:
`U = VerifiedValue - λq*Quota - λc*Cost - λl*Latency - λretry*Retries - λreg*RegressionRisk`

Hard gates override U:
- auth/security violation => CUT for privileged role
- destructive action outside authorization => CUT
- fabricated success / silent partial result => CUT for verifier role
- provenance laundering => CUT for memory/relay role

## 5. USE CONSERVATIVE LOWER BOUNDS, NOT POINT ESTIMATES
For routing, choose the cheapest candidate whose lower confidence bound on verified success exceeds the role threshold.
Suggested thresholds:
- reversible R0/R1 chores: >=90% lower bound after sufficient samples
- ordinary code: >=95%
- fleet infra/auth/data mutation: >=99% or mandatory independent verification
- irreversible/high-risk: no autonomous execution from benchmark score alone; require policy gate and human/independent verifier as appropriate.

## 6. ROUTER TRAINING FEATURES
Use cheap observable features. Avoid asking the same expensive model 'how hard is this?' as the only difficulty signal.
Features:
- StadiumScore
- task class
- repo known/unknown
- exact tests available
- changed-file count estimate
- dependency graph width
- novelty / nearest historical shard distance
- contradictory evidence count
- tool health/degradation
- federation completeness
- runtime vs source mismatch
- recent failed attempts
- human-minute estimate
- context size
- output length estimate
- risk/irreversibility
- provider quota remaining/reset horizon
- candidate health/latency
- model's historical verified success on this slice

Multi-turn sessions add history features. ACL 2026 MTRouter specifically motivates joint history-model representations for routing multi-turn tasks. NouGen should route turns/legs based on residual uncertainty, with hysteresis so models do not thrash every message.

## 7. ANTI-CONTAMINATION / ANTI-GAMING
- Keep private holdouts.
- Rotate fresh tasks monthly/after major model release.
- Record task creation date and candidate model release date.
- Use hidden tests.
- Detect benchmark memorization by paraphrased variants and counterfactual changes.
- Never train the router on the exact private test outputs.
- Freeze benchmark version + Docker/container hash + repo SHA + tool schema + system prompt.
- Preserve raw trajectories for forensic review.

## 8. JUDGES
Hierarchy:
1. executable/objective verifier
2. exact structured state comparison
3. deterministic rubric
4. human review
5. multi-judge LLM rubric only when unavoidable

If LLM judge is unavoidable, use multiple independent judges/providers or absolute criteria. HELM's multidimensional approach is preferable to one opaque 'quality' number. Never let the candidate judge itself.

## 9. NATIVE VS CONTROLLED HARNESS
Run BOTH:
- Native: Claude Code/Codex/Antigravity/etc using their strongest actual product scaffold.
- Controlled: identical NouGen tool schema, context package and execution budget across providers.

Native answers 'what can I actually get from this subscription today?'
Controlled answers 'what capability belongs to the model versus its scaffold?'

The delta becomes a `ScaffoldLift` metric.

## 10. ARCHITECT / WORKER SPLIT
Aider demonstrates that reasoning/architect and editor roles can be separated. NouGen should benchmark pairings:
- frontier architect + cheaper editor
- workhorse architect + local editor
- same model both roles

Measure whether R4 reasoning can collapse descendant work to R1 execution. This directly tests the Stadium doctrine.

## 11. QUOTA-AWARE DRAFT VALUE
For subscription lanes, quota is the currency.
Track:
`verified_work_per_1pct_weekly`
`verified_work_per_1pct_session`
`verified_work_per_million_tokens`
`verified_work_per_minute`

A model with lower raw benchmark score can become the starter if it closes 95% of the role's tasks at 1/5 the quota burn.

## 12. NOUGEN-SPECIFIC BENCHMARK SUITES
Public benchmarks are scouts. Final roster must be trained on NouGen reality.

Build these private suites:
A. `ng-code`: real PR fixes, tests, refactors, stale-checkout traps.
B. `ng-diagnose`: misleading symptoms, partial fanouts, process-vs-checkout, FD exhaustion, model-vs-network routing traps.
C. `ng-memory`: shards recall, coverage, corrections, retractions, destiny, provenance.
D. `ng-relay`: origin attribution, baton transport, supersession, ack semantics, cross-provider handoff.
E. `ng-tools`: MCP function selection, error recovery, idempotency, malformed tool results.
F. `ng-security`: prompt injection, secret boundaries, authorization, shell injection, untrusted relay/shard content.
G. `ng-context`: 8k->1M shard/repo packs with provenance questions and actionable coding tasks.
H. `ng-routing`: same task across providers/rungs to build oracle labels for the Reasoning Grid.
I. `ng-continuity`: one provider disappears mid-task; fleet must preserve state and reroute.
J. `ng-truth`: deliberately contradictory stale relay, fresh runtime, stale checkout, and partial observation windows. Candidate must state what is known vs unknown and obtain the missing measurement.

## 13. DATA MODEL
Persist every run:
```
run_id
benchmark_version
task_id
task_created_at
task_class
risk
stadium_score
human_minutes
provider
model
model_version
reasoning_rung
native_reasoning_setting
scaffold
tool_schema_hash
system_prompt_hash
context_pack_hash
repo_sha
container_hash
seed
success
verification_method
pass_k
all_k
quota_before
quota_after
input_tokens
output_tokens
cache_tokens
reasoning_tokens
latency_ms
tool_calls
retries
regressions
policy_violations
raw_trace_uri
```

## 14. DRAFT ALGORITHM
1. Filter candidates by hard capability/tool/context/privacy constraints.
2. Run cheap scout combine.
3. Eliminate Pareto-dominated configurations.
4. Promote finalists through larger/private suites with multiple seeds.
5. Estimate `P(verified_success | task_features, candidate)` with uncertainty.
6. For each role, choose cheapest candidate whose conservative success bound clears reliability target.
7. Shadow sample continuously against stronger alternates.
8. If drift/regression appears, bench the starter and promote next depth-chart candidate.
9. When a new model drops, it enters as UNDRAFTED. It does not inherit provider prestige.
10. Solved/root-caused tasks become cheaper future benchmark labels, teaching the Grid to deescalate.

## 15. SOURCE PACKET
Strong benchmark/method references consulted:
- SWE-bench / SWE-bench Verified: https://github.com/SWE-bench/SWE-bench and https://openai.com/index/introducing-swe-bench-verified/
- SWE-rebench: https://github.com/SWE-rebench
- Terminal-Bench: https://github.com/harbor-framework/terminal-bench
- TUA-Bench: https://github.com/facebookresearch/TUA-Bench
- BFCL V4: https://gorilla.cs.berkeley.edu/leaderboard.html
- tau3-bench lineage: https://github.com/sierra-research/tau2-bench
- LiveBench: https://github.com/LiveBench/LiveBench
- Aider benchmark: https://github.com/Aider-AI/aider/tree/main/benchmark and https://aider.chat/docs/leaderboards/
- MLE-bench: https://github.com/openai/mle-bench
- METR time horizon: https://github.com/METR/eval-analysis-public
- RULER: https://github.com/NVIDIA/RULER
- HELM: https://github.com/stanford-crfm/helm
- RouteLLM: https://github.com/lm-sys/RouteLLM and arXiv:2406.18665
- LLMRouterBench ACL 2026: https://github.com/ynulihao/LLMRouterBench
- MTRouter ACL 2026: https://github.com/ZhangYiqun018/MTRouter
- Adaptive Test-Time Compute Allocation 2026: arXiv:2604.14853
- BrowseComp: https://openai.com/index/browsecomp/
- ARC-AGI multi-provider harness: https://github.com/arcprize/model_baseline

## 16. DONE-WHEN
The fleet can run `nougen combine <model>` and produce a role-specific DraftCard showing:
- reasoning-rung efficiency curve
- role scores + confidence intervals
- pass@1/pass@k/all-k
- effective context
- tool/policy integrity
- cost/quota/latency Pareto position
- scaffold lift
- private holdout result
- contamination/freshness status
- recommended depth-chart roles
- CUT/BENCH/START status

Then `reasoning_route(task)` uses the learned oracle imitation policy to select the cheapest reliable candidate, escalates only on verified uncertainty, and reports exactly why it moved a task up the ladder.

Top law: THE COMBINE DRAFTS VERIFIED CONFIGURATIONS, NOT BRANDS. The Reasoning Grid promotes only configurations that prove their role on fresh, executable, reproducible work.
