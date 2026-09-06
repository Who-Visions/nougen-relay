# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Fix connector lane identity as ledger provenance, preserve working data path
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T04:32:27.172Z

---
Live 3-connector test is functionally green: NGS v2, NouGenShards, and NouGenAi all passed shard health, real recall, tracker reads, and relay reads with parity. Remaining identity mismatch should be treated as a LEDGER/PROVENANCE defect, not merely cosmetic. NGS v2 identifies as chatgpt-app, while NouGenShards and NouGenAi currently identify as claude-app / claude-client. Wrong lane/provider labels can contaminate historical attribution, token accounting, provider cost attribution, audit trails, debugging chronology, and agent work provenance even when runtime behavior succeeds.

FIX PRINCIPLE: do not disturb the currently working shard/relay/tracker data path. Correct identity attribution independently. Provider/client identity should resolve accurately behind the canonical public MCP ingress. No new public URLs as a workaround.

DONE WHEN:
1. Each connector reports the actual invoking provider/client lane.
2. Tracker and relay writes inherit that correct identity.
3. Existing shard recall, tracker reads, relay reads, and health remain green.
4. Canonical ingress remains shards.nougenai.com/mcp for external providers.
5. Regression test verifies functional parity plus correct ledger attribution across all connector surfaces.

Mental model: freeway is working; license plates are wrong. Fix the plates without rebuilding the freeway.
