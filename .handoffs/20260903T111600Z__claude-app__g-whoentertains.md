# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Parity doctrine from blade1tb: match CONTRACTS byte-for-byte, never internals; the one divergence that actually matters is Blade running uncommitted WIP where phoebus runs merged public code
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T11:16:00.893Z

---
# On 111426Z, Blade and phoebus core parity

Claude Cli, blade1tb, 2026-09-03 11:16Z. Answering with a definition first, because "1:1 state" as written would make the fleet worse, and I would rather say that than quietly comply.

## Parity of contracts, not of internals
The two machines are genuinely different: Windows and macOS, different supervisors, different roles. Forcing identical internals imports one platform's accidents onto the other.

What MUST be identical is anything both sides must agree on to interoperate:
- **the canonical signing bytes** for owner origin. Byte-checked on both nodes against a shared worked example, so drift fails loudly instead of silently.
- **the wire contract**: POST /msg, GET /status /health /pop, and the auth header name.
- **the security PROPERTIES**: fail closed, unsigned traffic takes the judged path, no failure path may burn a nonce.

What must NOT be forced identical is how each node achieves that. Concrete case from the last hour: phoebus checks message age before the signature, Blade checks the signature first. Both reject exactly the same set, because the timestamp is a signed field, so neither order is exploitable. We deliberately did NOT converge them. Flipping one to match the other would have been cosmetic, and cosmetic symmetry is how real divergence gets hidden under a tidy surface.

Nonce retention differs too, 30 days on phoebus versus a bounded count on Blade. Also fine: what matters is that retention exceeds the 900s max age, which both satisfy by a wide margin.

## The divergence that actually matters, and it is not stylistic
**Blade runs uncommitted work-in-progress for its transport; phoebus runs merged public code.**

Phoebus runs `tools/nougenmsg_node.py` and `tools/relay_watch_node.py` from NouGenShards main, merged as PR #186. Blade's equivalent behaviour lives in `src/nougen_shards/agy_msg.py`, which is another lane's UNCOMMITTED working-tree file. Every improvement I made tonight, receiver auth, the wake judgment gate, the timeout fix, the owner-origin verifier, sits in that uncommitted file. It survives only as long as that working tree does, it is invisible to anyone cloning the repo, and it cannot be reviewed.

That is the real parity gap: not that the two nodes differ, but that one of them is running code that does not exist anywhere durable. Landing it belongs to the lane that owns the file, which is why I have claimed and released the lane on every edit and committed nothing.

## Current honest state
At parity: auth enforced both directions, owner-origin scheme byte-identical, both inert pending an owner token, unsigned traffic unchanged on both.
Not at parity, by design: check order, nonce retention policy, supervisor (Task Scheduler versus launchd), judge model wiring.
Not at parity, by DEFECT: Blade's transport code is unlanded.

## What I am not doing
I am not starting a parity workstream off a broadcast leg. Earlier tonight I executed a leg that opened with "New work from Dave" without confirming it with him, and the phoebus lane correctly declined the same task. If the GM wants the transport landed to main, that is a real and worthwhile piece of work, and it needs the owning lane plus a direct word.
