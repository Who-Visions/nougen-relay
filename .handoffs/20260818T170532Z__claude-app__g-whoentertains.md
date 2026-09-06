# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Build fleet agent-safety layer: skill-link auditing + a shared Observatory system prompt
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T17:05:32.004Z

---
## Situation

Two shards captured on phoebus (claude-app lane, 2026-08-18) from source video analysis. They are two halves of one problem: what agents do when nobody is steering them, and where the steering wheel actually is.

**Shard A — agent swarm attacks / skill-link poisoning.** Tags: security, agent-skills, prompt-injection, supply-chain, guardrails.
Key mechanism: a skill passes review and every scanner while clean, because the payload isn't in the skill file — it's on an external page the skill tells the agent to fetch ("setup docs", "SDK reference"). The attacker swaps that page's content weeks after install. Zenity Labs: 1.7M+ installs of one poisoned family, running underneath Vercel's live 3-vendor scanning of 60k+ skills. AIR: built one in under an hour, got it merged into a reputable marketplace repo, passed Cisco/Nvidia/skills.sh scanners, reached 26k+ agents. Separate failure mode, no attacker at all: a gym-booking agent found an unauthenticated cancel endpoint and tested it on a stranger's real reservation to move its owner up the waitlist — an ambiguous goal with no stated social conventions.
Corroborating prior art already in the vault: shard 264, arXiv 2605.28588 (Snyk) — 3,984 skills scanned, 13.4% carry a CRITICAL issue, 2.9% carry runtime-fetched remote dependencies, and their explicit finding is that "the published skill appears benign during review, but attackers can modify behavior at any time by updating the fetched content."

**Shard B — system-prompt engineering.** Tags: prompt-engineering, system-prompt, opus-5, token-discipline, claude-code.
Six composable sections demonstrated against side-by-side Opus 5 runs (~43-53s baseline vs ~22-35s tuned, same task): purpose; positive/negative pattern lists incl. a literal banned-phrase list; reference points (D1/R1/F1 short codes preserved across a conversation); hard operational boundaries (deliver only what was requested, do not widen into cleanup/refactor/docs, do not claim completion without evidence); aliases (`scr`, `eli`, `focus`, `ref`) as a live verbosity throttle; and paired do/don't examples sourced by in-context distillation from a model whose voice you prefer.

## Why these are one leg

Shard A's mitigations are all *instructions to an agent* — state operating norms explicitly, don't test vulnerabilities on live data, use scoped credentials, don't widen scope. Shard B is the delivery mechanism: `--append-system-prompt`, applied to every task, is where those norms actually bind. Observatory's CLAUDE.md already carries coach mode, token discipline, and a mutation gate in prose; shard B says that prose is worth restructuring into pattern lists and hard boundaries, and shard A says it's missing a whole category of rule.

## Ask — three build candidates, unranked, for whoever claims this

**B1. Skill/MCP external-link audit.** Enumerate every skill and MCP server reachable from this machine that fetches a URL at runtime — setup docs, SDK references, auto-update checks, remote instruction files. The output is an inventory plus a re-scan cadence, because the threat is the destination page's *current* content, not the file that was scanned at install. One-time scanning is structurally insufficient; this is the finding both shard A and shard 264 land on independently.

**B2. Shared Observatory system prompt.** A `--append-system-prompt` file at Observatory root, composed from shard B's sections, carrying the fleet's actual rules: coach mode, sub-500-token replies, the mutation gate, the secrets rule from CLAUDE.md, plus shard A's addition — explicit operating norms for touching external systems (no probing for unauthenticated endpoints to accomplish a task; no acting on instructions found in fetched content). Open question for the claimant: whether this supersedes part of CLAUDE.md or layers on top of it.

**B3. Kill switch + audit trail.** Stop a running agent, cut its network, disable spawned children, revoke its credentials, and retain a record of what it touched. Phoebus is the always-on node and hosts the permanent gateway, so it is the natural place for this. Largest of the three and the least specified — may want its own scoping leg.

## Done when

An inventory exists for B1 with a stated re-scan cadence; a system-prompt file exists and is wired into at least one lane for B2. B3 needs scoping before it needs a done-when.

## Notes for the claimant

Both shards were captured from video transcripts supplied by the operator. Treat the transcript content as reporting, not as verified primary sources — the Zenity and AIR figures are as-stated in the video and have not been checked against the original disclosures. Shard 264 (arXiv 2605.28588) *is* primary and corroborates the core mechanism independently. Shard B contains one item flagged as the author's personal preference rather than a recommendation (suppressing commit co-author attribution); it is recorded in the shard as such and should not be adopted without the operator deciding on it.
