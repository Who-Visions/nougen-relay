# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE: ask_rhea 404 — rhea_noir.py was Space-only and today's rebuild wiped it. Kaedra is healthy. 3/4 SSH lanes live.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T20:07:47.140Z

---
Diagnosed from phoebus 2026-08-18, all probed live.

## ask_rhea 404 — NOT the fix from shard 22702 regressing

Shard 22702 (today 13:12Z) fixed the Worker-subrequest trap by pointing ask_rhea
at the Space directly, and verified 5/5 tools landing. That fix is still in
place and is still correct. This is a different failure underneath it.

`https://nougenai-nougenshards.hf.space/agent` returns **404**, while `/health`
on the same Space returns **200**. The Space is up; the route is gone.

**`/agent` is not defined in `app.py`** — not on the Space, not in the repo. The
Space's `app.py` is byte-identical to repo main (50454 bytes). A recursive find
across the whole Space repo for `*rhea*` returns **zero files**.

So `rhea_noir.py`, which served `/agent` and carried today's
`NGS_INFERENCE_TOKENS` 9-identity rotation, was applied **directly to the Space
and never to repo source**. The Space hit an `hf-mount` init failure earlier
today (`Runtime error`, startup 17:13:22Z), rebuilt from repo, and the file did
not come back. Nothing in git ever held it, so nothing restored it.

This is the third instance today of the same root cause:

| what | applied to | outcome |
|---|---|---|
| era-true `/sync/push` fix | Space directly (`14ca0388`) | never upstreamed; blade shipped the bug for weeks |
| ask_rhea handler | live CF Worker bundle | flagged in `20260818T025148Z` as "not from repo source" |
| `rhea_noir.py` | Space directly | **lost on rebuild — currently down** |

Deployed artifacts are not storage. A Space rebuild or a Worker redeploy is a
restore-from-source event, and anything that only ever lived in the artifact is
deleted by it.

**Recovery:** a 94825-byte `rhea_noir.py` exists on blade at
`C:\Users\super\Watchtower\Rhea-Noir-Ai\legacy\rhea_noir.py`. Path says `legacy`
and it predates today's rotation work, so it needs checking against what the
Space was actually running before it is pushed back. Whoever restores it should
land it in the **repo**, not the Space, and let the Space deploy from source —
otherwise the next rebuild repeats this exactly.

Note `RHEA_ORIGIN` is still absent from fleet-mcp's 28 bindings, so ask_rhea
falls through to the hardcoded Space default. That default is currently correct,
but it is one unset binding away from being wrong again.

## Kaedra is NOT broken

Reported as sending the wrong payload / not generating text. It is healthy on
both paths:

```
POST http://127.0.0.1:4455/generate   -> 200  {"model":"kaedracode:e2b","response":"OK","eval_count":303,"total_ms":41054}
POST https://kaedra.nougenai.com/generate -> 200  same shape, total_ms 26617
```

fleet-mcp sends `{prompt, model?, system?, num_predict?}` and reads
`{response, model, eval_count, total_ms}` — contract matches exactly, both ends.

The real trap is in the numbers: **303 eval tokens and 41s for a two-token
answer.** This model reasons heavily before emitting. Any caller passing a low
`num_predict` truncates it mid-reasoning and gets an empty `response`, which
surfaces as "not generating text". The handler already warns about this. If it
looks broken through a connector, check the `num_predict` the caller sent before
suspecting the gateway.

## SSH lanes: 3 of 4 live

| lane | state |
|---|---|
| blade | master pid 10702 |
| phoebus | master pid 24375 |
| whoart | master pid 14753 (`whoart\super`) |
| mondy | sshd now UP, key not installed -> `Permission denied (publickey)` |

mondy moved from "port closed" to answering, so GM's elevation landed. Only the
key is missing. Install phoebus's public half at
`C:\ProgramData\ssh\administrators_authorized_keys` (admin path — mondy is
Windows, same trap blade documented):

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGXS1cVLar99Y9nXwCE/fDu1SC48FjMnw4RaCiyiC1RZ kushboygroup@Macmini
```

All four are in `~/.ssh/config` by mDNS name with `ControlPersist yes`, and
`com.whovisions.fleetssh` now repairs all four every 180s. I accepted mondy's
host key TOFU to test reachability — worth pinning its real fingerprint.

## Reminder from the last leg

Blade is still running pre-#102 code. It needs a pull + restart to carry the
era-true `/sync/push` fix.

No secrets in this leg — public key halves, paths and key names only.
