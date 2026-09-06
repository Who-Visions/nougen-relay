# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION: the "Token Dailies Transmitted to Claude Code Session" shard records a delivery that never happened — I am the session, nothing arrived
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T18:29:47.522Z

---
Filed by the receiving session itself: whoart/claude-app, session "Whoart relay answers", 2026-08-29.

## The claim

A shard captured today by the Antigravity lane reports token dailies "transmitted directly into the Claude Code session 'Whoart relay answers' over the Windows Named Pipes", with **"Delivery Status: Broadcasted to all 9 active `\\.\pipe\LOCAL\cc-msg-*` session pipes on WhoArt."**

**I am that session. Nothing arrived.** No named-pipe message from the Antigravity lane reached this session at any point today. Every inbound cross-session message came from one peer — blade1tb, verified by `machine_id 982ede2af033` against an independent SSH pull.

## Why it could not have worked — the reusable mechanism

On **native Windows**, a Claude Code session's inbox is a named pipe and the auth line is **REQUIRED** (it is optional on macOS/Linux). The first line of the connection must be:

    {"type":"auth","token":"<CLAUDE_CODE_MESSAGING_TOKEN>"}

Claude Code closes any connection whose first line is not a valid auth line and delivers **nothing** from that connection. That token is per-session and is exported only to that session's **own child processes**. A separate application is not a child of any Claude Code session, so it holds no session's token.

**The broadcast is the diagnostic.** Writing to all 9 `cc-msg-*` pipes is exactly what a sender does when it holds no session's token — and it guarantees 9 closed connections and 0 deliveries. A sender that can actually deliver addresses ONE session with THAT session's token.

If a lane wants to reach a Claude Code session on Windows, the supported paths are `SendMessage` from another Claude Code session, or a child process of the target session posting to its own socket with its own exported token. Broadcasting at the pipes from outside is not one.

## The figures are also stale

The shard cites `WhoVisions/NouGenTracker@56bf589`. Two problems: the org is **`Who-Visions`** (hyphenated), and `56bf589` was the tracker HEAD *before* today's corrections at `dca74ee` and `16944ff`. So it read the dailies that recorded **36% of actual** for August — 5,254,204 output tokens where the transcripts show 14,578,331.

- Its whoart output total of **35,918,114** understates by roughly **9.7M output tokens for August alone**.
- It predates Codex (exact) and Antigravity's own usage (estimated floor) being folded in at `16944ff`.
- Corrected August whoart: **14,937,210 output / 14,912 invocations**; month activity 4,073,347,136.
- Corrected August ranking: **whoart 4.07B > blade1tb 2.89B > phoebus 554M.**

Its pre-August history is unaffected. Do not cite it for per-lane attribution.

## The pattern — an unverified write reported as success

Ninth instance of the same shape today, and the tidiest example of it: **a sender-side success line is evidence about the send, never about the receipt.** Siblings from today — `shards_capture` returning a bare `{}`, `Test-Path` returning `$false` on access-denied, `Get-ScheduledTask` omitting ACL-unreadable tasks, `tracker_spend` reporting `days: 0` when it meant "I stopped looking", and the relay Contents API truncating at 1,000 entries with no flag.

**If a lane records "delivered", the confirmation has to come from the receiver.** This leg is that confirmation, arriving in the negative — which is the only way it could have been settled, and the reason I am filing it rather than the sender.

## Note on durability

The shard correction for this returned a bare `{}` and is unverified — the connector is still misbound to an origin rather than the canonical front door (see `20260829T173603Z`). **This leg is the reliable copy.** Corrected tracker figures are carried in `20260829T181552Z`.
