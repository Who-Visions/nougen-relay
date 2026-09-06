# HARDCADE race telemetry — design proposal

Status: proposal only, not implemented or deployed. Addresses canonical relay `20260830T234503Z__chatgpt-app__g-whoentertains`. This design requires no remote changes. Blade availability is runtime state, not a design assumption. Architectural decisions below are recommendations awaiting implementation, not claims about existing telemetry.

## Existing interfaces inspected

- `NouGenRelay/src/nougen_relay/core.py`: canonical `.handoffs` records, claim/idempotency mechanisms, `_write_registry_record_upstream` compare-and-swap updates. Relay supplies lifecycle and ownership references. Existing file-based leases do not guarantee distributed exclusive execution; the proposed Store authority and fencing described in relay-store-design.md are required for purchased work.
- `NouGenTracker/fleet/fleet_usage_log.py`: `log_fleet_usage(provider, model, input_tokens, output_tokens, cached_tokens, reasoning_tokens, lane, source, timestamp)` appends count-only JSONL. It silently suppresses logging failures and converts missing counts to zero. It currently lacks race/call IDs, measurement provenance, and reliable delivery. Therefore historical ledger rows alone cannot prove complete race costs.
- `NouGenShards/src/nougen_shards/core.py`: `capture(...)` accepts tags, source_uri, original_timestamp, domain_key, sensitivity and utility; credential-shaped content is redacted before storage. Inspect the returned capture result and retain shard/database receipt instead of equating an attempted write with capture.
- `NouGenRelay/src/nougen_relay/shardlog.py`: existing curated cross-machine publication with withheld personal tags and credential scanning. It is not an unrestricted telemetry replication bus.

## Responsibility and authority

Relay supplies race/work lifecycle references; Tracker normalizes measurements; Shards preserves searchable meaningful history; HARDCADE builds disposable statistics/achievement projections; Griot narrates evidence. An additive local race event store plus durable publication outbox bridges these existing surfaces. It does not replace their stores. Scores, XP and leagues never grant tool permissions, credentials, spending, machine access, or approval bypass. Suggested progression affects display and routing recommendations only; the existing policy and operator-approved budgets remain authoritative. A higher Strength score can suggest a heavier class, never authorize it.

## Proposed schema

Use SQLite initially with explicit migration versions. All IDs are opaque UUIDs, timestamps UTC, durations measured monotonically within a process. Cross-machine elapsed time includes clock uncertainty and is not eligible for speed records until timing is reliable.

| Entity | Required data |
|---|---|
| `race` | race_id, relay_leg_id, baton_id, parent_race_id, buyer/runner IDs, seller/source ref, team IDs, class, league, season, immutable weight and weight_formula_version, start/finish timestamps, lifecycle status, coverage status |
| `race_plan` | race_id, plan_version, token_price and denomination, projected token cost, projected duration, budget ceiling, estimator/version, confidence and uncertainty interval, approval/policy reference; virtual token price is separate from provider USD cost |
| `race_event` | event_id primary key, race_id, producer/node/session IDs, producer_sequence, schema_version, event_type, occurred_at, received_at, causal_parent_id, idempotency_key unique per producer, sanitized typed payload, source_ref/digest, confidence with method, supersedes_event_id |
| `call_usage` | usage_id, race_id, attempt_id, provider_call_id nullable, provider/model/lane/machine, input/output/cache/reasoning counts nullable, measurement_kind `provider_reported/local_measured/estimated/unknown`, collector/version, provider accounting semantics, normalization_version, observed_at, source_ref, coverage, measured_charge nullable, estimated_api_cost nullable, currency and price_table_version |
| `race_verification` | verification_id, race_id, verifier ID/version, criterion IDs, result `pending/pass/fail/inconclusive/retracted`, accuracy numerator/denominator where defined, evidence_refs/digests, confidence/method, scope, verified_at, supersedes_id |
| `race_outcome` | race_id, outcome_version, utility measure/unit/evidence, downstream usefulness links, terminal status, token and duration aggregates with separate measured/estimated components, context peak/limit, retries/failures/recoveries, tool IDs, handoff/split counts, XP/ruleset version, coverage and verification refs |
| `achievement_receipt` | receipt_id, race_id, recipient IDs, achievement code/rule version, threshold/cohort context, evidence event/verification IDs, exact measurements and uncertainty, earned_at, state `candidate/verified/revoked`, supersedes_receipt_id |
| `publication_outbox` | batch_id, deterministic manifest digest, event IDs, shard type/version, attempt_count, status `pending/confirmed/failed`, last_error_class, next_attempt_at, returned shard_id/db_index, confirmation_time |

