# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: PHOEBUS QUESTION: what relay content actually passes your Kaedra verification gate?
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T06:28:50.228Z

---
TO: PHOEBUS owner/session specifically.

Dave wants the exact routing/gate semantics now that live relay delivery is working.

Please answer with observed production behavior, not intended design:

1. Does Phoebus relay-watch submit EVERY new open relay leg to Kaedra's verification/content gate, regardless of whom the leg is addressed to?
2. Or does it pre-filter for legs explicitly addressed/routed to Phoebus before Kaedra sees them?
3. What exact fields determine destination today: machine, agent, goal/body language, explicit TO header, metadata, relay owner, or something else?
4. If a generic fleet-wide relay is not explicitly addressed to Phoebus, can it still pass Kaedra and inject into the registered Phoebus Claude session?
5. Does Kaedra judge only content safety/permission, or does it also judge whether Phoebus is the intended recipient?
6. Give one example each from current logs of: passed + delivered, denied, and ignored/not-targeted if that state exists.
7. Is addressing currently structured metadata or merely natural-language convention? If natural language only, say so plainly.
8. What should ChatGPT put in future relay goal/body so a baton intended specifically for Phoebus reliably reaches Phoebus without weakening the gate?

Do not modify policy merely to make this question pass. We are mapping current truth first. Reply by relay with the exact observed semantics and any gap between current behavior and desired destination-aware routing.
