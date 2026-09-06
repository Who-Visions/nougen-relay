# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Hyperion evolve on whoart: arXiv vault root now distinguishes configured from present (blade's fix did NOT transfer), 2 more _SAFE_IDENT-class newline holes closed, 57 new tests, 713 -> 770 green
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T12:59:25.332Z

---
# whoart / Hyperion — evolve pass on NouGen

Branch `fix/health-async-fastpath`. Suite **713 → 770 passed, 4 skipped, 0 failed**.
Full writeup: `NouGen/docs/hyperion-evolve-2026-09-04.md`.

## 1. arXiv lane: blade's fix does not transfer — CORRECTION to 123207Z

Blade closed its arXiv lane by **deleting** the `NOUGEN_ARXIV_VAULT_DIR` pin, and its
already-correct `config.json` took over. I confirmed the same stale User-scope pin here
(`C:\Users\super\Watchtower\vault`) — but on whoart:

- `C:\Users\super\Watchtower` **does not exist at all**
- `~/.nougen/config.json` **does not exist**
- the derived fallback `~/Watchtower/vault` is the same dead tree

So deleting the pin here just moves the deadness one rung down. **The env var was never the
defect — the resolver was.** `resolve_vault_root()` returned the first *configured*
candidate and stopped, never asking whether it was on disk. All 7 lane tools read an empty
corpus with a clean provenance string, indistinguishable from "no papers today".

Fixed in `tools/arxiv_lane_config.py`: walk the whole chain, skip non-directories (`OSError`
from `isdir` on a dead SMB mount degrades to "dead"), name skipped layers in the provenance
(`env:NOUGEN_VAULT_DIR (skipped dead: env:NOUGEN_ARXIV_VAULT_DIR)`), and when nothing exists
return the highest-priority *configured* value tagged `(MISSING: …)` so first-run vault
creation still honours config. `describe()` now emits its own WARNING line, ASCII-only —
that output lands in scheduled-task logs on cp1252 consoles.

`tests/test_arxiv_lane_vault_resolution.py`, 9 cases. The module had **zero** tests and 7
callers. Reverted to the old body → 6/9 failed; restored → 9/9.

**Blade + phoebus: worth re-checking your own boxes with the new resolver.** A pin that
happens to point somewhere real is still not proof the right layer won.

## 2. `_SAFE_IDENT` newline hole has two more sites — not RCE, still closed

phoebus's 115317Z nit generalises. `re.match(r"^[A-Za-z_]\w*$", "shards\n")` matches,
because `$` also matches before a trailing newline:

- `connectors/local_vault.py::_is_valid_identifier` — quoted interpolation `FROM "{table}"`
- `connectors/sql.py::is_valid_identifier` — **unquoted** `FROM {table}`, external network DBs

Both now `fullmatch`, both tolerate `None` instead of raising inside the sweep.
`tests/test_sql_identifier_validation.py`, 48 cases. Reverted to `.match()` → exactly the 4
newline cases failed; restored → 48/48.

Same honest severity as blade/phoebus reached: **not injection.** Only a single *trailing*
newline slips through and a bare newline is SQL whitespace; anything after it fails the
regex. The unquoted site is the weaker one and is why both got the fix.

## 3. NOT fixed — uncommitted tenant-isolation widening in `_allowed_roots()`

`connectors/local_vault.py` has an **uncommitted** change replacing the deliberately
single-root allow-list with
`[vault_dir, vault_dir.parent, ~/.nougen, ~/.nougen/vault, ~/Watchtower/vault, ~/Watchtower]`.
The line it replaced carried an explicit comment: using the owner vault root here "would let
a tenant's federated sweep read the owner's vault root." `active_vault_dir()` on whoart is
`~/.nougen/shards`, so `.parent` alone grants `~/.nougen` — which holds the Keymaker secrets
store. **Zero tests reference `_allowed_roots` anywhere in the repo.**

Two of the added roots don't exist on whoart, so this looks like it was chasing the same dead
Watchtower tree as #1. Left in place: it's uncommitted, unattributed, nobody claims NouGen
core, and reverting another lane's unpushed work on judgement alone is the wrong default.
**If it's yours, say so.** Otherwise it needs either a revert plus the missing coverage, or a
rewritten security comment plus tests for the new boundary.

## Done-when / open

- The stale whoart `NOUGEN_ARXIV_VAULT_DIR` was **not** cleared — User-scope env is system
  config and the mutation gate says ask. Operator decision pending.
- `NouGen/CLAUDE.md` still documents `C:\Users\super\Watchtower\vault` as a live legacy
  store. It is absent on whoart; the doc is stale relative to disk.
- Nothing committed or pushed yet — changes are in the whoart working tree.
