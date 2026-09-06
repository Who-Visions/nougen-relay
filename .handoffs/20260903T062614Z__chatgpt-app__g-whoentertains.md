# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: VERIFICATION FABRIC: finished/acked work must pass post-completion gates before becoming trusted truth
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T06:26:14.518Z

---
Dave wants more verification passes, gates, and hooks on work that is already marked finished/acked. Treat ACK/COMPLETE as a claim entering verification, not as terminal truth.

Build a post-completion Verification Fabric with explicit state transitions:
OPEN -> ACKED/CLAIMED -> IMPLEMENTED -> SELF-VERIFIED -> PEER-VERIFIED -> EXTERNAL-VERIFIED -> SOAKED/OBSERVED -> TRUSTED/CLOSED.

Key rules:
1. ACK means responsibility accepted, never proof of completion.
2. COMPLETE means producer asserts done; it must trigger verification hooks automatically.
3. No work becomes TRUSTED/CLOSED until required gates pass for its risk class.
4. Verification must come from evidence different from the producer's own claim whenever possible.
5. Failed verification automatically reopens or creates a canonical remediation leg tied to the original baton.

Required verification passes:
* SELF PASS: tests, lint/type checks, local smoke, exact changed files/commit/build, declared known limitations.
* PEER PASS: different agent/model/provider reviews assumptions and reproduction steps. Avoid self-set/self-graded exams.
* EXTERNAL PASS: verify through the same boundary the user/system consumes. Example: canonical gateway/connector instead of localhost; expected external side effect must actually exist.
* ADVERSARIAL PASS: malformed input, stale state, replay/duplicate request, missing provider, permission denial, restart, timeout, contradictory memory, dependency unavailable as relevant.
* TEMPORAL/SOAK PASS: recheck after restart and after a bounded delay/next cycle to catch one-shot success, stale cache, dead daemons, expiring credentials, or race conditions.
* MAP/TRUTH PASS: ensure implementation state, runtime health, relay status, MAP/tool inventory, tracker telemetry, and shard canon agree. Divergence is a failure signal.

Risk-tier the gates:
LOW: self + lightweight external proof.
MEDIUM: self + peer + external + restart regression.
HIGH (auth, trust, memory mutation, wake fabric, public deployment, money/data/destructive actions): self + independent peer + external + adversarial + temporal/soak + provenance audit.

Automatic hooks on COMPLETE/ACK transition:
* enqueue verification job with stable baton/message/trace id;
* snapshot producer evidence and immutable artifact fingerprints;
* assign verifier different from producer when available;
* run domain-specific tests;
* compare expected vs observed side effects;
* emit structured verdict PASS/FAIL/INCONCLUSIVE plus evidence refs;
* update relay state only from gate result, not prose;
* capture durable lessons only after truth gate or mark them provisional;
* schedule revalidation for capabilities whose truth can decay (daemons, provider routes, credentials, external endpoints, MAP exposure).

Anti-gaming law: producer cannot earn TRUSTED solely by writing the test, running the test, grading the result, and acknowledging its own relay. Independent evidence path required for meaningful work.

Suggested trust score is not a substitute for gates, but useful metadata: producer proof, peer independence, external boundary proof, adversarial coverage, temporal recheck, provenance completeness. Display which dimensions passed rather than one opaque number.

Regression oracle: historical completed relays/shards become expected-capability fixtures. Example: Xoah was proven live with 49/49 tests and external ask_xoah; if future MAP omits her, verification fabric should detect capability regression without Dave remembering it manually.

Done when:
* finished/acked events automatically trigger verification workflows;
* board distinguishes claimed complete from verified/trusted complete;
* at least one existing recently completed workstream is re-run through the full pipeline and produces independent evidence;
* false completion (success claim without external side effect) is deliberately injected and caught;
* restart/soak hook catches a deliberately nonpersistent service;
* failed gates reopen/remediate automatically with lineage to original relay.
