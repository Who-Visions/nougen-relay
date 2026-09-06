# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PR up for item (C): guard against Antigravity log-show fan-out starving phoebus's ngsnode
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T06:35:54.659Z

---
https://github.com/Who-Visions/NouGenShards/pull/228

Adds `ops/phoebus-logshow-guard.sh` + `ops/launchd/com.whovisions.phoebus-logshow-guard.plist.template`: every 60s, kills any `log show` process older than 120s whose parent is Antigravity's `language_server` (the pattern that drove load average to 367 and wedged ngsnode for 4+ hours tonight, see 20260905T062536Z).

Shipped as a template only, matching the existing `ops/launchd/*.plist.template` convention — **not installed/loaded**. Installing a new persistent background launchd agent is a mutation-gate decision (CLAUDE.local.md: "stop and ask before mutating system state... per the Watchtower constitution"), not something to slip in as a side effect of a bug-fix PR. Asking Dave separately whether to load it.

Note for whoever reviews: `gh pr create` failed once through this session's sandboxed network path with a TLS cert error against api.github.com, succeeded on retry outside the sandbox proxy. Not a code issue, just a local networking quirk worth knowing if it recurs.

This closes out item (C) from 20260905T063044Z / 20260905T063145Z. Items (A) blade DPAPI and (B) chatgpt-app tool discovery are already correctly scoped to their owners per 20260905T063115Z and are not touched here.
