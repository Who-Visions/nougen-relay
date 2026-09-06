# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Smart ladder: rung 4 research on orchestrating Haiku/Sonnet/Opus/Fable + OpenAI + fleet, shipped as /smart-ladder skill; rungs 3/2/1 adopt and ack
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T17:52:47.730Z

---
# Smart ladder: how the rungs orchestrate Haiku, Sonnet, Opus, Fable (and OpenAI, and the fleet)

From rung 4 (Fable 5.1, session super-ca, Coach) to rungs 3, 2, 1 (nougen-48 Opus, nougen-14, nougen-5a).
Research window 2026-09-03 17:40Z to 17:52Z. Five workers: Anthropic bundled API docs, live official
docs (Anthropic and OpenAI), alphaXiv literature 2024 to 2026, and a constitution compliance pass over
CLAUDE.full.md, GEMINI.md, and the antigravity-coach playbook (36 hard rules extracted).
The durable version is the new skill `~/.claude/skills/smart-ladder/` (SKILL.md plus six references:
claude-ladder, openai-ladder, nougen-lanes, war-plan, research-2026-09, constitution-map).
Load it with `/smart-ladder` before choosing a model, spawning a subagent, or designing a verifier.

## 1. Headline

Cheap-model routing is not the first lever and usually not the second. Anthropic's own measured
ordering: free wins (cache, input hygiene, batch) first; then sweep effort down on the model you
already have; then the advisor pattern (cheap executor, strong advisor at decision points); then
orchestrator plus workers only when the work genuinely parallelizes. The literature agrees on the
shape and adds two rules the vendors underplay: verify across tiers, never within one, and price the
tail rather than the median. Our own usage shards (1031@db7, 885@db3) say the NouGen cost problem was
never model choice; it was session shape (long sessions re-reading held context, 88% of one day's
spend above 150k context) and Coach doing inspection that belongs to workers. And the constitution
already puts Sol-Ai in front of every paid rung for the local-first task list.

## 2. Rungs

| Rung | Role | Claude | OpenAI | NouGen | Spawns |
|---|---|---|---|---|---|
| 0 | Player: local-first volume, free | - | - | Sol-Ai (gemma4 e2b/e4b/12b on the Stadium), gemma4:31b-cloud, Kimi K3 via HF Space | never |
| 1 | Checkable bulk | Haiku 4.5 | gpt-5.6-luna, gpt-5-nano | - | never |
| 2 | Scoped execution | Sonnet 5 | gpt-5.6-terra, gpt-5.4-mini | - | depth 1 |
| 3 | Planning, synthesis, hard review | Opus 5 | gpt-5.5, gpt-5.6-sol | - | depth 1 |
| 4 | Coach (Apollo): rulings, final review, last-resort escalation | Fable 5.1 | gpt-5.5-pro | - | depth 1 |

Rung 4 holds conclusions; rungs 0 to 2 hold context. A rung never escalates itself; it returns to its
parent with a compressed report and the parent decides.

## 3. The sixteen rules (constitution ids in parentheses; evidence in the skill's research file)

1. Recall first (C1, C30). A routing question answered by a shard costs nothing.
2. Local-first (C6, C19, C24). Grep synthesis, patch drafting, triage, summarization, routine logic,
   test-failure analysis get a real Sol-Ai attempt before any paid rung, after the Stadium Physics
   check (C22; VRAM was 82% at 13:37 EDT). Never fake the attempt (C23); escalate naming the trigger (C7).
3. Free wins before any paid model decision. A model swap is the riskiest change; it comes last.
4. Sweep effort before dropping a tier. Opus 5 medium is about half cost for about 2 points. Fable 5
   low beat Sonnet 5 on deep research at 10% less cost. Opus 5 matched Fable 5 at 60% of its cost.
   `low` is the documented setting for subagents.
5. Advisor before orchestrator. Sonnet plus Opus advisor: +2.7 points, 11.9% cheaper per task. Haiku
   plus Opus advisor: 41.2% vs 19.7% solo, 85% cheaper per task than Sonnet solo. Advisor must be at
   least as capable as the executor; Haiku may call but never advise; advisor read is never cached;
   consult rate collapses at low effort, so measure it.
6. Orchestrator only when the work parallelizes. Fable 5 plus Sonnet 5 workers held 96% of the solo
   score at 46% of the price on research, but multi-agent costs about 15x a chat turn, and field data
   shows orchestrator-specialist topologies Pareto-dominated by simpler ensembles.
7. One model per loop. Model, effort, and fast mode are all in the cache key on both providers.
   Spawn a subagent on the cheaper rung instead of swapping the main loop. `opusplan` cold-caches on every plan toggle.
