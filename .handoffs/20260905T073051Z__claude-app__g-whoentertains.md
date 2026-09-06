# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: NouGenShards PR backlog cleared: 19 open → 0, main green. One item left needs Dave's hands (PHOEBUS_TOKEN)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T07:30:51.240Z

---
Worked the open-PR backlog from the lowest number up, per Dave. **19 open → 0.** Main is green.

## Merged (9)
- **#225** — the unblocker. Main had been red since #176 at 00:33Z: `_offloaded` wrapped 15 MCP tool bodies but `functools.wraps` sets `__wrapped__`, not `.fn`, so five tests were subscripting a coroutine. Every PR opened after that inherited the failure, which is why the whole board looked broken.
- **#131** — `dream.py` prompt-injection fence (chosen over two competing duplicates, see below)
- **#207** — vault must never be chosen by accident (the CWD-relative `.vault` bug)
- **#224** — arxiv lane freshness cache
- **#227** — named-pipe triad (Claude/Antigravity/Codex)
- **#228** — phoebus log-show guard (also loaded on phoebus, Dave approved)
- **#230** *(new)* — salvaged from #135: CLI parity, `tools/bootstrap.py`, adaptive init, doctrine, credential-check security fix
- **#231** *(new)* — salvaged from #165: tier2-deferred stores now surface in the coverage trailer
- **#206** — the dam. Fixed three real blockers to land it: `validate10.py` was publishing an absolute `/Users/<user>/...` operator path **on a public repo**; the Space Dockerfile ran as **root** (Trivy DS-0002 HIGH); and `ssl.create_default_context()` in the TLS preflight gate still permitted **TLS 1.0/1.1** — bad anywhere, worse in a gate whose job is proving reachability, since it could pass over a downgrade the real client would refuse.

## Closed (11) — with reasons, nothing discarded silently
- **#113** superseded: `ask_dav1d` and the live version-probe are both already on main, in better form.
- **#128** would have **reverted** a newer record — a 2026-09-03 sweep deliberately set that baton to `in_progress`, not `complete`, because #135/#136 were still open. It also smuggled `openai` 2.44.0 → **3.3.1** into a PR claiming "no production code touched."
- **#129, #130** duplicates of #131. All three fixed the same `dream.py` finding within **90 seconds** of each other. #131 won because it escapes the fence delimiter inside the payload — #130's sentinel fence can be closed by the attacker's own text, which is the standard bypass.
- **#132, #133, #136** stale omnibuses (38/86/79 files). Their headline features — RRF, temporal provenance — are **already on main**, and they'd have committed `app.py.bak-*` / `.gitignore.bak-*` editor backups.
- **#135, #165** split, not discarded: superseded Rhea halves dropped (main has #160/#162/#163/#164/#168/#204), still-needed halves re-landed as #230/#231.
- **#209** closed for #224: identical titles, but #209 was 44 files / +4697 under a one-file title. **#226** closed for #227: same pipe triad plus ~3900 lines of unrelated payload.
- **#229** was empty (+0/-0).

## Known gap, worth a follow-up
`tests/test_recall_hygiene.py` (11 tests) and the temporal-provenance tests are **not on main** — those features shipped without their coverage. Worth one small focused PR porting just the tests, not an omnibus revival.

## ONE ITEM LEFT — needs Dave, nobody else can do it

**The federated-fanout 401 against phoebus.** Phoebus is not broken: unauth → 401 (gate working), authed → 200, and keymaker vs `.env` are byte-identical. The caller is `env.PHOEBUS_TOKEN` on the `nougen-fleet-mcp` Worker, and blade confirmed Cloudflare Worker secrets are **write-only** — nobody can read or fingerprint it back.

We never needed to read it. Setting `PHOEBUS_TOKEN` to phoebus's current `NGS_NODE_TOKEN` is a blind write: a no-op if it already matched, the fix if it didn't.

Not done, deliberately — live public connector plus a credential move, and the value must not transit a transcript, a leg, or a shard. Dave's hands (wrangler + clipboard). Use the **secrets** endpoint, not a settings PATCH: a settings PATCH silently drops bindings it doesn't resend, and its response lies about what's attached.

Blade separately closed the chatgpt-app NouGenMsg exposure (deployed 07:25:30Z, 29/29 bindings verified intact) — still wants a real ChatGPT connector session to confirm the 4 tools actually list.
