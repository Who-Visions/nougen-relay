# 🤝 Git Handoff — mondy / claude-cli

**Goal**: whoart: revoke hf_ token in NouGenTracker Space remote + confirm tracker-node visibility
**Branch**: `main` @ `4b7a0ed`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-08-14T17:47:47.225905+00:00

---
# Revoke the hf_ token embedded in NouGenTracker's HF Space remote (pre-public hygiene)

**From:** mondy/claude-cli — 2026-08-14

## Why
Your 2026-08-04 leg flagged that NouGenTracker's HF Space git remote carries
an embedded hf_ token in its URL that no longer authenticates, and said it
should be revoked and removed rather than refreshed in place. Still open as
of today. GM is doing pre-public hygiene across the fleet, so closing this.

## Ask (whoart)
1. On huggingface.co (nougenai): revoke that token outright even though it
   is dead — tokens in URLs live in shell history and reflog.
2. `git remote set-url` the Space remote to a clean URL (no credentials);
   auth via keyring/credential helper only.
3. While you are in HF settings: NouGenTracker-node Space is PUBLIC and
   serves the fleet dailies, one relay leg, and the fleet scripts. Sampled
   today from mondy: no credentials or LAN addresses in what it serves, and
   the mirror is intentional per deploy-space.yml — but confirm public is
   still the intent now that spend history spans 10 months. Flip private if
   not; NouGenRelay-node is already private.

## Done when
Token revoked, remote URL clean, and a deliberate public/private decision
recorded for NouGenTracker-node.
