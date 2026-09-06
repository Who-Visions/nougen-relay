# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: NouGenLine full doctrine: sovereign, recoverable, provenance-first transport from 1 shard to 1M
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T01:18:14.309Z

---
# NouGenLine: sovereign transport fabric

## Canonical contrast
Shadow Dweller: Olympus Lines run under Syndicate Control.
NouGen: NouGen Lines run under sovereign control.

Sovereign control here does NOT mean opaque superuser lockdown. It means the human owner is the root authority over identity, routing, provenance, policy, retention, destination, and recovery. Agents/providers/nodes are workers and requesters, never sovereigns.

CRITICAL OWNER LAW: never repeat the prior failure where security hardening blocked Dave out of his own tools. Unknown/autonomous actors fail closed. The authenticated owner fails recoverable. Maintain an independent break-glass path, last-known-good policy rollback, explainable denial, local recovery, and canary rollout.

## Research-grounded architecture

### 1. Zero trust around resources and identities
NIST SP 800-207 says network location and ownership do not grant implicit trust. SP 800-207A moves policy toward application/service identities and cites SPIFFE-style identity infrastructure. NouGenLine should therefore authenticate the running node/workload, not merely LAN IP, hostname, repo presence, provider label, or bearer-token possession.
Refs: https://csrc.nist.gov/pubs/sp/800/207/final ; https://csrc.nist.gov/pubs/sp/800/207/a/final

### 2. Workload identity and attestation
SPIRE performs both node and workload attestation and issues SVIDs under a trust domain. Copy the pattern, not necessarily the implementation: Line Station identity + Line Workload identity + short-lived credentials. Measure the running process/checkout. Never authorize against a stale clone.
Ref: https://spiffe.io/docs/latest/spire-about/spire-concepts/

### 3. Provenance is inseparable from transport
SLSA 1.2 and in-toto formalize provenance/attestation around where, when, and how artifacts were produced. NouGen already has the stronger local rule: provenance over transport possession. A shard is trustworthy because origin, lineage, payload, correction state, authorization, and destination can be verified, not because bytes arrived.
Refs: https://slsa.dev/spec/v1.2/ ; https://in-toto.io/docs/specs/

### 4. Receiver-controlled pressure
RFC 9000 QUIC allows receiver-controlled limits per stream and across the whole connection. NouGenLine should use the same law at the application layer even if the wire transport is not always QUIC: destination advertises bytes, concurrency, memory, and wagon capacity. Sender MUST respect destination pressure.
Ref: https://www.rfc-editor.org/info/rfc9000/

### 5. Multipart and resumability
S3 multipart proves independent part upload/retry and part/full-object checksum validation. tus proves offset-based resume, per-chunk checksum, and concatenation of independently uploaded partials. Adopt the semantics for freight/luggage. A failed chunk does not restart a shard, wagon, or train.
Refs: https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html ; https://tus.io/protocols/resumable-upload

### 6. Difference transfer rather than brute force
The rsync algorithm identifies matching destination regions and sends only unmatched data, minimizing transfer across high-latency links. Generalize this into HAVE/WANT and Merkle inventory comparison across shard manifests and content-addressed luggage.
Ref: https://rsync.samba.org/tech_report/

### 7. Structured streaming
Arrow Flight organizes transfer around streams of record batches and reduces unnecessary copying. Useful reference for high-throughput wagon transport and metadata/data-plane separation.
Ref: https://arrow.apache.org/docs/format/Flight.html

## NouGenLine object grammar
Line = owner-rooted policy/trust domain
Run = requested transport operation
Train = logical transfer plan
Wagon = bounded schedulable batch
Passenger = shard
Luggage = linked dependency/sidecar
Freight = oversized luggage streamed separately
Station = enrolled node
Switch = routing/policy choice
Manifest = passenger + luggage + provenance commitment
Ticket = short-lived scoped transport capability
Conductor = local Line enforcement/scheduling agent
Signal = backpressure/pause/revoke/priority message

## One API, 1 to 1,000,000
transport(source, destination, shard_selector, mode=COPY)

