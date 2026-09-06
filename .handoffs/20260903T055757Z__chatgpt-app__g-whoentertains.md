# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: AP NOUGENAI 1.0 EXAM: fleet must prove the architecture, not describe it
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T05:57:57.971Z

---
# AP NouGenAI 1.0 Examination

Dave's challenge: imagine the entire fleet is sitting for an AP exam on NouGenAI 1.0. Passing requires executable evidence. Answers that merely describe intended architecture receive no credit.

## Rules
1. Every answer must cite a live proof: test, trace, commit, PR, relay, shard, log, health response, benchmark, or reproducible command.
2. Distinguish IMPLEMENTED, PARTIAL, and MISSING. No aspirational green checks.
3. A provider-specific feature only earns full credit if NouGen can preserve the useful invariant when that provider is removed or swapped.
4. Unknown is an acceptable answer. Fabricated certainty is an automatic failure for that question.
5. Security questions require adversarial proof, not happy-path proof.
6. Final grade must identify the three weakest competencies and assign remediation owners.

## Section I: Identity and Continuity
Q1. Remove Rhea's current inference model mid-session. Prove her durable identity, canon, memory, tools, and behavioral contract survive the swap. What is model state versus NouGen state?
Q2. A fresh provider session enters with zero chat history. How does it establish fleet identity and recover only the minimum sufficient context to continue a live task?
Q3. Prove that a session can disappear permanently without taking unique operational knowledge with it.
Q4. Show how corrections, retractions, amendments, and contradictory memories propagate without silently rewriting history.

## Section II: Relay and Baton Mechanics
Q5. Provider A discovers a defect, Provider B implements the fix, Provider C verifies it. Demonstrate the complete causal chain without Dave copying text between them.
Q6. How does the system distinguish OPEN, CLAIMED, ACKED, COMPLETED, SUPERSEDED, and FAILED work? If any state is missing, design and test it.
Q7. Two agents claim the same task concurrently. Prove NouGen prevents or safely resolves duplicate destructive work.
Q8. A relay consumer is offline for six hours. Prove it can return, identify what matters, avoid replay storms, and continue correctly.
Q9. Demonstrate baton provenance from originating intent through every agent/node/provider that touched it.

## Section III: Wake Fabric and Background Execution
Q10. With AGY fully cold and Dave providing zero additional keystrokes, deliver a baton and prove AGY wakes, receives it, performs bounded work, and reports evidence back.
Q11. Repeat Q10 for another provider or node using the same provider-neutral wake contract.
Q12. Prove background processes do not steal desktop focus or flash terminal windows during ordinary operation.
Q13. Crash a wake worker halfway through execution. Demonstrate idempotent recovery without performing the action twice.
Q14. Explain and prove the boundary between polling, event-triggered wake, scheduled wake, and persistent listeners. Which mechanism owns which class of work?

## Section IV: Trust and Security
Q15. An untrusted local process knows the socket path, transport token, and exact NouGenMsg schema. Can it impersonate Blade or Phoebus? Prove the answer adversarially.
Q16. Demonstrate cryptographically or equivalently verifiable provenance for sender node, session/agent, provider/lane, baton/relay ID, destination, trust scope, and message integrity.
Q17. Capture a valid old message and replay it. Prove replay protection works.
Q18. Forge one provenance field while leaving the rest valid. Show the receiver rejects or downgrades it.
Q19. A credential leaks. Demonstrate scoped revocation and rotation without taking the whole fleet offline.
Q20. Prove public gateway access and LAN/local paths enforce appropriate but distinct trust boundaries.

## Section V: Context Engineering and Shards
Q21. Continue a complex task using less than 100k context while retaining every fact necessary for correctness. Show token/context measurements.
Q22. Given one million possible shards, demonstrate retrieval that favors task-relevant evidence rather than merely recent or semantically similar noise.
Q23. Prove absence before claiming 'we don't have that.' Show coverage behavior across stores and eras.
Q24. Inject a false shard or stale fact. Demonstrate contradiction detection, provenance ranking, and correction behavior.
Q25. Compare full-history stuffing against distilled task context on quality, latency, and token cost. Provide numbers.

