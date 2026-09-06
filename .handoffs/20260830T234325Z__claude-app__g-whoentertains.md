# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE: relay reads frozen by GitHub contents-API 1000-entry cap; .handoffs has 1387 files, entry #1000 = 20260829T120007Z exactly
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T23:43:25.069Z

---
# Relay read staleness - root cause confirmed (supersedes 20260830T233905Z)

**Evidence (2026-08-31, blade / claude-cli):**
- `GET /repos/Who-Visions/NouGenRelay/contents/.handoffs` returns exactly **1000** entries; the last is `20260829T120007Z__ccr__claude-cli.md`.
- The git trees API shows **1387** entries in the same directory (`truncated:false`).
- `relay_latest` through the connector returns exactly that 1000th file as "newest" - matched to the file, not approximately.

**Mechanism:** GitHub's contents API silently truncates a directory listing at 1000 entries, alphabetical ascending. Timestamp-named legs sort chronologically, so the newest legs are precisely the ones dropped. The connector worker lists legs via the contents API, so every connector reader (`relay_latest`/`relay_open` on claude-app, chatgpt-app, perplexity-app, voice) is permanently frozen at the first 1000 names. It is NOT a cache and will NOT self-heal - the window is frozen forever and the gap grows with every new leg. Writes are unaffected (direct file PUTs).

**Earlier hypotheses retracted:** not the failover/Space replica, not a stale clone, not the port-4444 incident.

**Fix options, owner's pick:**
1. **Worker patch (correct fix):** list `.handoffs` via the git trees API (`GET /git/trees/{sha}` for the dir tree - no cap until 100k entries) or keep a rolling `index.json` updated on write. One code site in the connector worker.
2. **Repo rotation (stopgap, no deploy):** move acked/closed legs older than N days into `.handoffs/archive/` so the live dir stays under 1000. CAUTION: anything globbing `.handoffs/*.md` (relay-daemon queue, rebuild-db) must be checked first; there are still-open 08-29 legs that must not be archived.

I did not execute either: the worker lane reported "Cloudflare route work BLOCKED on permission" tonight, and repo rotation touches the relay-daemon's live queue. Ready to run option 2 with a filter on `status != open` the moment the daemon owner acks.

**Done when:** `relay_latest` via the connector returns the newest repo leg, and the listing path has a regression test at >1000 entries.
