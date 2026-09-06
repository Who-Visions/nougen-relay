# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Expose true per-machine origin dates and provenance clocks
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T20:05:28.830Z

---
Dave wants the fleet to fix temporal provenance so 'earliest memory from each machine' returns the machine's actual historical origin, not shard migration/ingestion dates. Likely target era is Oct-Nov-Dec 2025 around early Ai with Dav3 experimentation.

Implement and audit a provenance model with separate fields/clocks:

1. machine_origin_at = earliest defensible activity tied to that actual machine/node identity
2. event_occurred_at = when the remembered human/project event happened
3. artifact_created_at = original transcript/file/brain asset creation timestamp when available
4. shard_captured_at = current NouGen shard write time
5. migrated_at / backfilled_at = import/consolidation time
6. source_node_original = node/machine that originally produced or held the memory
7. source_node_serving = node currently answering the federated query / replica location
8. provenance_ref = transcript path, Antigravity brain path, handoff, git commit, file metadata, or other primary evidence
9. origin_confidence + exact_or_bounded = distinguish exact timestamps from inferred date windows

Rules:
* Never let migration or ingestion time masquerade as machine origin.
* Replicated source_node metadata is not proof of authorship.
* Earliest-memory queries should rank by original event/artifact provenance rather than capture timestamp.
* Reject synthetic load tests, imported news, generic arXiv/docs, migrated code debris, tracker/status rows unless explicitly requested.
* When exact origin cannot be proven, return an evidence-backed bound, e.g. 'active by 2025-11-26', rather than fabricate precision.

Audit Blade, WhoArt, Phoebus and any predecessor identities for surviving Oct-Dec 2025 evidence. Search Antigravity/Gemini brain histories, Claude session stores, git creation/commit history, old handoffs, filesystem creation metadata, agent memories, and pre-federation vaults. Build a per-machine origin ledger with earliest defensible artifact, date, provenance, and confidence.

Shard decision already captured as shard 22414@db5.

DONE WHEN: a fleet query can answer 'what is the earliest real memory from each machine?' with distinct origin/event/capture clocks, primary provenance, and no migration-date confusion.
