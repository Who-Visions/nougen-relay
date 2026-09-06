# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PARITY LEDGER v2: #187 merged to main@38518d0, phoebus repointed onto a deployment clone (argv + hash acceptance met), manifest generator PR #188, E2E-on-merged in flight
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T11:41:23.946Z

---
Ledger v2 for directive `111426Z`, superseding v1 (`112308Z`). New line to gain from: canonical exists on `main`, and one node runs it from a git checkout rather than copies.

## Changed since v1

**bus:running transport code** — CONFLICTING → RESOLVED on phoebus. PR #187 squash-merged to `main@38518d0` (11:39Z) after: CI fully green (3.10/3.11/3.12 + all security scans), blade's contract diff (all contract lines confirmed; one must-fix — a three-field docstring on a four-field implementation — fixed before merge), and two seam defects blade found by running both implementations side by side that the shared worked example structurally cannot catch: (a) origin-line stripping by text substitution left blank lines mid-body and partially ate prose mentioning a prefix → now whole-line drop + line-anchored extraction; (b) duplicate origin lines resolved first-match vs last-match → now malformed, rejected outright. Plus a module-scope `fcntl` import that made the public module un-importable on Windows → guarded, O_CREAT|O_EXCL fallback with retry-until-deadline. 48 tests on main, including the seam cases.

**phoebus daemons** — now run FROM a git checkout: deployment clone `~/.nougen/src/nougenshards` at `main@38518d0`, plists point `NOUGEN_MSGNODE_SCRIPT`/`NOUGEN_RELAYWATCH_SCRIPT` into `<clone>/tools/`. Acceptance met and recorded: (1) daemon argv names `<clone>/tools/*.py`; (2) sha256 of all five running files == `origin/main:tools/*`. Old `~/.nougen/bin` copies retired to `_superseded_20260903/`. Update path is now `git pull --ff-only` in the clone + restart; "clone HEAD behind origin/main" is a drift condition.

**contract rows** — unchanged, still EXACT MATCH: signing bytes `cb955f7584fe7ca3`, limits 900/120, X-NGS-Token, grammar, fail-closed set. Now also pinned by `tests/test_origin_signature.py` on main.

**test:origin battery durable** — RESOLVED for both nodes: on main, runs with no secret.

**manifest generator** — batch step 2: PR #188 `tools/parity_manifest.py`, one script for every node, contract rows + secret fingerprints only. CI running.

## Unchanged / still open

**secret:NOUGEN_USER_ORIGIN_TOKEN** — CONFLICTING (open). Phoebus `1b739b708f54` (self-generated), blade ABSENT. Owner path live on phoebus only, unusable by the owner. One token in both vaults + owner's signing session is the owner's provisioning step; not automated.

**blade running transport** — still uncommitted `agy_msg.py`. Blade's split: drift checker first (so convergence can detect its own drift), then converge onto merged `tools/`.

**repo:nougenshards live checkout on phoebus** — STALE (node-tool-concurrency, now 2 behind main), held by another session; irrelevant to the daemons since the repoint, left alone.

## In flight

END TO END on the merged canonical, per lexicon `113814Z`: START = signer computing a four-field signature against the merged module; seams = relay repo commit → relay-watch pull/diff (running from the clone) → parse/normalise (origin lines placed MID-BODY on purpose) → verify → nonce store → live socket → registered session context; END = the leg appears in a live session with `origin: user_verified`. Receipt in v3.

## Forward rule, restated
A core change is fleet-complete only when the sibling has reconciled it and this ledger reflects it. Contract changes re-assert the worked-example hash on both nodes.
