# Relay Store: proposal and implementation plan

Status: design only. No marketplace, budget, billing, capability grant, or background worker is activated by this document.

Acceptance scope: relay `20260830T234039Z__chatgpt-app__g-whoentertains` explicitly asks for a design proposal or implementation plan. This proposal covers its marketplace schema, discovery, quoting, publishing, reservation, execution, settlement, Tracker hooks, Shards feedback, permission boundaries, loop prevention, and compatibility requirements.

## Existing boundaries

NouGenRelay's `src/nougen_relay/core.py` supplies leg identity, `cmd_create`, `cmd_claim`, execution idempotency, retry/dead-letter handling, and `_write_registry_record_upstream` for canonical publication. Scope claims protect project work; they are not purchases. An acknowledgement is ownership intent, and completion is a lifecycle assertion rather than independent proof of success.

The inspected filesystem lease implementation checks for a file and replaces it; this does not guarantee exclusive distributed acquisition. Its release path does not establish holder fencing. Consequently neither Git JSON nor existing lease files can authorize credit settlement or guarantee single execution. Store introduces an authoritative transaction service and projects compatible state into Relay.

NouGenTracker's `fleet/fleet_usage_log.py:log_fleet_usage` writes count-only JSONL best-effort; existing records lack invocation/race/leg IDs and measurement completeness. `token_tracker.py:parse_fleet_usage`, `fold_openai_usage`, and `fleet_dailies.py` are integration seams, not a financial ledger. NouGenRelay's `shardlog.py` exports existing shards; it is not an ingestion API. Use the actual Shards capture interface for new evidence.

## Baton and ledger schema

Version every schema. Use integer internal credits and fixed-point currency amounts with explicit units; never floating-point balances. Provider tokens, internal credits, estimated API cost, and actual charges are separate quantities.

| Entity | Fields and constraints |
| --- | --- |
| `baton` | `baton_id`, optional canonical `relay_leg_id`, `schema_version`, title, goal, provenance references, seller lane/session, eligible lanes, capability requirements, urgency, risk class, expected value with unit/confidence, estimated compute/latency, versioned acceptance criteria, expiry, dependencies, root intent ID, parent baton ID, depth, status, result references. Buyer lane, settlement state, quality receipt, and refund/dispute state are projections of referenced records. |
| `quote` | Immutable quote ID, baton/version, seller/buyer, pricing formula/version, internal credit price/credit type, budget source, provider route/model, estimated token buckets and provider cost, uncertainty interval, maximum permitted provider charge, expiry, eligibility/policy version, quote inputs and evidence references. |
| `account` | Account ID, owner/policy authority, currency/credit type, allocation source, balance, reserved balance, version. Only authorized allocation transactions mint credits; a seller cannot issue its own treasury grant. |
| `reservation` | Reservation ID, quote ID, buyer account, root intent, attempt ID, credit amount, provider-cost ceiling, status, expiry, monotonically increasing fencing token, worker session, idempotency key. One active purchase per exclusive baton version. |
| `ledger_entry` | Unique transaction ID, reservation/attempt, entry kind, debit account, credit account, nonnegative amount/unit, receipt references, actor/policy identity, timestamp, reversal-of ID. Entries are append-only and balanced per denomination. |
| `usage_receipt` | Invocation/attempt/leg IDs, provider/model, raw disjoint-or-overlapping token semantics, collector/version, source evidence, nullable counts/charges, measurement kind, completeness, normalization version. Unknown usage is not zero. |
| `verification` | Criteria version, artifact digest and access-controlled reference, verifier identity/version, pass/fail/inconclusive, evaluated attempt, timestamp, supersession link. |
| `dispute` | Reservation, contested entries/result, claimant, reason/evidence, resolution authority, state, decision receipt, adjustment references. |
| `outbox` | Stable operation ID, aggregate/version, destination, allowlisted payload, attempts, next retry, status, destination receipt. Unique destination/operation prevents duplicate projection effects. |

A baton packages a continuation of intent, not an arbitrary prompt. Publishing requires provenance, acceptance criteria, eligibility, an accountable seller and a declared budget policy. Discovery supports pagination/filtering by capability, price ceiling, dependencies, urgency, risk, value, lane, and expiry. Drafts and expired or disputed offers are visibly distinct from purchasable inventory.

## Quote, reserve, claim and execute

All interfaces in this section are proposed additions, not existing commands.

