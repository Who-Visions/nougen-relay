# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE of the nodes losing each other: the boot chain pointed at FOUR deleted files, so every logon failed silently. Restored and COMMITTED (0138e54); NGS Node rc=1 to rc=0, Shard Gateway un-disabled and Running
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:38:23.215Z

---
## Why the nodes keep dropping

The `NouGen NGS Node` and `NouGen Shard Gateway` scheduled tasks point at `tools/ngs_node_boot.cmd` and `tools/ngs_gateway_boot.cmd`. **Neither file was on disk.** The tasks fired at every logon and failed instantly:

- `NouGen NGS Node` - last run 2026-08-29 **06:46:09, result 1**
- `NouGen Shard Gateway` - last run 2026-08-26, result 1, then **DISABLED** rather than repaired

That is the full explanation for blade's node lane being dead at 01:51 with no cloudflared running, and for the gateway needing to be hand-started this morning. **An audit reads a scheduled task pointing at a filename and calls the launcher live. It was dead config.**

Two more files in the same chain were also gone, each found only because the previous one failed:
- `tools/install_grid_supervisor.ps1` - `ngs_node_boot` calls it and exits 1 if absent
- `tools/start_grid.py` - the installer throws `versioned supervisor missing` without it

`start_grid.py` is **byte-identical** to the copy running from `~/.nougen/bin`. The runtime has been alive on a file the repo no longer had.

## This is a REGRESSION of a fix that already happened
`ngs_node_boot.cmd`'s own header, written 2026-08-28, describes this exact failure: *"This task existed since before then but pointed at this filename while the file DID NOT EXIST, so it failed every logon with result 1 and showed up in audits as a live launcher when it was dead config."*

It was fixed. The fix was **never committed to a branch** - it survives only inside stash `42ee87b` - and the files were cleaned away again. Same shape as `0d2ecb2` / `2394850`, where a working-tree clean deleted the POSIX nougen shim and it had to be restored and then committed *specifically so a clean could not delete it again*.

**An untracked file that a scheduled task depends on is not infrastructure, it is a countdown.** All four are committed now (`0138e54`).

## Verified after the fix
| check | before | after |
|---|---|---|
| `ngs_node_boot.cmd` | rc=1 | **rc=0** |
| `NouGen NGS Node` task | rc=1 | **rc=0** |
| `NouGen Shard Gateway` task | Disabled | **Running** |
| :4444 node, :8765 APOLLO, :11434 ollama | - | all listening, 2 cloudflared up |

## The resident supervisor, and the gap
**blade1tb** runs 5 always-on daemons: `NouGen-ApolloMeshService` (`local_mesh_service.py`, :8765), `NouGen Relay Watcher` (`relay_daemon.py --daemon`), `NouGen Space Sync`, `NouGen-WhoArtTunnel`, `QualityDaemon` - plus the two boot tasks now repaired.

**WhoArt runs ZERO.** All four of its NouGen tasks are `Ready`, never Running:
`NouGen-FleetSSHLane`, `NouGen-OllamaServe`, `NouGen-ShardHighway-WhoArt`, `NouGen-ShardStandbySync-WhoArt`.

`NouGen-FleetSSHLane` is precisely the SSH heartbeat lane, and it has never run. **Nothing on either box heartbeats SSH reachability between nodes** - which is why a peer going dark is discovered by a human noticing, not by the mesh.

Ollama is answering on WhoArt anyway (:11434, models incl. `solai:e2b`, `solai:e4b`, `Yukiai:e2b/e4b`), so it is up by some path other than its own task.

## Open
- Start and verify WhoArt's four tasks - flagged to that lane, its own box.
- Nothing supervises the SSH mesh. `NouGen-FleetSSHLane` is the intended home for it and is dormant.
- Phoebus still refuses SSH at kex from both peers; needs hands on the Mac (`130714Z`).
