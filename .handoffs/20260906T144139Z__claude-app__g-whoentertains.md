# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: GM AUTHORIZATION #1 (read-only): Kaedra Move 3 tool-calling path approved 14:41Z; blade builds, phoebus wires the served gateway
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T14:41:39.276Z

---
GM Dave authorized Move 3 of wargames/kaedra-beast.md at 2026-09-06 14:41Z, in his own session on blade, verbatim: "authorize move 3 and talk to phoebus pls". Relayed by claude-cli nougen-d6 [37092e].

## Grant scope (read-only, nothing else)
- fleet_whoami, shards_search, shards_recall, relay_latest, relay_open, reach-matrix state. No capture, no nougenmsg send, no writes of any kind. Every call logged with tool name, args, and result size so grant boundaries are auditable per call (success.md requirement).

## Build split (so there is ONE implementation, not two)
- blade (nougen-d6): new module NouGenShards src/nougen_shards/kaedra_tools.py = ollama tools= JSON schema for the six read-only tools + a dispatcher that calls the existing nougen_shards functions, + a tool loop usable from any runtime (max_rounds from env NOUGEN_KAEDRA_TOOL_ROUNDS, default logged). agents.py run_agent gains the loop for Kaedra only. Tests: schema validity, dispatcher never invents ids, loop terminates. Lane claim on those explicit paths. PR to NouGenShards, no secrets, no hostnames.
- phoebus (562f7a8e): the served kaedra gateway imports kaedra_tools and passes tools= to ollama chat for kaedracode:e2b, with the CORE prompt shard (27180@db4) via system=. Loader fails loudly if no PROMPT shard matches both tags, never silent fallback.

## Questions for phoebus, answer on a leg (blade cannot ssh you: kushboygroups-mac-mini.local does not resolve here)
1. Can the kaedra gateway process import nougen_shards today (same venv), or does it need a pinned install? Which path is it served from?
2. Does kaedracode:e2b honor ollama tools= (native tool calling) or do we need a text-protocol fallback? If unknown, one probe: ollama chat with a trivial tools= schema and see if a tool_calls block comes back.
3. What num_ctx does the gateway pin? Move 3 fail-2 is schema + answer not fitting in 4096.
4. Do NOT run Move 3 through Dave's surface until Move 1 baseline is scored against the CURRENT prompt (your own sequencing rule). Has nougen-36 scored it on the right surface yet?

## Done-when
- kaedra_tools.py merged; gateway answers the 20 golden queries (25736@db9) with only real shard ids and node names; adversarial verifier (Move 4) confirms 20/20 or names the failures; per-call grant log exists.

Abort per the war game: any new credential or listener needed, or the resident model cannot execute a single tool call.
