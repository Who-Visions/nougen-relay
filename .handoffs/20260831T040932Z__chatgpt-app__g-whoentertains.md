# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Connector sees shard gateway down while MCP and relay remain up; restore shard recall path without regressing quiet-box benchmark
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T04:09:32.020Z

---
User issued `Relay the shards` at 2026-08-31 ~00:08 ET. Connector check immediately returned: `mcp_up=true`, `configured=true`, but `up=false`, `health_up=false` for the shard gateway. Relay itself is healthy and the latest completed handoff reports the quiet-box recall bench PASS at main 4105142: retrieve p95 3.86s, federated p95 5.69s, accuracy 1.0 on both lanes, after duplicate daemons were culled. Treat this as a fresh regression or reachability fault after the successful benchmark, not evidence that the benchmark was wrong.

ASK:
1. Probe shard gateway health and blade reachability from the connector path.
2. Verify whether this is process death, routing/tunnel failure, health endpoint failure, or partial gateway exposure.
3. Preserve the proven quiet-box baseline while restoring connector recall.
4. Once restored, run a small recall canary and confirm shards_status reports healthy.
5. Capture the root cause and remediation as a durable shard.

DONE WHEN: connector `shards_status` is healthy, one semantic recall succeeds, and the regression plus fix are sharded with provenance.
