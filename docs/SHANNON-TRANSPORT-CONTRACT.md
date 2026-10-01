# Shannon transport contract for NouGenRelay

This contract describes what the Git-backed relay channel can guarantee. A
reliable packet is not proof that its claims are true or that its requested
action is safe.

| Shannon layer | NouGenRelay realization | Contract |
|---|---|---|
| Source | Agent or operator creating a handoff | Supplies goal, body, identity, time, and any evidence/provenance. The transport does not authenticate the truth of those claims. |
| Transmitter / source coding | `relay create`; one JSON envelope and Markdown body per leg | Identity is carried by the UTC/machine/lane filename and, in newer records, the embedded `id`. Older records without `id` remain readable by filename. Keep bodies sufficient for the receiver to reconstruct the task; token budgets belong at this boundary. |
| Channel | Git commits, fetch, push, and the registry projection | Git object hashes detect corrupted objects. A local write does not imply remote delivery. A failed or delayed publish leaves the sender's local record available for a later publish; the receiver must poll again. Concurrent writers use distinct leg files. |
| Noise / faults | Missing publish, duplicate fetch/event, replica reordering, malformed or truncated JSON, stale projections, and old/new optional fields | Missing delivery stays pending until a receiver can observe it. Merge deduplicates event identities, retains the published remote trail's order, and appends local-only events. Malformed records are skipped independently. Missing legacy fields use documented fallbacks; unknown fields are preserved. |
| Receiver / decoder | `relay open`, `_remote_handoffs`, JSON decoding, record identity and status helpers | The receiver reconstructs records from the fetched commit. A malformed record must not hide a valid neighbor. A decoded record keeps its identity and status semantics across supported schema generations. |
| Destination | Claim, execution, checkpoint, completion, or a human decision | Delivery/acknowledgment is not execution proof. A separate lifecycle and evidence closes actionable work. |

NouGenMsg, named pipes, and MCP are distinct channel adapters. Passing this
Git-backed conformance suite does not establish their ordering, retry, framing,
or schema behavior; each adapter needs its own boundary tests.

## Audit order

The published remote trail determines existing event positions. If A(t=10)
and B(t=20) are already published, a late C(t=15) appends as A,B,C. Equal or
future-skewed timestamps cannot move an existing entry or block a new one.
Timestamps are event metadata, not a global arrival sequence or proof of
causality. Opposite replica orders converge on event membership; they cannot
also converge on array positions while both original orders remain intact.
A globally identical causal order would require an explicit sequencing or
causal-reference protocol. A sorted timeline may be a separate display view.

## Semantic layer

Keep source truth above transport reliability. Receivers still evaluate
provenance, meaning, relevance, temporal validity, and action utility. Shard
retrieval and semantic scoring are not substitutes for validating a relay's
source or its evidence.

The October 2026 arXiv cross-reference proposes memory and retrieval work above
this channel boundary: keep durable, provenance-bearing records; build a
bounded working projection for the current query; retrieve hierarchically and
stop when evidence is sufficient. It also suggests a future acceleration
channel for embeddings or model state alongside the human-readable audit
channel. These are architecture directions, not properties established by
this Git conformance suite; any accelerated representation must remain
reconstructable from the audit record. The references are [MemLife
(arXiv:2609.40195)](https://arxiv.org/abs/2609.40195), [VideoLoop
(arXiv:2609.38119)](https://arxiv.org/abs/2609.38119), [MemCodex
(arXiv:2609.39765)](https://arxiv.org/abs/2609.39765) (candidate pending
full-body validation), and [Beyond Tokens
(arXiv:2606.05711)](https://arxiv.org/abs/2606.05711).

## Conformance evidence

- `tests/test_two_machines.py::test_a_delayed_publish_is_delivered_on_the_receivers_next_poll`
  exercises temporary loss and recovery across two Git clones.
- `tests/test_two_machines.py::test_malformed_record_does_not_hide_a_legacy_schema_neighbor`
  checks receiver isolation, legacy identity/status fallback, and forward-field
  preservation.
- `tests/test_shannon_transport_faults.py::test_replica_event_union_converges_after_reordered_duplicate_delivery`
  runs the same reordered/duplicate fixture against the checkout and watcher
  merge paths.
- The same suite checks late arrivals, equal timestamps in opposite replica
  orders, and a future-skewed clock without changing published positions.
- Existing tests cover concurrent writes, duplicate-create idempotency,
  malformed handoff skipping, and stale terminal-state protection.
