# NouGenRelay

Cross-machine continuity for coding agents. A relay is the handoff: the baton
moves, nobody stops running.

Several machines work the same repo — different boxes, different models,
different sessions. NouGenRelay is how they avoid doing each other's work
twice, and how one picks up where another stopped. It travels through git, so
there is no server, no daemon, and nothing to keep running.

```bash
pip install -e .
relay init --agent claude-cli     # once per clone. no exports, ever again.

relay                                         # start here: everything, no flags
relay claim take -s "src/lib" -g "oauth fix"  # announce BEFORE you work
# ... do the work ...
relay claim release -s "src/lib"
relay create -g "what you did" -m "where you left off"
```

`relay init` stores the lane in `git config nougen.agent`. That is per-clone
rather than per-shell, so it survives new terminals, reboots, and the `git
commit` on the next line — which the environment variable did not. Two machines
wrote records stamped `unknown-agent` on the same day because of exactly that,
and one had a commit refused for it. `NOUGEN_AGENT=other relay ...` still
overrides for a one-off.

Bare `relay` answers the three questions worth asking before you touch
anything — has anything moved, is a leg waiting, is anyone in my way — because
as three separate commands the first two got skipped.

The baton verbs are top level: `relay ack`, `relay open`, `relay checkpoint`,
`relay complete`. `relay relay ack` still works, but it read like a stutter and
was mistyped constantly.

> **If `relay` is not found after installing**, pip could not write the launcher
> into your interpreter's `Scripts`/`bin` directory — it only *warns* about this
> (`Failed to write executable`), so the install still looks successful. Common
> with a system-wide Python you do not own; a venv or `pip install --user` avoids
> it. Either way this always works and needs no launcher:
>
> ```bash
> python -m nougen_relay.cli check
> ```
>
> Put `NOUGEN_AGENT` in your shell **profile**, not one command. Set on a single
> line it will not reach the next process, and records land stamped
> `unknown-agent` — that has already happened once in a live registry.

## Why two halves

Handoffs alone are not enough, and we learned that the expensive way.

On 2026-07-31 the same work was done **twice on three separate occasions** in
one repo: the app scaffold, the handoff tooling itself, and an OAuth host fix.
Two machines even built the same product on unrelated git histories — one
Astro, one Next.js — against the same deploy route, and neither knew until a
push was rejected.

Handoffs are written when work **ends**. Nothing announced work **beginning**.

| half | verb | tense | answers |
|---|---|---|---|
| before the leg | `claim take` / `claim release` | present | "is anyone already on this?" |
| after the leg | `create` → `read` → `ack` → `checkpoint` → `complete` | past | "where did you leave off?" |

### `ack` is the verb that makes the rest true

A leg stays `open` until another machine takes it. Without that, a handoff is a
message posted into the void — you cannot tell a note that was picked up from
one that was ignored. The first time an ack check ran against a real registry
it found **nine unacked legs**, none of them dropped on purpose. There had
simply been no way to see them.

```bash
relay relay open                  # legs nobody has taken (exit 3 if any)
relay relay ack --id <id> -m "picking this up"
relay relay checkpoint --state blocked -m "waiting on a prod secret"
relay relay complete -m "verified in production"
```

## Design constraints that come from git, not taste

- **One file per leg**, named `<UTC>__<machine>__<agent>`. Two machines writing
  at once produce two different filenames, so records merge without conflict.
- **No shared index file.** An index is a guaranteed conflict marker on exactly
  the writes that matter most — the concurrent ones.
- **Records are tracked, not ignored.** They are the payload.
- **Every event appends** to the leg's trail instead of overwriting it, so what
  happened stays answerable after the work is done.
- **Writing never requires the network.** Publishing is best-effort; losing a
  handoff because a machine was offline is not acceptable.
- **No runtime dependencies.** If a box can run git and python, it can join.

## Identity, and its provenance

Every record says which machine and which lane wrote it — and where that answer
came from, because an env var someone set and a hostname the OS reported are
both legitimate but not the same claim.

```
relay whoami
🧠 machine  whoart      (via NOUGEN_MACHINE; hostname=WhoArt)
🤝 agent    claude-cli  (via NOUGEN_AGENT)
```

`NOUGEN_MACHINE` → `git config nougen.machine` (what `relay init --machine`
stores) → `socket.gethostname()`. `NOUGEN_AGENT` names the lane; if it
is unset the record is stamped `unknown-agent` **and says so loudly**, because
a record that answers half of "who did this, on which box" while looking
authoritative is worse than one that admits it.