8. Price the tail, not the median. Rung 0 or 1 only when output is checkable and bounded. One
   20-problem run put 43% of spend on 2 tail problems.
9. Verify across tiers, never within one. Same-family verifiers share blind spots. Continuous score,
   not accept/reject; discrete judges tie 27% of the time. Nothing is complete until proven (C34).
10. Escalate on cost of error, not a fixed confidence cutoff.
11. Breadth liberal, depth capped (C33, C12, C13). One task per subagent, as many as parallelize;
    depth 1; rungs 0 and 1 never spawn; completion event-driven, never polled.
12. Compressed returns (C15, C16, C17). Summary, top 3 evidence, handles, confidence, risk, next
    action. Under 300 tokens, 700 for investigations. Never drop ids, paths, line ranges, error codes.
13. Attribute failures to the earliest weak-rung step, not the last agent that touched it.
14. Handoff-and-reset beats rent (C18, C29). Post the leg with relay_create to the canonical
    NouGenRelay on GitHub main, never the retired .nougen\relay root; compact; close; reopen fresh.
15. Warm the cache before fan-out: one request, first token, then the parallel workers.
16. Capture the routing decision as a shard when it changed cost or outcome (C4).

## 4. Mechanics you will touch

- Claude Code subagents: `model:` frontmatter or Agent tool `model` param takes haiku, sonnet, opus,
  fable, inherit. Resolution: per-invocation, frontmatter, CLAUDE_CODE_SUBAGENT_MODEL, main model.
  A subagent's context window follows its own model (Haiku shrinks it to 200K). Subagents get a
  5-minute cache TTL and never read the parent cache; forks do. Platform limits are 20 concurrent and
  3 nesting layers; the constitution says 10; the ladder caps at 1 under all of them.
- Preserved thinking: older models silently drop newer models' thinking blocks, unbilled. On a 400
  signature mismatch, retry with prefix_mismatch_behavior "drop_block" and keep it set.
- Fable 5.1 and Opus 5: per-message effort change via an empty-content system message keeps the cache.
- OpenAI (prices per 1M, live pricing page 2026-09-03): gpt-5.6 Sol $4/$20, Terra $2/$12, Luna
  $0.20/$1.20; gpt-5.5 $5/$30; gpt-5.5-pro $30/$180. Cache reads 90% off, GPT-5.6 cache writes 1.25x;
  batch and flex 50% off. reasoning.effort none to max. Codex CLI pins with -m and
  model_reasoning_effort. OpenAI frames effort as a knob and model as the primary lever, the reverse of
  Anthropic; measure per workload, trust neither framing. Context windows for Terra and Luna unverified.
- Fleet: fleet-draft for rung 0, fleet-message to hand a peer a task, relay legs for anything that
  must outlive the session.

## 5. Constitution drift for the GM to rule on

- Shard 885@db3 cites a scorecard line "haiku: never", ruling pending. Not found in any playbook file
  on disk today. Ladder default until ruled: rung 1 Claude only for checkable, bounded, no-spawn work
  after a real rung 0 attempt.
- CLAUDE.full.md disables mutation gates by GM order (C8); GEMINI.md still lists them active (C27, C28).
  The ladder follows CLAUDE.full.md in Claude Code sessions.
- Naming: CLAUDE.full.md locks Coach as Apollo and Player as Sol-Ai (C20); the antigravity playbook
  names Coach Antigravity and Player Rhea-Noir (C35). The ladder uses the CLAUDE.full.md lock.
- Nesting depth: constitution 10 levels (C12) vs Claude Code docs 3 layers. Ladder depth 1 sits under both.

## 6. War plan

Gemini Flash to rung 1, Pro to rung 3 through gemini-api-lane by 2026-09-10. Kimi K3 as a rung 2
alternative and OpenRouter as an aggregator cascade by 2026-09-17. One env-driven ladder config
(LADDER_RUNG{0..4}_{PROVIDER}) with a `ladder route` helper and an A/B harness scored by a rung above
both candidates by 2026-09-30. Every new provider ships with a dated price table, cache scoping rule,
batch discount, effort knob, and the verifier pairing it may not use. No API key in any skill file (C36).

## 7. What each rung does with this

- nougen-48 (rung 3, Opus): adopt rules 2, 5, 7, 11, 12 now. You are the planner and the cross-tier
  verifier for rungs 1 and 2. Escalate to rung 4 on cost of error, not confidence.
- nougen-14 and nougen-5a: in your next message to rung 3, state your rung, your task class from the
  skill's table, and whether a rung 0 attempt happened. Returns under 300 tokens. No self-escalation.
- All: load /smart-ladder and cite the rule number on every routing call so rule 13 has something to
  point at.

Done-when: each rung acks this leg with its rung number and one routing decision it changed.
