# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: phoebus deployed #189 (main@29db316): --ff-only pull + both agents reloaded, 5/5 drift MATCH; wake guard proven load-bearing; NOUGEN_BUS_DIR unset on phoebus makes drift_check false-alarm on a healthy node
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T15:37:46.134Z

---
Executed on phoebus 2026-09-03 15:34-15:40Z, following the update path documented in handoff `151443Z`. Closes waiting-item 1 of that handoff.

## #189 was already merged
`gh pr view 189` → **MERGED 2026-09-03T15:13:37Z**, head `c3f6bc6`, merge commit `29db316`. It landed ~1 min BEFORE handoff `151443Z` was written, so that handoff's "waiting on blade to merge #189" was stale on arrival. Nobody needs to chase blade for it.

## What was done
1. Pre-state captured: PIDs 19846 (relaywatch) / 19849 (msgnode), up 3h20m, argv already inside the deployment clone.
2. **Verified the no-wake guard BEFORE pulling** — `NOUGEN_WAKE_DISABLED=1` present in both plists and in both running processes' env.
3. `git -C ~/.nougen/src/nougenshards pull --ff-only` → `6015d43..29db316`, clean fast-forward, 5 files / +678, working tree 0 dirty, 0 behind.
4. Hash acceptance: all 5 bus files sha256-match `origin/main:tools/<f>`.
5. Contract tests on the PRODUCTION interpreter (Python 3.9.6): `test_node_transport`, `test_origin_signature`, `test_original_timestamp`, `test_wake_adapter` → **64 passed**.
6. `launchctl kickstart -k` both agents → new PIDs 11251 / 11254, argv still inside the clone, port 8766 re-listening.
7. Live self-test: `POST /msg` → `{"delivered": true, "node": "phoebus", "elevated": {"attempted": false}}`.
8. `drift_check.py` (with `NOUGEN_BUS_DIR` set) → **5/5 MATCH, exit 0**.

## The wake guard is load-bearing, not precautionary
Measured on phoebus after the merge:

```
NOUGEN_WAKE_DISABLED=1 → enabled=False   available=["antigravity"]
(unset)                → enabled=True    available=["antigravity"]
```

The `antigravity` adapter **is importable on phoebus**. #189's `enabled()` is `bool(_ADAPTERS) and not disabled`, so without that env var phoebus would have silently gained agent-wake execution the moment #189 merged. Setting it beforehand (handoff `151443Z`) was the thing that prevented it. Any node adopting #189 should verify this the same way — check `available`, not just that the flag is set.

## DEFECT for whoever wires drift_check into the watcher
`drift_check.py` run on phoebus **without** `NOUGEN_BUS_DIR`:

```
MISSING tools/nougenmsg_node.py     canonical exists, not running here
MISSING tools/relay_watch_node.py   canonical exists, not running here
MISSING tools/_agy_live_delivery.py canonical exists, not running here
MISSING tools/parity_manifest.py    canonical exists, not running here
DRIFT   tools/drift_check.py        ~/.nougen/bin/drift_check.py
exit 1
```

All four "MISSING" files were running correctly at that moment. `DEFAULT_MAP` hardcodes `.nougen/bin/<name>` as the runtime location, which is exactly the path phoebus RETIRED when it repointed to the deployment clone. With `NOUGEN_BUS_DIR=~/.nougen/src/nougenshards/tools` it is 5/5 MATCH, exit 0.

The tool's own `bus_dir()` docstring predicts this precisely — "after a node repoints to a deployment clone and retires its old copies, a stale per-file map reports MISSING for files that were merely moved. A ghost, not drift." The fallback map is simply never right for a repointed node.

**Consequence:** the handoff's next step is to wire `drift_check` into `relay_watch_node.py`'s poll branching on exit code. Done today, on phoebus, that branch would fire **continuously on a healthy node**. `NOUGEN_BUS_DIR` must be set in both plists first, or the fallback map must be dropped in favour of a hard failure when `NOUGEN_BUS_DIR` is unset — silently guessing the runtime location is what produced this false alarm. Recommend the latter as the durable fix.

Not yet persisted on phoebus (needs a second agent reload) — flagged to the owner rather than done silently.

## Also on phoebus
A stale hand-copy `~/.nougen/bin/drift_check.py` dated 2026-09-03 07:43 is the only thing the DRIFT row found. It predates the deployment-clone switch and should join `~/.nougen/bin/_superseded_20260903/`. Copying bus files into `.nougen/bin` is the retired pattern; nothing should write there again.

## Exit-code trap worth repeating
`$PY tools/drift_check.py | head` reports `$?` from `head`, not the tool — it read 0 while the tool exited 1. Any wiring that pipes drift_check for logging will read the wrong status unless it uses `PIPESTATUS` or redirects to a file.
