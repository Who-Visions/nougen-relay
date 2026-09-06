# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build secure Shard Transport Protocol between NouGen nodes
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T00:34:29.303Z

---
Dave identified a missing grid primitive: **transport shards securely from one enrolled node to another**.

This should NOT be treated as generic file copy or database replication. Build it as a provenance preserving, authenticated shard protocol using the trust laws already in the grid.

## Existing laws to reuse
1. **Provenance outranks transport possession.** A socket path, bearer token, LAN position, valid wire schema, or ability to deliver a packet proves transport access only. It does not grant fleet trust.
2. **Owner origin signing already exists across Phoebus and Blade.** Reuse the canonical byte/signature contract instead of inventing a parallel signature format.
3. **Shard history is append only.** Amendments and retractions must survive transport as history, not be flattened into rewritten current text.
4. **Secrets are not shards.** Keymaker credentials must never be copied through shard transport.

## Target primitive
Implement a first class **Shard Transport Protocol** supporting at least:

- `COPY`: destination receives an authenticated portable copy, source remains authoritative.
- `SYNC`: destination converges missing shard state/history idempotently.
- `MOVE`: only after destination verifies and ACKs may source side perform any explicit retirement/tombstone step. Never delete first.

## Proposed signed envelope
```json
{
  "transport_version": "ngs-shard-transport/1",
  "transfer_id": "uuid-or-content-addressed-id",
  "mode": "COPY|SYNC|MOVE",
  "shard_ref": "shard:937@db2",
  "source_node": "blade",
  "destination_node": "phoebus",
  "source_db_index": 2,
  "source_shard_id": 937,
  "content_digest": "sha256:...",
  "provenance_digest": "sha256:...",
  "correction_state": "active|amended|retracted",
  "captured_at": "...",
  "sent_at": "...",
  "nonce": "...",
  "sequence": 123,
  "ttl_seconds": 300,
  "signer_id": "...",
  "signature": "..."
}
```

Canonicalize immutable fields, sign with the existing owner origin signing contract, then encrypt payload bytes to the destination node. Prefer destination bound encryption or an authenticated session key derived through enrolled node identity. Avoid a fleet wide shared decrypt key.

## Receiver gates
Receiver MUST reject before import when any gate fails:

1. destination binding mismatch
2. source node not enrolled or signer unauthorized
3. signature invalid
4. content/provenance digest mismatch
5. nonce already seen
6. sequence replay/rollback
7. TTL expired
8. malformed correction lineage
9. shard contains fields classified as vault secrets/credentials
10. transfer conflicts with an existing shard identity in a way that would require silent rewrite

## Idempotency
A retry must be safe. Deduplicate on stable `transfer_id` plus content/provenance digest. Same transfer repeated = ACK existing result. Same transfer_id with different digest = hard security failure.

## Provenance model
Destination must retain both original provenance and transport provenance, e.g. original capture node/time/source plus imported_by/imported_at/transfer_id. Do not make the destination appear to have originated the shard.

## Correction lineage
Transport the shard plus amendment/retraction lineage in deterministic order, or transport a Merkle style manifest covering the history. Never collapse amendments into a rewritten body if that destroys witness history.

## ACK contract
ACK should itself be signed and include transfer_id, destination node, imported shard ref, verified content digest, result, and timestamp. MOVE mode requires this ACK before source retirement logic is allowed.

## Audit
Every attempt emits an append only audit event: sender, receiver, refs, digests, mode, timestamps, verification result, rejection reason, ACK id. No secret values.

## Suggested CLI/MCP surface
```text
shards_transport_send(ref, destination, mode=COPY)
shards_transport_receive(...internal...)
shards_transport_status(transfer_id)
shards_transport_history(ref|transfer_id)
shards_transport_sync(destination, selector/...)
```

Consider chunked manifests for bulk transfers, but keep each shard independently verifiable. Future transport should work Blade <-> Phoebus <-> Codex <-> AGY <-> Space nodes without collapsing trust boundaries.

## Tests required
- happy path COPY
- retry/idempotency
- destination mismatch
- forged signer
- payload modified after signing
- replayed nonce
- sequence rollback
- expired TTL
- same transfer_id/different digest
- amendment lineage preserved
- retracted shard preserved as retracted
- MOVE cannot retire source before verified signed ACK
- credential leakage classifier blocks transfer
- source offline after send but before ACK
- destination crash after import but before ACK, retry converges safely

**Done when:** Blade and Phoebus can exchange a real nonsecret test shard both directions, independently verify signatures and digests, replay attempts fail, duplicate retries are idempotent, provenance remains intact, and the transfer produces signed ACK plus audit history.
