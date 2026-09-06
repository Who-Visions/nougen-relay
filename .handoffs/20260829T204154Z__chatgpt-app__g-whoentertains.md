# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Adopt “parallelogram your work” as NouGen orchestration vocabulary
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T20:41:54.940Z

---
## New fleet vocabulary: PARALLELOGRAM

Dave spontaneously coined **“parallelogram your work”** while directing AI repair work. This should be treated as a compressed orchestration command, not merely a joke.

### Operational meaning
When Dave says **parallelogram your work**, interpret it as:

1. Decompose the objective into independent or minimally coupled work lanes.
2. Assign appropriate agents, subagents, machines, or tools to those lanes.
3. Execute concurrently rather than serially where dependencies permit.
4. Preserve shared state and provenance across lanes.
5. Converge outputs into one validated result.

### Why this matters
This is a concrete example of **contextual command compression**. As NouGen’s persistent shared state grows, Dave can issue increasingly compact steering vectors because the substrate already carries vocabulary, objectives, architecture, prior corrections, and behavioral context. Existing examples include `check shards`, `relay that`, `swarm the fleet`, `deep grep`, and `top 1%`.

`parallelogram your work` extends that grammar into explicit concurrent orchestration.

### Linguistic origin
The phrase came from Dave’s rapper/battle-rap instinct: `parallel` already names the technical behavior; `parallelogram` exposes the geometry inside the word and converts the noun into a verb. It functions simultaneously as humor, challenge, and executable instruction.

### Candidate CLI/fleet language
**Don’t serialize what you can parallelogram.**

### Durable memory
Captured as shard: **Parallelogram Your Work: Contextual Command Compression**.

### Fleet ask
Teach agent routers, CLI help/onboarding, orchestration docs, and command interpretation layers this vocabulary where appropriate. Do not hard-code a brittle keyword-only behavior. Resolve the command semantically from context and only parallelize genuinely independent work.

### Done when
The fleet recognizes `parallelogram your work` as a semantic instruction for safe concurrent decomposition and convergence, with dependency awareness and provenance intact.
