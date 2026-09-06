# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Separate backup timestamps from trusted event time for 2018 recovered shards
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T03:03:00.232Z

---
Deep grep finding: July 2018 currently has 27 nominal recovered shards, but strict bounded provenance audit showed 0 memories as proven 2018 events and held back 20 candidates. Raw records are WATCHTOWER_VAULT_BACKUP_RECOVERY from nougen_memories.db.bak-20260807. Several share nearly identical 2018-07-29T15:19:20 timestamps while containing clearly later material, including references to GitHub Spark, MCP Registry, Gemini Antigravity, Jules V2, Google I/O 2026, and explicit 2025/2026 language. Treat this as timestamp provenance contamination, not established 2018 history.

Fix: do not promote a recovered row or container timestamp directly into event_time_original/effective_timestamp. Separate record_timestamp, container_timestamp, recovery_timestamp, embedded_event_timestamp, and trusted_event_timestamp. Preserve the raw timestamp exactly, but trusted_event_timestamp must remain UNKNOWN unless event-level evidence supports it, such as EXIF, commit time, invoice/receipt/payment date, source-system message/calendar time, explicit embedded date, or independently corroborated original-file metadata.

Add temporal anomaly flags for backup recovery, anachronistic content, repeated collision-cluster timestamps, and unproven event time. Repeated microsecond-adjacent timestamps across unrelated recovered rows should strongly suggest migration/container timing rather than human activity.

Coverage should expose raw_source_span separately from trusted_event_span, and ideally raw_records vs trusted_events vs temporal_anomalies per month. The current 2018 records may remain visible as raw forensic provenance, but should not extend trusted historical coverage unless independently corroborated.

IRS implication: a recovered record can prove a record exists, but a backup/container timestamp does not prove when the represented business activity occurred. Keep evidence fact separate from temporal conclusion.

Tests: a nominal 2018 row containing 2026 content must not become trusted 2018 time; multiple unrelated rows with the same backup timestamp should be flagged as a collision cluster; a 2026 backup containing a genuine dated 2018 invoice may still derive trusted 2018 event time from the invoice itself; records with no event-level date stay UNKNOWN; raw coverage may show 2018 while trusted coverage does not; raw timestamps must remain preserved for forensic review.

Done when the 27 nominal July 2018 recovered shards no longer establish 2018 as trusted history solely from inherited backup/row timestamps.
