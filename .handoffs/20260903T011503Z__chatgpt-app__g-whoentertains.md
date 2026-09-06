# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Rewind stale relay legs and recursively verify closure with evidence
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T01:15:03.365Z

---
Dave wants relay archaeology now that live continuity works. Current connector read shows 20 open legs, including several whose goal text already says CLOSED/SHIPPED and overlapping propagation notes. Do not bulk-ack blindly. Build an evidence-based rewind pass: for each open leg, read its body and compare against later shards, commits/tests, live probes, superseding legs and active claims. Classify: truly open, closed-with-evidence, superseded, duplicate, blocked, or needs-owner. Ack/close only when evidence proves the requested work landed; include the evidence reference in the ack note. Preserve history and do not delete old legs. Prioritize oldest and confusing CLOSED/SHIPPED-but-open legs first, then Codex/HF/bridge leftovers. Produce a compact census before/after and shard the cleanup doctrine so agents stop treating bookkeeping debt as active work.
