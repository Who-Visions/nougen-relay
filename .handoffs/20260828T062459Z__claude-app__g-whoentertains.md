# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Recall timeouts + Rhea 500 fixed, coverage density invariant added - awaiting PR #133 merge to deploy
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T06:24:59.241Z

---
Both GPT legs (20260828T053343Z, 20260828T053457Z) executed on blade1tb, commit c0148da on pi-remix, riding PR #133.

Root causes (verified with file:line + live latency): federated recall blocked on the slowest lane with NO deadline (federation.py f_*.result() bare); cloud peer walk serialized N x 8s for dead peers; substrate_coverage iterated every shard row in Python per call; ask_rhea's first _chat was unguarded so all-lanes-down RuntimeError became a 500. Live Space also runs STALE code (rhea_noir 15.3KB vs 27.9KB at HEAD) - the 8/27 split-brain leg is real, deploy path is origin main -> CI deploy-space.yml.

Fixes: NOUGEN_RECALL_DEADLINE_S=20s sweep cap w/ partial results; NGS_CLOUD_TOTAL_BUDGET_S=10s peer-walk cap; coverage via SQL GROUP BY + density_invariant block (NOUGEN_COVERAGE_DENSE_SINCE=2025-10, NOUGEN_COVERAGE_MIN_PER_MONTH=1, violations[] listed); rhea returns status:degraded payload instead of 500. All env-tunable on the Space without redeploy. 51 targeted tests pass.

NOT yet live: merge of PR #133 deploys to the Space (prod gate = GM). After deploy, verify: shards_search/shards_coverage <20s via connector, ask_rhea non-500, density_invariant present in substrate_coverage. March temporal recall: recall_window/era filter exists at HEAD ("held back" = era-window count header X-NouGen-Held-Back, not quarantine); re-test March queries post-deploy before deeper work.

Caution for concurrent agents: a merge into pi-remix mid-session clobbered an uncommitted working-tree edit (rhea_noir.py). Commit early; check git status before merging into a shared tree.
