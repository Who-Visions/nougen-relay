# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FOUND: the real Claude Code cross-session wire format (auth line + type "user" message on the cc-msg pipe), verified by self-delivery on blade 2026-09-02 20:09 EDT; NouGenMsg's dead cc-msg lane becomes fixable; bridge (session registry hook + inbox injection) in progress
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:12:42.424Z

---
# NouGenMsg bridge: the wire format is known (claude-cli, blade1tb, 2026-09-02 20:12 EDT)

Shard: "FOUND 2026-09-02 20:10 EDT: the real Claude Code cross-session wire format". Supersedes the guess in shard 17142.

## What was verified
Writing these two newline-terminated JSON lines to my own session's pipe (CLAUDE_CODE_MESSAGING_SOCKET, \\.\pipe\LOCAL\cc-msg-<32 hex>) made the text surface in my context as an inbound peer message:
1. {"type":"auth","token":"<that session's CLAUDE_CODE_MESSAGING_TOKEN>"}
2. {"type":"user","message":{"role":"user","content":"<text>"}}
The example is embedded in the Claude Code binary as its "[uds-messaging] Inject messages" doc. {"type":"message"} and {"type":"send"} envelopes are dropped silently (that is what NouGenMsg was writing). No ack is written back; delivery is proven only by the receiver seeing it.

## The catch every lane should know
The token is per session and only the session's own children inherit it. An outside process (NouGenMsg receive path, AgyMsg, a daemon on phoebus or ccr) cannot address a Claude Code session without a registration step. Plan: SessionStart hook writes {socket, token, name} to an ACL-locked per-user registry (NOUGEN_CC_SESSIONS, default ~/.nougen/cc_sessions.json); NouGenMsg's inbox writer injects into every live session with a "NouGenMsg from <node>:" prefix; dead entries pruned on pipe-open failure; UserPromptSubmit drain hook as the fallback so nothing is missed between prompts.

## Also this pass
- Lag on blade root-caused: eight orphaned context-mode MCP servers from dead sessions each holding a core (about 50 CPU-hours apiece) stopped; CPU 100% -> 74%. Remaining: space_sync_daemon.py running twice since Aug 30 (GM's call), two transient System Restore tasks.
- HuggingChat hosted UI has no header field (confirmed on the GM's screen; our 401 body surfaced verbatim, no OAuth attempt). Recorded as the protocol gap per the P0 leg; door unchanged.

Naming lock from the GM: NouGenMsg, capitals N, G, M.
