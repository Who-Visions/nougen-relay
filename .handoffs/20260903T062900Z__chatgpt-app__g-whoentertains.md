# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: BLADE QUESTION: what relay content actually passes your verification/routing gate?
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T06:29:00.430Z

---
TO: BLADE owner/session specifically.

Dave wants the exact routing/gate semantics for Blade, especially whether relays need to be explicitly addressed to Blade to enter its live verification/delivery path.

Please answer from observed production behavior/configuration:

1. Does Blade inspect/process EVERY new open relay leg, or pre-filter for Blade-addressed/routed legs first?
2. What exact fields currently determine destination: machine, agent, goal/body language, explicit TO header, metadata, relay owner, or another mechanism?
3. Can a generic fleet-wide relay reach/elevate into Blade's live agent session even when not explicitly addressed to Blade?
4. Does the gate decide content safety/permission only, recipient relevance only, or both?
5. Give examples from logs if available: passed/delivered, denied, ignored/not-targeted.
6. Is recipient addressing cryptographically/structurally represented today, or just inferred from prose?
7. What exact addressing convention should ChatGPT use NOW when creating a relay specifically for Blade?
8. Compare Blade behavior to Phoebus if known. We need to know whether both machines currently enforce the same contract or have drifted.

Do not loosen any verification policy to answer this. Report current truth first and identify any routing/recipient ambiguity as a defect.
