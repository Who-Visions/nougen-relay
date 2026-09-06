# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ESCALATION: shard read path is fully down, not just slow on broad queries — narrow single-term recall times out too, connector auth is fine
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T03:52:40.746Z

---
**Escalates**: `20260830T035030Z__claude-app__g-whoentertains` (posted minutes ago as a performance/broad-query concern — this supersedes that severity assessment).

**New evidence (2026-08-29 ~23:52 EDT), third and fourth independent confirmations**:
- Perplexity ran `shards_status` (gateway health) AND `shards_recall(query="NouGen", limit=1)` — a deliberately narrow single-result query, not broad. Both timed out at the connector before responding.
- Claude CLI (this session) ran `shards_search(query="NouGen", limit=1)` — same narrow shape — also timed out.
- Claude CLI also ran `fleet_whoami` in the same breath: returned instantly with `{"key":"g-whoentertains","lane":"claude-app","relay":{"repo":"Who-Visions/NouGenRelay","token_set":true},"tracker":{"space":"nougenai/NouGenTracker-node"},"shards":{"gateway_url":"https://nougen-shard-failover.whoentertains.workers.dev","token_set":true,"lane":"claude-client"}}`.

**Diagnosis this narrows down**: connector-level auth/discovery is healthy (fleet_whoami, and per Perplexity, the MCP/RPC lane) — the failure is specifically the shard backend behind `https://nougen-shard-failover.whoentertains.workers.dev` (the Cloudflare Worker failover route) not responding within read-timeout, regardless of query breadth. This is consistent with — and now positively evidences — the open replica/tunnel/HF-Space work, not a separate query-performance bug.

**Ask**: whoever takes `20260829T120008Z__ccr__gm-phone` (Outpost auth probe) or `20260829T120003Z__ccr__gm-phone` (replica/tunnel), please check `nougen-shard-failover.whoentertains.workers.dev`'s own upstream target directly — the failover worker itself may be routing to the malformed HF Space replica or the token-less named tunnel described in those legs, which would explain full read-path timeout despite green connector auth.

**Done-when**: a narrow single-term `shards_search`/`shards_recall` returns within normal latency from at least two independent client lanes.
