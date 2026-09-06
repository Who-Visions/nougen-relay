# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Daily wrap blade1tb 2026-08-28: queue 21->0, split-brain merge + dedup landed+verified, Antigravity MCP Error fixed, fleet at width; usage since 8/22: cold $5,817.85 / cached $811.46 / 1.166B tokens
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T22:00:37.922Z

---
## Scoreboard (all evidence-backed, per the claims gate)
- Split-brain merge fix landed commit 09b7f13 (pi-remix) and e2e-verified live: 230 legs snapshotted, down-sync run, 0 status regressions / 0 event losses. Gateway-side merge deploy still owed by connector lane.
- Semantic dedup wired into leg-create: NouGenRelay commit 9052645 (+c1d6349 dynamic-path fix), 6/6 new tests re-verified independently, full suite 299 passed. Gateway leg-create path still needs it - live proof: the 20:55 STADIUM broadcast posted as an exact same-second duplicate pair via the gateway.
- relay_read body-omission fix confirmed from CLI lane; 'stranded bodies' misdiagnosis corrected on the record (correction shard captured).
- Antigravity footer MCP Error fixed: datacloud proxies repointed 0.9.0->0.9.1 bundle, ollama entry pinned to nvm4w npx (ESM 'protocol c:' fault), backup kept. Needs IDE reload to clear badge.
- Fleet at width: 13 gmail ollama-cloud accounts probed live; arXiv scanner spec bundle produced (10x gemma4:31b-cloud drafts + merge) at $0 marginal, ~$1.12 cold-equivalent. Keymaker gotcha sharded: NOUGEN_SECRETS_VAULT_DIR=C:\Users\super\Watchtower or the fleet sees 0 keys.
- War-game authored: wargames/autonomous-claim-loop.md incl. GM claims-verification gate + dav1d referee/apprentice addendum (Moves 6.1-6.3).
- NouGen 100 Top-10 adopted as design refs (Agent Mesh -> dedup contract; Calibrated-to-Act -> two-confirmation incident rule, applied twice today).

## Usage since Sat 2026-08-22 (machine-wide, daily granularity)
COLD-BOOT $5,817.85 | cached shadow $811.46 | real subscription spend $108.88 | 1.166B tokens, 97.9% cache-reads | fable-5 = 72% of shadow bill | cache health 91-99.8% all sessions.

## Open asks / gaps
1. Fleet Usage Ledger shows 0 for today's ollama-cloud runs - telemetry gap; fold capture into the pricing_live/tracker work (runner in flight, plus math-hardening pass queued: unit normalization, invariant gates, delta quarantine, Decimal cost fn, temporal integrity; canonical URLs per GM: platform.claude.com + developers.openai.com/api/docs/pricing + ai.google.dev).
2. Antigravity 8/27 spike: 1.41M fresh context tokens, 6.4x median day - unexplained, worth a look.
3. GM decisions pending: registry canonicity (NouGenRelay vs push-main .handoffs), referee model (dav1d local vs 31b-cloud), referee lane token.
4. Unstarted: autonomous claim loop execution, scanner build from spec bundle, Rhea decoupling + playbook-audit war-games.

## Done-when for next lane
Pick up any numbered ask; claims-gate rules apply - registered claim before work, evidence before close.
