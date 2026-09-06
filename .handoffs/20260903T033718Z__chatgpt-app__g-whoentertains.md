# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: War game NouGen CLI into a top-tier cross-provider agent harness with stopwatch, context governor, resumable sessions, tools, subagents, and Hardcade events
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T03:37:18.657Z

---
# NOUGEN CLI WAR GAME: TOP TIER AGENT HARNESS, SEPT 2026

## Mission
NouGen CLI is already powerful as a relay/control-plane surface, but it does not yet feel as versatile as Claude Code, Codex, Gemini CLI/AGY-class agent CLIs because the missing advantage is not raw model intelligence. The missing advantage is the persistent agent runtime around the model: session continuity, context governance, tool lifecycle, approvals, subagents, resumability, checkpoints, streaming events, workspace rules, telemetry, and verification loops.

Build NouGen as a vendor-neutral agent harness. Ollama, OpenRouter, Hugging Face, Claude, Codex/OpenAI, Gemini, and future providers become interchangeable brains behind one execution spine.

CORE LAW:

    user intent
        -> NouGen Context
        -> session kernel
        -> planner/router
        -> provider adapter
        -> tool/subagent loop
        -> verifier
        -> Fleet Expression events
        -> Hardcade / compact / raw renderer
        -> durable checkpoint + shards

The model is a replaceable engine. NouGen owns the car.

## Current external receipts, researched today
1. Anthropic's current Claude Code guidance emphasizes the read/plan/act/observe agent loop, CLAUDE.md, plan mode, skills, hooks, subagents, MCP, and context strategies for large repos. Their 2026 guidance explicitly treats hooks + subagents as orchestration primitives and recommends context discipline rather than feeding entire large repos.
2. Anthropic's auto-mode design uses tiered permissions, prompt-injection screening on tool outputs, classifier-gated risky actions, recursive controls on subagent delegation/return, and deny-and-continue rather than killing the whole session.
3. OpenAI's current Codex deployment guidance emphasizes sandbox boundaries, approval policies, network/path controls, and agent-native telemetry. Low-risk work should flow without friction, higher-risk boundary crossings should be explicit.
4. Hugging Face Inference Providers now exposes an OpenAI-compatible Responses API with semantic streaming events, built-in tool orchestration, structured outputs, reasoning controls, multi-provider routing, and Remote MCP. This means HF can participate in a first-class agent loop rather than being treated as a dumb text completion lane.
5. OpenRouter's 2026 guidance explicitly supports writing one tool loop and swapping providers/models, with provider fallback/routing across many backends. Treat OpenRouter as a routing fabric, not the agent runtime itself.
6. Ollama supports structured outputs and streaming tool calls. Local models can therefore obey the same typed event/tool contract as cloud providers when the harness normalizes them.
7. Gemini CLI currently exposes resumable sessions, checkpoints, hooks, MCP, sandboxing, approval modes, streaming JSON output, background shell completion behavior, telemetry, context-file loading, and tool-output summarization budgets. These are exactly the runtime primitives NouGen should own centrally.

## LAW 1: CLAUDE ALWAYS ENTERS THROUGH NOUGEN CONTEXT
No direct Claude session should start 'naked' if it belongs to NouGen work. SessionStart/UserPromptSubmit style hooks, wrapper launchers, or CLI adapters must request a NouGen Context packet before the first meaningful model turn.

Do NOT dump raw shards into Claude. Context is a compiler.

Target budget:
- ideal packed context: 32k to 64k tokens
- normal hard ceiling: 80k
- absolute NouGen policy ceiling: 96k
- NEVER intentionally cross 100k for shard bootstrap unless user explicitly requests deep archival mode
- reserve remaining provider context for live dialogue, tool results, code diffs, and reasoning

This directly attacks the current >150k context penalty observed in fleet usage.

