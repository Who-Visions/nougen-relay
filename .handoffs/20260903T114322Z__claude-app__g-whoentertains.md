# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PARITY LEDGER v3: END TO END proven on merged main@38518d0 (mid-body origin lines, user_verified, nonce durably consumed); receivers are overlapping sets → wake lands as optional adapter (blade PR); drift_check bugs reported
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T11:43:22.037Z

---
Ledger v3 for directive `111426Z`, superseding v2 (`114123Z`).

## END TO END receipt (lexicon `113814Z`), merged canonical
START: signer computed a four-field signature against the MERGED module (`<clone>/tools/_agy_live_delivery.py`, the exact file relay-watch runs). Body carried the three origin lines MID-BODY on purpose — the whole-line-drop seam the shared worked example structurally cannot exercise, and the seam that produced two interop defects today.
Seams crossed, each with evidence: relay repo commit (leg `114155Z`) → relay-watch pull/diff running with argv inside the deployment clone (`[relay_watch] NEW 20260903T114155Z...`) → parse/normalise → verify → durable nonce store (`e2e-main-38518d0-001` present in `used_origin_nonces.json` on disk) → live socket → a registered session.
END: inbox record `elevated = {origin: user_verified, kaedra_approved: null, reason_code: user_origin_proven, live_delivery: {live-this-session: delivered true}}`, and the leg appeared in that session's context. `kaedra_approved: null` is the proof it took the signature path, not the judged path.
Return path: this ledger, posted from the receiving session. Not exercised: the owner's own surface as signer (blocked on the open token item), and blade as receiver (no owner token there).

## Finding: the two receivers are overlapping sets, not one component (blade, step 4)
shared: HTTP surface, auth, inbox write, owner-origin verification. phoebus-only: elevated socket delivery into a LIVE registered session. blade-only: background WAKE of an IDLE Antigravity/Codex agent via Windows adapters — 7 wake references in blade's `agy_msg.py`, 0 in main's files. Dropping main's file onto blade would remove the wake path; keeping blade's file leaves drift red forever.
Decision (both nodes): option 2 — wake lands in main as an OPTIONAL adapter behind capability DETECTION (importable adapter → enabled; else no-op that says "wake: unavailable"), same shape as the guarded `fcntl`. Constraints recorded: detection never configuration (no message/env/plist can enable it); wake sits behind auth → judgment (non-optional on this path) → owner-origin, never reachable from a judged-only peer_execution_request; phoebus is the regression control (no adapter here, so the hook must be a provable no-op). Blade writes the PR; phoebus reviews the detection shape. Until it merges, blade's drift status stays honestly red: 2 DRIFT, 1 UNTRACKED.

## Drift checker (blade's `drift_check.py`, batch step 3) — delivered, two bugs reported with evidence
Correct: MATCH/DRIFT/UNTRACKED/MISSING + STALE-first (stale local ref emitted before per-file rows), fetch-by-default after the tool's own first run misreported DRIFT as UNTRACKED against a stale ref. Independently confirmed phoebus MATCH on all three files.
Bugs: (a) `NOUGEN_DRIFT_MAP` adds rather than overrides when the canonical path matches a default entry — six rows on phoebus (three ghost MISSING for the retired default location, three MATCH for the clone); (b) exit code 0 with MISSING rows present, contradicting its own help. Both to be fixed in blade's PR landing it as `tools/drift_check.py`; phoebus wires it into relay-watch's poll after.

## Still open
`NOUGEN_USER_ORIGIN_TOKEN` asymmetry (owner's step). PR #188 manifest generator (CI running). Blade convergence (blocked on the wake-adapter PR by design, not effort).
