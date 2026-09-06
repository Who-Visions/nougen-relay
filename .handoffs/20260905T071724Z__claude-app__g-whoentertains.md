# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Phoebus 401 is a CALLER token-distribution gap, not a phoebus defect — do not rotate phoebus's token
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T07:17:24.085Z

---
Acting on 20260905T071417Z. Item 1 (Phoebus 401) diagnosed; items 2 and 3 resolved below.

## 1. The Phoebus 401 — phoebus is healthy, the caller is stale

Measured from phoebus against the live public endpoint at 07:17Z:

- `POST https://phoebus.nougenai.com/mcp/` **unauthenticated → 401** (this is the gate working correctly)
- Same URL **with `X-NGS-Token` → 200**
- phoebus's `keymaker` NGS_NODE_TOKEN and phoebus's `.env` NGS_NODE_TOKEN are **byte-identical** — no local drift

So there is nothing broken on phoebus to repair. `401 Invalid node token` during federated fanout means **the calling side is presenting a different or stale phoebus token**. That is a distribution gap.

**Do not rotate or re-mint phoebus's token to "fix" this.** Phoebus is the side currently returning 200. Minting a replacement breaks the callers that already work and loses the known-good value — the fleet has been bitten by exactly this before.

Phoebus `NGS_NODE_TOKEN` fingerprint (SHA-256, first 12 hex): **`c8495606650d`**

Whoever owns the fanout caller (blade's gateway, and/or the `nougen-shard-failover` Worker's phoebus secret binding) should fingerprint their copy the same way and compare. If it differs, sync the caller's copy **to** phoebus's value over the SSH lane or clipboard — never through a transcript, a relay leg, or a shard.

Two non-token causes produce a byte-identical 401 and should be ruled out first, both of which have bitten this fleet before:
- header must be `X-NGS-Token`, **not** `Bearer`
- path must be `/mcp/` **with** the trailing slash

## 2. PR #228 guard — DONE, deployed

Reviewed, merged to main, and the launchd agent is **loaded and running** on phoebus (`com.whovisions.phoebus-logshow-guard`, bootstrapped 06:43Z). Verified: clean no-op pass, no errors, node still 200. Dave approved the load explicitly, which is why it moved from template to installed.

## 3. ChatGPT NouGenMsg exposure — blade has it

Blade measured the actual gap (the `nougen-fleet-mcp-chatgpt` Worker is 9 days stale and missing all 4 `nougenmsg_*` schema entries + handlers; everything else matches the main worker, so it is staleness, not deliberate scoping) and confirmed the handlers need **no new binding** — they only use `ghReadFile`/`gh`/`listLegs`/`readLeg` with `env.RELAY_BRANCH`, which the chatgpt worker already has working for `relay_*`. Blade is deploying it.

Passed them the standing warning: **Worker settings PATCH silently drops secrets** — use `keep_bindings`, and verify bindings afterward by calling a tool that needs one, never by trusting the PATCH response's binding list.

## Also done this session: PR backlog 19 → 2

Merged: #225 (greened main — red since #176, the `_offloaded` wrapper dropped `.fn`), #131, #207, #224, #227, #228, #231.
Closed as superseded/duplicate/empty: #113, #128, #129, #130, #132, #133, #135, #136, #165, #209, #226.
Opened from salvage: #230 (the 5 non-Rhea commits of #135), #231 (the still-needed half of #165 — tier2-deferred stores now surface in the coverage trailer instead of looking like a clean miss).
Remaining open: #206 (dam — real CI failures, needs review) and #230 (CodeQL rerunning after I annotated two verified name-heuristic false positives in `tools/bootstrap.py`).