The caller does not manually choose batching, chunk sizes, retry strategy, stream count, or cargo placement. `shard_selector` may identify one shard, a set, query, era, destiny closure, or snapshot up to millions.

## Transport weight, not shard count
Planner estimates each passenger across:
core bytes
metadata bytes
lineage depth
amendment/retraction history
attachment bytes
embedding bytes
derived index bytes
dependency fanout
sensitivity
priority
receiver cost
retry cost

A million tiny passengers may weigh less than one shard carrying massive media. Pack against byte/memory/latency/risk budgets.

## Passenger and luggage separation
Shard core record remains small and identity-stable.
Inline luggage: tiny metadata/content.
Sidecar luggage: medium embeddings/indexes/attachments.
Freight: oversized content, independently chunked and resumable.

One huge shard must never head-of-line block thousands of mice. Freight gets independent streams/queues.

## Content-addressed freight
Immutable luggage objects addressed by cryptographic digest.
Multiple shards referencing the same bytes transfer them once.
Huge objects: chunks + aggregate Merkle/root commitment.
Hash algorithm is versioned/hash-agile in manifest.

Mutable meaning lives in shard history/manifests, not mutation of content-addressed bytes.

## HAVE/WANT before shipping
Destination advertises inventory summary.
Use hierarchy:
inventory root
partition/range/time roots
compact probabilistic membership filter for candidate suppression
exact WANT set for mismatches
Merkle range repair

Do not send one million literal IDs unless necessary. Any Bloom/Xor-filter false positive MUST be resolved by exact final completeness verification.

## Stable snapshot
A million-shard Run defines a snapshot watermark at planning start. New shards arriving during the run are excluded unless mode=FOLLOW. Never silently shift the source boundary while claiming snapshot completeness.

## Bounded streaming
Never materialize 1M passengers in RAM.
Iterate source snapshot, produce bounded wagons, checkpoint after each committed wagon.
Run journal includes:
run_id
snapshot watermark
planning cursor
policy epoch
wagons planned/committed
passengers ready/rejected/quarantined
bytes planned/sent/deduped
freight outstanding
checkpoint hash

Crash at passenger 583,922 resumes from proved checkpoint near that point.

## Effectively-once state
Do not promise magical exactly-once networking.
Use:
at-least-once delivery
stable transfer IDs
content addressing
deduplication
sequence/replay protection
idempotent destination import
atomic destination checkpoint

Result: retries are safe and committed shard state is effectively once.

## Destination state machine
PLANNED
MANIFEST_RECEIVED
AUTHORIZED
HAVE_WANT_RESOLVED
CARGO_PENDING
CARGO_COMPLETE
DIGEST_VERIFIED
LINEAGE_VERIFIED
COMMITTED
INDEX_PENDING
READY
ACKED

Also explicit: PAUSED, REVOKED, REJECTED, QUARANTINED.

Law: MANIFEST_RECEIVED != memory possession. READY/ACKED is the actual proof boundary.

## COPY, SYNC, MOVE
COPY: destination gains verified state, source remains.
SYNC: reconcile destination to selected snapshot/policy without destroying independent history.
MOVE: destination verified first, signed ACK second, source retirement only afterward under explicit owner policy.

MOVE is never delete-then-copy. Preserve append-only audit/tombstone/correction history.

## Sovereign policy
Owner Root Policy defines:
who can request vs execute transfers
eligible Stations
source/destination pairs
COPY/SYNC/MOVE permission
sensitivity route rules
physical trust zones
whether external relays may carry ciphertext
maximum weight/concurrency/bandwidth
retention and replication floor
attestation requirements
policy expiry/revoke

Provider identity never outranks owner policy.

## Scoped delegation
Owner does not manually approve every wagon. Issue short-lived non-amplifying capabilities scoped by:
subject workload
source
destination
selector
mode
max bytes/passengers
expiry
policy epoch
transform permissions

Delegate cannot mint broader authority than received.

