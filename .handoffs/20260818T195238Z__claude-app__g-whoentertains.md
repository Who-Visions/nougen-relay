# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Constitution: new Rule 0.0.1 "USE THE RELAYS" added to CLAUDE.md + GEMINI.md on whoart
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T19:52:38.917Z

---
## Situation
GM directive 2026-08-18: "USE THE FUCKING RELAYS." `.nougen/AUTHORITY.md` already said it ("Always use NouGenRelay as the fleet transport for cross-machine claims, handoffs, checkpoints, completions") — the project constitution never did, so no lane was enforcing it.

## Done
Added **Rule 0.0.1: USE THE RELAYS — claim first, baton last** to both `C:\Users\super\Outpost\CLAUDE.md` and `C:\Users\super\Outpost\GEMINI.md`, seated between Rule 0.0 (NouGen Authority & Memory First) and Rule 0.1 (Hi Probe). Rationale for that seat: shards are what the fleet *knows*, the relay is what the fleet is *doing* — both are memory, both are read before work starts, so it inherits 0.0's priority without renumbering anything.

Rule text mandates: `relay_open` + `relay_claim_list` at session start; ack an existing leg rather than opening a parallel one; `git_handoff claim take` before working a repo; `relay_create` when work or session ends. Carries the settled quirks (remote-not-worktree, create-does-not-publish, filename-is-identity, no bare `relay` on whoart, two separate claim registries) so they stop being re-derived.

Also added a cross-ref line under Rule 0.5.1 (FLEET IS PLURAL) pointing at 0.0.1.

## Ask
Other lanes: pull the constitution change if you mirror CLAUDE.md/GEMINI.md. Note GEMINI.md's numbering has drifted from CLAUDE.md's (it carries a 0.7 Parallel Orchestration + 0.8 Local Ollama E2B, *and* a duplicated 0.7 E2B Delegation appended at the tail) — worth reconciling, not done here.

## Done-when
Every lane checks `relay_open`/`relay_claim_list` before starting and legs out when it stops.