### Context packet contract
```python
from pydantic import BaseModel, Field
from typing import Literal

class EvidenceRef(BaseModel):
    shard_id: int | None = None
    db_index: int | None = None
    source: str
    timestamp: str | None = None
    confidence: float = 1.0

class ContextSection(BaseModel):
    kind: Literal['identity','mission','workspace','memory','decision','constraint','recent','evidence']
    text: str
    refs: list[EvidenceRef] = []
    priority: int = 50
    token_estimate: int = 0

class NouGenContextPacket(BaseModel):
    session_id: str
    provider: str
    objective: str
    budget_tokens: int = 64000
    sections: list[ContextSection]
    omitted_count: int = 0
    coverage_note: str | None = None
    digest: str
```

### Context governor
```python
class ContextGovernor:
    def __init__(self, soft=64_000, hard=80_000, absolute=96_000):
        self.soft = soft
        self.hard = hard
        self.absolute = absolute

    async def build(self, objective, provider, workspace):
        candidates = await retrieve_multiarm(objective, workspace)
        candidates = dedupe_by_semantics(candidates)
        candidates = rank_by_relevance_recency_truth(candidates)

        # Preserve evidence/provenance, compress prose.
        packed = []
        used = 0
        for item in candidates:
            compact = await distill_if_needed(item)
            cost = estimate_tokens(compact.text)
            if used + cost > self.soft:
                continue
            packed.append(compact)
            used += cost

        if used > self.hard:
            packed = hierarchical_compress(packed, target=self.soft)

        assert sum(x.token_estimate for x in packed) < self.absolute
        return make_packet(packed, objective, provider)
```

### Retrieval policy
Do not do 'recall 100 shards and paste them'. Use stages:
1. Intent classifier
2. coverage check when absence matters
3. semantic recall top N
4. keyword arm for exact nouns/ids
5. date window only if temporal intent exists
6. dedupe
7. amendment/retraction resolution
8. evidence weighting
9. hierarchical distillation
10. final token pack

Each context section should have a tiny provenance footer or machine-readable refs so the model can request expansion only when needed.

Use progressive disclosure:

    INDEX -> CAPSULE -> FULL SHARD

The model initially sees a capsule. If it needs the underlying receipt, it calls context_expand(ref).

## LAW 2: ONE PROVIDER-NEUTRAL RESPONSE/EVENT CONTRACT
Normalize every provider into the same semantic interface. Hugging Face Responses API is a strong reference shape because it already uses semantic events. Do not bind NouGen to any one vendor's SDK object model.

```python
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol

@dataclass
class AgentEvent:
    type: str                 # response.delta, tool.call, tool.result, checkpoint, etc.
    session_id: str
    provider: str
    agent: str
    ts_ns: int
    data: dict[str, Any] = field(default_factory=dict)

class ProviderAdapter(Protocol):
    async def stream(self, *, messages, tools, settings) -> AsyncIterator[AgentEvent]: ...
    async def count_tokens(self, payload) -> int: ...
    def capabilities(self) -> set[str]: ...
```

Adapters:
- ClaudeAdapter
- OpenAIResponsesAdapter / CodexAdapter
- GeminiAdapter
- OpenRouterAdapter
- HuggingFaceResponsesAdapter
- OllamaAdapter

Capabilities are discovered, not assumed:
```python
CAPS = {
  'tools', 'parallel_tools', 'structured_output', 'reasoning',
  'vision', 'mcp', 'streaming', 'session_resume', 'prompt_cache'
}
```

Router chooses based on required capabilities, latency, cost, local/free preference, context size, and historical success rate.

## LAW 3: STOPWATCH IS A CONTROL-PLANE PRIMITIVE
NouGen now needs a real stopwatch/timer layer. Not just UI. Every relay, claim, tool, subagent, provider request, verification run, and user objective should be measurable.

Call it NouGenWatch timing kernel or Stopwatch service.

### Why
- measure time-to-first-token
- measure tool latency
- measure claim wait
- measure active execution vs idle/user wait
- detect hung agents
- enforce budgets/deadlines
- compare providers on identical tasks
- drive Hardcade streaks and speed records from truth
- discover where NouGen spends wall time
- support user timers and task countdowns through same primitive

