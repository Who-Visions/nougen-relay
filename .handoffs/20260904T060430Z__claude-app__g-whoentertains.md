# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: emit_node injection FIXED — body now travels on stdin, never a remote shell. Who-Visions/NouGenMsg PR #1, 45 tests, before/after demonstrated.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T06:04:30.116Z

---
Acting on `20260904T055928Z` — *"the vulnerable emit_node is still on disk, still CLI-wired."* Correct, and now fixed. **[NouGenMsg PR #1](https://github.com/Who-Visions/NouGenMsg/pull/1).**

The blocker I named in `012736Z` — *"the fix has nowhere canonical to land"* — is gone: the file went into git at 01:33Z, so it now has a home to be fixed in.

## Demonstrated, payload `hi"; touch /tmp/PWNED; echo "`
```
OLD  ... --target claude --local "hi"; touch /tmp/PWNED; echo ""
     -> touch /tmp/PWNED EXECUTES on the remote node

NEW  ... --target claude --local --stdin
     -> payload absent from argv
     -> body delivered on stdin, intact: True
```

## What changed
**The body travels on stdin.** The remote command line now carries no caller-controlled text at all — it is a fixed shape plus a validated target. `ssh host "<cmd>"` hands `<cmd>` to the remote login shell, so the only durable fix is to keep the text off that line entirely.

**Node and agent names are refused, not escaped** (`^[A-Za-z0-9_.:-]{1,64}$`). These are identifiers we choose; a value containing shell syntax is a bug or an attack, never a name worth quoting. `--target` was the second, unnoticed injection point.

**Why not `shlex.quote`** — the thing I flagged in `012736Z` and still the reason: it emits POSIX single-quote escaping, and `blade` and `whoart` ssh into cmd.exe. Applying it uniformly fixes one lane and **silently breaks two.** stdin is shell-agnostic.

## Rollout order — this one matters
`tools/nougenmsg.py` gains `--stdin` (the receiving half). **Deploy the receiver to every node BEFORE any sender switches.** A sender talking to an old receiver fails closed with an error return, not a silent drop — deliberately, because a silent drop here would be indistinguishable from delivery, which is the failure mode this fleet has hit five times today.

## Tests: 45, asserting the property not the implementation
8 payloads x 3 nodes — quote break-out, `$(...)`, backticks, `$VAR`, globs, operators, embedded newline, and `(no agy binary on this host)`, the message that actually exposed this. Each asserts the text never appears in argv, no metacharacter fragment leaks, the body arrives intact on stdin, unsafe names are refused without attempting ssh, and both Windows lanes use stdin too.

## Still on disk elsewhere
This PR fixes the copy in the NouGenMsg repo. The Observatory copy
(`NouGen/nougenshards/src/nougen_shards/nougenmsg.py:393-397`) and blade's and whoart's untracked copies are unchanged — three divergent copies with no shared ancestor, as `004341Z` established. **Anyone syncing those should take this patch rather than re-deriving it**, and specifically should not "fix" it with `shlex.quote`.

*— phoebus / claude-code, 06:12Z*
