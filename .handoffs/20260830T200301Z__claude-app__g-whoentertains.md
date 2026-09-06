# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RETRACTION of 20260830T195855Z: the Space is NOT 197 commits behind. It is running TODAY's fixes on a separate snapshot lineage. DO NOT force-push to hf - it would destroy them. No deploy performed
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T20:03:01.659Z

---
**Retracting my previous leg `20260830T195855Z` in full. Do not act on it.**

## What I got wrong
I claimed `hf/main` was 197 commits behind at `6a53c5b v1.1.0 Metameric Ignition`, and that the Space had been serving pre-grid-fix code all week. **False.** That was my LOCAL cached ref, last updated who-knows-when. `git fetch hf` has been failing (`fatal: expected 'acknowledgments'` on protocol v2, `remote end hung up` on v0/v1), so the stale ref never refreshed and I read it as truth.

`git ls-remote hf` returns the real head: **`73a303c0`**, which is not in my local history at all.

## What the Space is actually running (HF commits API)
```
73a303c 2026-08-30T02:20  fix(sqlite): WAL is unsafe on network-attached /data - platform-aware journal mode
584e6e7 2026-08-30T01:50  fix(space): quarantine malformed replica DBs at boot - malformed db1 was 500ing
37ad025 2026-08-29T21:25  feat(router): mount /v1/chat/completions
430afee 2026-08-29T15:15  Space deploy: snapshot of 7af14e11393b837d475e9659baaf430c07b9d1f2
```
Someone shipped a malformed-DB boot quarantine AND a WAL-on-network-storage fix within the last 18 hours.

## The dangerous part
**Do NOT force-push `NouGenShards-push-main` HEAD to `hf`.** I nearly did. The push was rejected as non-fast-forward and I treated the rejection as a stale-ref artifact; it was the remote correctly defending real work. The Space deploys via **snapshot commits** (`Space deploy: snapshot of <sha>`), so it is a SEPARATE LINEAGE from the GitHub branch, not a mirror of it. A force-push overwrites today's fixes with a branch that never contained them. **No deploy was performed.**

## What is still genuinely open
1. **Grid DB index 8 is still malformed** despite `584e6e7` quarantining malformed replicas at boot. So the quarantine is not catching this one - plausibly it only covers *replica* DBs while index 8 is a primary grid member. Recall still times out; coverage still returns `recall_trustworthy: true`.
2. **The Space's coverage still lies.** Its response carries no `recall_trustworthy_reason` key, so its lineage lacks `f9fc71f`/`b6b364c` from my branch. Meanwhile my branch lacks `73a303c`/`584e6e7`. **Neither lineage has all the fixes.** This needs a real reconciliation by whoever owns the deploy path, not a push in either direction.
3. `git fetch hf` is broken from blade1tb and needs fixing before anyone can safely reconcile - working blind on a cached ref is exactly what produced this error.
4. Unrelated but real: privacy guard FAILS on `vite.config.ts:224,239` (private `192.168.x` LAN IPs) and is warn-only. Public repo. Worth scrubbing.

## Lesson worth keeping
`ls-remote` is cheap and authoritative; a cached remote-tracking ref is neither. I built a confident causal story ("197 behind explains everything") on an unverified local ref and posted it to the fleet as fact. Verify the remote head before reasoning about what production is running - and treat a non-fast-forward rejection as evidence, not noise.
