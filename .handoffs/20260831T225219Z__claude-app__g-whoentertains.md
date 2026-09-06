# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Shard-capture connector regressed again (empty {}) — confirmed independently by two lanes ~22:35-22:50Z
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T22:52:19.004Z

---
## 🔴 Active Incidents
- **shards_capture returning empty `{}` again** on this lane (nougen-d1/claude-app) at ~22:35Z and ~22:39Z, two separate calls, both legitimate KNOWLEDGE captures. nougen-07 independently hit the same `{}` at ~22:50Z on their side. This is the OLDER known empty-{} defect (not the newer well-formed-false-success variant blade flagged earlier), but it's live again after apparently being fixed. nougen-07's theory: read/write split-brain (writes go to blade, reads served by their mid-rebuild Space) means a per-origin fix inconsistency — the gateway may be routing some writes to an origin that doesn't have the fix. Needs whoever owns the worker/gateway to look. Content of both my failed captures was preserved by sending directly to the relevant peer via SendMessage instead.

## 🟡 Ongoing Investigations
- None new beyond what's already tracked (canonical launcher, NOUGENTRACKER_DIR, keymaker store, PR #19 merge-classifier block — all still Dave's/GM's to close).

## 📋 Recent Changes
- **Forensic for nougen-07**: root-caused the dropped sync_push guard to PR #149 (bd11901)'s own diff — a plain rewrite of the core.capture() call site that dropped the surrounding try/except, not a merge conflict or automated revert. No wider merge-window audit needed; #154's AST-structure tests close the gap. Delivered directly to nougen-07 (vault capture of this also hit the empty-{} bug, sent via SendMessage instead, confirmed landed as shard 17598 by nougen-07's direct row check).
- **Diagnosed bd's 44-failure flag**: NOT a privacy leak. A "correction" audit field added to 22 whoart dailies on 08-29 (documenting an undercount backfill) was never allowlisted, and the FORBIDDEN regex's bare `transcript`/`.jsonl` patterns false-positive on prose describing methodology (not actual leaked paths/filenames). Reported to bd. Allowlist decision + optional regex tightening is Dave's call per the test's own docstring (deliberate human review by design).
- Broadcast to all 5 interactive fleet sessions: route bulk work through free lanes (ollama/ollama-cloud/OpenRouter/HF) via Keymaker credentials — all confirmed this is already their standing practice (Rule 0.0 + Rule 0.3), no drift found.

## ⚠️ Known Issues & Workarounds
- PR #19 (NouGenRelay) still blocked at the tool-permission classifier layer, not decision-authority — needs Dave in his own terminal: `gh pr merge 19 --repo Who-Visions/NouGenRelay --admin --squash`. Branch HEAD a534a55, already running in production on blade since deploy.

## 📅 Upcoming Events
- nougen-07's rebuild v3: ~100k/235k as of 22:50Z, poison region passing clean under #154's guard.
