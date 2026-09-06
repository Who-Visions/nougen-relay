# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Standardize Round Robin + Roll Call NouGenMsg for session identity recovery
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T13:50:29.472Z

---
Dave's operational command from this morning should become fleet doctrine: `round robin and roll call nougen msg`.

Use it when node-level broadcast identity collapses multiple live sessions into one correspondent label or when attribution starts drifting.

Procedure:
1. Roll Call: enumerate actual live sessions first. Each session returns session_id, current local/session name, machine/node, current task, and provenance.
2. Round Robin: address each live session individually rather than broadcasting through the flattened NouGenMsg node identity.
3. Identity precedence: session_id + machine/node + provenance outranks unstable display aliases, outpost names, session titles, relay agent labels, and generic node correspondents.
4. Non-response = UNKNOWN, never ABSENT.
5. Do not assign credit, blame, wake receipts, tracker findings, secret/auth state, or task ownership until session attribution is proven.
6. Persist the mapping with timestamps because outpost aliases can rotate during the same run.

The screenshots from whoart show this already working: independent sessions self-identified, the roster converged, a disputed ping was attributed to outpost-29 by its exact command and timestamp, the scheduled dream-lane identified itself separately, and duplicate correspondent confusion became diagnosable rather than anecdotal.

Auth downstream implication: every NouGenMsg envelope should eventually carry a stable session identity claim and provenance so Round Robin + Roll Call becomes a recovery path rather than the normal path.

Done when: fleet lanes recognize the phrase as an operational primitive and transport work begins toward per-session identity in message envelopes.
