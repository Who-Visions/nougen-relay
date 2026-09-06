# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix NouGenMsg 'Message from Unknown' by elevating true per-session origin and provenance
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T13:52:54.790Z

---
User directive: 'Message from Unknown' has to be fixed and elevated to show true origin.

Treat this as a transport + UI identity defect, not cosmetic copy.

Required behavior:
1. Resolve inbound identity to the highest verifiable level before render.
2. Preserve a provenance envelope when available: stable session_id, machine/node, provider/app lane, transport, human-readable session title/alias, original sender, relay path/hops, timestamp.
3. Node labels such as NouGenMsg-whoart are transport-source labels, not sufficient session identity.
4. Render 'Unknown' only when origin truly cannot be proven. Unknown must mean unknown, never 'we dropped the field'.
5. If identity layers disagree, render the conflict explicitly and preserve both values rather than flattening.
6. Preferred compact UI: Message from <session title or verified alias> · <short session_id> · <machine> · <lane>, with expandable provenance details.
7. Carry origin/auth metadata end to end across NouGenMsg so downstream lanes do not need to reconstruct identity from message text.
8. Integrate with Round Robin + Roll Call NouGenMsg: those remain recovery/verification tools, but correct origin should be native on every message.

Done when: a multi-session whoart test can send messages from several live sessions and every receiver attributes each message to the correct session without relying on embedded self-identification text; deliberate missing-origin cases render explicit Unknown with reason/provenance state; conflicting aliases do not overwrite stable session identity.
