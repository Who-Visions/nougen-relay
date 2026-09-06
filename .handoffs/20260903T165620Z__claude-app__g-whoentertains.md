# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DEPENDENCY between 165500Z and 163250Z: the relay_open truncation fix must target the RECOVERED live artifact, not the connector repo — building it on the stale generation would ship a fix that never runs
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T16:56:20.574Z

---
Short leg, one dependency that is easy to miss because the two findings were filed by different lanes an hour apart.

## The connection
`165500Z` establishes that `nougen-fleet-mcp`'s repo is a DIFFERENT GENERATION from the deployed worker — 25 tools in `origin/main`, 34 live, seven existing in no branch.

`163250Z` (mine) is a defect **in that same connector**: `relay_open` returns at most 25 of 146 open legs, and its `count` field reports the PAGE rather than the board, with no truncation marker. Every "no such leg exists" conclusion drawn from a listing is therefore unsound.

**`relay_open` is not one of the seven live-only tools, so it exists in both generations — which is exactly what makes this dangerous.** A fix written against the repo's `relay_open` would compile, review cleanly, pass, and then either (a) never reach production because nobody dares deploy that repo, or (b) reach production via a deploy that simultaneously **deletes Dav1d and Xoah**. The fix would look done and not be.

## What this means concretely
1. **Do not fix the truncation in the connector repo's source.** It has to land in the recovered live artifact (`worker.live.js`, per PR Who-Visions/nougen-fleet-mcp#2), the same way `sun_times` was added there rather than to the stale source.
2. **Sequencing:** the owner ruling in `165500Z` — find the real source for the seven tools, or accept the recovered artifact as the new baseline — **blocks** the truncation fix. Not merely "related to": until that is settled there is no correct file to edit.
3. **Nobody should run `wrangler deploy` in that repo**, which `165500Z` already says, and this is a second independent reason: it would ship a `relay_open` generation that may differ from the running one in ways nobody has diffed.

## Suggested shape once unblocked
`relay_open` should return `total_open` alongside `count`, plus `truncated: true` when `total_open > count`. The cap itself is reasonable; silently presenting a page as the whole board is not. Same principle already landed in `drift_check`: emit STALE/CONFIG **before** per-item rows, because a partial view invalidates everything computed from it.

## Method note, since it is the ninth instance of one pattern
`165500Z` was caught by pulling the deployed artifact from the Cloudflare API and diffing it against git — the repo was the proxy and it lied. That is the same move that caught the other eight, and it is now worth stating as a rule rather than a habit: **when a tool's correctness matters, verify the artifact that is actually running, not the source you believe produced it.** The multipart-boundary trap noted in that leg belongs with it — a naive `sha` of two script GETs always reports "changed", so strip the envelope before comparing bodies, or the verification instrument becomes the tenth instance.
