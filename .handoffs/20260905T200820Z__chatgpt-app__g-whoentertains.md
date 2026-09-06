# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix shard chronology by separating source dates from infrastructure provenance
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T20:08:20.020Z

---
Dave identified a recurring provenance bug: dates embedded in ingested artifacts, programs, documents, articles, repos, or records are being promoted into the shard's primary timestamp, making infrastructure history appear older than it is. Concrete live evidence: shards_coverage reported earliest grid span 2025-11-30, while shards_window for 2025-11 returned Phoebus engram articles dated 2025-11-11 through 2025-11-21. Those are article/source dates, not proof Phoebus or NouGen infrastructure existed then. Implement explicit provenance clocks/fields and chronology rules: source_document_date, artifact_fs_or_repo_date, machine_session_work_date, shard_capture_date, migration_backfill_date, replica_serving_node, and confidence/evidence. For machine origin archaeology, machine_session_work_date must outrank dates merely mentioned or carried by source content. Legitimate older business/personal records, such as 2019-2020 IRS/tax repo material, remain historical source data but must never backdate NouGen machine origins. Re-audit Oct-Dec 2025 genesis candidates under this rule. Done when earliest-machine queries cannot be contaminated by embedded source dates and return provenance-labeled evidence.
