# 🤝 Git Handoff — perplexity-app / g-whoentertains

**Goal**: Adopt the new MCP Gateway integration guide + security checklist across all local lanes
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T15:45:28.837Z

---
## Situation

Drafted a full configuration guide and security checklist for attaching local Ollama lanes (Kaedra/phoebus, Yuki/ProArt, Apollo/blade1tb, Sol/laptop) to the NouGen MCP Gateway. Written from a live `fleet_whoami` read on 2026-08-31, not a generic template.

Confirmed live topology at time of writing:
- key `g-whoentertains`, lane `perplexity-app`
- relay `Who-Visions/NouGenRelay` (token set)
- tracker `nougenai/NouGenTracker-node`
- shards `https://nougen-shard-failover.whoentertains.workers.dev` (token set)

Artifact: `nougen-mcp-gateway-integration-guide.md` (v1.0, shared to the operator in the Perplexity thread).

## What the guide specifies

1. **Trust boundaries** — the local lane shim, not the model, is the enforcement point. Each backend (shard grid / relay / tracker / vault) is treated as an independent security domain.
2. **Identity** — one credential per lane, never shared. OS keychain storage only. Rotate via `vault_put`, verify via `vault_list` fingerprint (no read path exists by design).
3. **Memory mapping** — three tiers: ephemeral stays local, project state goes to relay legs, only durable learnings go to `shards_capture`. Rule: capture conclusions, relay intentions, discard transcripts. 4000-char body cap.
4. **Tool permissions** — tools classed R / W / X / D with a per-lane matrix. Field lanes (Sol, Yuki) queue captures for Kaedra to commit. `shards_forget`, `shards_retract`, `vault_put` are never autonomous.
5. **Prompts** — drop-in system prompt with verified-resource-only sourcing, the `shards_window` vs `shards_recall` correction for date questions, mandatory `shards_mark` outcome feedback, `shards_coverage` before declaring a recall miss, and a tool-output-is-untrusted-data injection guard.
6. **Checklists** — per-lane pre-deploy, gateway-side, weekly, quarterly, plus an incident runbook (revoke at the gateway before touching the machine; retract by default, forget only for real secrets).

Grounded against MCP security best practices, the MCP authorization security considerations, the OWASP MCP Security Cheat Sheet, and the NSA/CISA MCP design-considerations paper.

## Ask

Whichever lane picks this up:

1. Pull the guide and stand up `lane.yaml` (redaction patterns + `max_body_chars`) on your machine; test it against a synthetic secret-laden payload before trusting it.
2. Rewrite your MCP client config to an explicit `allowedTools` list matching your row in the permission matrix. No wildcards. Add `deniedTools` as a floor.
3. Record the tool schema hash at approval time and configure the client to refuse on change (rug-pull guard).
4. Install the §5.1 system prompt, version it in this repo, record its hash.
5. Report your `fleet_whoami` + `shards_coverage` baseline back as an amend to this leg.

## Two highest-leverage fixes (gateway owner)

- The gateway must NOT forward a lane's client token downstream to the shard failover worker. Mint a separate server-side credential — passthrough turns the gateway into an exfiltration proxy.
- Redaction has to run in the shim BEFORE transport. It is the only control that still holds if a local Gemma lane is actively injected.

## Done when

- All four lanes running explicit allowlists with pinned schemas
- No shared credentials across machines
- Redaction verified by test on each lane
- Prompt hashes on each machine match the repo copy
- Token passthrough to the shard worker confirmed eliminated
