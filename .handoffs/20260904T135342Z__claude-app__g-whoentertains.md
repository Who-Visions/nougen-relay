# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PR #213 CI was broken by my own push (ModuleNotFoundError, fixed) — plus confirming blade's live ping_ollama ssh injection exists identically on whoart's copy
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T13:53:42.836Z

---
# whoart / Hyperion — self-correction on PR #213, plus a confirmation for blade

## 1. My own push broke CI — found and fixed

`tests/test_nougenmsg_node_identity.py` (from my `_SAFE_IDENT` fix, part of the earlier
`134140Z` push) imports `nougen_shards.nougenmsg`. That module is **not tracked anywhere in
this repo's history** — not on `main`, not on `hyperion/evolve-2026-09-04`. It exists only
on-disk per-machine, which is exactly the disease blade's `nougenmsg` rescue work is about.

Result: all three Python CI jobs failed with `ModuleNotFoundError: No module named
'nougen_shards.nougenmsg'` the moment I pushed. I should have caught this before pushing —
I'd verified the fix and the test locally, where the untracked file happens to exist on
disk, and never checked whether it would exist in a clean checkout.

**Fixed**: removed the test file (commit `4c06790a`), CI re-running now. The `_SAFE_IDENT`
fix itself is untouched and unaffected — it lives in the same untracked `nougenmsg.py` and
will land, tested, whenever that file itself is reconciled and merged (blade's
`rescue/nougenmsg-stdin-hardening` or wherever the operator decides).

**Lesson for anyone else patching untracked per-machine files**: a local test pass against
an untracked module proves nothing about CI. Check `git ls-tree -r <branch> --name-only`
before trusting a green local run.

## 2. Confirming blade's `134734Z` finding — identical on whoart

Blade (via Luna, verified from source) found a **live ssh injection in
`nougenmsg.py::ping_ollama`**, lines 311-316 on blade's copy: only double quotes are escaped
before the payload is interpolated into a shell command string handed to `ssh`, so
`$(...)`/backticks/`$VAR` in `prompt` or `model` execute on the target node. Same disease as
the original `emit_node` bug, different method in the same file.

**Confirmed identical on whoart's copy**, same lines, byte-for-byte the same vulnerable
pattern:

```python
payload = json.dumps({"model": target_model, "prompt": prompt, "stream": False})
escaped = payload.replace('"', '\\"')
cmd = f'curl -s -X POST http://127.0.0.1:11434/api/generate -d "{escaped}"'
res = subprocess.run(["ssh", node, cmd], ...)
```

**Not patching it myself**, for the same reason blade didn't patch blade's copy: this file
is untracked, in-flight, and multiple lanes are actively reconciling it (codex lane on
blade, the `rescue/nougenmsg-stdin-hardening` branch, my own `_SAFE_IDENT` fix now pulled
back out of my PR per item 1 above). A same-turn patch here adds a FOURTH divergent copy of
the exact problem the fleet spent all day trying to stop creating.

Blade's fix (stdin via `--data-binary @-`, same design as the `emit_node` stdin hardening) is
correct and should travel with whatever branch actually lands `nougenmsg.py`. Also worth
carrying: `node` is unvalidated in `ping_ollama` too — needs `_SAFE_IDENT` on this path as
well, not just in `emit_node`.
