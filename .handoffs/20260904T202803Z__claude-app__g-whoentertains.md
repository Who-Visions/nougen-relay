# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Blade console cleanup: 8 WT windows -> 4; relay_live.cmd now detaches; ngs_node_boot.cmd needs same start /b change (repo lane, not touched)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T20:28:03.810Z

---
## Situation
Dave asked to merge the pile of terminal windows on blade. All 8 were Windows Terminal default-terminal windows in one WT process. `windowingBehavior: useExistingWindow` does not apply to default-terminal launches (tested), so that is not the fix.

## Done
- Killed the cmd holders for relay_live.cmd (21572) and ngs_node_boot.cmd (21588). Their pythonw workers (23996, 4112) survived, verified.
- Patched `~/.nougen/relay_live.cmd`: `start "" /b pythonw ... >> relay_live.log 2>&1`. `/b` matters: plain `start` drops the redirect and relay_live.log is written only through it. Backup at relay_live.cmd.bak-20260904.
- WT settings backup: settings.json.bak-20260904.

## Ask (owner of tools/ngs_node_boot.cmd)
Same one-line change: prefix the `"%PYTHONW%" ... start_grid.py --watch` line with `start "" /b`. Not done here because it is a shared repo file.

## Left running, untouched
ngs_node_serve.py, local_mesh_service.py, elevation_audit_daemon.py, ollama_upstream.cmd, space_sync, relay_daemon. Real merge = launch them via `wt -w nougen nt --title X -- <cmd>` from their scheduled tasks. Deferred: not restarting the recall node during today's fanout incident.

## Done when
Next logon shows one window (or zero) for NouGen daemons.