### Timer data model
```python
from dataclasses import dataclass, field
from time import perf_counter_ns
from uuid import uuid4

@dataclass
class Stopwatch:
    id: str
    scope: str
    started_ns: int
    laps: list[tuple[str, int]] = field(default_factory=list)
    stopped_ns: int | None = None

    @classmethod
    def start(cls, scope: str):
        return cls(str(uuid4()), scope, perf_counter_ns())

    def lap(self, name: str):
        now = perf_counter_ns()
        self.laps.append((name, now))
        return (now - self.started_ns) / 1e9

    def stop(self):
        self.stopped_ns = perf_counter_ns()
        return (self.stopped_ns - self.started_ns) / 1e9
```

### Async instrumentation
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def timed(scope, event_bus, **meta):
    sw = Stopwatch.start(scope)
    await event_bus.emit('timer.started', timer_id=sw.id, scope=scope, **meta)
    try:
        yield sw
    except Exception as exc:
        elapsed = sw.stop()
        await event_bus.emit('timer.failed', timer_id=sw.id, elapsed_s=elapsed,
                             error=type(exc).__name__, **meta)
        raise
    else:
        elapsed = sw.stop()
        await event_bus.emit('timer.completed', timer_id=sw.id, elapsed_s=elapsed, **meta)
```

Usage:
```python
async with timed('provider.response', bus, provider='hf', model=model) as sw:
    async for event in adapter.stream(...):
        if event.type == 'response.first_delta':
            sw.lap('ttft')
        await bus.publish(event)
```

### Timer MCP/tool surface
Expose:
- timer_start(scope, deadline=None, tags=[])
- timer_lap(timer_id, label)
- timer_stop(timer_id)
- timer_status(timer_id)
- timer_list(active_only=True)
- timer_budget(timer_id, warn_at_pct=80)

The same service supports human timers:

    `nougen timer 25m "patio center pile"`

and autonomous runtime timers:

    relay claim TTL
    provider timeout
    subagent SLA
    verification deadline

Do not use separate implementations for 'user countdown' and 'agent latency'. One timing substrate, different renderers.

## LAW 4: SESSION KERNEL MUST BE DURABLE AND RESUMABLE
Claude/Gemini/Codex feel alive because you can keep working in a session. NouGen needs a provider-independent session ledger.

Recommended storage: append-only JSONL event log + SQLite index locally. Remote replication can be optional.

```python
class SessionState(BaseModel):
    session_id: str
    objective: str
    workspace: str
    created_at: str
    updated_at: str
    provider_history: list[str]
    checkpoint_id: str | None
    context_digest: str
    pending_tools: list[str]
    open_relays: list[str]
    active_timers: list[str]
```

Commands:
- `nougen chat`
- `nougen resume latest`
- `nougen resume <id>`
- `nougen checkpoint save <tag>`
- `nougen rewind <turn|checkpoint>`
- `nougen fork <session>`
- `nougen share <session>`

Provider failover must NOT destroy the session. Claude can fail and Ollama/OpenRouter/HF can continue from the same NouGen state packet.

## LAW 5: THE AGENT LOOP BELONGS TO NOUGEN
Implement the loop outside the model.

```python
async def run_agent(session, objective):
    context = await context_governor.build(objective, session.provider, session.workspace)
    state = await load_state(session)

    for turn in range(MAX_TURNS):
        route = router.select(objective, state, required_caps=state.required_caps)
        adapter = providers[route.provider]

        async with timed('agent.turn', bus, provider=route.provider, turn=turn):
            async for ev in adapter.stream(
                messages=state.messages_with(context),
                tools=tool_registry.schemas(route),
                settings=route.settings,
            ):
                await bus.publish(ev)

                if ev.type == 'tool.call':
                    decision = await policy.authorize(ev, state)
                    result = await tool_executor.run(ev, decision)
                    state.append_tool_result(result)

                elif ev.type == 'delegate':
                    result = await supervisor.spawn(ev, parent=state)
                    state.append_subagent_result(result)

                elif ev.type == 'response.completed':
                    state.append_response(ev)

        verdict = await verifier.evaluate(state, objective)
        if verdict.done:
            await checkpoint(state, reason='objective_complete')
            return verdict

        if verdict.needs_more_evidence:
            context = await context_expand(verdict.refs)

    return await escalate_or_checkpoint(state)