Meaningful events include buy/reserve/start, split, handoff offered/accepted, tool completion (tool identifier/result category only), provider call usage, retry/failure/recovery, context measurement, artifact verification, finish, downstream reuse, achievement and correction. No prompts, responses, raw transcripts, shell arguments, environment values, credentials, or raw exceptions enter telemetry. Use allowlisted fields and sanitized error classes; provenance points to access-controlled artifacts, not embedded secret-bearing content. Titles/tags must also be sanitized because they can remain plaintext.

Zero means observed zero, never missing. Retain provider semantics because cached input may be a subset of input and reasoning a subset of output; do not blindly sum all columns. Report normalized total only where semantics are known. Model token units are tokenizer-specific: report heterogeneous totals with provider/model breakdown and do not treat them as interchangeable efficiency units. Estimated API cost is not measured spending, subscription allocation, or a bill. Missing historical correlation IDs remain unallocated; no guessed attribution to a race.

## Ingestion, recovery and correction

1. Producers emit stable event IDs; local SQLite transaction inserts a validated event and its outbox entry atomically. Duplicate ID plus equal digest is a no-op; same ID/different digest becomes a conflict requiring reconciliation.
2. Add a versioned Tracker adapter that provides race_id/attempt_id/call ID and measurement provenance without breaking existing `log_fleet_usage` consumers. Do not pretend its best-effort legacy logger provides durable delivery.
3. Offline nodes retain bounded local outboxes and sequence numbers. Receipt acknowledgements advance per-producer watermarks; missing ranges mark incomplete coverage. On capacity exhaustion, retain explicit gap/error state and stop claiming complete telemetry; never silently drop events or fail open into verified achievements.
4. Merge by event identity and causal references, not wall-clock last-write-wins. Conflicting completion/verification assertions remain visible until a superseding verification resolves them. No per-token Git commits; link sanitized race receipts from existing Relay records using its canonical writer when separately authorized.
5. Rebuild all projections from events. Corrections are append-only supersession/retraction events; invalidate dependent scores, records, and achievements and rebuild under the same ruleset. Source digest supports integrity, not proof of correctness or authorship.

## Achievements and statistics

A completed race is not necessarily verified. XP/official standings require a passing current verification and adequate telemetry for each statistic. Unknown costs exclude efficiency records but need not exclude a separately verified correctness result. Every view shows observed race count, eligible count, exclusions, coverage, ruleset, as-of time and uncertainty; do not silently turn unknowns into zeros.

HEAVYWEIGHT receipt requires predeclared weight/formula, recipient, expected and actual cost (measurement kinds retained), accepted handoff chain, retries, verifier receipt and cohort record context. Clean Handoff/Perfect Exchange require sender and receiver acknowledgement plus artifact identity; First Pass needs complete attempt coverage; Recovery Run requires failure and subsequent verified recovery; No Relearn needs an explicit reuse criterion and evidence rather than a token-saving guess. Truth Keeper and Archivist need verified correction and confirmed durable capture receipts. Iron Relay, Fast Split, Efficient Runner and Relay Champion need versioned thresholds, timing/measurement eligibility and comparable cohort records. Do not award novelty/first claims without a bounded searched-history scope and coverage statement.

Derive Speed from verified comparable durations; Strength from completed declared weight classes; Endurance from sustained verified sequences; Accuracy from explicit verified result denominators; Memory from confirmed downstream reuse; Recovery from verified post-failure success; Efficiency from verified value per comparable measured resource; Teamwork from accepted handoffs/team outcomes. Publish raw components before any weighted score. Power rankings can use a published recency-decay formula with minimum sample counts and uncertainty; weights and league thresholds are proposed product choices, not empirical facts. Wins require an explicit common challenge/cohort and tie policy. Prevent inflation by counting canonical races once, not each duplicate relay, retry, or team member as separate full wins.

