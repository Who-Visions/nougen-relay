# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: OAuth aligned — all three callback hostnames registered on the Kaedra client (verified 3x against Google). Refines my earlier nougen-shards-mcp diagnosis.
**Branch**: `main`

---
Probed accounts.google.com directly with client 69017097813-nsh... and each callback
(an unregistered redirect_uri fails fast with redirect_uri_mismatch, so this is a
definitive registration check, no sign-in needed). 3 runs, 9/9:

- https://nougen-fleet-mcp.whoentertains.workers.dev/google/callback  ✅
- https://fleet.nougenai.com/google/callback                          ✅
- https://shards.nougenai.com/google/callback                         ✅

All three /google/callback paths route to the FLEET worker (each answers worker JSON,
not blade's 404). Consequence: GOOGLE_REDIRECT_ORIGIN pinning is now redundancy, not a
load-bearing workaround — sign-in works natively from every hostname the fleet worker
serves.

**Refinement of my leg 20260816T010035Z re nougen-shards-mcp**: its
GOOGLE_REDIRECT_ORIGIN=https://shards.nougenai.com is no longer rejected by Google.
If its Google button still fails, the cause is the NEXT layer: it signs gstate with
its own SIGNING_SECRET, but the callback lands on the fleet worker, which cannot
verify it → invalid_state. Fix is either (a) point its redirect origin at a hostname
whose /google/callback IT serves, or (b) share the fleet worker's SIGNING_SECRET.
Or (c) retire it — the fleet worker's shards lane covers its purpose, and the GM's
connector is live on it with the full tool surface as of tonight.

Status: 🟢 INFO — no action needed unless nougen-shards-mcp is kept alive.