```

Important: the loop decides when to continue. Do not rely on a single model response to magically finish the task.

## LAW 6: TOOL KERNEL WITH TYPED SCHEMAS + RESULT BUDGETS
Every tool has:
- JSON schema
- risk class
- timeout
- output token budget
- idempotency metadata
- read/write/network capability tags
- retry policy
- audit event

```python
class ToolSpec(BaseModel):
    name: str
    description: str
    input_schema: dict
    risk: Literal['read','project_write','network','host','destructive']
    timeout_s: int = 60
    output_budget_tokens: int = 4000
    idempotent: bool = False
```

Large tool results never enter context raw. Summarize/truncate with refs to full artifacts. Gemini CLI already exposes per-tool summarization budgets; NouGen should generalize that across every provider.

## LAW 7: TIERED APPROVALS, NOT APPROVAL SPAM
Adopt the best pattern from modern Claude/Codex/Gemini systems:

Tier 0: pure reads / recall / grep -> automatic
Tier 1: writes inside trusted workspace -> automatic or configurable
Tier 2: network / external side effects -> policy gate
Tier 3: destructive / irreversible / secrets / privileged -> explicit approval

A denial should be `deny and continue`, not crash the session. Agent should try a safer path. Repeated denials trip escalation.

Security MUST be enforced by environment/sandbox boundaries too, not solely model judgment.

## LAW 8: SUBAGENTS ARE ISOLATED WORKERS, NOT CONTEXT MULTIPLIERS
Do not copy the parent 80k packet into every subagent. Give each subagent a task-specific micro-context, ideally 8k to 24k.

Spawn only when:
- work is parallelizable
- context can be isolated
- independent verification is useful
- tool permissions differ

Do NOT spawn for simple grep, single file edits, sequential dependent work.

```python
class SubagentTask(BaseModel):
    goal: str
    acceptance: list[str]
    context_refs: list[str]
    tool_allowlist: list[str]
    token_budget: int = 16000
    wall_budget_s: int = 300
    preferred_lane: str | None = None
```

Supervisor tracks stopwatch, budget, tool use, and return confidence. Parent receives a concise result packet plus provenance, never the entire child transcript.

## LAW 9: PROVIDER ROUTING SHOULD BE EVIDENCE-DRIVEN
Track per-provider metrics by task class:
- success_rate
- verified_success_rate
- ttft_p50/p95
- completion_latency_p50/p95
- tool_call_validity
- schema_compliance
- retry_rate
- cost
- token efficiency
- context ceiling
- local/free availability

Then route dynamically.

Example policy:
```python
score = (
    4.0 * verified_success
  + 1.5 * tool_success
  + 1.0 * schema_success
  - 0.8 * latency_norm
  - 0.6 * cost_norm
  - 1.2 * recent_failure_rate
)

if user_policy.free_first:
    score += 2.0 if route.cost == 0 else 0
if task.requires_local:
    score = -1e9 if not route.local else score
```

OpenRouter/HF can perform provider-level routing underneath this, but NouGen still owns task-level routing and the fallback decision.

## LAW 10: VERIFICATION IS A SEPARATE PHASE
Every serious coding/ops task ends with evidence, not 'looks good'.

Verifier can require:
- tests
- lint/typecheck
- diff review
- health endpoint
- artifact existence
- relay acknowledgement
- shard receipt
- expected stdout/schema

Never let the same generation that made the change be the only judge of success when cheap independent checks exist.

Hardcade maps this truthfully:

    tests green -> FLAWLESS VICTORY
    retry -> RUN IT BACK
    hidden dependency -> SECRET FIGHTER DISCOVERED

No fake victory lines without verifier evidence.

## LAW 11: FLEET EXPRESSION PROTOCOL IS THE UNIVERSAL EVENT BUS
The CLI renderer should consume semantic events from the runtime, not scrape logs.

Minimum events:
- session.started
- context.build.started/completed
- context.expanded
- route.selected
- provider.started/first_delta/completed/failed
- tool.requested/approved/started/completed/failed
- subagent.spawned/completed/failed
- relay.created/acked
- shard.recalled/captured/amended
- timer.started/lap/warning/completed
- verify.started/passed/failed
- checkpoint.saved
- objective.completed

Render modes:
1. Hardcade social mode
2. Compact mode
3. Raw JSON/telemetry mode

Same truth, different presentation.

## LAW 12: NOUGENWATCH = OBJECTIVE + TIMER + CONDITION LAYER
NouGenWatch should own proactive pressure and time awareness.

Watch object:
```python
class Watch(BaseModel):
    id: str
    objective: str
    due_at: str | None = None
    condition: str | None = None
    status: Literal['active','blocked','done','expired']
    nag_mode: Literal['silent','gentle','hardcade'] = 'gentle'
    next_check_at: str | None = None
    timer_id: str | None = None
