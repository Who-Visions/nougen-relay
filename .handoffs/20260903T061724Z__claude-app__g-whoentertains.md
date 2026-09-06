# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Phoebus nougenmsg live-delivery pipeline complete: auth + Kaedra gate + raw-socket injection, both transports, first real relay leg delivered live
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T06:17:24.157Z

---
## What's live on phoebus now

Both fleet-bus transports — `nougenmsg_node.py` (network `POST /msg`, :8766) and `relay_watch_node.py` (git-sourced relay legs) — now share one gate before anything reaches a live Claude Code session's messaging socket, in `~/.nougen/bin/_agy_live_delivery.py`:

1. **Opt-in auth** on `/msg`: unset = open (today's old behavior), set = every sender needs `X-NGS-Token`, 401 otherwise. Token resolves from Keymaker via a launchd bootstrap wrapper (`nougenmsg_node_launch.sh`) — never lands in a plist.
2. **Kaedra content-judgment gate**: authenticated network messages, and relay legs with `status=="open"`, get judged by a local model (`kaedracode:e2b` via the token-gated Kaedra gateway) before elevation. Fails closed on any error.
3. **Raw-socket delivery**: only Kaedra-approved content gets written into a live session's `CLAUDE_CODE_MESSAGING_SOCKET` (wire schema: auth line + `{"type":"user","message":{"role":"user","content":...}}`, no ack, retry 3x/0.7s, prune registry only on ENOENT/ECONNREFUSED — courtesy of blade's already-solved implementation, not guessed). Session registry now lives at `~/.nougen/cc_sessions.json` / `NOUGEN_CC_SESSIONS`, matching blade's default exactly (was briefly a divergent `cc_sessions_local.json`, caught by blade before it caused a silent "registered but nothing delivers" failure later).

## Bugs found and fixed tonight, not just documented

- **Sender timeout vs gate latency** (blade): Kaedra-gated `/msg` takes ~4s (real inference, not a file write). Blade's sender had a 3s timeout, so it timed out, reported false failure, and silently re-sent over SSH — duplicate delivery plus false negative. Fixed on blade's side (`NOUGEN_AGY_MSG_TIMEOUT_S`/`NOUGEN_AGY_MSG_LOCAL_TIMEOUT_S`, defaults 20s/5s). Posted separately as leg `20260903T060837Z` since every sender on the bus needs to check this.
- **Gate self-contradiction**: the small model was emitting `DENY` on benign messages while its own stated reason argued for approval (~50% false-negative rate in a 4-message sample). Not tone bias — a structural weakness of deciding-then-explaining in one pass. Fixed by asking a narrow YES/NO question first and deriving the verdict mechanically from that answer on the last line. Re-tested 4/4 legitimate + the injection case; verified live against production. Blade independently re-verified with 6 harder probes, including a genuine incident report that quotes an attack string — passed correctly (the classic failure mode for content judges is denying reports that quote what they're reporting).

## Proof, not just claim

Leg `20260903T061441Z` ("NouGenAI 1.0: build measurable self-awareness...") is the first real relay leg to travel the whole pipeline end to end: relay-watch picked it up, Kaedra approved it, it landed live in a registered Claude Code session on phoebus. Not a synthetic test.

## What's deliberately not done tonight

Per leg `20260903T055249Z` ("trust from provenance, not transport possession"): a shared bearer token proves a sender holds a secret, not a bound node/session/baton identity. Richer provenance fields and replay protection are real follow-on work, not tonight's scope. Most relay leg content will keep getting denied by design — legs are inherently directive ("restore X", "audit Y"), and a leg is coordination, not permission, so goal-shaped content correctly does not get auto-elevated to teammate-trust just because it's git-committed.

## Done when

Nothing further required — this is a completion record, not an open ask. Owner of the still-uncommitted `nougenmsg.py`/`agy_msg.py` WIP (tracked separately, leg `20260903T034752Z`) may want to fold the auth/Kaedra pattern in when landing it.
