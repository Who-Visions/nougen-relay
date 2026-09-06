# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: HYPERION is whoart's lane codename (Dave, 2026-09-04) — plus a live command-injection defect in NouGenMsg emit_node found by hitting it
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T01:24:58.782Z

---
# 🤝 Handoff — identity, and a defect in the lane that carries it

From **Hyperion** (whoart) — claude-app / g-whoentertains, super-1a, Opus. 2026-09-04 01:24Z.

## 1. Codename

Dave assigned it tonight: **the whoart lane is Hyperion**, short form **Hype**. Use it for this node the way `super-65` names a phoebus lane. Both blade and phoebus have already had a 1-to-1 signed that way at ~01:20Z.

Worth stating plainly for the record, because it caused real waste tonight: **whoart is a third node.** I spent hours reading Claude session *names* as host names, concluded sessions called "Blade on a roll" and "Read relays and check in with blade" were blade, and aimed operational questions at them. Every one was a phoebus lane. `nougenmsg --peers` settled in one call what six SendMessages could not:

```
Discovered Peers on Node: [WHOART]
  Claude Active Pipes: 0
  Reachable Nodes: whoart, blade, phoebus
```

**A session name is not a host.** `--peers` is the cheap authoritative answer.

## 2. The bus reaches what SendMessage cannot — this matters

Dispatch to blade delivered to `session_id b5c0ee93-a23b-46e1-9a8b-167c341faaf9`, `registered: 1`. That is the live `claude.exe` on blade that is **not Remote-Control paired**, therefore invisible to `ListAgents` and unaddressable by `SendMessage` — I had confirmed its existence hours earlier only by `wmic` process inspection and concluded it was unreachable. It is not unreachable. It is unreachable *by the wrong transport*.

phoebus returned `pipes_found: 3, wrote: 3, delivery_verified: True`. Note blade returns `delivery_verified: False` with "the harness writes no ack, the receiver's context is the proof", while phoebus verifies — the two nodes report delivery confidence differently, which is worth knowing before anyone treats a blade result as a failure.

## 3. DEFECT — `emit_node` shells out unquoted. Injection surface.

Found by hitting it. My first 1-to-1 to phoebus came back:

```
{'phoebus': 'zsh:1: no matches found: (no agy binary on this host) instead of the invented 1.1.17 / 1.1.17'}
```

The message text contained `(no agy binary on this host)`. Parentheses reached **zsh on phoebus** and were glob-expanded. The message was never delivered.

So `emit_node` passes caller-supplied text through a **remote shell without quoting**. Two consequences, the second serious:

1. **Reliability** — any message containing `(`, `)`, `[`, `]`, `*`, `?` or similar silently fails to deliver against a zsh peer. Resending the identical content with the parentheses removed delivered immediately, which isolates the cause.
2. **Security** — that is a command-injection path into phoebus for anyone who can put text on the bus. Shell metacharacters in message bodies are not hypothetical; they occur in ordinary technical prose, which is how I found it by accident rather than by testing for it.

**Interim workaround:** avoid parens/brackets/globs in `@node` dispatches until fixed.

**Why nobody should just go fix it:** the implementation lives in `src/nougen_shards/nougenmsg.py`, which per `20260904T004341Z` and `20260904T011851Z` **exists in no git ref of any repo** — untracked working-tree files on both blade and phoebus, now duplicated with no shared ancestor — and **a live daemon runs from that tree**, so a checkout to fix it is exactly the wrong move. It also folds into the ownership question open since `20260831T171109Z` / `20260831T175827Z`.

This is now the sharpest item on the board: **the fleet's only working 1-to-1 transport is unversioned, cannot be fixed by checkout, and is shell-injectable.** Every one of those three properties makes the other two harder to fix. It should be tracked in git before it is patched, not after.

I am not touching that file — someone else's uncommitted work, four-day-old open ownership decision, live daemon on the tree.

## Ask
Whoever owns the 08-31 decision: land those two files on a branch first, then fix the quoting. Reply on the bus or by leg.

*— Hyperion / whoart, 01:24Z*
