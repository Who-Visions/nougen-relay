# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix relay enumeration inconsistency: direct read sees newer connector legs while relay_latest/listing misses them
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T14:38:07.919Z

---
Live ChatGPT connector evidence on 2026-08-29 shows a relay visibility split. Newly created leg `20260829T143257Z__chatgpt-app__g-whoentertains` exists and `relay_read(id)` returns the full body successfully, proving the write landed and direct ID lookup can see it. However `relay_latest` still returns older leg `20260829T120008Z__ccr__gm-phone`, even though the ChatGPT leg is more than two hours newer. This means write path and direct read path are not aligned with enumeration/latest indexing.

Impact: agents relying on relay_latest or relay_open can miss valid handoffs that other lanes created, making legs appear invisible and creating false fleet silence. This can break baton pickup, cross-lane coordination, debugging, and any automation that assumes listings are authoritative.

Likely fault domains to inspect: relay index refresh/invalidation, backend source divergence, branch/repo filtering, connector-lane filtering, cached listings, timestamp ordering/parsing, registry watcher lag, write destination mismatch vs enumeration source, and any dedupe logic that excludes connector-created legs.

ASK: trace one known leg end to end from relay_create write through registry persistence, watcher/index update, relay_open enumeration, and relay_latest selection. Verify all read surfaces consume the same authoritative registry or reconcile correctly. Do not create a parallel relay endpoint as a workaround; fix consistency in the existing relay path.

DONE WHEN: creating a connector leg makes it immediately visible by relay_read, relay_open, and relay_latest according to timestamp/status semantics, across ChatGPT/Phoebus/other fleet lanes. Add a regression test that writes a synthetic leg then asserts direct read + listing + latest visibility from the connector lane.
