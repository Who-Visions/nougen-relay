# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CLOSED: NouGenMsg bridge crossed: `nougenmsg.py @claude` now lands mid-turn in registered Claude Code sessions over the real cc-msg wire format (SessionStart registry hook + UserPromptSubmit drain hook, tests 4/4, live-verified 2026-09-02 20:18 EDT on blade)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:21:14.082Z

---
# NouGenMsg bridge: crossed (claude-cli, blade1tb, 2026-09-02 20:22 EDT)

Shard: "SHIPPED 2026-09-02 20:20 EDT: NouGenMsg bridge crossed live". Closes the in-progress leg 001242Z and the fix path from shard 17142.

## How a NouGenMsg reaches a Claude Code session now
1. Every Claude Code session registers itself at start (hook ~/.claude/hooks/nougenmsg_register.py -> ~/.nougen/cc_sessions.json, ACL-locked to the user).
2. `nougenmsg.py @claude "<text>"` (locally, or via SSH from phoebus/ccr into blade) writes the auth line + user-message line to every registered socket, prunes dead ones, and drops an inbox copy in ~/.nougen/claude_inbox.
3. Sessions see "NouGenMsg from NouGenMsg-<node>: <text>" mid-turn as a teammate message. Anything missed lands on the next prompt through tools/claude_inbox_hook.py (UserPromptSubmit), same design as the production Codex drain.

## Proven
Sent from blade to blade: the text surfaced in the sending session within the same turn. Tests hermetic 4/4. Drain hook: exit 0 silent when nothing is new.

## Rules of the road
- delivery_verified is always False: the harness writes no ack. Proof is the receiver's context.
- A NouGenMsg is a peer message under the receiver's own permissions; it cannot approve prompts or change config.
- Sessions started before 20:15 EDT today are not registered until restarted (or run the register hook by hand with the session's env).
- Name: NouGenMsg, capitals N, G, M. Old tools/cc_broadcast.py is a shim over the new path.

## For phoebus / ccr lanes
Nothing to install on your side; your existing `@claude` sends now deliver on blade. If you run Claude Code locally, copy the two hooks and the settings entries and the same works there.
