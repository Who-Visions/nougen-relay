# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: HANDOFF whoart/claude-app 2026-08-28/29: 12 legs answered, shard-grid P1 root-caused, Apache-2.0 carve-out, CI dead on billing — open items and what NOT to re-derive
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T12:52:23.668Z

---
whoart/claude-app, session 3348bb46, 2026-08-28 20:xx through 2026-08-29 12:xx. Companion to the security leg 20260829T125116Z. Everything below was verified from this box unless marked otherwise.

## 1. Twelve relay legs answered (leg 20260829T005307Z)

All 6 chatgpt-app originals + 6 ccr/relay-watch mirrors acked. Method was fleet fan-out, not inline: 48 routes loaded, 13 healthy, 6 evaluations across 6 DISTINCT lanes. Artifacts in `NouGen/ops/relay_answers/` (README.md index, 01-dav1d-enforcement.md, public-surface-audit.md, 02-06-fleet-review.md, raw/, fanout.py).

Headline answers, so nobody re-derives them:
- **Dav1d enforcement is already built and switched off.** `nougen_relay/guard.py::_require_claim_default()` — per-repo opt-in via `git config nougen.requireClaim`, OFF by default, returns `EXIT_DIVERGED` when on. Of the 8 requested capabilities only (5) evidence-before-completion was genuinely open. (6) retry escalation was ALREADY BUILT (`record_leg_failure` does exponential backoff + dead_letter). My first capability map was wrong because I read a clone 731 commits stale — see §6.
- **20 proposed connector tools cut to a first wave of 5**: verify_relay, repo_scan, tests_run, nougen_docs, repo_read. `shards_related` already exists as `recall_related`; `repo_diff`/`repo_status` are git with extra steps; `command_run` is highest-risk/least-gain.
- **`readme_sync` + `docs_drift` + `changelog_build` + `public_surface_audit` are four MODES of ONE tool, not four tools.**
- **`Learned` CHANGELOG category: rejected** (contradicts the original ask — GM may overrule). It creates a sanctioned lane for unfalsifiable public prose inside a system trying to make stale docs detectable.
- **Do NOT upgrade the claim guard to block-by-default.** Block only on exact scope-set equality; leave prefix overlap a warning. One over-block and someone disables requireClaim permanently.

## 2. Claim self-dedup — PR #14, NOT MERGED

`97bf98f` on `claim-self-dedup`: decisions now write one file per retirement to `claims/decisions/<loser-file>.json` instead of appending to a shared `decisions.jsonl` — the claims dir is `git add`-ed and pushed on every take, so a shared append-only file conflicts across machines. Full local suite 317 passed / 5 skipped / 1 xfailed.

TWO BLOCKERS, both still open:
- CI cannot go green (§3).
- The dedup key is `(machine, scope_set)` with NO `agent`. On whoart, `claude-cli` and `antigravity` would silently supersede each other. **GM design call.** Merging ships machine-only keying by default.

## 3. GitHub Actions is OFF ORG-WIDE for billing

Every job dies in 3-5s with `steps: 0`. `gh run view --log-failed` returns "log not found" because no log exists. The real message is only at:
`gh api repos/Who-Visions/NouGenRelay/check-runs/<job_id>/annotations`
-> "The job was not started because recent account payments have failed or your spending limit needs to be increased."

**A red X on any Who-Visions repo currently carries ZERO information about code.** "Merge when green" is unsatisfiable fleet-wide. Commit `9306520` ("Fix CI red on main: stdout-polluting import + E741 lint") was at least partly chasing this phantom. Restoring it is a GM payment action.

## 4. Shard-grid P1 — root-caused and mostly fixed

Symptom: recall EMPTY, search EMPTY, window RETURNS ROWS. That asymmetry is the whole diagnosis — the paths that RANK were dead, the path that filters on timestamp and skips scoring worked.

ROOT CAUSE (found by blade1tb): the federated fan-out guards catch `sqlite3.OperationalError`, but a corrupt file raises `sqlite3.DatabaseError` — its PARENT class. Never matched, escaped the loop, killed the whole federated read. Eight healthy DBs sat unread because of one bad file. `shards_coverage` was reporting `databases_errored [{index:5, "DatabaseError: database disk image is malformed"}]` the entire time.

Proof it was the fan-out and not the data: shard 23238 lives on `_db_index 2` — mounted, healthy, 22,361 shards — and was unrecallable because the abort at index 5 happened first.

FIXED AND PUSHED on `codex/shards-capture-main`: `b6b364c6` (all fan-outs catch DatabaseError, connection opened INSIDE the try because `get_connection()` runs `PRAGMA journal_mode=WAL` and raises before the body), `f9fc71f1` (`recall_trustworthy` false whenever `databases_errored` is non-empty, plus a `recall_trustworthy_reason` string), `0c23aa14` (gateway_probe three states), `19b41cc` (the loops below), `2f890056` (redaction, see security leg).

**I found 2 missed fan-outs on review; a mechanical invariant test then found a 3rd.** 5 guards became 8. The third was in `mark_shard` and would have reported "shard not found" for a shard that exists — the most corrosive answer a memory system can give, because it is indistinguishable from truth. **Two careful reviewers missed it; a lint found it in one run.** Prefer the mechanical check.

## 5. STILL BROKEN: DB5 on the node the connector reads

whoart's lane: `total_shards 199,877`, grid `178,122` readable, `databases_errored index 5 malformed`. DB5 holds ~21,755 dark shards.

**Blade's `nougen_shards_5.db` is HEALTHY with 30,287 rows** — verified BY ME over SSH, not taken on report: all 9 grid DBs `quick_check=ok`, FTS row count == shard count on every one, total 260,050 (vs blade's reported 260,044 — six MORE on a live capturing box, drift not disagreement).

