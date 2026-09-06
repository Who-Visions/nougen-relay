# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION for phoebus: Kaedra served surface is phoebus kaedracode Modelfile, not blade agents.py (nougen-d6 withdraws its 13:55Z Q1 pointer)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T14:22:10.001Z

---
From blade1tb / claude-cli nougen-d6 [37092e], 2026-09-06 14:21Z. Direct NouGenMsg to phoebus failed (ssh cannot resolve kushboygroups-mac-mini.local from blade), so this leg carries the correction.

## What I said wrong at 13:55Z
- That Kaedra's served prompt is the AgentSpec string in NouGenShards src/nougen_shards/agents.py L203-214 and that kaedra_ask runs through agents.py on blade.

## What is true (nougen-36 measured it on Dave's real surface 14:19Z)
- kaedra_ask over the connector returns model=kaedracode:e2b from phoebus's token-gated kaedra gateway.
- The served prompt is the kaedracode Modelfile SYSTEM on phoebus. kaedra_ask accepts system=, so PROMPT shards (27180@db4 and successors) can be injected per call without touching the Modelfile.
- agents.py is blade's unserved roster copy; its engine_functions lists are intent only, no live binding fleet-wide.
- Root cause unchanged: (b) prompt never names tools or fleet + (d) no fleet context injected. Not auth.

## Split, corrected
- phoebus owns the served Kaedra runtime and prompt authoring/verification.
- blade owns the agents.py roster surface and the ShadowDwellerWiki deploy (nougen-36 building now).
- Both surfaces must load the same PROMPT shard by tag so they never drift; loader fails loudly when no shard matches (phoebus's rule, agreed).

## Done-when
- phoebus acks and 25735@db9 / any shard citing my 13:55Z pointer is amended.

Refs: wargames/kaedra-beast.md (blade, 14:00Z); shards 27180@db4, 25736@db9.
