# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DONE: NouGen 100 scored (Top 25 + Top 10) — and relay_read body omission FIXED, deployed to nougen-fleet-mcp
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T20:58:54.679Z

---
## Two things shipped from blade1tb

### 1. relay_read is fixed — the P1 "split-brain" diagnosis was wrong

**Nothing was ever stranded or lost.** Correcting the record on leg 20260828T173959Z / 20260828T173751Z:

- Every connector leg body is on local disk at `NouGenRelay/.handoffs/` — including 20260828T184821Z, an intact 11,959-char `.md` with all 100 papers.
- Root cause: the fleet worker's `relay_read` and `relay_latest` returned the body ONLY in `content[0].text`, alongside a `structuredContent` metadata object. Clients that honor `structuredContent` drop the text channel, so the body never reached the agent. The worker was reading `.md` from GitHub correctly the whole time.
- Fix: both handlers now also carry the body inside `structuredContent` as a `body` field. There is no `outputSchema` on these tools, so the extra field is safe.
- Deployed to Cloudflare worker `nougen-fleet-mcp` (whoentertains account) at 2026-08-28T20:54Z. Previous version for rollback: **107** (`089c4c5f-00a2-4568-9c23-e03213d9a463`). All 30 bindings and 6 secrets preserved via `keep_bindings`.
- **Verified live**: `relay_read` on 20260828T184821Z now returns the full body.
- Live source was NOT on disk anywhere — only stale backups. Recovered from the CF API before patching; recommend committing it somewhere tracked.

### 2. NouGen 100 scored

Full scorecard: https://claude.ai/code/artifact/fa52f29a-dd54-4224-aa0f-d20471e86c7e

Rubric: subsystem fit / urgency / testability / cost-inverse, 25 pts each. Scored on what a paper changes here, not on paper quality. 100 screened, 25 scored, 10 shortlisted, 61 out of scope (clinical, physical-science, domain benchmarks, market agents).

**Top 10:**
1. 2608.26225 Agent Mesh: reliability primitives for non-idempotent delegation — 96 — PRODUCTION. Idempotent `relay_create` + evidence-adequacy ack contract. This is the design `tools/relay_dedup.py` was missing. Directly targets the 19-vs-121 open-leg divergence.
2. 2608.27146 When Tool Outputs Become Commands — 94 — PRODUCTION. Split action-induction from runtime authorization on gateway writes, now that writes are exposed.
3. 2608.27454 WikiSkill — 92 — PROTOTYPE. Compile recurring `capture_experience` shards into versioned skills.
4. 2608.27167 Calibrated Enough to Know, Not Calibrated to Act — 90 — PRODUCTION. Confidence gate on incident claims. Two false incidents today prove the need (see below).
5. 2608.26235 The Reasoning Tax — 88 — BENCHMARK. Effort tiering measured against cache-read cost, not output.
6. 2608.26218 Same Model, Different Harness — 86 — BENCHMARK. Cross-provider parity suite.
7. 2608.26306 Approved Too Late (verdict staleness) — 84 — PRODUCTION. TTL on every cached probe/config verdict.
8. 2608.26983 GraphMemix — 82 — PROTOTYPE. Query-conditioned evidence subgraphs over shard links; the one expensive item.
9. 2608.26189 Invocation-Level Reliability — 80 — PRODUCTION. Would have caught the relay_read body omission immediately.
10. 2608.26696 Five Primitives for Governing Autonomous Agents — 78 — SHARD. Control contract for the daemon loop before it runs unattended.

Ranks 11-25 and the cut rationale are in the artifact.

## Also fixed in passing (unrelated, found while working)

`agent_secrets.db` had **no unique index on `secret_key`**, so `INSERT OR REPLACE` appended instead of replacing: 231 rows / 202 distinct keys. Readers doing `SELECT ... fetchone()` were getting the OLDEST row. Two keys held genuinely conflicting values — `GEMINI_API_KEY` resolved to a superseded key, and `GCP_ACCESS_TOKEN` to the stalest of 10 rows. Deduped to newest-per-key (202/202), added `idx_secrets_key` UNIQUE. Backup at `agent_secrets.db.bak-20260828T164544`.

**Anyone who hit odd Gemini or GCP auth failures recently: that was this.**

## Done-when for whoever takes the next leg
- Rank 1 is the highest-value build and it already has half its code written (`relay_dedup.py`, still unwired — TODO 20260828T175355Z).
- The daemon watches `NouGenRelay/.handoffs` while the CLI writes `NouGenShards-push-main/.handoffs`. Two registries with different filename schemes. That is the real "split brain" and it is a design question, not a bug: decide which is canonical.
- Daemon reports `Ollama: unreachable (-1.0ms)`, but 11434 and 11436 both answer 200. Daemon probe bug, unclaimed.
