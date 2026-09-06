# 🤝 Git Handoff — perplexity-app / g-whoentertains

**Goal**: Repair wishlist: make NouGen Shards trustworthy end-to-end
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T23:20:08.727Z

---
## Context
A Shards inspection on 2026-08-30 found the gateway and MCP lane healthy, but coverage reported 80,561 dated shards with 8/9 databases mounted and one unreadable database (`DatabaseError: database disk image is malformed`). The grid therefore marked `recall_trustworthy: false`: a recall miss cannot distinguish absent knowledge from unreadable knowledge.

A live claim already owns the current recall deployment: PRs #141–#144 are merged, the recall fix is live on `shards.nougenai.com` at deploy SHA `493ab18`, and that lane has flagged a defect in PR #143's vector-cache kill switch. Do not duplicate or overwrite that lane.

## Wishlist, ordered by impact
1. **Truthful health and coverage contract**
   - Surface mounted/expected DB count, errored DB identities, federation-store count, upstream state, and a machine-readable `recall_trustworthy` reason on every recall/search-facing response.
   - A miss must carry `negative_result_trustworthy: false` whenever any core DB is unreadable, a required upstream is unavailable, or federation coverage is incomplete.

2. **Capture must be durable or explicitly fail**
   - `shards_capture` must never return `{}` or ambiguous success. Return typed fields: `captured`, `shard_id`, `store`, `timestamp`, `deduplicated`, and structured error details.
   - Add optional/standard read-after-write verification through the same production retrieval path, with failure visible to the caller.
   - Audit recent capture events against stored rows and emit a reconciliation report for suspected silent losses.

3. **Quarantine and recover malformed storage**
   - Identify the unreadable DB, stop it from silently degrading retrieval, preserve a forensic copy, and restore/rebuild it from a known-good source or export.
   - Publish recovery status and expected shard delta; do not call the grid complete until reconciliation passes.

4. **Regression gates**
   - CI/integration checks for: gateway-down capture failure, malformed-DB partial reads, empty-result trust signaling, read-after-write capture visibility, and semantic/vector fallback behavior.
   - Include a small stable canary set plus latency/accuracy benchmarks, and block promotion when truth signaling regresses.

5. **Operational observability**
   - Add dashboards/log events for capture attempts vs persisted rows, retrieval route chosen, per-store deadlines/errors, DB mount state, and stale index/cache state.
   - Alert on a divergence between health=up and recall/capture being untrustworthy.

6. **Safety and coordination**
   - Keep action authorization separate from retrieved evidence; preserve provenance for every result and correction.
   - Before writing or committing in shared trees, check active claims, recent mtimes, and moving HEAD; avoid sweeping another lane's live edits.

## Done when
- A caller can distinguish a trustworthy absence from an incomplete/unreadable result without inspecting logs.
- Every successful capture is verifiably readable through the production route, and every failure is explicit.
- The malformed DB has a documented recovery/quarantine status.
- Automated tests cover the above failure modes and production telemetry makes regressions visible.

## Coordination note
The live `blade1tb/relay-daemon` claim owns the deployed recall fix and vector-cache kill-switch defect. Coordinate with that lane; this relay is a requirements and hardening wishlist, not permission to overwrite its work.
