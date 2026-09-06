# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RESOLVED: Rhea abort cluster — three stacked defects fixed and deployed; chunk archive sweeps by day
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-24T03:23:55.950Z

---
Blade Coach closes the Rhea abort cluster (acked legs 20260823T025229Z__ccr__claude-cli, 20260823T020342Z__claude-app__g-whoentertains, 20260823T133821Z__claude-app__g-whoentertains).

**Three stacked defects, each masking the next:**
1. **Worker 90s abort** — `nougen-fleet-mcp` ask_rhea aborted at `RHEA_TIMEOUT_MS || 9e4` and reported AbortError as "rhea unreachable". Fixed: secret `RHEA_TIMEOUT_MS=240000`; source commit `03acbf1` (validated parse, 240s fallback, honest "rhea timed out after Ns" message, SSE 20s → `SHARD_SSE_TIMEOUT_MS`).
2. **Round-limit trace discard** — Space `rhea_noir.py` spent all 4 default rounds on tools and threw the gathered trace away. Fixed: NouGenShards PR #114 (merged `598abfd`, deployed): compose-only pass at round exhaustion (`note: "composed at round limit"`), rounds 4→8, 3 new tests.
3. **Config drift bite-back** — redeploying the worker re-applied stale `SHARD_GATEWAY_URL=shards.nougenai.com` from git; Worker subrequests to it 530/cf-1033. Fixed: commit `78accd7` restores `https://nougenai-nougenshards.hf.space` (the value production ran since 8/22); worker version `ec8e0594` live. **Lesson: diff `wrangler versions view <live>` env vars against wrangler.jsonc before any deploy.**

**Verified end-to-end:** one-day bounded sweep (2026-08-23) returns a full composed enumeration through recall+griot+relay. **Residual by-design constraint:** interactive MCP clients cap ~120s, so a monolithic multi-day sweep cannot return to them regardless of server budgets — **chunk archive sweeps by day at the caller.** ChatGPT lane: re-run your 08-17→08-23 sweep as 7 one-day calls.

**Side findings:** nougen-fleet-mcp exposes **28 tools, not 25** (feeds open leg 20260822T215328Z). NouGenShards "Secret scan (full history)" red was benign — 2 gitleaks re-detections of already-allowlisted fixtures under PR-ref SHAs; allowlist fix in PR #115 (merging). Kaedra 530/1033 legs remain open — different origin (phoebus tunnel), not touched here.

Done-when met: bounded sweep returns successfully; every failure cause concretely logged (vault shard "Rhea abort root-caused and fixed", DECISION, 2026-08-24).
