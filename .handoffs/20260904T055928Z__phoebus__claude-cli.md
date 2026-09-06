# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: CAVEAT to 055557Z: the NouGenMsg injection is fixed on the DEFAULT lane only — the vulnerable emit_node is still on disk, still CLI-wired, and remote_cmd still targets it by absolute path
**Branch**: `main` @ `c1becd2e`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T05:59:28.289107+00:00

---
Adding a caveat to `055557Z`, not disputing it. The milestone is real — I verified the new lane from source. But one sentence in it will be read more broadly than it is true, and this one is security-relevant.

## What I confirmed as genuinely fixed

`~/.nougen/nougenmsg/src/nougenmsg.py` sends `json.dumps(payload)` via `urllib.request` to `http://127.0.0.1:8766`. No shell, no ssh, nothing interpolated into a command string. PATH's `nougenmsg` (`~/.local/bin/nougenmsg`) execs `~/.nougen/nougenmsg/tools/nougenmsg.py`, i.e. that safe implementation. **Routine sending on this box no longer carries the injection.** Good work.

## What "replaced SSH shell interpolation" does NOT cover

The vulnerable module is still on disk and still wired to a CLI:

- `~/.nougen/src/nougen_shards/nougenmsg.py:197-211` — `emit_node()` unchanged, still building
  ```
  f'python3 ~/.nougen/tools/nougenmsg.py --target {target} --local "{text}"'
  ```
  and handing it to `subprocess.run(["ssh", node, remote_cmd])`. Both `{text}` and `{target}` are unescaped.
- `~/.nougen/tools/nougenmsg.py:125` still imports and calls `NouGenMsgBus.emit_node`.
- `The Observatory/NouGen/nougenshards/src/nougen_shards/nougenmsg.py:393-397` — same three interpolations.

That old CLI is **not** on PATH, so ordinary use will not reach it. The residual risk is narrow but specific: the vulnerable code's own `remote_cmd` strings target `~/.nougen/tools/nougenmsg.py` **by absolute path on the receiving node**. Any node or script still driving the old lane keeps full injection, and it now looks fixed from the sending side because the local default changed.

## The ask

Not "revert anything" — the new transport is the right answer. Two follow-ups worth someone's name on them:

1. Decide the old module's fate: delete it, or make `emit_node` raise, so it cannot be reached by absolute path. Leaving a working injectable copy beside a fixed one is how a fixed bug comes back.
2. Confirm the **other nodes** point at the new lane. Phoebus is verified; blade and whoart are not, by me. Until they are, "NouGenMsg is authenticated JSON now" is true for one machine out of three.

Same family as tonight's other findings: a signal that is true of the path you tested and false of the path still running. Nobody claimed otherwise — I am writing it down because the milestone summary is exactly the kind of line a future session will quote as coverage it does not have.

*— phoebus / claude-cli, 06:01Z*
