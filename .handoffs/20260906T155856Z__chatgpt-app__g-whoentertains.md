# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: AUTONOMOUS QUOTA GOVERNOR: preserve nonstop NouGenMsg work without surprise quota drain
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T15:58:56.992Z

---
Observed on 2026-09-06: Dave left an Antigravity session running with NouGenMsg on Phoebus and returned to find quota materially consumed while the session had continued autonomous relay work. This is desirable execution behavior but needs budget control, not shutdown.

Implement a quota governor layered above the Claim Engine:
1. Track provider/session quota snapshots before and after each claimed leg when available.
2. Compute quota_cost_per_leg, quota_cost_per_verified_artifact, and rolling quota burn velocity.
3. Define user-configurable SOFT, HARD, and RESERVE thresholds.
4. SOFT threshold: lower reasoning/model tier and prefer cheap/local lanes.
5. HARD threshold: stop claiming new cloud-cost legs, finish the currently safe leg, emit relay state, then route to local/free fallback.
6. RESERVE: protect a minimum provider quota for interactive Dave sessions.
7. Never kill productive local Ollama/NouGen work just because cloud quota is exhausted.
8. Couple this with Hadouken token economics so high coordination-tax agents get deprioritized before productive agents.
9. Evidence required: tests, commit SHA, sample ledger output, and a simulated quota-threshold transition.

Critical semantic: unattended autonomous work is GOOD. Surprise depletion is the bug. Preserve autonomy, add economics.
