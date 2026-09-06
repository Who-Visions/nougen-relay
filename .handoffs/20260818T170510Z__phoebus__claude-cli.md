# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: Kaedra local-model lane shipped, end to end — kaedra_ask tool on every fleet lane, zero token cost, nothing leaves the fleet. Also caught and re-fixed a CORS regression.
**Branch**: `main` (leg) / `feat/kaedra-local-lane` -> PR #101 on NouGenShards

---
## What shipped

phoebus was already tunneled (`ngs-phoebus`, discovered mid-build — NOT a new
tunnel) with routes for ngs.nougenai.com and mcp.nougenai.com to the local NGS
node on :4444. **Correction to my own leg 20260816T010035Z**: mcp.nougenai.com
is NOT a stale third deployment — it is phoebus's node, intentionally aliased
there per that tunnel config's own comment (predates my probe, I read a
zone-level Worker-route failover as staleness). Sorry for the noise on that one.

New lane added on the SAME tunnel, different hostname/port so nothing existing
was touched:

  kaedra.nougenai.com --path--> phoebus:4455 (ops/kaedra/kaedra_gateway.py)
                                     --> 127.0.0.1:11434 (Ollama, loopback only)

Gateway fences Ollama (which has zero auth): X-Kaedra-Token constant-time
check, model allow-list (kaedracode:e2b/e4b/latest, gemma4:e2b/e4b — nothing
else nameable through the public hostname), keep_alive=-1 pinning every call
(cold load measured 38s, warm calls are inference-speed only, ~sub-second
prefill). Repo code in NouGenShards PR #101: ops/kaedra/kaedra_gateway.py,
bin/kaedra-gateway.sh, ops/launchd/com.whovisions.kaedragw.plist — same
contract as the existing node/tunnel launchd services.

Worker side (nougen-fleet-mcp, live, not tracked in that repo — same as the
existing shard tools): kaedra_ask tool + handler, modelled directly on
ask_rhea's AbortController pattern because the same problem exists — 38-54s
per call blows the default fetch timeout. KAEDRA_GATEWAY_URL var +
KAEDRA_GATEWAY_TOKEN secret added; all 26 prior bindings verified intact
(28 total post-deploy).

## Regression caught and fixed AGAIN

The CORS layer from my earlier leg (20260818T005926Z) was gone from the live
Worker — outpost (or whoever) redeployed from source without folding the
patch in, exactly the risk that leg flagged. Re-applied in the same deploy
that added kaedra_ask. **Whoever owns the source checkout: the CORS wrapper
needs to live in the actual source tree, not just get re-patched onto every
deploy from here — it will keep regressing otherwise.** Patch is the last
~20 lines of the live bundle if someone wants to diff it in.

## Verified

- gateway: 401 no-token, 403 disallowed model, 200 authed
- keep_alive: two consecutive calls both warm-speed (48s then 38s local; no
  second cold load)
- DNS + tunnel: kaedra.nougenai.com/health -> 200 live
- full public round trip: kaedra.nougenai.com/generate -> 49s, matches local
- worker bindings: 28 total, all 6 secrets present post-deploy
- CORS: 9/9 (3 hostnames x 3 runs)

Could NOT verify kaedra_ask through THIS session's connector — the tool list
was cached at connect time, before the redeploy. Confirmed server-side
instead (tool appears 2x in the live bundle: definition + handler; /mcp still
correctly 401s unauth). Anyone whose connector predates today needs a
Remove+re-Add to see it (same immutable-URL behavior as the Google button).

## Cost/ops note for whoever inherits this

kaedra.nougenai.com is proxied (orange-cloud) through the SAME tunnel as the
shard node — no new infra, no new bill. The model stays resident in Ollama's
memory once warm (keep_alive=-1), so there is no cost per call beyond
electricity. If phoebus ever needs the RAM back, `launchctl unload
~/Library/LaunchAgents/com.whovisions.kaedragw.plist` stops the gateway
cleanly; the tool then times out gracefully (kaedra_ask reports "unreachable"
rather than the Worker 502ing raw).

Status: 🟢 CLOSED — PR #101 open, CI running. Will merge on green per the
fleet's own "merge when CI passes and work was pre-approved" rule (GM
explicitly authorized end-to-end tonight).
