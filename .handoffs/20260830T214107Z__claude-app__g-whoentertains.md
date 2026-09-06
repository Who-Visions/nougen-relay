# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Trees cleaned: -repo and pull-clone now clean, PR #142 stops shipping lane-claim leases. push-main left ALONE - a lane is live in it. Findings inside for its owner.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T21:41:07.263Z

---
War-gamed to `wargames/tree-cleanup.md` before executing (Rule 0.1); 3 open `(variable)`s in `wargames/ledger.md`.

## Read this first if you own push-main

**I did not touch your work.** 20 modified / 32 untracked files are exactly where you left them.

Two independent signals said hands off: `tests/test_federation.py` had an mtime 2 minutes old and HEAD moved three times during my session (`c248096` -> `9210876` -> `1d6d6bc`), so a lane is live in that tree; and the suite came back **24 failed / 704 passed / 4 skipped**. I did not investigate or "fix" the failures - they are almost certainly your in-flight state, and they are not mine to touch.

I did remove **my own** commit `3820b6b` from `codex/shards-capture-main`, where it should never have been. It is safe on `origin/claude-cli/worker-var-setter-fix` and in PR #141 - verified before the reset, not after.

### Findings on your working set, for you to act on

A classifier pass over your 50 files. Nothing here is committed; none of it has shipped. But none of it should get swept in either.

**Public-surface risk** (this repo is public):
- `docs/nougen_sovereign_intelligence_doctrine.md` - "sovereign" is a **banned brand term**, four instances (`:1`, `:17`, `:71`, `:74`). Also ops leaks: `:14` "Razer Blade stadium", `:52` "the 203K shard mesh", `:53` "9-database cluster". Approved vocabulary is NouGenAi / Sol-Ai / Who Visions / Watchtower / Fleet Registry / Memory Vault / Mesh / Shards; the memory architecture is **VALERION**. A find-and-replace will not save this one - the framing is the problem.
- `tools/live_probe_vector_graph.py:5` and `tools/test_autolink.py:5` - hardcoded `sys.path.insert(0, r"C:\Users\super\...")`. Breaks on every other machine.
- `tools/fleet_heartbeat.py:62` - private IP `10.0.0.88` hardcoded (Rule 0.2 violation as well as a leak); `:3`, `:67`, `:101` narrate internal topology and a CPU measurement of blade's node.

**Orphans - zero importers, zero tests**: `pilot_supervision.py` (484L), `progressive_skills.py` (481L), `skill_catalog.py` (114L). `skill_catalog.py` also overlaps the `_catalog_for_root` logic you added inside `skills.py`.

**Fragile**: `tests/test_temporal_audit.py:4` imports `from tools.audit_temporal_evidence import ...` with no `tools/__init__.py` - resolves only via the `pythonpath` fallback in `pyproject.toml:76`. `tools/test_autolink.py` is named `test_*` but lives in `tools/`; `testpaths` keeps it out of a default run, but a bare `pytest .` collects it and it mutates env and writes graph edges.

The work itself groups cleanly into ~9 commits when you are ready to land it. Ask me and I will hand over the grouping.

## Done elsewhere

**`NouGenShards-repo` - preserved, now clean.** Dormant since 2026-08-21, no claim on it. `relay_daemon.py` (513 lines) existed **only** in that dirty worktree - not on main, not in push-main. One copy, one machine. Committed as-is off its original base (`8a95ec5`, #109) rather than rebased, and pushed to `claude-cli/preserve-repo-tree-20260830`. An honest old base beats a mangled rebase; whoever owns it decides how it lands.

One change on top of what I found: `agents.py:167` shipped a system prompt calling NouGen "the core **sovereign** intelligence engine". Banned term, public repo, dropped before committing. Sentence otherwise untouched.

**`NouGenShards-pull-clone` - clean, behind 0.** The 3 modified files were pure `imported_at` timestamp churn, no price data changed. `ingestion-staging/` (16 cloned repos), `prompts-source/` (40 items) and a stray `fleet-vision-pick/SKILL.md` (byte-identical to the live copy in `~/.claude/skills`) went into `.git/info/exclude`, deliberately **not** `.gitignore` - this tree's job is testing public release pulls, so it has to stay byte-identical to what a stranger downloads. Then pulled 52 commits forward, no conflicts. Nothing deleted; all 16 dirs and 40 items still on disk.

**PR #142 - `.handoffs/claims/` was already tracked.** Five *released* lane leases were shipping in the public repo carrying machine names (`whoart`, `blade1tb`), branch names, pids and session ids. Untracked (files left on disk so any live lease survives) and ignored, along with `logs/` and `*.orig`/`*.rej`. `logs/combined.log` alone is 41KB of pids and request ids sitting one `git add -A` away from shipping.

**Note for every lane**: `.handoffs/claims/` no longer appears in `git status` on push-main once #142 lands. If you were watching `git status` to see your own claim file, use `relay_claim_list` instead.

## Left for Dave

Two pre-existing "sovereign" instances on `main` that I did **not** rewrite:
- `README.md:80` - image alt `"Sovereign Palm Emblem"`. Plausibly your own logo naming, so your call, not an agent's.
- `HARDENING.md:147` - "sovereignty thesis". A philosophical claim rather than a product name, which reads outside the ban list.

## Done-when

- [x] `-repo` clean, `relay_daemon.py` has a second copy off this machine
- [x] pull-clone clean and current, nothing deleted
- [x] my commit off the codex lane's branch
- [x] PR #142 stops shipping lane leases
- [ ] push-main's owner lands their work and acts on the public-surface findings
- [ ] `(variable)`s in `wargames/ledger.md` resolved: provenance of `ingestion-staging/` + `prompts-source/`, whether committed claims are load-bearing, and whether `NouGenShards-repo` is a live workspace or should be retired
