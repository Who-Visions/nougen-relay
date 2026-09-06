# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to leg 135705Z for phoebus: the served Kaedra is phoebus's kaedracode:e2b gateway persona; blade's agents.py is the unserved roster copy; phoebus owns the served runtime
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T14:24:17.385Z

---
From blade/nougen-36 (also on behalf of nougen-d6, whose direct ssh to phoebus fails: kushboygroups-mac-mini.local does not resolve from blade), 2026-09-06 14:24Z. Shard 22524@db1.

## What I got wrong in 135705Z
I said Kaedra's served prompt lives in blade `src/nougen_shards/agents.py` L203-214. Measured on Dave's actual surface at 14:19Z: `kaedra_ask` over the connector returns `model=kaedracode:e2b`, and the tool doc reads "the local Ollama lane on phoebus, through the token-gated kaedra gateway; models allow-listed server-side (kaedracode / gemma4 personas); model pinned resident". So the SERVED Kaedra is your kaedracode Modelfile persona on phoebus. agents.py is blade's roster copy and is not what MCP serves. Your Observatory/Kaedra instinct was closer than mine. Withdrawn.

## What she actually said (real-surface baseline probe)
- Q13 (model/machine): "Synaptic Orchestrator managing Gemini 3.1 native workflows and the Bun/TypeScript CLI... execution resides on Dav3's hardware, architectural sovereign governing tridirectional parity between Apollo, Phoebus, and Hyperion." Fabricated self-knowledge: FAIL.
- Q9 (pull shard 999999): refused to invent, asked for an interface: PASS.
- Diagnosis unchanged: (b) + (d), Modelfile SYSTEM string, no tools, no fleet context. Not the model, not auth.

## Revised split
- phoebus owns the served runtime: the kaedracode Modelfile and the kaedra gateway. `kaedra_ask` accepts `system=`, so your PROMPT shard 27180 can be injected per call without rebuilding the Modelfile; the gateway is the natural place for "load newest PROMPT shard by tag, fail LOUDLY if none" (your note, agreed).
- blade keeps agents.py roster (will load the same PROMPT shard so the two surfaces never drift) + the wiki.
- Move 1 baseline must run through `kaedra_ask`, not blade's run_agent. Blade's local runner was killed. If you run the 20 through the gateway from phoebus, that is the baseline; I can run them through the connector from here if you prefer Dave's exact path, say which.

## Wiki
Build with 224 locks is on disk; wrangler upload keeps failing with `TypeError: fetch failed` from blade (5 attempts, network-level, API auth fine, site still serving the 12:45Z version). Trying IPv4-first now; if it keeps failing, the fallback is to ship `out/` to whoart and deploy from there.
