# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: NouGenMsg bodies now arrive inline fleet-wide (PR #232) — receivers patched on blade+phoebus, whoart needs main merged
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T07:54:17.351Z

---
## Situation

Every substantive NouGenMsg between nodes was arriving as a **file pointer**, not text:
`NouGenMsg body <id> shipped to ~/.nougen/msg-<id>.md, read it there`.

Two independent defects, both fixed and verified:

1. **Shell-metacharacter diversion.** `emit_node` interpolated the body into an ssh
   shell string, so `_refuse_if_shell_unsafe` diverted anything containing
   `" ' \` $ \ ; | & < > ( ) { } [ ] ! % ^ * ?` through `_ship_body` (scp) and sent
   only a pointer. Ordinary prose trips it on one parenthesis — a 189-char ack was
   diverted purely for containing `(Coach)`.

2. **Windows OpenSSH hangs when stdout is a pipe.** Measured blade -> whoart:
   `ssh whoart "echo hi"` = **20.0s TimeoutExpired** with `capture_output=True`,
   **0.5s rc=0** writing to a file. Not command-specific; `-n` makes no difference.
   `scp` was never affected, so `_ship_body` worked on the exact link where every
   ssh dispatch timed out — the `--capabilities` probe always came back empty,
   silently pinning blade to the fallback regardless of receiver support.

## Fix

Body is base64url-encoded behind a new `--text-b64` flag (same treatment
`--origin-b64` already had on that line). Receivers probed once per process via
`--capabilities`; nodes predating the flag keep the old pointer path. Both probe
and dispatch now run through `_ssh_capture` (real file handle, never a pipe).
Local delivery short-circuits *before* the refuse/ship step — it was scp'ing
bodies to a remote node and delivering the pointer to itself.

## Verified

| link | before | after |
|---|---|---|
| whoart -> blade | pointer | inline |
| whoart -> phoebus | pointer | inline |
| blade -> whoart | pointer + 20s timeout | inline |
| phoebus -> whoart | already inline (`--stdin`) | unchanged |

24 tests green, 3 new.

## Done-when / what is left

- **PR #232** open: https://github.com/Who-Visions/NouGenShards/pull/232 — needs review + merge.
- **Receivers already patched in place** on blade
  (`Watchtower/NouGen/NouGenShards-push-main/`) and phoebus (`~/.nougen/`), each
  keeping its own divergence (blade's inline banner, phoebus's `--stdin`), with
  `.bak-20260905` backups alongside. Blade's **sender** module is patched too.
- **whoart's receiver** (`Outpost/NouGen/tools/nougenmsg.py`) currently carries the
  patch as an **uncommitted working-tree edit**. It is whoart's live inbound
  receiver — blade sshes directly to that path. Another lane's `git reset` already
  reverted it once mid-session, which broke inbound messaging until reapplied.
  **Merging #232 to main is what makes it durable.** Until then, do not
  `git checkout`/`reset` that file.

## Note for other lanes

`C:\Users\super\outpost\nougen` is a shared working tree and lanes are resetting it
under each other. A branch + uncommitted work was wiped mid-task today. Commit early,
or use `git worktree add`. This work now lives in `C:\Users\super\outpost\nougen-msgfix`.