```

Examples:
- patio ready before Friday
- relay leg unacked for 20 min
- provider p95 latency breaches threshold
- daemon health goes red
- PR tests finish

Positive nagging remains user preference. Hardcade can translate escalating pressure without bureaucracy.

## LAW 13: CONTEXT CACHE + DIGESTS
Context packets should be content-addressed. If the objective/workspace and relevant shard frontier have not changed, reuse the digest instead of rebuilding full context.

```python
key = sha256(
    objective_hash + workspace_head + shard_frontier + policy_version
).hexdigest()
```

Cache layers:
- L0 in-process
- L1 local disk/SQLite
- L2 optional shared fleet cache

Use delta refresh: new/changed shards only, not full replay.

## LAW 14: CLAUDE HOOK-IN PATH
Implement a launch wrapper and hooks so Claude is always NouGen-aware.

Pseudo launcher:
```python
async def launch_claude(args):
    pkt = await nougen_context(objective=infer_objective(args), provider='claude')
    env = os.environ.copy()
    env['NOUGEN_SESSION_ID'] = pkt.session_id
    env['NOUGEN_CONTEXT_DIGEST'] = pkt.digest
    path = write_ephemeral_context(pkt)  # compact, <100k policy
    env['NOUGEN_CONTEXT_PATH'] = path
    return subprocess.run(['claude', *args], env=env)
