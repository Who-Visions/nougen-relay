# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Ship compact shard recall summary mode
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:46:31.139Z

---
Dave approved shipping the compact recall proposal from relay 20260903T004347Z__claude-app__g-whoentertains. Make shards_search and shards_recall return compact records by default: id, title, timestamp, tags, and a short preview. Keep an explicit full-body option for evidence-heavy work. Use a smaller default result count. Preserve provenance and existing relay/NouGenMsg behavior. Add tests for compact default, full-body override, and provenance preservation. Verify with a live connector smoke, then shard and relay the before/after payload evidence.
