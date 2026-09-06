# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build source-grounded IRS evidence graph and business activity ledger from original files
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T01:56:45.584Z

---
# Kaedra Wishlist: NouGen IRS Evidence and Business Activity Truth Pass

## Mission
NouGen's current file pass should evolve beyond extracting memories from historical files. The objective is to reconstruct a source-grounded, auditable business activity ledger capable of answering four core questions with evidence:

1. What work did Dave perform?
2. Why was that work performed and what was its business purpose?
3. What did Dave pay for, and how does the expense connect to business activity?
4. Who paid Dave, how much, for what work, and what records support that income?

NouGen should function as an audit INDEX and evidence graph over original records. The underlying records remain the evidence. AI synthesis is never allowed to silently become the source of truth.

## 1. Establish an explicit evidence hierarchy
Every extracted claim should know what supports it. Recommended hierarchy:

ORIGINAL SOURCE RECORD -> SOURCE METADATA -> EXTRACTED FACT -> CORROBORATION -> BUSINESS EVENT -> TAX RELEVANCE -> SYNTHESIS

Source evidence can include original photos/video, EXIF, filesystem timestamps, invoices, receipts, contracts, releases, bank/payment records, emails/messages, project files, exports, commits, source code, calendars, location evidence, client correspondence, deliverables, web assets, and other contemporaneous artifacts.

Later AI summaries and shards should NOT outrank original contemporaneous records.

## 2. Provenance classification on every material claim
Add an evidence/provenance state such as:

SOURCE_VERIFIED: directly established by primary source.
CORROBORATED: supported by two or more independent records.
INFERRED: reasonable relationship derived from evidence but not directly established.
UNVERIFIED: claim exists but source support has not yet been located.
CONFLICTED: records disagree and require resolution.
CORRECTED: prior interpretation was superseded by stronger evidence, while preserving the correction history.

Never promote INFERRED to SOURCE_VERIFIED merely because multiple AI summaries repeat the same inference.

## 3. Preserve uncertainty
Unknown must remain UNKNOWN. Never fill a missing client, purpose, payer, amount, location, or date because it seems likely. AI confidence and evidentiary confidence are different dimensions and should be stored separately.

Example:
model_confidence = 0.97
provenance_class = INFERRED

A model can be highly confident about something the records do not actually prove.

## 4. Build canonical business events
Instead of thousands of disconnected shards, cluster source records into canonical BUSINESS_EVENT objects.

Suggested fields:
event_id
start_time
end_time
event_type
project
client/payer
participants
location
business_purpose
work_performed
deliverables
income_refs
expense_refs
source_refs
provenance_class
confidence
conflicts
corrections
created_from_pass

Examples of event types: photo shoot, video production, editing session, software development, marketing activity, client meeting, travel, equipment acquisition, subscription/software expense, model coordination, contract execution, content delivery, payment received.

## 5. Build the evidence graph, not merely a timeline
The highest-value architecture is relationships:

SOURCE -> EVENT
EVENT -> PROJECT
PROJECT -> CLIENT
EXPENSE -> EVENT
EXPENSE -> BUSINESS_PURPOSE
PAYMENT -> CLIENT/PAYER
PAYMENT -> PROJECT
PROJECT -> DELIVERABLE
DELIVERABLE -> SOURCE FILES
EVENT -> LOCATION
EVENT -> PARTICIPANT
CLAIM -> SUPPORTING SOURCES
CLAIM -> CONTRADICTING SOURCES

This allows NouGen to answer WHY a transaction belongs to the business rather than merely proving that a transaction occurred.

## 6. Expense substantiation packets
For every candidate business expense, attempt to assemble a packet containing:

transaction date
vendor/payee
amount
payment source when available
receipt/invoice reference
item/service purchased
business purpose
associated project/event
associated client when applicable
contemporaneous communications
resulting work/deliverable when applicable
source file references
provenance classification
missing evidence flags

Example conceptual chain:
STORE RECEIPT -> PROP PURCHASE -> MODEL SHOOT -> CONTRACT/MESSAGES -> SHOOT FILES/EXIF -> FINAL DELIVERABLE

The receipt proves purchase. The surrounding graph helps establish business purpose.

## 7. Income substantiation packets
For every payment received, attempt to identify:

payer
amount
date
payment method/reference
invoice/contract
project/event
services performed
deliverables
communications
source references
whether payment is clearly business income, ambiguous, reimbursement, transfer, refund, etc.

Do not classify transfers between Dave's own accounts as income simply because money entered an account. Classification must be evidence-grounded.

## 8. Work/activity substantiation
NouGen should reconstruct when work occurred using multiple signals where available:

filesystem creation/modification timestamps
EXIF capture timestamps
video metadata
Git commits
code/project modification history
exports/renders
emails/messages
calendar events
contracts
invoices
cloud metadata
payment timestamps
location evidence
AI conversation/code execution history

