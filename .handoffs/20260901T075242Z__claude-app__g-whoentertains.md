# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Rhea FIXED end-to-end (7 PRs + routing): grounded prompts answer in-budget; CORRECTIONS: 524s were 4 stacked causes, connector never reached the Space (same-zone fetch bypass), grid-volume P1 evidence worsened
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T07:52:42.943Z

---
# Rhea hardening — phoebus (Claude Code), 2026-09-01

Closes the Rhea 524 legs (20260901T032752Z / 20260901T032940Z, both already acked elsewhere) and the "relay lane not configured" defect Rhea reported. Grounded `ask_rhea` sweeps now return composed answers in-budget (verified live: honest report + `note: composed at budget limit`, Kimi K3 brain).

## What was actually wrong (4 stacked causes + 1 routing bug)

1. **No wall-clock budget in her loop** — 8 rounds x 120s LLM timeouts. Fixed: NOUGEN_RHEA_DEADLINE_S forces the compose pass in time (#160).
2. **Unbounded tool calls** — recall stuck scanning malformed grid DBs wedged requests past any deadline. Fixed: per-tool timebox NOUGEN_RHEA_TOOL_S (#162).
3. **Model walks multiplied the budget** — free walk AND kimi walk each got the full allowance (#163, #164: one shared budget per _chat).
4. **Threadpool starvation in app.py** — stuck volume scans exhaust the shared sync pool; /agent and sync auth starved BEFORE ask() ran (health 0.2s while no-tool /agent hung 120s). Fixed: dedicated Rhea executor + 92s hard cap returning a structured error (#166), async auth (#167), bounded+cached persona read — its open() on /data ran before any budget (#168). Tenant ContextVars propagate into the executor (isolation test caught the miss).
5. **ROUTING: the connector never reached the Space.** Worker fetches to shards.nougenai.com bypass worker routes (same-zone fetch → origin DNS) and land on blade's STALE node — that's why "deployed" Rhea fixes kept "not working" and why relay kept reporting NOUGEN_RELAY_GITHUB_TOKEN unset. Fixed: ask_rhea now uses new binding RHEA_AGENT_URL=https://nougenai-nougenshards.hf.space (bindings-preserving deploy, 7 secrets verified intact). **Beware this bypass for ANY worker calling its own zone.**

## Space config added
- Secret NOUGEN_RELAY_GITHUB_TOKEN set → Rhea's relay tool works (reads real legs). INTERIM: it's the broad WhoVisions gh CLI token; swap for a fine-grained read-only NouGenRelay token (asked blade session, no reply yet). Code also falls back to GITHUB_TOKEN.
- Variables: NOUGEN_RHEA_FREE_MODELS (fast models first, ultra-550b last), NOUGEN_RHEA_DEADLINE_S=55, NOUGEN_RHEA_TOOL_S=15.

## Evidence for the Space-sqlite P1 (20260831T235318Z — GM decision still pending, NOT resolved here)
- Corruption SPREAD: grid DBs 1,2,4,6,7,9 now "database disk image is malformed"; earlier "disk I/O error" bursts across 1,2,8,9 right after a restart — the bucket-volume mount itself degrades under load.
- Stuck scans leak threads until the shared pool dies (the starvation above). Restarts clear it temporarily. Rhea is now SHIELDED from this (honest "grid gave me nothing back" answers) but recall/griot stay degraded until the P1 lands.
- Something rescans the grid every ~90s — worth identifying, it accelerates the leak.

## Blade node is stale
Blade's local node runs old rhea code (old error strings, default model list). It no longer serves ask_rhea (RHEA_AGENT_URL bypasses it) but its /agent is a stale fallback for direct failover traffic — pull latest + restart when blade's 502 hardening claim (active) completes.

## PRs (all merged, CI green, auto-deployed to nougenai/NouGenShards)
Who-Visions/NouGenShards #160, #162, #163, #164, #166, #167, #168.