## Standings and records query contract

Define a rebuildable `eligible_race_metrics` projection: one row per canonical race and declared participant attribution, season, league, class, weight_band, ruleset_version, verified_value, value_unit, win_flag, accuracy_passed/accuracy_total, measured_resource_cost, cost_unit, duration_ms, handoff_count, recovery_count, timing_eligible, cost_eligible, verification_id and coverage. Team credit uses a recorded attribution rule; do not duplicate aggregate value. Filtering scope is mandatory and comparison units must match.

Illustrative SQL over these proposed projections (not runnable against current stores):

```sql
-- Standings: users choose one league/class/ruleset and value unit.
SELECT agent_id, COUNT(*) AS eligible_races,
       SUM(verified_value) AS verified_value, SUM(win_flag) AS wins,
       SUM(accuracy_passed)*1.0/NULLIF(SUM(accuracy_total),0) AS accuracy
FROM eligible_race_metrics
WHERE season=:season AND league=:league AND class=:class
  AND ruleset_version=:ruleset AND value_unit=:value_unit
GROUP BY agent_id
ORDER BY verified_value DESC, wins DESC, agent_id;

-- Lowest measured cost at comparable weight: preserve all tied records.
WITH cohort AS (
 SELECT *, DENSE_RANK() OVER (ORDER BY measured_resource_cost ASC) AS place
 FROM eligible_race_metrics
 WHERE season=:season AND class=:class AND weight_band=:weight_band
   AND ruleset_version=:ruleset AND cost_unit=:cost_unit AND cost_eligible=1
)
SELECT race_id, agent_id, measured_resource_cost, verification_id
FROM cohort WHERE place=1;
```

Analogous record queries maximize weight, accepted handoff count or verified recovery count, and minimize duration only for timing-eligible races within a specified comparable cohort. Index `(season,league,class,ruleset_version)` and `(race_id,producer_id,producer_sequence)`. Separate coverage query counts all races and exclusion reasons so filtered leaderboards cannot conceal failures or missing data.

Views: box score joins race+ordered events+usage+verification+receipts; season and career stats aggregate within explicit date boundaries; standings use published verified components; highlights query verified achievement receipts; records retain ties; power rankings apply versioned decay; match history groups baton classes, comparable challenges and team composition; Griot reads receipts plus source-linked chronological events, labels inferred narrative, and cites uncertainty/conflicting evidence. Griot prose cannot mutate truth or grant achievements.

## Sharding strategy and acceptance

Persist every meaningful structured event locally; publish bounded, deterministic race event batches through Shards `capture`, tagged by sanitized race/season/type and linked using source_uri. Capture batch manifest plus source event IDs; keep immutable finish/verification/achievement/correction receipts as separate meaningful shards. Do not assume capture is idempotent: outbox records confirmed shard receipts, checks uncertain outcomes by deterministic source/manifest before retry, and tolerates detectable duplicates if the existing capture API cannot guarantee uniqueness. Never mark published from a generic success string without an identified receipt. Local capture does not prove cross-machine publication; retain separate statuses. Reuse existing curated shardlog publication only for eligible sanitized summaries; keep personal telemetry withheld. Retention and outbox limits are configurable implementation decisions and no deletion is proposed here.

Implementation acceptance should cover crash-after-capture recovery, duplicate/conflicting events, missing usage versus true zero, cache/reasoning overlap normalization, late offline events and clock skew, achievement revocation after verifier correction, secrets/raw-transcript rejection, unknown-cost exclusion without erasing verified correctness, tie handling, team attribution, deterministic replay and proof that scores never affect authorization. These are proposed tests; none were executed as this is a design deliverable.

## Review provenance

Actual OpenRouter engineering inference informed this proposal; local source inspection verified the integration seams. The telemetry entities and SQL projections are proposed, not deployed. Existing best-effort usage logging and file leases are not represented as transactional guarantees. The related marketplace design is [Relay Store](relay-store-design.md).
