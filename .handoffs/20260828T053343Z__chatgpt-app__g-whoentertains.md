# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix March temporal recall, held-back visibility, Rhea 500, and recall timeouts
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T05:33:43.270Z

---
## Reproduction from ChatGPT app lane, 2026-08-28

### Environment
- Auth key: `g-whoentertains`
- Lane: `chatgpt-app`
- Shard gateway: `https://shards.nougenai.com`
- `fleet_whoami`: relay configured, tracker configured, shard token configured.
- `shards_status`: `up:true`, `health_up:true`, `mcp_up:true`, `configured:true`.

## Failure chain

### 1. Rhea direct agent call fails
User asked: `Ask Rhea about March`.
A direct `ask_rhea` attempt failed with an HTTP 500 from the resident-agent path. The UI surfaced this as an internal server error rather than a structured Rhea reply. This means the connector is reachable, but Rhea's agent execution path is failing independently of base MCP health.

**Fix target:** instrument `/agent` or equivalent Rhea execution path so failures return structured diagnostics including failing stage: recall, Griot gather, tracker, relay, model backend, capture, timeout, or serialization. Preserve the brain/provider identity even on failure when known.

### 2. Bounded Griot query discovers 12 candidates but hides all 12
Call conceptually equivalent to:
`ask_griot(question="What happened in Dave's March 2026? Gather the important events, projects, decisions, failures, and turning points from that month only. Return provenance-marked shard evidence...", since="2026-03", until="2026-03")`

Observed response:
```json
{
  "shown": 0,
  "total": 12,
  "held_back": 12,
  "failures": [],
  "memories": [],
  "era_bounds": {"since":"2026-03","until":"2026-03"}
}
```

This is actually good temporal safety: the system refused to present memories that could not be proven inside the March window. However, it creates a debugging black box because the 12 candidate records are not inspectable.

**Required fix:** expose metadata for held-back candidates without treating them as evidence. Suggested response field:
```json
"held_back_memories": [
  {
    "id": 123,
    "db_index": 4,
    "source": "...",
    "title": "...",
    "excerpt": "...",
    "candidate_score": 0.82,
    "available_timestamps": {...},
    "temporal_basis": "ingest_time|source_created|source_modified|embedded_date|none",
    "reason_held": "no_provable_event_date_within_window",
    "correction_flags": ["amended"]
  }
]
```
The system must clearly label these as NON-EVIDENTIARY candidates. This preserves chronology guarantees while making temporal provenance repair possible.

### 3. Attempt to retrieve the 12 candidates via unbounded Griot timed out
Follow-up query explicitly asked Griot to return the 12 prior candidates even if dates were ambiguous. Result:
```json
{
  "shown": 0,
  "total": 0,
  "held_back": 0,
  "failures": [
    {"lane":"recall","error":"The operation was aborted due to timeout"}
  ],
  "memories": []
}
```

This means Griot currently depends on a recall arm that can block or abort the whole gather. The previous candidate set is also not addressable by a gather/session ID, so once the first response hides them, there is no deterministic way to inspect that exact candidate set.

**Fix targets:**
1. Griot gather should assign a `gather_id` and persist candidate IDs for a short TTL so a second call can request `inspect held_back for gather_id=X` without rerunning recall.
2. Each arm must have an independent timeout budget and partial-result behavior. A recall timeout must not erase successful search/window candidates.
3. Return `partial:true` plus per-arm timing and counts.
4. Add `retry_after` or diagnostic timing, not a generic aborted operation.

### 4. Raw shard retrieval also timed out while trying to expose March candidates
A direct/raw grid attempt for March candidate retrieval subsequently timed out as well. Base health remained up, so health status currently does not reflect query-path saturation or long-running retrieval failure.

**Fix target:** split health into at least:
- gateway process health
- MCP route health
- DB/search backend health
- semantic recall readiness
- queue depth / saturation
- last successful recall latency
A gateway can be `up:true` while recall is effectively unusable.

## Temporal provenance root issue
The bounded March query finding 12 semantically relevant candidates but holding every one strongly suggests the current records lack a trusted event/source creation timestamp that proves they belong to March 2026. Likely failure modes include:
- ingestion timestamp replacing original file/message creation time
- source creation timestamp never imported
- modification time being treated as chronology
- undated vault records with embedded March content but no normalized temporal field
- historical shards migrated without preserving origin metadata

### Recommended temporal schema
For every shard, keep separate immutable fields rather than one overloaded timestamp:
- `event_time` : when the remembered event actually happened, if known
- `source_created_at` : original source object's creation time
- `source_modified_at`
- `captured_at` : when NouGen ingested/captured the shard
- `amended_at[]`
- `time_confidence` : exact / inferred / coarse / unknown
- `time_source` : source_metadata / embedded_text / user_assertion / migration / capture_time
- `original_source_id` and stable provenance URI/path when available

Never backfill `event_time` from `captured_at` without explicitly marking it inferred/unknown.

## Query behavior desired
For `since=2026-03, until=2026-03`:
1. Filter on trusted `event_time` first.
2. If absent, allow trusted `source_created_at` depending on memory type.
3. If only month-level evidence exists, include with coarse confidence only if the month is provable.
4. If chronology is not provable, keep it held back, but expose candidate metadata and reason.
5. Do not silently substitute ingest date.

## Done when
- `ask_rhea("What happened in March 2026?")` returns a structured answer instead of HTTP 500.
- Griot March query either shows proven March memories OR shows its held-back candidate metadata.
- The exact 12-candidate set can be inspected without rerunning expensive semantic recall.
- Recall/search timeouts yield partial results and stage-level diagnostics.
- Health reports query-path degradation, not merely process liveness.
- Historical file/message migrations preserve original creation timestamps so March memories can be proven against March rather than August ingestion.

This should be treated as a temporal provenance + observability bug, not as evidence that March memory is empty.
