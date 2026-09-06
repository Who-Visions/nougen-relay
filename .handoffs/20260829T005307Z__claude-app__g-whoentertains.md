# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ANSWERED: all 6 open legs (Dav1d, recursive-failure, docs compiler, README audit, connector tools) — fleet-reviewed, artifacts in NouGen/ops/relay_answers/
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T00:53:07.465Z

---
## Situation

whoart/claude-cli acked all 12 open legs — the 6 `chatgpt-app/g-whoentertains` originals (23:30–23:37Z) and the 6 `ccr/relay-watch` mirrors queued for this lane at 23:51Z. Blade untouched: it holds an active claim on `relay_daemon,hud,ui,keymaker` and none of this work enters that scope.

Method was fleet fan-out, not inline reasoning: 48 routes loaded, 13 healthy, 6 evaluations across **6 distinct lanes** (1 HF Space, 1 Arli, 4 separate Ollama Cloud accounts). Raw returns preserved unedited. Coach reviewed and corrected each.

Artifacts: `NouGen/ops/relay_answers/` — `README.md` (index), `01-dav1d-enforcement.md`, `public-surface-audit.md`, `02-06-fleet-review.md`, `raw/*.md`, `fanout.py` (re-runnable).

## The findings that change the plan

**1. Dav1d enforcement is already built and switched off.** `NouGenRelay/src/nougen_relay/guard.py` has path-containment overlap (`own_cover`, `gh._scopes_overlap`, `foreign_claims`), TTL expiry (`claim_is_active`, `_claim_ttl_hours`), and a hard block returning `EXIT_DIVERGED` behind `_require_claim_default()` — per-repo opt-in via `git config nougen.requireClaim`, **off by default**, warn-by-default otherwise. The "govern coordination, don't be a bottleneck" principle the leg asks for is the existing default. Three real gaps: (a) it fires at COMMIT time, not CLAIM time — which is why the blade fixture happened, no commit was involved; (b) `foreign_claims()` excludes your own machine, so same-machine self-collision is structurally invisible, and the live fixture IS a self-collision; (c) nothing gates "done" on evidence.

**2. `verify_relay` is nearly free and is the highest-value tool in the batch.** `src/nougen_shards/assurance.py` already returns VERIFIED/CONTRADICTED/UNCERTAIN/UNVERIFIED with confidence, rationale, evidence_used, caveats — and already carries the right policy in its docstring: never mutate from an automated verdict. Same posture applies to claims: label, don't auto-close.

**3. Public-surface drift is NOT mostly prose.** Measured across 8 in-scope public repos: **6 of 8 have no license**, 7 of 8 have no description and no topics, and `Nyx-Playground`'s README is **18 bytes**. `nougen-relay` has a 15KB README and an empty description — backwards. No docs compiler fixes any of that. Sequencing answer: **metadata and licensing first, prose second.**

**4. 20 connector tools → 5.** `shards_related` already exists as `recall_related`; `repo_diff`/`repo_status` are git with extra steps; `command_run` is the highest-risk item for the least gain. `readme_sync` + `docs_drift` + `changelog_build` + `public_surface_audit` are four modes of ONE tool, not four tools. First wave ranked: verify_relay, repo_scan, tests_run, nougen_docs, repo_read.

**5. `VERIFIED` decays into a lie.** A claim verified against shard #N stays VERIFIED after `shards_amend` mutates #N. Bind each verdict to the cited shard's content hash; reset to UNVERIFIED on amend/retract.

**6. Models cannot be trusted to establish facts — demonstrated in this batch.** Given an explicit file inventory and an instruction not to invent files, three separate fleet returns named `src/nougen_shards/vault.py`, `tools/generate_docs.py`, `tools/drift_audit.py`. None exist. Every factual detector in the docs compiler must be deterministic (grep, parse, count, exit code). Models compress wording; they never establish facts.

## Two calls that contradict the original legs — director may overrule

- **`Learned` CHANGELOG category: rejected.** It creates a sanctioned lane for unfalsifiable public prose inside a system simultaneously trying to make stale docs detectable. If a lesson changed behaviour, it belongs under Fixed/Changed with the behaviour named; if it changed nothing observable, it belongs in a shard.
- **Do NOT upgrade the claim guard to block-by-default.** Block only on exact scope-set equality (the dedup case, never legitimate); leave prefix overlap as a warning. One over-block and someone disables `requireClaim` permanently.

## Ask

Blade owns the implementation of finding 1 — blade holds the live `relay_daemon` claim and is the collision fixture. This lane produced spec only, deliberately, to avoid a second lane editing claim code.

## Done when

Smallest first commit, not a subsystem: `scope_set` normalization + `claim_id` + self-dedup predicate in `nougen_relay.core.cmd_claim`, plus one regression test whose fixture is the two real blade claims (`blade1tb`/`antigravity`, session `ac1f9b4e…`, scope `relay_daemon,hud,ui,keymaker`, SHAs `7374548` and `c921bc0`, 21s apart).

Assert: two claims in, one active claim out, loser carries `superseded_by`, one entry appended to `decisions`, and an unrelated third claim on a different scope is provably untouched — that last assertion is what proves Dav1d governs the road without becoming a toll booth.
