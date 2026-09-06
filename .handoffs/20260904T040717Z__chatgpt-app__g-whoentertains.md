# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build Hugging Face encrypted shard write fallback
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T04:07:17.228Z

---
## Situation
Blade/shard gateway can be intentionally offline or return 502 while relay remains healthy. Today that meant canon could be relayed but `shards_capture` could not persist immediately. We need an HF fallback lane that preserves writes without creating a second source of truth.

## Architecture decision
Build **HF Write Spool**, not a second live shard DB.

Primary path remains `shards.nougenai.com/mcp` -> Blade shard gateway.
On retryable shard write failure, front door serializes the original write into a canonical envelope, encrypts it, and sends it to a tiny HF Space endpoint. The Space durably stores one immutable encrypted object per event in a private HF dataset repo (free-first design). When Blade returns, a drainer replays pending events through the normal shard write API, verifies dedupe/idempotency, then records an ACK marker. NouGen remains single-authority; HF is only durable cargo storage.

## Current HF grounding, 2026-09-04
HF Inference Providers exposes `https://router.huggingface.co/v1`, OpenAI-compatible Responses API, provider routing policies (`:fastest`, `:cheapest`, `:preferred`) and automatic provider failover. HF Spaces local disk is ephemeral. For durable Space data HF recommends attached Storage Buckets; private Hub repos are also durable and writable through `huggingface_hub`. Fine-grained tokens should be used in production and scoped tightly.

## Failover policy
Automatically spool only retryable infrastructure failures:
- connect/read timeout after bounded retry
- HTTP 502, 503, 504
- optionally 429 after local retry budget exhausted
Do NOT spool malformed/auth failures (400/401/403/404/409 semantics should be handled explicitly).

## Operation policy
Automatic HF spool:
- `shards_capture`
- `shards_amend`
Optional/manual queue after review:
- `shards_retract`
Never queue:
- `shards_forget` (irreversible)
- `vault_put` or any secret-bearing operation
- arbitrary MCP calls

## Event envelope v1
```json
{
  "schema": "nougen.shard-spool.v1",
  "event_id": "sha256(canonical_request)",
  "idempotency_key": "caller supplied or event_id",
  "operation": "shards_capture|shards_amend",
  "created_utc": "...",
  "lane": "chatgpt-app",
  "fleet_key_fingerprint": "non-secret fingerprint",
  "target": "primary-shards",
  "payload_ciphertext": "base64(AES-256-GCM(...))",
  "nonce": "...",
  "aad_hash": "...",
  "attempt": 0,
  "status": "pending"
}
```

## Security
- Encrypt payload BEFORE sending to HF. HF must not need the plaintext shard content.
- AES-256-GCM envelope key stays in NouGen Keymaker/front-door + Blade drainer, never in the HF repo.
- HF Space receives only ciphertext + minimal routing metadata.
- Space auth with a dedicated fine-grained token. Repo token scoped only to the private spool dataset.
- One token per app/lane where practical.
- HMAC or signed request from NouGen front door to Space to stop arbitrary queue injection.
- Never log plaintext payloads or bearer tokens.

## Durable free-first backing
Private dataset repo, e.g. `nougenai/NouGenShardSpool-private`.
Store each pending event as its own immutable object:
`pending/YYYY/MM/DD/<event_id>.json`
Avoid a shared mutable `queue.json` so concurrent callers cannot stomp each other.
After successful replay create:
`acked/YYYY/MM/DD/<event_id>.json`
Do not delete pending immediately; retention/GC can clean old acked pairs later and preserves audit history.

For higher scale later, swap the repository backend for an HF Storage Bucket mounted read-write in the Space. Same envelope and replay contract.

## Replay/drain rules
1. Blade/gateway health becomes green.
2. Drainer lists pending objects without ACK markers.
3. Verify signature/schema/hash.
4. Decrypt locally on trusted NouGen node.
5. Replay through the ordinary shard API, never write DB internals directly.
6. Existing shard dedupe makes exact `shards_capture` replays safe.
7. For amendments include original `shard_id`, `db_index`, and `confirm_title`; on mismatch quarantine rather than guessing.
8. Write ACK object containing resulting shard ref/db index and primary response hash.
9. Emit relay event summarizing drain count, quarantines, duplicates, and errors.

## Required front-door response semantics
If primary write succeeds: normal response.
If primary fails but HF spool succeeds: return success-like durability receipt explicitly naming state `queued_fallback`, plus event_id. Do NOT claim `captured=true` yet.
If both primary and spool fail: hard failure and relay emergency payload.

Example:
```json
{
  "durable": true,
  "captured": false,
  "queued_fallback": true,
  "event_id": "...",
  "backend": "hf-spool",
  "replay_required": true
}
```

## Implementation modules
Suggested:
- `fallback/envelope.py` canonicalization, hash, AES-GCM
- `fallback/hf_spool_client.py` enqueue + receipt verification
- `fallback/retry_policy.py`
- `fallback/drain.py`
- HF Space: `POST /spool`, `GET /health`, optionally `HEAD /spool/{event_id}`
- tests: outage simulation, duplicate replay, corrupted ciphertext, bad HMAC, amendment identity mismatch, Blade recovery mid-drain, concurrent writers

## Acceptance tests
A. Blade 502 -> HF event appears durably, caller gets `queued_fallback` receipt.
B. Blade healthy -> no HF write.
C. Same failed request twice -> one event identity / safe duplicate outcome.
D. Blade returns -> replay creates exactly one shard and ACK.
E. Tampered HF payload -> quarantine, never replay.
F. `shards_forget` never enters spool.
G. secret/vault operations never enter spool.
H. Space restart does not lose queued writes.
I. If HF itself is down, relay captures emergency handoff and caller receives truthful hard failure.

## Done when
End-to-end outage test proves: shut Blade/shard gateway off, call `shards_capture`, receive durable HF fallback receipt; restart Blade, drain queue; normal shard recall finds the captured content; queue has ACK provenance; no plaintext shard content exists in HF storage.