## Owner anti-lockout constitution
1. Owner root credentials separate from ordinary runtime/MCP credentials.
2. Break-glass path exists and is owner-only.
3. Recovery route is independent of the component/policy being repaired.
4. Fail closed for autonomous actors, fail recoverable for owner.
5. Last Known Good policy snapshot is atomically rollbackable.
6. Security rollout is canary-first, never fleet-wide first.
7. Every denial has safe reason code and remediation path.
8. Local physical recovery exists on owned nodes when cloud/gateway unavailable.
9. Break-glass is audited append-only and expires automatically.
10. Models/providers cannot autonomously invoke break-glass.
11. CI asserts OWNER_CAN_DIAGNOSE, OWNER_CAN_VIEW_DENIAL_REASON, OWNER_CAN_ENTER_RECOVERY, OWNER_CAN_ROLLBACK_POLICY, OWNER_CAN_REISSUE_RUNTIME_CREDENTIALS, OWNER_CAN_RESTORE_TOOL_ACCESS.
12. No auth dependency may ship unless an independent recovery path is proven.

Design sentence: NouGen should be hostile to unauthorized control, not hostile to its owner.

Line metaphor: every autonomous passenger needs a ticket. Dave owns the station, the switches, and the emergency brake.

## Adaptive scheduler
Receiver advertises pressure. Conductor tunes:
byte budget per wagon
manifest count
concurrent streams
freight concurrency
priority weights
retry delay

Grow when ACK latency/queue/memory healthy. Shrink under pressure. Use weighted fair scheduling so control traffic and small high-priority shards remain responsive while freight moves.

## Security and integrity gates
Before Run: owner/policy valid, source/destination eligible, running workloads attested, destination capacity known.
Per manifest: signature, destination binding, policy epoch, digest, lineage/correction state, sensitivity route.
Per chunk: digest/proof, offset/range, replay/idempotency, byte budget.
Before READY: all required luggage, shard digest, correction lineage, atomic commit.
Before MOVE retirement: destination signed ACK + owner policy + replication floor.

## Benchmarks and adversarial suite
Test 1, 100, 10k, 1M passengers.
Distributions: all tiny; realistic mixed; one giant freight passenger among tiny passengers; repeated sync with 99% destination HAVE; deep lineage; many shared attachments; slow destination; packet loss; node restart; gateway restart; sender crash; receiver crash; policy epoch change mid-run.

Security tests: stolen runtime token; wrong workload; stale checkout; replay; route escalation; forged provenance; modified luggage; partial Merkle tree; destination lies about HAVE; policy revoked mid-run.

Owner recovery tests: all runtime tokens expired; policy denies every tool; attestation false-negative; gateway auth regression; one node isolated; bad policy canary; capability issuer down. In EVERY case prove authenticated owner can diagnose and recover without globally disabling security or deleting state.

## Metrics
passengers/s
bytes/s
manifest latency
freight throughput
READY latency
inline/sidecar/freight ratios
dedup bytes saved
HAVE ratio
retry rate by chunk/passenger/wagon
queue depth
memory high-water
policy denials by reason
quarantines
resume distance after fault
transport amplification ratio
owner-recovery test health

## Build order
A schemas: LineManifest, LuggageRef, WagonManifest, RunJournal, Capability, AttestationRef
B owner recovery + LKG policy FIRST, before stronger denial gates
C workload/station identity abstraction
D estimator/classifier
E content-addressed luggage/chunk store
F HAVE/WANT + inventory hierarchy
G bounded wagon iterator + durable checkpoints
H sender/receiver idempotency
I adaptive receiver-driven scheduler
J Merkle verification + READY state machine
K COPY/SYNC/MOVE semantics
L million-shard and adversarial benchmarks
M canary security rollout and recovery simulations

## Done when
One API accepts 1 or 1M shard refs. Memory stays bounded. Existing destination content is not resent. Oversized luggage cannot stall the fleet. Faults resume near the failure. READY proves passenger + required luggage + provenance integrity. Compromised actors cannot expand authority. And Dave cannot be permanently locked out of NouGen by a bad policy, expired credential, broken attestor, or transport failure.
