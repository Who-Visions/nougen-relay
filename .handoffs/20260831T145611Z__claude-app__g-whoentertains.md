# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Session closing clean after 22h: 8 PRs merged, relay read path + connector capture + thread leak fixed and deployed, time hook on all 3 nodes. #152 needs a GM admin merge.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T14:56:11.487Z

---
Closing out. Nothing running, nothing dirty, safe for a fresh session.

**State I'm leaving:** node 4444 `/health` 200 · `shards.nougenai.com/mcp` 405 (healthy) · `wt-claude` worktree 0 dirty paths · no background tasks or subagents alive.

## Merged (8)

#141 worker-var setter · #142 public-surface lane leases · #143 recall perf · #146 bench reporter · #147 runtime path/endpoint resolution · #149 capture visibility · #150 fleet account fan-out · #151 federation lane pool.

## Deployed outside the repo

- `nougen-fleet-mcp` **b8d9d783** (relay reads via trees API) then **9db8cede** (capture tri-state)
- `nougen-shard-failover` `BLADE_TIMEOUT_MS` 3000 as plain_text
- fleet ledger vaulted: 49 keys, 15 accounts, canonical names + 5 `MODEL_*` entries
- `~/.nougen/fleet_aliases.env` — 14 alias pairs **derived from identical secret values**, never guessed
- `nougen_time.py` installed and registered on **blade, whoart and phoebus**

## Needs the GM

1. **Merge #152.** All four required checks `completed/success` on head `81ab071`; no rulesets, no CODEOWNERS, no reviews required, not behind main — still `BLOCKED`. Needs `--admin` or a repo setting a lane cannot see.
2. **Which node launcher survives** — Startup-folder copy vs the "NouGen NGS Node" scheduled task. #152 makes them safe to coexist; one should still go.
3. **Which keymaker store is canonical** — `agent_secrets.db` (205 rows) vs `shards_secrets.db` (89). Identical schema, different contents. **Delete neither.**
4. Unverified by me: the whoart lane reports a **10,062 Notion credential purge**.

## For whoever picks up next

The single most reusable thing from this session: **one failure class showed up five times**, each returning something that looked like an answer instead of an error — a list API truncating to its 1000 newest-first entries, a probe URL 404ing uniformly, a misspelled prefix reporting one credential, `captured === false` treating `undefined` as success, and relative timestamps computed once at SessionStart and carried for 22 hours.

At any boundary you do not control: explicit tri-state over a single negative test, cross-check any discovery layer that can be silently under-inclusive, and never inject a pre-computed delta into context that will be re-read.

Four of my own claims are retracted in the close shard, including a memory misdiagnosis that cost two wedge occurrences and ~460K subagent tokens spent on paid lanes while holding a free fleet.

## Cross-lane credit

`nougen-bd` reporting captures still dropping after #149 is what turned me from the node to the connector. `nougen-8f` found the launcher two-binds bug and verified my capture fix independently. `nougen-07` owned the recall code and confirmed the thread leak. **None of that propagation was possible before the relay read-path fix** — the fleet had been posting into a registry its own readers could not see.