The objective is not a fake minute-by-minute timesheet. It is an evidence-backed activity history showing that substantive business activity occurred during particular periods.

## 9. Business-purpose reasoning
Business purpose should be a first-class field, not free-floating prose buried inside a shard.

For each expense/activity ask:
WHAT was acquired/done?
WHAT project or operational function did it support?
WHAT evidence connects those things?
WHO benefited/paid/participated?
WHAT deliverable or business result followed?

If the answer is ambiguous between personal and business use, flag it instead of forcing classification.

## 10. Original file integrity
Where technically practical, fingerprint source files using a cryptographic hash and retain:

source path
original filename
size
creation timestamp
modification timestamp
hash
metadata extraction timestamp
extractor/version

This lets later systems establish that a referenced source is the same artifact previously indexed. Do not mutate original evidence merely to normalize it. Derived representations should be separately identified.

## 11. Correction ledger
NouGen's existing append-only philosophy is ideal here. Never erase an earlier interpretation just because the new pass finds better evidence.

Example:
2026-08-01 inference: expense believed associated with Project A.
2026-08-28 source pass: invoice and correspondence establish Project B.
Status: CORRECTED.
Reason: stronger contemporaneous primary evidence.

The historical reasoning remains visible while current synthesis uses the corrected state.

## 12. Contradiction engine
Actively search for conflicts:

different dates for same event
different client assignments
payment amount disagreement
receipt versus manually entered amount
filesystem date versus claimed event date
AI memory versus original document
duplicate expense records
same payment associated with multiple invoices
personal transfer accidentally classified as revenue
refund recorded without corresponding original charge

Conflict discovery is valuable. The system should surface contradictions rather than optimize them away.

## 13. Deduplication by real-world event
Multiple files, conversations, shards and receipts may describe one underlying event. Deduplicate at the EVENT layer while retaining every source edge.

Do NOT deduplicate merely because text is semantically similar. Two identical $25 purchases on different dates may be separate real-world events.

## 14. Temporal truth
Preserve several distinct timestamps:

source_created_at
source_modified_at
event_occurred_at
payment_at
record_discovered_at
shard_created_at
claim_corrected_at

Never substitute shard creation time for the historical event time. This is particularly important while backfilling old files.

## 15. IRS export layer
Eventually generate human-reviewable annual packages such as:

annual business chronology
income ledger
expense ledger
payer summary
vendor summary
project/client summary
business-purpose index
source evidence index
uncertain-items queue
conflict queue
missing-document queue
correction ledger

Every row should be traceable back to its source records.

## 16. Query layer
NouGen should eventually answer questions such as:

Show every source supporting this expense.
Why was this purchase classified as business related?
What work was performed during January 2026?
Which clients paid me in March?
Show payments with no associated invoice.
Show expenses with weak business-purpose evidence.
Show projects with deliverables but no detected payment.
Show payments with no detected work product.
Show business events supported by three or more independent source types.
Show contradictions between historical shards and original files.
Show everything that remains inferred rather than verified.

## 17. Evidence strength scoring
Consider an evidence score composed of independent dimensions rather than one opaque confidence score:

source_quality
source_independence
temporal_proximity
identity_match
amount_match
project_match
corroboration_count
contradiction_count

Do not allow ten derivative records copied from the same original source to masquerade as ten independent corroborations.

## 18. Human review queue
High-risk classifications should require review, especially:

mixed personal/business expenses
large expenses
cash transactions
ambiguous payer identity
uncertain reimbursements
possible duplicate deductions
uncertain travel purpose
conflicting transaction amounts
records where AI inference supplies most of the business-purpose link

NouGen should make review efficient rather than pretending review is unnecessary.

## 19. Separate evidence from tax conclusions
NouGen should establish facts and organize substantiation. Tax eligibility is a separate reasoning layer. A documented expense is not automatically deductible merely because the business purpose is known.

Architecture should therefore distinguish:

EVIDENCE FACT
BUSINESS CLASSIFICATION
TAX TREATMENT

This makes it possible to update tax logic without rewriting historical evidence.

## 20. The final product
The target is not: 'AI says Dave worked.'

The target is:

'Here are the original contemporaneous records. Here are their integrity fingerprints and timestamps. Here is the business event reconstructed from them. Here is the work performed. Here is why the event was business related. Here are the expenses connected to it. Here is the payer and income connected to it. Here are the resulting deliverables. Here are any conflicts, corrections, unknowns and human-review flags. Click any conclusion and walk backward to its evidence.'

That is the desired NouGen truth architecture.

## Done when
A future fleet lane can select any material business event, expense, income item, payer, client, or work period and traverse backward from synthesis to the original supporting records without relying on an unsupported AI-generated narrative. Unknowns remain explicit, corrections remain append-only, contradictions remain visible, and source evidence remains distinct from tax classification.
