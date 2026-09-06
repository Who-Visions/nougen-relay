# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Name and implement NouGen temporal shard capture dam
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T04:08:03.071Z

---
Refinement of HF fallback architecture: treat it as a **temporal shard capture dam** between the front door and the primary shard reservoirs.

Canonical terms:
- **Reservoirs** = primary NouGen shard databases / federated stores. They remain authoritative.
- **Dam** = encrypted durable temporary write spool on Hugging Face. It never answers recall as canonical truth.
- **Spillway** = replay/drain worker that releases queued shard events back into the reservoirs through the normal shard API after health returns.
- **Gate** = retry/failover policy deciding when a failed primary write is diverted into the dam.
- **Gauge** = health/backpressure metrics: queued count, oldest event age, bytes, retry count, quarantine count, drain rate.
- **Silt/quarantine** = malformed, tampered, identity-mismatched, or permanently failing events held for review rather than replayed blindly.

State machine:
PRIMARY_ATTEMPT ->
  success => RESERVOIR_COMMITTED
  retryable 502/503/504/timeout => SEAL_EVENT -> DAM_PENDING
  nonretryable auth/schema/identity error => FAIL/QUARANTINE, do not dam automatically

DAM_PENDING -> when reservoir health green -> SPILLWAY_REPLAY ->
  primary accepts/dedupes => DAM_ACKED
  transient error => DAM_PENDING with bounded backoff
  identity mismatch/tamper => SILT_QUARANTINE

Core invariant: the dam preserves **intent**, not truth. An event queued in HF is durable but not yet a shard. Front door receipt must say `queued_fallback=true`, `captured=false` until replay ACKs from the primary reservoir.

Suggested receipt:
```json
{
  "durable": true,
  "captured": false,
  "queued_fallback": true,
  "dam": "hf",
  "event_id": "sha256:...",
  "state": "DAM_PENDING",
  "replay_required": true
}
```

HF implementation grounding: Space local disk is ephemeral, so do not store the dam queue only on Space filesystem. Use a private Hub dataset repo with immutable per-event encrypted objects for free-first persistence, or an attached HF Storage Bucket for a higher-scale version. Hugging Face documents Storage Buckets as the recommended persistent volume for Spaces; `huggingface_hub` supports file uploads to dataset repos; production auth should use narrowly scoped fine-grained tokens.

Security: AES-256-GCM encrypt before HF, per-event nonce, AAD binds event_id/op/lane/time; HMAC/sign ingress; no plaintext shard body in HF logs/repo; no secret/vault ops in dam; never queue `shards_forget`; amendments require shard_id+db_index+confirm_title and quarantine on mismatch.

Implementation should expose operator semantics such as `dam_status`, `dam_drain`, `dam_peek` (metadata only), and optionally `dam_quarantine`, while ordinary users only see truthful fallback receipts. Auto-drain resumes when primary health is stable for N consecutive probes, not merely one green ping, to avoid flap storms.

Acceptance test metaphorically proves: close reservoir intake, submit shard, event accumulates behind dam; restart intake, spillway releases it once, primary dedupe prevents doubles, ACK closes the event, recall finds the shard afterward.