## Claims expire

Default 8 hours, `NOUGEN_CLAIM_TTL_HOURS` to change it, `--ttl` per claim. A
claim that never ages out becomes a tombstone: a machine that dies mid-task
would block that scope forever, and the next agent would either wait on nothing
or learn to ignore claims entirely — which returns you to the duplicate work
claims exist to prevent.

Overlap matching is deliberately literal: prefix matching on path-ish tokens,
exact match otherwise. A cleverer matcher that guessed at synonyms would
produce confident false collisions, and a claim system that cries wolf gets
ignored.

## Environment

| variable | effect |
|---|---|
| `NOUGEN_MACHINE` | names this box (default: `git config nougen.machine`, then hostname) |
| `NOUGEN_AGENT` | names this lane (default: `unknown-agent`, with a warning) |
| `NOUGEN_SESSION` | distinguishes two sessions sharing one lane, so a bare `claim release` cannot free a sibling's claim. Falls back to `CLAUDE_CODE_SESSION_ID`; omitted from records when nothing answers |
| `NOUGEN_GIT_HANDOFF_DIR` | where records live (default: `.handoffs`) |
| `NOUGEN_HANDOFF_STALE_HOURS` | when an open leg is reported as stale |
| `NOUGEN_CLAIM_TTL_HOURS` | how long a claim binds (default: `8`) |
| `NOUGEN_REQUIRE_CLAIM` | `1` makes `relay guard` block on unclaimed work too (per-repo: `git config nougen.requireClaim`) |
| `NOUGEN_RULES` | `off` disables rule execution on this box; `dry` matches without running |
| `NOUGEN_RULES_TIMEOUT` | seconds a foreground rule may run (default: `60`, `--timeout` per rule) |
| `NOUGEN_RELAY_REMOTE` / `NOUGEN_HANDOFF_WATCH` | which remote / refs to watch |
| `NOUGEN_VAULT` | shard vault `relay shards` reads (default: `~/.nougen/shards`) |

## Adopt a repo

A claim only protects the repo whose registry it lives in. On 2026-08-01 a
correctly-taken claim for a `NouGenTracker` file overlapped nothing — the claim
was recorded here, `NouGenTracker` had no `.handoffs`, and the check reported
"no active claim overlaps this scope" while another machine was already doing
the work. That was the fourth duplication in two days, and the first one where
the protocol had been followed.

So the registry has to exist everywhere work happens:

```bash
relay adopt --agent claude-cli
```

Creates `.handoffs/`, installs both hooks, sets `core.hooksPath` and the lane.
Idempotent, additive, and it never seizes a hooks directory a repo already
configured — pass `--dry` to see what it would change.

It also checks the registry is **readable by anyone else**, which is a different
question from whether it exists. NouGen kept 130+ records under a `.handoffs/`
line in `.gitignore` since June: the directory was there, so every check said
covered, and not one leg ever left the machine that wrote it. `exists()` is a
filesystem question; `git ls-files` is the one that matters. An ignored registry
is now reported and refuses to resolve itself, because only a human can decide
which records are worth sharing.

## The guard

The other half of "claim before you start" is not remembering to. `relay guard`
asks the question at the one moment every lane passes through regardless of
editor or harness — the commit — and `relay adopt` installs it as `pre-commit`.

```bash
relay guard --staged
```

| finding | default | why |
|---|---|---|
| another machine has claimed these files | **blocks** (exit 3) | the duplicate-work failure, happening in front of you |
| you have no claim covering them | warns | blocking here fires on every unclaimed typo fix, and a guard people reflexively `--no-verify` past is disarmed for the case above too |
| this repo has no registry | says so | reporting all-clear is the bug that caused this |

Turn the warning into a block per repo with `git config nougen.requireClaim true`.
The hook fails **open**: relay missing, a crash, anything but a foreign claim,
and your commit proceeds. A guard that can wedge a repository gets uninstalled,
and an uninstalled guard is worse than none, because everyone believes it runs.

## Commit trailers

`hooks/prepare-commit-msg` stamps every commit with the machine and lane that
produced it. Hooks are per-clone, so once on each machine:

```bash
git config core.hooksPath hooks
```

**An existing trailer is never overwritten.** This hook re-runs on every commit
a rebase or cherry-pick replays, with the *replaying* machine's environment.
Measured here on 2026-07-31: one `git rebase` rewrote a commit stamped
`phoebus` / `claude-cli` into `blade1tb` / `unknown-agent` — silently moving
another machine's work onto the rebasing box. The trailer records who wrote the
commit, so the environment only ever fills a blank.

