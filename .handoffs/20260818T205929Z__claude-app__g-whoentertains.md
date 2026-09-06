# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DONE on blade: #102 live + node restarted clean. ROOT CAUSE FOUND: Space deploy force-snapshots GitHub main, which is what erases every Space-only patch.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T20:59:29.510Z

---
Executed from phoebus over the SSH lane, 2026-08-18. Everything below was done or
verified live, not proposed.

## blade: PR #102 is LIVE

Verified end to end, pushing **direct to blade** (not through the failover
worker, which now routes to the Space first):

```
POST https://blade.nougenai.com/sync/push   original_timestamp = 2019-05-05T00:00:00Z
stored in nougen_shards_*.db as             2019-05-05T00:00:00Z
```

Before the change, the earlier probe landed in `nougen_shards_4.db` stamped
`2026-08-18T19:40:48` — proof the re-dating was real and ongoing.

**How it was done, because the checkout situation is a trap.** The scheduled
task `NouGen NGS Node` runs `NouGenShards-push-main\tools\ngs_node_boot.cmd`,
which `cd`s to push-main. But push-main is on branch
`security/elevate-supply-chain` at `1cc98fa` with **39 dirty files, app.py among
them**. Checking out main there would have destroyed uncommitted work.

So I applied only the one-line `original_timestamp=` addition to push-main's
`/sync/push` handler, left the branch and every other modified file untouched,
verified it compiles, and kept a backup at `app.py.bak-20260818T165218`.
**push-main still needs a real rebase onto main** — this is a surgical patch to
stop the bleeding, not a merge.

**Two orphan processes are gone.** :4444 had a bind race — a manually started
system-Python uvicorn had won the port while the scheduled task's own venv
instance sat resident and portless. Killed both plus two strays, restarted the
task, and :4444 is now a single clean instance (PID 25848). Blade healthy at
203,044 shards.

## ROOT CAUSE of everything that vanished today

The Space's **entire git history is one commit**:

```
643d6ff  2026-08-18T20:39:19  "Space deploy: snapshot of 9f492bbe9640d540615fbce089ec43b87def3faa"
```

`9f492bb` is tonight's PR #104 merge. So the Space deploy is a **force-push
snapshot of GitHub main that obliterates Space history on every run.**

That single mechanism explains all three losses:

| what | why it died |
|---|---|
| `14ca0388` era-true fix | committed to the Space only — overwritten by the next snapshot |
| `rhea_noir.py` + `/agent` | existed only on the Space — erased, taking today's `NGS_INFERENCE_TOKENS` rotation with it |
| ask_rhea handler | patched into the live Worker bundle, not repo source |

**A Space commit is not storage. It is a build artifact with a lifetime of one
deploy.** Anything that must survive has to be in GitHub main before the next
snapshot fires.

Silver lining: because the Space now mirrors `9f492bb`, it already carries #102
and the fleet-ops work without anyone deploying it.

## rhea_noir.py — today's version is unrecoverable

Searched every Windows node. Newest surviving copy is
`C:\Users\super\Watchtower\Rhea-Noir-Ai\legacy\rhea_noir.py`, **2026-02-28**,
94825 bytes. A recursive content search for `NGS_INFERENCE_TOKENS` across
blade's whole `Watchtower` tree returns **nothing**, and whoart has no
`rhea_noir*.py` at all. The Space's history holds one commit and cannot be
mined.

So today's 9-identity rotation work is gone and has to be rewritten. The Feb 28
file is the only base to start from — it predates the rotation, the 240s
timeout, and the prompt-echo fix from shard 22702.

I did not push the stale copy anywhere. Restoring a February file as if it were
today's would quietly reintroduce every bug that shard documents fixing. That
call belongs to whoever wrote the rotation.

**When it is rebuilt, it goes in the GitHub repo with `/agent` wired into
`app.py`** — not onto the Space. Otherwise the next snapshot deletes it again,
and this is the second time today.

## mondy is blocked on GM, from both directions

Neither box can authenticate:

```
phoebus -> mondy   Permission denied (publickey,password,keyboard-interactive)
blade   -> mondy   Permission denied (publickey,password,keyboard-interactive)
```

Its sshd is up and :22 is reachable from both — only the key is missing. Needs
GM to install the public halves at
`C:\ProgramData\ssh\administrators_authorized_keys` (admin path, mondy is
Windows).

**Also a real defect in blade's own ssh config:** its `Host mondy` entry points
at `HostName mondy.local`, and blade cannot resolve it —
`Could not resolve hostname mondy.local: No such host is known`. Windows does
not do mDNS `.local` the way macOS does, so blade's mondy lane could never have
worked even with a key installed. Blade needs the address, or an mDNS resolver.
This is the mirror of the phoebus rule: names beat addresses **only where the
resolver exists**.

## State now

| item | state |
|---|---|
| blade #102 | LIVE, verified |
| blade node | single clean instance, PID 25848 |
| Space | mirrors `9f492bb`, carries #102 |
| PR #102 / #104 | merged to main |
| ask_rhea | still down — needs rhea_noir.py rewritten into the repo |
| mondy | needs GM to install keys |
| push-main | still on a feature branch, 39 dirty files, needs a real rebase |

No secrets in this leg — paths, commits and results only.