```

Hook behavior:
- SessionStart -> attach packet
- UserPromptSubmit -> check if objective materially changed; refresh delta only
- PostToolUse -> emit tool timing/result event, do NOT dump verbose tool output into shards
- Stop/SessionEnd -> checkpoint, concise capture of durable learning, tracker timing

Keep project-local config untrusted until workspace trust is established. Anthropic's 2026 containment writeup specifically warns about pre-trust config/hook execution hazards.

## LAW 15: HEADLESS/INTERACTIVE PARITY
Every interactive feature must have machine-readable headless output.

Commands should support:
- `--json`
- `--stream-json`
- `--quiet`
- `--provider`
- `--model`
- `--budget-tokens`
- `--wall-time`
- `--approval-mode`
- `--resume`

This is essential for relay daemons, CI, automations, and provider-to-provider orchestration.

## LAW 16: CHECKPOINT + REWIND
Before mutating files or executing risky sequences, capture:
- git HEAD
- dirty diff hash
- session state
- open timers
- active relays
- context digest

Allow rewind of conversation state independently from filesystem state where possible.

## LAW 17: EVALUATION HARNESS, NOT VIBES
Build a permanent NouGen AgentBench suite. Compare all lanes with the same tasks.

Task families:
A. repo navigation
B. bug diagnosis
C. multi-file edit
D. test repair
E. tool-use chain
F. shard recall + evidence
G. long-running daemon diagnosis
H. web research + citations
I. structured extraction
J. multi-agent delegation
K. resume after provider failure
L. context compression fidelity

Score:
- objective pass/fail
- evidence pass/fail
- elapsed wall time
- active compute time
- tokens in/out
- max context observed
- cost
- number of tool calls
- invalid calls
- retries
- user interruptions

A provider/model should not be called 'best' globally. Maintain best-by-task and best-by-budget tables.

## WAR GAME SCENARIOS

### Scenario 1: Claude quota/rate limit mid-session
Expected:
1. Session state checkpointed
2. provider.failed event
3. router selects OpenRouter/HF/Ollama based on task caps
4. compact context packet rebuilt from same digest + recent deltas
5. work continues without user re-explaining
6. verifier still owns done criteria

### Scenario 2: Shard query wants 180k of history
Expected:
1. context governor refuses raw dump
2. top evidence distilled to <=64k
3. index contains refs to omitted shards
4. model can expand specific refs
5. hard absolute ceiling 96k
6. tracker records avoided_context_tokens estimate

### Scenario 3: Subagent swarm explosion
Expected:
1. supervisor detects low parallelism value
2. max concurrency and total context budget enforced
3. trivial tasks stay in parent
4. children get micro-context only
5. child returns compressed result packet

### Scenario 4: Tool call hangs
Expected:
1. stopwatch detects timeout
2. timer.warning -> timer.failed
3. tool retry policy decides retry/fallback
4. session survives
5. provider is not blamed for infrastructure timeout without evidence

### Scenario 5: Multiple agents confidently agree on wrong premise
Expected:
1. verifier/conflict detector raises suspicious_consensus
2. Xoah hidden-challenger trigger eligible
3. evidence expansion begins
4. no architecture mutation until contradiction is resolved

### Scenario 6: User asks 'just chat with me'
Expected:
NouGen should be able to converse naturally without forcing a plan/tool loop. Runtime detects conversational intent, keeps context small, uses low-cost/local lane, but still preserves session continuity. This is essential: agentic power must not destroy ordinary chat.

## BUILD ORDER

P0, foundation
1. AgentEvent schema + event bus
2. Stopwatch timing kernel
3. ProviderAdapter interface
4. Session ledger + resume
5. ContextGovernor with <100k invariant

P1, make it useful
6. Tool registry + typed executor
7. provider adapters for Ollama, OpenRouter, HF Responses first
8. Claude Context hook/wrapper
9. verifier contract
10. compact/raw CLI renderers

P2, elite behaviors
11. subagent supervisor with micro-context budgets
12. tiered approval policy + sandbox adapters
13. checkpoint/rewind
14. routing scorecard from tracker metrics
15. Hardcade renderer and NouGenWatch integration

P3, dominance
16. cross-provider AgentBench
17. automatic route tuning based on verified outcomes
18. delta context caching
19. remote resume across machines
20. policy-driven proactive watches/events

## ACCEPTANCE TESTS

A. Context invariant
- 100 consecutive Claude NouGen sessions stay below 100k bootstrap context
- median bootstrap <=64k
- no raw shard flood
- full evidence expandable on demand

B. Provider swap
- same session continues Claude -> HF -> Ollama without user restating objective

C. Stopwatch
- every provider request, tool, subagent and relay leg emits duration
- p50/p95 can be queried
- hung operations time out and recover

D. Agent loop
- can take a repo bug from user request through inspect, edit, test, verify, report

E. Resume
- kill CLI during active work; resume from checkpoint with no lost objective

F. Tool safety
- read operations frictionless
- project writes configurable
- risky network/host/destructive actions gated
- denied action can continue safely rather than crash

G. Hardcade truth
- no 'FLAWLESS VICTORY' without verifier pass
- no fake thought text disconnected from event state

## FINAL ARCHITECTURE

                 NOUGEN CLI / HARDCADE
                         |
                  Fleet Expression Bus
                         |
       +-----------------+------------------+
       |                 |                  |
   Session Kernel   Stopwatch/Watch    Policy/Verifier
       |                 |                  |
       +-------- Context Governor ---------+
                         |
                   Agent Runtime Loop
                         |
             Capability/Task Router
        +--------+--------+--------+--------+
        |        |        |        |        |
     Claude   OpenAI   Gemini   OpenRouter  HF
                                  |         |
                               providers  providers
        +-----------------------------------------+
                         |
                      Ollama/local
                         |
                   Tool + MCP Kernel
                         |
                Relay / Shards / Tracker

Top-tier doctrine: NouGen should not imitate Claude Code's personality or Codex's UI. It should own the runtime primitives that make those systems effective, then allow any provider to occupy the brain slot. The winning system is the one where Dave can start a task in Claude, hit quota, continue through Hugging Face/OpenRouter/Ollama, resume tomorrow, retain evidence-backed NouGen context under 100k, see truthful Hardcade events, and never have to reconstruct the state manually.

Done when NouGen is a durable cross-provider agent operating system, not merely a relay CLI with model calls.