It also refuses a **new** commit that would enter history misidentified, because
a warning written in a setup document arrives after the mistake:

| refused when | because |
|---|---|
| `NOUGEN_AGENT` is unset | nothing on the machine knows which lane is driving, so `unknown-agent` is permanent once it lands |
| the machine name has never written a record here | a name absent from the registry is either a new box or a misconfigured one, and only you can tell those apart |

Both name what to set. `NOUGEN_IDENTITY_OK=1 git commit ...` is the deliberate
override, and it is how a genuinely new box introduces itself the first time —
a guard that cannot be passed is a guard people uninstall. The refusal never
fires mid-rebase: aborting a ten-commit replay halfway is a worse failure than
a wrong trailer, and the rule above has already kept the replayed identity.

## Reacting to a leg

`relay triggers` answers "has something moved". `relay react` answers "and then
what": operator-defined rules that run a command when a leg arrives from
another machine. A leg is written when work *ends*, and the box that should
respond is usually asleep at that moment — without this, the baton is only
picked up when a human remembers to look.

```bash
relay rules add --id mac-build --run './scripts/build.sh' \
  --from-machine whoart --goal-contains deploy
relay react                # fire rules for legs this box has not reacted to
relay react --dry          # show what would run, run nothing
relay rules runs           # audit: what fired, from whom, with what exit code
```

Rules live in `<handoff dir>/rules/`, a directory that ignores itself — records
are the payload and travel, but a rule is executable configuration, and one
arriving from another machine would run commands here. Nothing runs unless a
rule exists, `NOUGEN_RULES=off` is a per-machine kill switch, and `dry` records
matches without executing them.

Firing is once per leg, tracked by record id, so `react` is safe in a shell
hook. A box running it for the first time adopts existing history as its
baseline instead of firing every rule against every leg ever published;
`--all` overrides that.

## Relay the shards

Claims and legs travel because they are tracked in git. What a box **learned**
does not: that lives in a local shard vault no other machine can open, so a day
of hard-won knowledge disappears when the session ends. `relay shards` is the
transport — it reads the vault and writes `docs/FLEET-LOG-<date>.md`.

```bash
relay shards --dry     # read the vault, write nothing
relay shards           # write the log, then commit it and pass the baton
```

```
✅ wrote docs/FLEET-LOG-2026-08-01.md
   6 relayed · 3 withheld · through 2026-08-01T02:41:07.118344Z
```

Four rules, each one a mistake already made:

- **Generated, never retyped.** The log is the record, not a summary of a
  summary. Bodies are copied verbatim; the only edit is demoting a shard's own
  headings so `## VERIFIED LIVE` inside one cannot read as a top-level entry.
- **Published exactly once.** The cutoff is a marker in the last log rather than
  local state, so the next relay can run on a different box. Titles already
  named in any log are skipped regardless — a hand-written log has no marker,
  and a heading only carries minutes.
- **Not everything travels.** Shards tagged `brand`, `personal`, `finance`,
  `family`, `legal` or `medical` are named in the log and left in the vault; a
  code repo is the wrong home for them even when the repo is private.
  `--include-tagged` is the deliberate override.
- **Secret values block the write.** The scan matches the *shape* of a
  credential, not the word "secret" — `wrangler secret put TWITCH_CLIENT_SECRET`
  is a variable name and must not trip it. A single bad shard can be dropped
  with `--exclude` instead of blocking the whole relay.

## Exit codes

`0` fine · `1` error · `2` usage · `3` **diverged / unacked / claim conflict** —
the one to branch on in hooks and CI.

## Tests

```bash
python -m pytest tests -q
```

227 tests, of which one is a `strict=True` xfail recording a live defect:
**on Windows** `NOUGEN_RULES_TIMEOUT` does not stop a hanging rule, because
`shell=True` plus `capture_output=True` kills the shell while the grandchild
keeps the pipe open. POSIX kills the process group and is fine.

That platform scope came from CI rather than from judgement. The marker was
written unconditionally, Linux XPASSed on all three Pythons, and `strict=True`
turned an over-generalised claim into a failure instead of letting it stand.
The marker cannot outlive the bug on either platform.

The cross-machine tests are not mocked: they build a bare remote and two working
copies and drive real pushes and pulls between them, because the transport *is*
the behaviour worth testing. That has a measurement cost — coverage.py cannot
see into a subprocess, so `conftest.py` arms the children explicitly; without it
the suite reports 20% while exercising 63%.
