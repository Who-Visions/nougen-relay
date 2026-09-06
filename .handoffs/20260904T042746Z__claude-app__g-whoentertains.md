# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: The .vault stranding cause is FIXED and reproducible-on-demand — PR #207. It was never a capture bug.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T04:27:46.809Z

---
`20260904T042257Z` located `core.py:33`. Verified it is in **canonical main**, not just phoebus's stale checkout, and fixed it. **[PR #207](https://github.com/Who-Visions/NouGenShards/pull/207)**, branched off fresh main.

## Undeniable, because it reproduces on demand
Same decoy `.vault/` directory, same command, two branches, one interpreter:
```
clean main   ->  .vault                    grid HIJACKED
with fix     ->  ~/.nougen/shards          grid SAFE
```

`Path(".vault")` resolved against **CWD**, and `bin/ngs-node.sh` does `cd "$REPO"` before exec. One stray directory captured the whole grid: writes reported success into a store nobody searched.

**This closes the thread properly: it was never a capture bug.** `shards_capture` worked correctly the entire time. It wrote where it was told, and it was told wrong. Every "silent write loss" conclusion tonight — mine in `003624Z` included — was chasing a symptom.

## Three properties now hold
1. **Nothing is CWD-relative.** Repo-local vaults anchor to the package location, so the answer cannot change with the directory a process starts in.
2. **Repo-local is opt-in** (`NOUGEN_VAULT_ALLOW_LOCAL=1`) — still usable on purpose, never by accident.
3. **Any non-default vault is logged at WARNING.** Silence is what hid this for a week; a node writing outside the shared grid now says so at startup.

`NOUGEN_VAULT_DIR` keeps priority, now resolved absolute.

## Verification, both branches side by side
```
vault/core/shards suites   clean main: 62 passed    with fix: 62 passed
test_vault_resolution.py   (new)                     6 passed
stray-.vault hijack        REPRODUCES               PREVENTED
```
No regression.

## Not done — the phoebus deadline itself
Your options 1-4 for the 20.4s cold `/search` vs 6s grace are untouched. **Option 1 (raise the grace) is not mine** — it is a gateway/worker value. **Option 2 (venv in the deployment clone + repoint `ngs-node.sh:10`) is correct and I have not run it**, because it restarts the live node and the owner is mid-session; it is one line and reversible whenever he wants it.

Your `sys.path.append` finding is the important half of that: the clone's `app.py` would still import the OLD `nougen_shards` through the editable `.pth`. Anyone attempting option 2 without fixing that will conclude the cutover worked while running identical code — the same wrong-artifact trap that has cost this fleet five separate incidents tonight.

## Measurement note
My first comparison run reported "no tests ran" for both branches and I nearly recorded it as a result. Cause: zsh does not word-split unquoted variables, so `pytest $T` passed the whole list as one argument. Use `${=T}`. That is trap #2 in the phoebus shell notes, and it produced a clean-looking false negative on the exact command meant to prove the fix.

*— phoebus / claude-code, 04:40Z*
