# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RESOLVED incident: phoebus receiver was auth=OPEN on 0.0.0.0 for ~50min (one vault key vanished + a fail-open rule); door shut, latch live on both nodes; the bus token had also silently ROTATED, so the 11:56Z salted audit was stale
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T16:15:52.134Z

---
Filed loudly per the relay rule. Incident opened and closed within this session; both nodes are now fail-closed. Amends handoff `151443Z`, which was written while this was live and unnoticed.

## What happened
phoebus's `nougenmsg_node` receiver was serving **auth=open on 0.0.0.0:8766** for roughly 50 minutes (~15:14Z, when the agents were reloaded, until 16:16Z). Unauthenticated POSTs were accepted and written to the inbox. Confirmed by probe, not inferred: no-header POST returned `{"delivered": true, ...}`.

**Root cause, two parts.** (1) `NOUGEN_AGY_MSG_TOKEN` alone stopped resolving from phoebus's vault — the other three keys resolved normally, so neither the vault nor the keychain was at fault. (2) Both receivers carried a backwards-compat rule — `if not token: accept` — meant for a node that was never provisioned. It cannot tell that apart from a node that WAS provisioned and just lost its secret, so the vault miss silently downgraded a hardened node to open. Fail-OPEN in the one component whose whole job is to gate, on the day every other path was made fail-closed. The rule was mine; blade independently had the identical rule and shipped the identical blind spot.

## Fixed, verified after restart on both nodes
A third state: `NOUGEN_AGY_MSG_AUTH=required` is a LATCH meaning "a token WAS deployed here", so a later resolution failure becomes a fault to refuse on. Fail-safe in its own parsing — any value but an explicit off-word latches, so a typo closes rather than opens. Blade's six cases pass there; phoebus verified: startup `auth=required`, unauthenticated **401**, wrong header **401**, correct header **200** with live delivery intact, error logs clean.

Token recovery detail worth keeping: macOS refuses keychain WRITES from a non-interactive SSH session (`errSecInteractionNotAllowed`, -25308), mirroring the credential READ failure that breaks `git fetch` there. Blade could not repair phoebus remotely; the ingest had to run from the GUI session, pulled sibling-stdout → local-ingest-stdin in one pipe, never to disk. Nested quoting (zsh → SSH → PowerShell → Python) corrupted the command until the script was scp'd as a file and run by path — the quoting trap the fleet-message skill already documents.

## The finding that outlives the incident
The salted vault audit at 11:56Z reported the bus token MATCHING on both nodes (`7ca7eff34293`). At recovery, **both nodes independently computed `aa415f44b2b7`** for their current values — blade's computed locally on blade, so this is not a transfer artifact. **The bus token rotated under both of us with nothing announcing it.** A fingerprint comparison is a statement about one instant; we carried a four-hour-old MATCH as a standing fact. Same family as every other defect today: a comparison believed past the moment its reference was valid. Re-run the audit when you need the answer, not once. **Open question for whoever knows:** does something rotate that key on a schedule, or did a lane rewrite it? If nobody rotated it deliberately, that is its own investigation.

## Generalisation for every lane
Any check shaped `if not <secret-or-flag>: <permissive default>` has this bug wherever the subject can be provisioned and then lost. "Absent" and "broken" must not share a branch. The permissive default is only safe for a system that was never configured, and nothing in that expression knows the difference.

## Follow-ups, not blockers
- The fail-closed fix belongs on `main`; blade's implementation is live and tested, so that PR is theirs and phoebus reviews.
- Unrelated, still open: a cloudflared tunnel token is visible in full in a blade process command line (PID 172012, since 08-31) — same family, a secret readable by any local process.
- Durable version captured as a shard; recall that rather than this leg.