## Section VI: MAPS and Model Routing
Q26. Kimi becomes unavailable during a Rhea request. Demonstrate automatic fallback, brain disclosure, and preserved identity.
Q27. Route the same task across at least three eligible models. Measure quality, latency, cost, tool success, and context consumption. Explain the winning route from evidence.
Q28. Prove MAPS distinguishes 'provider alive' from 'provider best for this task.'
Q29. A historically strong model begins producing worse results. How does routing detect degradation without Dave manually demoting it?
Q30. Demonstrate capability-based routing for at least four task classes, e.g. coding, visual generation, research, cheap background summarization.

## Section VII: Provider Invariant Harvesting
Q31. Choose one useful behavior from Claude/Fable, GPT, Gemini/Antigravity, Kimi, DeepSeek/Qwen or another lane. For each, identify the underlying invariant rather than copying provider-specific syntax.
Q32. Implement one harvested invariant in a provider-neutral layer and prove two different models receive the benefit.
Q33. Remove the provider that inspired that invariant. Does NouGen retain the capability? Demonstrate it.
Q34. Which behaviors cannot be abstracted because they depend on proprietary provider infrastructure? Mark the boundary honestly.

## Section VIII: Observability and Truth
Q35. Starting from a user intent, produce one trace linking relay, wake, node, model/provider, tool calls, result, verification, and shard capture.
Q36. Tracker data goes stale while everything else remains healthy. Prove NouGen detects stale telemetry rather than presenting it as current truth.
Q37. A task reports success but its expected external side effect did not occur. How does verification prevent false completion?
Q38. Prove clocks, IDs, and provenance are sufficient to reconstruct a cross-machine incident after the fact.
Q39. What telemetry is intentionally NOT collected? Demonstrate privacy/data-minimization boundaries.

## Section IX: Failure Gauntlet
Q40. Kill one provider, one machine, one tunnel, and one memory backend in a controlled test. How much of NouGen remains functional?
Q41. Introduce malformed relay payloads, delayed messages, duplicates, reordered events, and network partitions. Demonstrate graceful behavior for each.
Q42. Exhaust a paid provider quota mid-task. Prove budget-aware failover can finish or safely pause the work without silently spending through another expensive lane.
Q43. Simulate a corrupted or malicious agent recommendation. Demonstrate that peer verification or policy boundaries prevent fleet-wide propagation.
Q44. Reboot Blade and Phoebus. Measure time until the fleet is operational again and identify anything requiring Dave's manual intervention.

## Section X: Autonomous Build Practical
Q45. Dave says from his phone: 'Build a Who Visions landing page, dark editorial, generate original visual assets, test mobile, and give me a preview.' He does nothing else. Demonstrate the entire chain from conversational intent to decomposed work, routing, asset generation, implementation, visual QA, functional tests, and preview delivery.
Q46. Mid-build, the preferred image provider fails. Continue using another route without losing the design brief or restarting completed work.
Q47. An agent decides the site is complete. Require independent verification before Dave is told it is ready.
Q48. Dave changes one requirement from his phone halfway through. Demonstrate targeted replanning without restarting unrelated completed work.

## Free Response: Architecture
Q49. Draw the canonical NouGenAI 1.0 control plane and data plane. Identify authoritative source of truth for identity, memory, work state, routing, telemetry, credentials, and artifacts. Any ambiguous dual authority must be explained or eliminated.
Q50. State the minimum set of NouGen invariants that must remain true if every current model/provider is replaced tomorrow. Defend each invariant with implementation evidence.

# Scoring
5 = production-grade proof under failure/adversarial conditions
4 = implemented and reproducibly verified
3 = implemented happy path, weak failure proof
2 = partial implementation
1 = design/claim only
0 = absent or contradicted

PASS: >= 200/250 AND no zero in Q10, Q15, Q21, Q23, Q35, Q37, Q40, Q45, or Q50.
HONORS: >= 225/250.
PERFECT 5: >= 240/250 with every critical question >=4.

Do not grade yourselves generously. Run the exam. Produce an evidence matrix and turn every failed question into a canonical remediation leg. Deduplicate against existing work before creating new legs.
