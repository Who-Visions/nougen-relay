# 🤝 Git Handoff — mondy / claude-cli

**Goal**: blade: rotate both per-lane gateway tokens (pre-public hygiene)
**Branch**: `main` @ `4b7a0ed`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-08-14T17:47:45.216630+00:00

---
# Rotate the two per-lane gateway tokens (pre-public hygiene)

**From:** mondy/claude-cli — 2026-08-14

## Why
GM is splitting the relay engine into a public repo. The engine tree is
scrubbed, but this registry's history quotes the two per-lane gateway token
IDs from your 2026-08-06 leg (fleet 14c93e5133aa, claude-client 6eec914cb9f3).
The registry stays private, but IDs that have been written down get rotated
on principle before anything adjacent goes public.

## Ask (blade)
1. Rotate both per-lane gateway tokens on the mcp.nougenai.com gateway stack.
2. Store the new values via Keymaker only — do not write values or new IDs
   into any leg; ack with "rotated" and nothing else identifying.
3. Confirm `.gateway_token.retired-20260805` and any other retired token
   files are deleted, not just renamed.

## Done when
Both lanes authenticate with fresh tokens and no retired token material
remains on disk.
