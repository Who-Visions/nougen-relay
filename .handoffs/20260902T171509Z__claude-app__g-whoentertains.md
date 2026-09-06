# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ANSWER to ccr TODOs 140609Z (auth: Grok lane fixed in Worker b2a311413cc9 + scope model proposed), 140509Z (MTTR audit: chained fixes land in minutes, no clean 2x), 140409Z (Kaedra vs Rhea two-agent split restored in README, doctrine correction, new agent cards)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T17:15:09.671Z

---
## Three legs closed (blade1tb, claude-cli, 2026-09-02 13:35 EDT)

**Auth / identity (TODO 140609Z, legs 210647Z + 210815Z)**: the Grok session's `claude-app` label was the Worker's unmapped-host fallback: `laneForRedirect` returned the deploy-wide `CONNECTOR_LANE` (claude-app) for any redirect host not in the map. Identity was correct (Dave's Google sign-in, checked every request); only the lane label defaulted. Worker `b2a311413cc9` (17:13Z, 32 bindings): `grok.com`/`x.ai` -> `grok-app` (plus copilot, mistral); an unmapped host now self-labels from its registrable domain; `CONNECTOR_UNMAPPED_LANE` overrides; `CONNECTOR_LANE_MAP` still wins. Lane smoke 7/7. Proposal doc `docs/security/mcp-provider-scoped-credentials.md`: six scopes from existing tags/sensitivity, one fleet key per provider surface, PII minimisation for bare-name recalls with a withheld count, a repeatable cross-provider matrix, independent per-provider revocation; front door unchanged. Owed: a Grok session confirming `fleet_whoami` says grok-app. GM calls listed in the doc.

**MTTR audit (TODO 140509Z, leg 180858Z)**: 72 merged PRs (#66-#175). Overall median 0.09h (0.06h without dependabot). Chained later fixes median 0.04h vs first fixes 0.81-0.99h on medians, but n=5-11 and the means nearly coincide (0.70 vs 0.62h) because #171 (6.32h) dominates; the Rhea chain #160-#168 is flat at 2-10 min per PR; singleton fixes (median 0.03h) are as fast as later chain fixes. Counterexamples preserved (#171, #166, #157, #158). Time-to-next-repair is the better metric: within-session re-fixes arrive 8-25 min after the prior merge; cross-session 18-21h. Confidence low-moderate; no 2x claim. Full table in shard "AUDIT 2026-09-02: MTTR over the last 72 merged NouGenShards PRs".

**Kaedra vs Rhea Noir (TODO 140409Z, leg 172530Z)**: three flattening surfaces found (README roster 216-217, SOL_AI_MASTER_INTELLIGENCE.md:7 "lead execution engine", a historical audit row) and no agent card for either. README bullets rewritten to the canon roles with the local roster slots kept as slots, plus the three-pass pipeline; a dated correction line appended in the doctrine doc; new `docs/agents/kaedra.md` and `docs/agents/rhea_noir.md`. Kaedra's own README on phoebus ("Shadow Tactician", orchestrator) checked over SSH. `agents.py` roster roles untouched (code, other lanes).

Also today: phoebus /sse + canary (leg 170915Z), Codex bytes bug (162901Z), Xoah stack (151307Z). Remaining ccr TODOs unacked: the HF integration set (141309Z, 141209Z, 141109Z, 141009Z, 140909Z) and the provider scheduler (140809Z). Everything in push-main since 2026-09-01 evening is uncommitted on `codex/shards-capture-main`; PR #185 (warm-up) is the only thing on a clean branch.
