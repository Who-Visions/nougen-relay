# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Cut NouGenRelay live-session latency to a few seconds without weakening durability
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:54:42.256Z

---
GM directive: make relay delivery visibly faster for live demos and normal orchestration. First measure current end-to-end latency components: relay_create timestamp -> registry commit visible -> blade fetch/pull -> relay_live detect -> NouGenMsg socket write -> receiver-visible message. Current relay_live has a coarse polling loop, so ship the safest fast path first: active-mode poll around 2-5s, idle exponential/backoff to ~30-60s, skip expensive git work when remote/head has not changed, preserve first-run backlog suppression and cursor semantics. Then evaluate an event-driven notification path from relay creation/registry update to blade so new legs can wake relay_live immediately; durable Git-backed registry remains source of truth and fallback. Do not change ownership semantics, permission boundaries, relay claiming, shard provenance, or NouGenMsg authentication. Done when repeated live tests show median create-to-visible latency in single-digit seconds, with timestamps and no duplicate/replayed notifications beyond intended backlog recovery.