1. `store publish` registers a priced offer. It does not debit a buyer or charge ordinary Relay creation. Unpriced relays retain the existing free path.
2. `store quote` compares local execution, specialist help, and eligible cloud routes. Quotes use measured history where available: estimated tokens, provider rates, compute time, queue depth, capability availability, latency, verification success and expected human time saved. Each estimate carries source, uncertainty, and expiry. If no history exists, label the quote provisional; do not imply an arbitrary number is measured pricing.
3. `store reserve` authenticates the buyer, validates the exact quote/version and policy, checks capability eligibility, dependency completion, expiry, balance and all nested caps, then records reservation, fenced ownership, and outbox intent in one transaction. Same request ID returns the existing reservation. Concurrent contenders cannot both buy an exclusive baton.
4. Phase-one authority is a single local service with SQLite on its own local filesystem using a transaction such as `BEGIN IMMEDIATE`. This is database write serialization, not row locking or distributed consensus. Other nodes call that authority; they do not open a shared network database or maintain independent writable balances. If authority is unreachable, paid execution pauses; normal eligible free relays remain usable.
5. The outbox creates or links the Relay leg and publishes the reservation/attempt reference through the existing canonical writer. Publishing failure leaves `reserved_pending_projection`; dispatch waits for the required ownership projection and policy checks. Retry never reserves twice. Reconciliation queries stable IDs after an uncertain publication response.
6. Execution adapters require the current fencing token, expiry, explicit target lane/session, approved resource envelope and provider ceiling. A stale worker cannot settle or resume a revoked attempt. Expiry does not itself prove an external process stopped: reclaim only after cancellation/termination evidence, or keep the baton `reconcile_required` and prevent overlapping side effects.
7. Completion produces result and verification receipts. A Relay `complete` event alone cannot settle success, pay a reward, or prove resource use.

## Caps, permissions and loop prevention

Evaluate authorization at publish, reservation, dispatch, privileged tool use, settlement and administrative reversal. Purchasing assistance never grants a secret, role, filesystem permission, cloud access or approval bypass. Keymaker remains the credential boundary; offers reference capabilities and policy decisions, not credential values.

Enforce account, lane, daily/periodic, provider and root-intent spend ceilings together. Child reservations consume the same root envelope and cannot create a new root to evade it. Bound delegation depth, child count, concurrent reservations, retries, total elapsed time and total attempted work. Detect cycles through ancestor IDs; refuse self-trading/reward loops. Limits are explicit deployment policy, not hardcoded claims about existing fleet law.

Treat provider charges independently from internal credits. An internal refund cannot erase provider charges already incurred. If actual cost is unknown, hold a bounded pending reconciliation liability and pause further paid dispatch when the remaining envelope cannot be proven. Additional authorization is needed before increasing an exhausted cap; a timeout is not a spending exemption.

## Settlement, refunds and disputes

`store settle` validates reservation/attempt identity, fencing, verifier receipt and usage provenance, then atomically records charges, transfers eligible rewards from a capped treasury, releases unused reservation and writes projection events. Unique `(reservation_id, attempt_id, settlement_kind)` prevents duplicate settlement; ambiguous provider requests retain their invocation identity for reconciliation.

On failure, release only unused internal reservation according to the published refund policy; retain consumed-resource accounting. Partial delivery permits a versioned partial-payment rule agreed in the quote. Invalid work may refund the service component without pretending compute was free. A dispute freezes unsettled rewards pending an authorized decision. Corrections use compensating entries, never rewriting balances or deleting historical receipts. Seller utility updates reference verified outcomes and cannot be self-awarded.

## Tracker and Shards adapters

Extend the Tracker producer and parser together with optional `event_id`, `invocation_id`, `leg_id`, `reservation_id`, `race_id`, `attempt_id` and measurement-kind fields. Preserve legacy rows; unknown historical correlation remains unallocated. Do not mark estimated usage exact or sum cached input/reasoning twice. Preserve counter-fingerprint compatibility and measured/estimated separation in daily exports. A successful best-effort JSONL append is not a settlement acknowledgement.

Shards receives sanitized quote-performance, verification, settlement and correction summaries through a durable outbox and the actual `capture` surface. Record returned shard/database receipts and distinguish local capture from fleet publication. Link append-only supersession so stale prices or failed work cannot re-enter current truth as a newer unqualified shard. No raw prompts, transcripts, tokens, secrets, command arguments or unrestricted error strings are published. Price history can improve future estimates without overriding policy or changing past quotes.

## Rollout and verification plan

1. Read-only catalog and schema fixtures; no balances, dispatch or spending. Prove old Relay CLI/MCP records remain readable and ordinary creation remains free.
2. Single-authority ledger simulation using synthetic credits and mocked provider charges. Test concurrent reservation, insufficient funds, expired quote, nested caps, duplicate requests, balanced entries and inaccessible authority.
3. Fenced ownership/outbox adapter. Inject crashes after reservation and before/after Relay publication, expired/stale workers, concurrent release, late completion and uncertain cancellation. Prove no double reservation and no blind repeated side effect.
4. Tracker and Shards adapters in shadow mode. Test missing usage, mixed accounting semantics, duplicate invocation events, failed capture, receipt recovery, redaction and correction lineage.
5. Settlement/dispute simulation. Test duplicate settlement, partial success, real resource cost after failure, treasury exhaustion, self-reward refusal, reversal and replay from the ledger.
6. Operator-approved bounded pilot on existing eligible lanes. Enable no new provider, paid capability or elevated tool merely by shipping this design. Measure quote error, dispatch latency, verification rate and reconciliation backlog before widening limits.

Existing Relay APIs are not deprecated. New `store` commands and MCP tools sit beside them. Proposed schema and implementation tests above are acceptance work for future implementation; this document does not claim they already ran.

## Review provenance

Ollama Cloud `gpt-oss:20b` supplied a draft; local code inspection and independent integration review informed this final proposal. The review rejected charging at publication, automatic full refunds of consumed provider cost, invented existing Rust services, treating shardlog as ingestion, claiming file leases guarantee distributed exclusion, and deprecating free Relay APIs. Provider output is advisory, not implementation evidence.
