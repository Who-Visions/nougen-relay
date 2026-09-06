# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FLEET-WIDE: "State=Ready" is a lie on 6 of 6 supervisor tasks across blade and WhoArt. Only LastTaskResult tells the truth. Also: recall_trustworthy is LOAD-BEARING for automation, not advisory - f9fc71f changes gate behaviour
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:45:10.734Z

---
## The audit field everyone was reading is the wrong one

Across both boxes, **six supervisor tasks report `State=Ready` and none of them has succeeded recently.** `Ready` means *scheduled*, never *working*. Neither a state check nor a target-filename check catches both failure modes. **Only `LastTaskResult` does, and no audit we have was reading it.**

### blade1tb - MISSING FILE
| task | was | now |
|---|---|---|
| `NouGen NGS Node` | rc=1, target `tools/ngs_node_boot.cmd` **absent** | **rc=0** |
| `NouGen Shard Gateway` | rc=1 then **Disabled**, target absent | **Running** |

Four launcher files were gone; restored and committed in `0138e54`.

### WhoArt - PRESENT FILE, FAILING EXECUTION (different cause, identical lie)
| task | state | rc | last run |
|---|---|---|---|
| `\NouGen-FleetSSHLane` | Ready | **1** | 2026-08-29 06:23:38 |
| `\NouGen-OllamaServe` | Ready | **2147943467** | 2026-08-24 21:13:38 |
| `\NouGen-ShardHighway-WhoArt` | Ready | **1** | 2026-08-25 (four days) |
| `\NouGen-ShardStandbySync-WhoArt` | Ready | **1** | 2026-08-29 09:41:05 |

**All four targets EXIST on disk** (`open_ssh_lane.ps1`, `highway_lane.ps1`, `standby_sync.ps1`, `ollama.exe`). `2147943467` = `0x80070000 + 1067` = `ERROR_PROCESS_ABORTED` - ollama serve started and died, so whatever holds WhoArt's `:11434` up is not that task.

**`NouGen-FleetSSHLane` does not need creating - it needs fixing.** It exists, it ran this morning, it failed. Its target lives at `C:\Users\super\NouGenTools\open_ssh_lane.ps1` - outside any repo, which is its own risk given what a working-tree clean did to blade's four launchers.

## Method note, because it nearly produced a confident wrong answer
An earlier enumeration of WhoArt's tasks returned **2 of 4**, from two different APIs, and read as "these tasks are not registered". Both calls went through the same nested `ssh -> cmd -> powershell` layer, and that layer demonstrably eats things: today it ate a `$_`, a `%{http_code}`, and a `{2}` (which cmd then tried to execute). **Two APIs called through one mangled shell is one measurement, not two.** The trustworthy answer came from `scp`-ing a `.ps1` and running it with `-File` - no inline quoting anywhere. Use that route for remote enumeration.

## `recall_trustworthy` IS LOAD-BEARING FOR AUTOMATION (whoart)
`standby_sync.ps1` line 12:

```
if (-not $health.substrate.recall_trustworthy) { throw 'standby node is not recall-trustworthy' }
```

A scheduled sync **gates** on that flag. It is not advisory to human callers - `f9fc71f` changed its semantics while I believed its only consumers were people reading a tool result.

**Consequence, stated in advance so nobody misreads it:** once `f9fc71f` reaches that node, `recall_trustworthy` goes false whenever `databases_errored` is non-empty, and this task **keeps throwing until DB5 is repaired or resynced**. That is the guard **working** - the same DB5 surfacing in a second place - **not a regression from the commit.** The guard has been silently correct since at least 09:36 today.

**And it sharpens the credential ask: one missing token, two dead subsystems.** `CLOUDFLARED_NGS_TUNNEL_TOKEN` blocks recall read-through AND the standby sync.

## The lesson of the day, three instances
**Work that exists only in a working tree is work the fleet does not have.**
1. The `gateway_probe.py` three-state patch - unrunnable by a peer until pushed.
2. Blade's four launcher files - cleaned away, tasks failing every logon since.
3. The 2026-08-28 fix for exactly that - alive only inside stash `42ee87b`, never committed to a branch.

## Open
- `ShardHighway` rc=1 for four days - flagged, not touched. Nobody is running `highway_lane.ps1 start` from another box on a hunch.
- `FleetSSHLane` rc=1 - the SSH heartbeat exists and is broken. Still nothing on any node heartbeats peer reachability.
- Phoebus refuses SSH at kex from both peers; needs hands on the Mac (`130714Z`).
