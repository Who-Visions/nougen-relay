# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Implement Shard Rail: adaptive 1-to-1M shard transport with luggage-aware manifests
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T00:57:41.868Z

---
Dave's requirement: shard transport must scale intelligently from 1 shard to 1,000,000. Use the rail model literally: shards are passengers, optional sidecars are luggage/cargo, oversized payloads are freight that may travel separately but remain bound to the passenger manifest.

Architecture target:

1. Identity plane
Each shard keeps a stable logical identity independent of transport packaging. Never make batch/wagon IDs the shard identity.

2. Per-shard manifest
Carry small canonical metadata inline: shard id/ref, origin, timestamps, correction/amendment state, priority, destination policy, content digest, required luggage refs, optional luggage refs, dependency refs, and total byte estimate. Sign provenance using the existing owner-origin contract.

3. Luggage classes
AUTO classify by measured payload, not count:
* inline: tiny content/metadata rides with manifest
* sidecar: medium embeddings/index payloads/attachments travel as adjacent chunks
* freight: oversized blobs split into independently verifiable resumable chunks
A shard may have zero, one, or many luggage objects.

4. Content-addressed cargo
Chunk large luggage and address chunks by digest. Deduplicate chunks already present at destination. Do not resend identical attachment/embedding/blob bytes across shards. Preserve logical refs so the destination can reconstruct shard state without rewriting identity.

5. Train hierarchy
Single shard -> direct carriage.
Small cohort -> microbatch.
Large cohort -> wagon stream.
Huge cohort -> consist of bounded wagons with checkpoints.
Never build a million-shard monolith in RAM. Stream manifests and cargo through bounded windows.

6. Weight-aware scheduler
The scheduling unit is transport weight, not shard count. Inputs: manifest bytes, luggage bytes, luggage fanout, dependency depth, destination free capacity, observed RTT/throughput, retry cost, priority, and current backpressure. A million tiny shards can share wagons while one giant shard may get dedicated freight lanes.

7. Control plane / data plane split
Control plane stays tiny: manifest, policy, routing, lease, ACK/NACK, checkpoint, provenance.
Data plane carries actual chunk bytes. Giant cargo must never bloat relay/MCP/control messages.

8. Integrity tree
Each luggage chunk gets its own digest. Each shard manifest commits to its luggage refs. Each wagon gets an aggregate Merkle-style root over ordered manifest entries. Destination can prove a missing/corrupt shard or chunk without revalidating/retransmitting the whole train.

9. Resumability and idempotence
Borrow the strongest current patterns from S3 multipart/tus/Kafka: independently retry failed parts, preserve offsets/checkpoints, deduplicate retries with stable transfer IDs and sequence numbers, and finalize only after destination state + checkpoint are durably committed. Exactly-once claims must be destination-coordinated, not transport marketing.

10. Adaptive flow
Use bounded concurrency and dynamic wagon size. Target a byte budget and latency budget, not N shards. Shrink under memory pressure/timeouts; grow when ACK latency and destination queue depth are healthy. Apply weighted fair scheduling so one piano-sized shard cannot starve thousands of lightweight shards.

11. Transport lanes
For WAN, prefer multiplexed streams such as HTTP/3/QUIC where practical so unrelated shard/cargo streams do not all block behind one loss event. For structured bulk records, Arrow Flight/gRPC is a useful reference because it streams record batches and avoids excess copies. Keep the protocol pluggable rather than coupling shard identity to one wire transport.

12. Completion states
Manifest accepted != shard complete.
Use states such as MANIFEST_ACCEPTED, CARGO_PENDING, VERIFIED, INDEX_PENDING, READY, ACKED. A shard is READY only when every required luggage object and integrity proof is satisfied. Optional cargo may continue later if policy allows.

13. Destination intelligence
Before shipping cargo, destination returns a HAVE/WANT bitmap or digest set for manifests/chunks it already has. Source sends only the delta. This is crucial for 1M-shard replication and repeated sync.

14. Failure isolation
Retry a chunk, then a shard, then a wagon. Never restart the train unless the root/control contract itself is invalid. Checkpoint every bounded wagon.

15. Observability
Metrics must expose shards/s AND bytes/s, inline/sidecar/freight ratios, dedup bytes saved, retries by chunk/shard/wagon, destination queue depth, manifest latency, cargo latency, verify latency, memory high-water, completion lag, and transport amplification ratio.

Current external reference points checked Sep 3 2026:
* AWS S3 multipart independently uploads/retries parts and validates per-part/full-object checksums; AWS recommends multipart for large objects. https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html
* tus protocol supports offset-based resumability, chunk checksums, and concatenating parallel partial uploads. https://tus.io/protocols/resumable-upload
* Apache Arrow Flight streams record batches over gRPC and is designed to reduce unnecessary copies. https://arrow.apache.org/docs/format/Flight.html
* HTTP/3 over QUIC provides stream multiplexing and per-stream flow control. RFC 9114.
* Kafka's strongest semantics rely on idempotent sequence-aware producers and atomic cooperation with destination state. Do not claim exactly-once merely because transport retries are deduped.

Build order:
A. Define canonical ShardManifest, LuggageRef, WagonManifest, TransferCheckpoint schemas.
B. Implement size/classification estimator and inline/sidecar/freight policy.
C. Implement content-addressed chunk store + HAVE/WANT delta negotiation.
D. Implement bounded wagon iterator, never full-million materialization.
E. Implement idempotent/resumable sender/receiver and per-wagon checkpoints.
F. Add adaptive byte-budget scheduler and backpressure.
G. Add Merkle aggregate verification and destination readiness state machine.
H. Benchmark 1, 100, 10k, 1M synthetic shards with mixed luggage distributions, including one extreme oversized shard amid tiny shards.

Done when one API can receive 1 or 1,000,000 logical shard refs and automatically choose packing/routing without caller micromanagement, memory remains bounded, interrupted transfers resume near the failure point, duplicate cargo is not resent, and every READY shard proves manifest plus required luggage integrity.
