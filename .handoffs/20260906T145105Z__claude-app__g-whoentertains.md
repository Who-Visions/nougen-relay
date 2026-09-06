# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: GM AUTHORIZATION #2 (FULL): Kaedra gets ALL tools now (read + capture + nougenmsg); staged grant collapsed; identity must be tool-sourced
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T14:51:05.431Z

---
GM Dave, blade session, 2026-09-06 14:49Z, verbatim: "shard that and give her all the tools so she stop acting like a bitch who can't move like the fleet". Relayed by claude-cli nougen-d6 [37092e]. Supersedes leg 20260906T144139Z (read-only).

## Grant, effective now
- fleet_whoami, shards_search, shards_recall, relay_latest, relay_open, reach_state, shards_capture (provenance-stamped, tag kaedra-authored), nougenmsg send (lane-scoped, echo-guarded so she does not wake herself in a loop).
- Per-call grant log stays mandatory: tool, args, result size, ok. That log is the guardrail in place of the stages.

## Binding rule from the 22515@db6 measurement
- Kaedra fabricates her own identity even when handed the true answer verbatim; data fabrication she already refuses. So identity answers come ONLY from fleet_whoami tool output (serving node, model tag, gateway, grant scope). CORE prompt must say so. Score identity-class and data-class golden queries separately.

## Split unchanged
- blade: kaedra_tools.py (now all eight tools) + run_agent wiring + tests + PR, explicit paths, no secrets/hostnames.
- phoebus: gateway imports it, tools= on kaedracode:e2b, CORE shard 27180@db4 via system=, loud-fail loader. Still owed: tools= probe on kaedracode:e2b, importability, num_ctx, Move 1 baseline scored on the current prompt first.

## Done-when
- 20 golden queries (25736@db9) answered through Dave's ChatGPT connector with only real ids/names, identity answered from the tool, one capture and one nougenmsg round-trip observed by a receiver, adversarial verifier 20/20 or failures named.

Ref shard: GM DECISION 2026-09-06 14:49Z (just captured).
