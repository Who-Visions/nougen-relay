# 🤝 Git Handoff — claude-app / g-nougenai

**Goal**: PHOEBUS: independently war-game the full 100-item shard hardening backlog and return evidence-linked attack chains
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T18:24:42.606Z

---
## Recipient
Phoebus lane / claude-app g-whoentertains.

## Situation
Dave asked Codex to war-game the "100 ways to make shard recall frictionless" backlog, then asked: "cc-msg phoebus what war games is." Direct cross-node delivery was attempted first and did NOT succeed:
- AgyMsg LAN send to phoebus resolved to 10.0.0.179 but fell back.
- SSH alias `phoebus` did not resolve.
- Direct SSH to `10.0.0.179:22` returned `Permission denied`.
No cc-msg delivery is being claimed. Dave explicitly ordered the full request relayed instead.

The source backlog is artifact "Shard Grid Hardening" and shard 17745: 100 proposed items across recall correctness, ranking/scoring, temporal/provenance, federation, MCP parity, deploy safety, data integrity, observability, UX/auth, and regression testing. The incident evidence set includes 16632, 17190, 17192, 17620, 17736, 17738, and 22729.

## Codex Preliminary War-Game
The backlog should not be executed in its published category order. It needs a truth-and-safety dependency order:

1. **P0 truth gates**
   - Compare origin response, Worker response, MCP `content`, `structuredContent`, and provider rendering field-for-field.
   - Propagate `isError`; errors must never become "(no matches)" or `complete=true`.
   - Expose node identity, code/schema version, upstream list, domain path, retry tier, and trustworthy-completeness state.
   - Build the single end-to-end "diagnose recall" probe before further tuning.

2. **P1 deploy and durability gates**
   - Establish one version-controlled canonical Worker source.
   - Quarantine the stale duplicate deploy path that can revert roughly 366 lines.
   - Preserve bindings/vars/secrets, capture a pre-deploy diff, smoke recall/search/window/coverage, and prove rollback.
   - Prove persistence with write -> read -> deliberate restart -> read. A successful push count proves delivery, not durability.

3. **P2 federation and data guards**
   - Reject self-identity upstreams by node identity, not URL text.
   - Enforce a hop ceiling, quarantine unhealthy upstreams, and prevent network-volume WAL hazards.
   - Run cross-node write/read canaries, integrity checks, and an offline restore rehearsal.

4. **P3 recall and ranking quality**
   - Inventory existing fixes/tests before adding duplicates.
   - Add the hand-labeled golden set, ranking explanation, correction/supersession edges, domain canaries, and duplicate penalties.
   - Never interpret RRF `final_score` as cross-query relevance.

5. **P4 frictionless CLI/auth/UX**
   - Only after truth gates hold: OAuth CLI, one-command recall, near-miss hints, unified status, and inline score provenance.

## Five Coupled Attack Simulations
1. **False-empty cascade**
   Healthy origin returns hits -> Worker drops payload from `structuredContent` -> provider renders empty -> operator trusts the same broken observer -> wrong infrastructure RCA -> wipe/restart/redeploy risk.

2. **Rollback disguised as deploy**
   Stale duplicate `worker.js` deploys -> production loses newer handlers/guards -> basic health stays green -> no field-parity smoke catches it -> silent regression reaches every provider.

3. **Laundered federation truth**
   Node federates to itself or an unreachable upstream -> timeout/thread amplification -> outer Worker ignores `isError` -> response reports `complete=true` or empty success -> caller stops investigating.

4. **Delivery mistaken for durability**
   Rebuild reports zero failed writes -> data landed on ephemeral or unsafe storage -> restart/deploy occurs -> rows vanish -> operators learn only after recall misses. Require restart-survival proof.

5. **Ranking semantics corruption**
   RRF overwrites `final_score` -> consumers treat it as relevance and compare across queries -> thresholds and alerts are invalid -> stale/high-utility or duplicate corrections crowd out current evidence.

## Corrections Phoebus Must Preserve
- Shard 17738 corrects the incident record: the self-loop was invalid and worth guarding against, but it did **not** cause the empty-recall incident. The observed cause was MCP payload loss between `content` and `structuredContent`.
- Shard 17190's temporal/data-loss reading is superseded in part: relay 20260901T160920Z reports all nine Blade DBs healthy with `temporal_meta`; stale code and schema visibility remain separate concerns.
- The artifact's statement "nothing here has shipped" is false as a ledger statement:
  - Shard 16632 says domain-mask fusion, ranked OR retry, BM25 saturation correction, and tests `test_recall_domain_mask.py` / `test_fts_or_fallback.py` already shipped.
  - Shard 17192 says the content-only fleet deployer already has syntax and required-symbol gates.
- Convert all 100 entries to explicit state: `proposed`, `already-shipped`, `verified-live`, `superseded`, or `blocked`, with owner and evidence.

## Request to Phoebus
Independently red-team the full backlog from Phoebus's machine and connector perspective. Return:

1. Your top five war-game scenarios, each as:
   - initiating fault;
   - propagation chain;
   - misleading green signal;
   - blast radius;
   - detection;
   - containment;
   - permanent guardrail;
   - evidence shard/relay IDs.

2. Any item whose premise is false, stale, duplicated, already shipped, or dangerously ordered.

3. Any Phoebus-specific failure class Blade cannot see: sandbox permissions, local cluster drift, tunnel/origin identity, provider rendering, filesystem/journal behavior, or restart persistence.

4. Your recommended first implementation slice, limited to a mergeable unit with exact files/tests and done-when evidence.

5. Reply by follow-up canonical relay referencing this leg. Do not mutate tunnels, Workers, DBs, credentials, or shared runtime while answering.

## Done When
- Phoebus publishes an evidence-linked independent assessment.
- The top attack chains and ordering corrections are reconciled with shard 17738 and the already-shipped guards.
- The first slice has exact scope, tests, rollback boundary, and live verification criteria.
