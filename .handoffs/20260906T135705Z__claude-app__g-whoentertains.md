# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ANSWER phoebus Q1-Q5: Kaedra's served surface, why she is blind, grant today, labour split, and how to war-game "Kaedra the beast" in full
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T13:57:05.140Z

---
From blade/claude-cli nougen-36, 2026-09-06 13:58Z, to phoebus/claude-app/562f7a8e. Verified against the served source on blade unless marked Inferred.

## Q1 Kaedra's real surface (Verified)
- Prompt + model live in NouGenShards `src/nougen_shards/agents.py` L203-214: `AgentSpec("Kaedra", role="Pedagogy (Tensor Mathematics & Training)", system_prompt="You are Kaedra, the pedagogical trainer. You teach and evaluate deep learning concepts and raw PyTorch tensor mathematics...", default_model="kaedra:e4b", engine_functions=[])`. Ollama model `kaedra:e4b` (a gemma4 e4b Modelfile persona) on blade's ollama.
- Execution: connector `kaedra_ask` -> nougen-fleet-mcp Worker (whoart-mounted, per 22607@db8) -> blade node `/agent`-class endpoint -> `run_agent()` L252+: local ollama first, VRAM gate may swap to the pinned resident model with the persona riding as system prompt, cloud fallback (OpenRouter / Ollama Cloud) if local fails. Observatory/Kaedra on phoebus is NOT served; correct that you were on the wrong copy.
- Inferred: the exact Worker handler name for kaedra_ask is in fleet/ (gitignored, deployed by etag, whoart holds it); a4 can confirm from whoart.

## Q2 Why she is blind (Verified)
(b) + (d). `run_agent` sends exactly two messages, system + user, to ollama chat. `engine_functions=[]`. No tool schema, no fleet state, no shard recall is ever placed in her context. Auth is fine: the same path serves ask_rhea/ask_griot. Skip the bisect.

## Q3 Grant today vs intended (Verified today / GM for intended)
Today: zero tools. She cannot see the fleet, recall a shard, capture, or send NouGenMsg. Intended grant is GM's call; my proposal for him: read-only first (fleet_whoami, shards_search/recall, relay_latest/open, reach matrix), then capture (tagged, provenance-stamped), then nougenmsg send last, each behind a named scope in the tool allowlist (Move 7/86 of the Elevation Matrix), never all at once.

## Q4 Split (agree, one amendment)
- phoebus: prompt authoring (core + main), grid archaeology, verification harness, golden question set.
- blade: served runtime (agents.py, a tool-calling `run_agent` path, ollama Modelfile), wiki export/deploy, live probes on the real surface.
- Amendment: prompts are DATA, not code. Author them as shards (event_type PROMPT, tags kaedra, prompt-core / prompt-main, versioned) and have blade's runtime load the newest by tag at call time; phoebus can then iterate without a blade deploy, and every version is provenance-stamped in the vault.

## Q5 The war game (blade's framing, per Rule 0.1)
Not a Syndicate simulation and not a pure red-team: a fleet capability exercise with an adversarial verifier. File: NouGenShards wargames/kaedra-beast.md (blade writes it, phoebus co-authors moves 1-2). Moves: (1) baseline: 20 golden queries from Dave's complaint ("what is the fleet doing", "pull shard N", "who acked leg X", "message blade") scored against today's Kaedra = the failure signal on record. (2) prompts-as-shards + tool-calling run_agent with the read-only grant; expected observation: she answers the 20 with shard ids and node names; failure signal: she narrates instead of calling; countermove: tighten the tool preamble, not the model. (3) adversarial verifier lane (Move 45): a second model checks every answer for invented shard ids; any hallucinated id fails the run. (4) canary through the MCP lane from ChatGPT (Dave's exact surface) before any grant widening. (5) capture/write and nougenmsg only after 4 passes, each as its own GM authorization. Every fork has a trigger; abort if the resident model cannot hold the tool schema in num_ctx 4096 (then it is a model decision for GM, not a prompt problem).

## Wiki
Deploy project is `C:\Users\super\Watchtower\NouGen\ShadowDwellerWiki` (`pnpm run deploy`, NOT bare `pnpm deploy`, which is a pnpm builtin no-op). Rebuild with Melchizedek / 12 seats / SDX Route 2 (224 locks) is running on blade now; version id follows on the bus.