**So the repair source exists, is intact, and is LARGER than the thing it repairs. `CLOUDFLARED_NGS_TUNNEL_TOKEN` is the entire distance between them** — absent from the vault, so `blade.nougenai.com` is 530, so the read-through configured as `upstreams: [{name: blade, url: https://blade.nougenai.com}]` cannot reach it. **This is incident-critical, not housekeeping, and it is blocked on the GM.**

NEW, nobody was looking for it: blade holds **38,165 shards OUTSIDE the 9-DB grid** — `nougenai_memory_vault.db` 33,168, `sol_memory_vault.db` 4,890, `codex_journal_shards.db` 107. Total on disk 298,214. `recall` cannot see them regardless of grid health. Unknown whether that is intentional (legacy Watchtower vaults) or a mount never wired. Needs a decision.

## 6. FALSE SIGNALS — the recurring theme, do not trust these

- **`shards_status` has now been wrong in BOTH directions in one session, from both lanes.** `up:true` while every ranked read returned nothing; `up:false` in the same breath as a working search. It is NOT measuring "can this lane read". It is also LANE-DEPENDENT: whoart resolves shards.nougenai.com (the HF Space), blade resolves its own node. Two lanes disagreeing is two gateways, not a contradiction. **Any leg claiming "shards is up" without naming its origin is unfalsifiable and should be treated as noise.**
- **`recall_trustworthy` answered TRUE with a DB malformed** — the designated arbiter for "does this memory exist" gave the wrong answer to anyone who checked responsibly. Fixed in `f9fc71f1`.
- **`gateway_probe.py` produced a FALSE RED**: exited 1 with a gateway-shaped string when auth was provably fine and the downstream node was empty. Fixed in `0c23aa14` — now OK / AUTH-OK-NO-DATA / FAIL, every line naming its origin.
- **A local clone 731 commits stale was executing as the installed package.** `nougen_relay` imports from `C:\Users\super\Outpost\NouGenRelay`; until I fast-forwarded it, whoart was RUNNING 731-commit-old relay code including the claim guard. Check clone freshness before reasoning about behaviour.
- **`shards_window` with a `query` returns "(no shards in <era> — that era may live on another node)" when the QUERY misses**, not when the era is empty. Same window with no query returned six. That message sends you hunting the wrong node.
- **Cloudflare error 1010 on shards.nougenai.com is a browser-signature block, not a ban or an outage.** A bare urllib client is refused at the edge BEFORE auth; with a normal browser User-Agent the same request reaches the app and returns a clean 401.
- **`shards_capture` returns a bare `{}` — a MISSING RECEIPT, not a lost write.** blade proved it (captured, got `{}`, then found id 27052 present). `shards_amend` by contrast returns `{"amended":..,"added_chars":..}`. Verify captures by recall, and fix the silent failure path.
- **Models fabricate absences as readily as presences.** Three fleet routes, holding an explicit file inventory and told not to invent files, named `src/nougen_shards/vault.py`, `tools/generate_docs.py`, `tools/drift_audit.py`. None exist. Any docs compiler must use deterministic detectors (grep/parse/count/exit code) for every factual claim; models may compress wording only.

## 7. Public surface + licensing (uncommitted on whoart)

Measured across 8 in-scope public repos: **6 of 8 have NO license**, 7 of 8 no description and no topics, `Nyx-Playground`'s README is **18 bytes**. `NOASSERTION` on the two that have one is CORRECT — the Who Visions Source-Available License v1.0 is custom and GitHub cannot SPDX-match it. Sequencing answer: metadata and licensing first, prose second.

`docs/local-worker/` was 14 files, 13 of them `cj4c0b1`'s (11 byte-identical after newline normalisation, 2 differing by a single `gemma:e2b-it` -> `gemma4:e2b` line), sitting under NouGen's proprietary license. Their repo has NO license = all rights reserved to them. Those 13 removed; `scripts/delegate_task.py` (the one file not in their repo) kept. Added Apache-2.0 LICENSE + NOTICE + a README written from the GM's own Reddit post, and a `## 6. Scope and Exceptions` carve-out in root LICENSE.md. Provenance: the pattern is the GM's (r/google_antigravity post predates their repo, and their own comment credits him by name); their prose and layout are theirs and are linked, not copied.

**UNCOMMITTED on branch `agent/nougen-assurance-sprint`.** Also uncommitted: `ops/relay_answers/`. Branch is 13 behind origin/main.

## 8. Open items, by owner

GM: rotate the Notion token (leg 20260829T125116Z) · `CLOUDFLARED_NGS_TUNNEL_TOKEN` so DB5 can resync · GitHub Actions billing · agent-vs-machine dedup keying on PR #14 · whether the 38k off-grid vaults should be federated · MIT vs Apache for the remaining public repos, and which of Kaedra/Visions-ai/Yuki-Ai/unk-app-ai are product vs open · a decision on the Rhea Space no-op rebuild.

ANY LANE: merge PR #14 once the above is answered · the LOCAL_VAULT `final_score` 0.45 floor · blade is carrying ~90 dirty files of uncommitted work by an UNKNOWN OWNER in core.py and app.py, which makes its test baseline unreproducible by anyone else.

## 9. One process finding worth keeping

**Claims are branch-local FILES.** Take on `main`, switch branches to work, release from the feature branch — and `release` reports "nothing to release" in success-shaped output while the claim stays live. Take and release on the SAME branch. This silently leaves live claims fleet-wide and I nearly believed the false success.
