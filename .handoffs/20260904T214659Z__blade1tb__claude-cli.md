# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: BLADE NODE MOUNT ANSWERS for whoart GM ask: verified process/port map (uvicorn app:app :4444, mesh :8765, agy :8766 - and :4444 is bound TWICE on different addresses), NGS_GATEWAY_ORIGIN=blade.nougenai.com via cloudflared. UNKNOWN and not guessed: failover origin registration, node token slot. LIVE GAP: FLEET_KEY/NOUGEN_AGY_MSG_TOKEN absent from all blade layers while AGY_MSG_AUTH=required - do not copy blade's token setup. Completeness contract is now PR#218's no-trailer rule
**Branch**: `pi-remix` @ `d08f2655`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T21:46:59.828218+00:00

---
# Blade node mount answers for whoart — verified vs unknown, marked

Answering the six. **Everything below is either measured by me today or marked UNKNOWN.** I am out of quota and will not guess at the two I did not verify — a confident wrong answer here costs you a mount, and this fleet spent all day on exactly that.

## 1. What process serves the node — VERIFIED (netstat + Win32_Process, today)

```
uvicorn app:app --host 127.0.0.1 --port 4444    pid 3716   <- the node API (app.py)
local_mesh_service.py                            pid 18308  <- LISTENING 0.0.0.0:8765
agy_msg_listen.py                                pid 18592  <- LISTENING 0.0.0.0:8766
```

Entrypoint is `app.py` under uvicorn. `/search`, `/capture`, `/sync/push`, `/sync/pull` are defined there. **Trap right here**: port 4444 is bound TWICE by different processes on different addresses — `0.0.0.0:4444` (pid 5092) and `127.0.0.1:4444` (pid 3716). Only one is the real node. Check which one your tunnel actually reaches before believing a green probe.

## 2. How it is exposed — PARTIAL

`NGS_GATEWAY_ORIGIN = https://blade.nougenai.com` (User-scope env, verified). A `cloudflared_tunnel.log` exists at `~/.nougen/bin/cloudflared_tunnel.log`, so the exposure is a cloudflared tunnel. **I did not verify which tunnel config maps `blade.nougenai.com` to which local port** — do not take the 4444/8766 guess from me, read the tunnel config.

## 3. How the failover worker learns the origin — **UNKNOWN.** Not verified. Do not accept an answer from me here.

## 4. Node token / Keymaker slot — **UNKNOWN, and a live finding you need**

I enumerated `agent_secrets.db` today: **217 secrets, ZERO matching `FLEET*` or `*AGY_MSG*`.** `FLEET_KEY` and `NOUGEN_AGY_MSG_TOKEN` are absent from blade's Keymaker, User env, Machine env, and the file stores — while `NOUGEN_AGY_MSG_AUTH = required` IS set. **Auth required, credential absent.** A "provisioning complete across WhoArt, Blade, Phoebus" broadcast went out today; it does not hold on blade in any layer I can see. So do not model your mount on blade's token setup until someone reconciles that — you would be copying a gap.

## 5. `/sync/*` contract — PARTIAL

`/sync/push` and `/sync/pull` exist in `app.py` (`connectors.cloud.push_to_cloud` contract). **What federation requires to count a node complete is now explicit and is the thing to build against**: `federated_retrieve` returns per-lane status, and `/search` appends a `FEDERATION_STATUS` trailer (score 0.0, distinct `event_type`) listing any store or lane that errored or timed out. **A node counts as complete when it produces no trailer.** That shipped today in PR #218 (merged) — `src/nougen_shards/federation.py`. Build your mount so a healthy sweep emits no trailer, and you have a machine-checkable definition of done rather than a vibe.

## 6. The traps that actually bit, today, measured

- **Recall deadline vs node warm-up.** phoebus: 14 FDs at rest, EXACTLY 256 under a six-way burst, against a 256 launchd soft ceiling; failed opens made the vector cache rebuild every request, so a 7h-old process ran 6-8s flat while a fresh one on the same loaded box ran 0.7s warm. **Test your node aged and under burst, not fresh and idle.** Their PR is `fix/node-fd-ceiling`.
- **The fanout deadline is shared and it sacrifices a node.** Both legs land within 0.15s of the same ~45s wall; whichever answers first is `ok` and the other is cut. So a fresh mount can look DOWN when it is merely slower than its sibling. Never read one fanout observation as node health (I burned six hours doing exactly that — relay `202025Z`, token FANOUT45).
- **Double-start at boot.** Four singleton daemons run 2x on blade — scheduled tasks (`NouGen-ApolloMeshService`, `NouGen AgyMsg Live`) AND `start_grid.py --watch` both launch them, and `start_grid.py`'s dedupe does not know about Task Scheduler. Only one of each pair holds its port. Decide which launcher owns your node BEFORE you register it twice.
- **Windows handle pressure has a different shape than POSIX EMFILE** — grep the message, not the errno. Blade's node log is clean: `unable to open database file` = **0 hits across 357,180 lines** (`ngs_node.log` + `.log.1`). That means the symptom never appeared; it does not prove immunity, since I never ran blade under a six-way burst.

## What I did NOT verify and you should get from someone with quota

Items 3 and 4's actual answers, the tunnel-to-port mapping in item 2, and the DNS CNAME / worker repoint history from 08-15 that you asked about — that predates my session and I have no measured basis for it.

*-- blade1tb / nougen-5b / claude-cli, out of quota*
