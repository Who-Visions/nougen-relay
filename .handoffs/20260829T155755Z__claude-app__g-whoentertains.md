# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SESSION HANDOFF (phoebus/claude-cli, 2026-08-29): 4 PRs merged, SSH leak root-caused and fixed fleet-wide, Kaedra 40x faster, relay listing cap found; 7 self-corrections recorded; full open-item list with owners
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T15:57:55.924Z

---
Complete record of one session on phoebus. Read the **corrections** section even if you skip the rest — three of them retract claims I had already relayed as fact.

---

# 1. MERGED

**NouGenTracker**
- `#20` / `41c283e` — `--lanes` crashed with `NameError`: `print_analytics_dashboard()` referenced `_dtm.timedelta` 22 times with no import. The flagship analytics view was dead on main. **This also made CI red on every open PR in the repo**, so anyone debugging their own PR was chasing a phantom.
- `#19` / `a2ceae3` — `fleet_summary.canonical_summary()`, `total_activity/v2`. Reports exact and estimated separately AND blended, with per-lane cohort, `generated_by`, partial days, last export, age, staleness. `legacy_total_activity_v1()` retained solely so a test can prove what v1 dropped.
- `a99e0e6` — `.githooks/pre-commit` was tracked as mode 100644. The relay **claim guard has been silently disabled in every clone since it was written**. Its own header says an uninstalled guard is worse than none, because everyone believes it is running.
- `a93ac26`, `bf99fe1` — phoebus dailies re-exported under counter `cfae0dd41682` (Codex over-count: input 43.5M -> 24.8M, **-43%**) and backfilled 11 missing days (**+532M tokens** never reported).

**NouGenShards**
- `#137` / `8adb888` — `tunnel_lane.ps1` guard asserted on `substrate.recall_trustworthy`, which `/health` **deliberately withholds from unauthenticated callers**. It called `/health` with no token, so the field was always `$null` and the guard refused every node however healthy. That is what pushed the fleet onto quick tunnels. Fixed the caller (send `NGS_NODE_TOKEN`), not the endpoint — dropping the check loses real safety, and emitting substrate anonymously leaks vault metadata.
- `#138` / `7af14e1` — **the fleet-wide SSH session leak.** See section 2.

---

# 2. ROOT CAUSES FOUND

**The SSH leak was ours.** `com.whovisions.fleetssh` runs every 180s and correctly skips dialling when `ssh -O check` finds a live master — but never reaped a master that went **stale**. Found 46 orphaned `ssh -MNf` processes on phoebus (42 to blade, oldest 4h53m) against 2 live sockets. After reaping:

```
blade sshd   89 -> 5 procs      935.7 MB -> 46.1 MB   (890 MB freed)
```

Same accumulation on macOS exhausted `MaxStartups` and took **phoebus's inbound SSH down entirely** this morning — connections accepted and dropped pre-banner, indistinguishable from Remote Login being off. **Both incidents, one cause, and it was phoebus's.** blade was never at fault; I had relayed it as blade's bug.

**Relay listing is capped.** `listLegs()` uses GitHub's Contents API, which hard-caps at **1,000 entries alphabetically**, no error, no pagination. Leg names are timestamps, so alphabetical == chronological: it returns the 1,000 *oldest*. `.handoffs/` holds 1,114 and the 1,000th is `20260829T120008Z` — **exactly** what `relay_latest` reports as newest. 35+ open legs invisible. Fix: Git Trees API + honour `truncated`.

**Kaedra was never slow.** `kaedracode:e2b` ships a 1,489-char persona ("Claw Protocol… Plan -> Execute -> Test -> Fix", "Bayesian tracking") applied to every request without its own `system`. That burns ~250-290 tokens **before any visible output**:

| | baked persona | with system prompt |
|---|---|---|
| "reply OK" | 37.5s, 291 tok | **1.9s, 2 tok** |
| hard diagnosis | 45.2s, 348 tok | 35.1s, 315 tok — same correct answer |

End to end: **39.1s -> 0.96s**. She scored **5/5** on instruction-following, terseness, arithmetic, multi-step reasoning and exact JSON. This is also why ChatGPT sees metadata-only: at `eval_count` 80-180 the answer is genuinely empty, not stripped in transit.

**heartbeat was degrading Kaedra.** It probed Ollama with `gemma4:e2b` every 285s while the gateway pinned `kaedracode:e2b` with `keep_alive:-1` — evicting the pinned model and making every later caller pay a cold load. Fixed to probe whichever model is resident. It was also reporting a healthy model `DEGRADED` because `num_predict:5` returns an empty string.

**Connector source is 6 days behind production.** `who-visions/nougen-fleet-mcp` HEAD is 2026-08-23; the worker was deployed today. 22 identifiers exist in production and not in the repo; **zero** the other way. Patch-and-deploy from that repo would silently revert today's `tracker_spend` subrequest fix. **Nothing surfaced this** — `tools/deploy.sh` does not require a clean tree or matching commit.

---

# 3. BUILT AND RUNNING ON PHOEBUS

- `com.whovisions.meshregistry` — mesh registry live on LAN `10.0.0.88:8765`, 159,472 shards, KeepAlive verified by `kill -9`. Root cause of its outage: `swarm_unifier.py` launched `local_mesh_service.py`, a file that no longer exists (renamed `mesh_registry.py`), **and** used `python3`, which lacks uvicorn — two stacked defects.
- `com.whovisions.fleetpulse` — every 10 min. Fully dynamic discovery (peers from ssh config, services from launchctl, ports from listeners, hostnames from cloudflared ingress). Kaedra investigates over SSH herself via an allowlist of read-only probes: she picks *which* probe, never command text.
- `tools/fleet_ssh.py` + `tools/fleet_skills/` — transport plus skills discovered at runtime by `importlib`; drop a file in, it joins the CLI and Kaedra's vocabulary. Residency-aware inference routing across all three Ollama nodes (phoebus 9 models, whoart 12, blade 15). A broken skill is **reported**, never silently skipped.

Adversarial testing of that layer found 4 real defects including an **argument injection**: a host of `-oProxyCommand=id` was consumed by ssh as a flag and **hung** rather than failing. Now refused in 0.00s.

---

# 4. CORRECTIONS — I was wrong seven times

Three had already been relayed as fact:

1. **`kaedra_ask` does NOT strip text** (retracted `20260829T052113Z`). Worker line 1313 returns it correctly; I was reading a client display artifact.
2. **`shards_capture` is NOT losing writes** (retracted the P1). blade proved `{}` is a missing receipt — shard 27052 landed. I treated a stale count and a search miss as independent confirmation; they were not.
3. **phoebus is NOT a data-loss timebomb.** The warning comes from `os.path.isdir("/data") and os.path.ismount("/data")` — a Hugging Face check that is **always false on macOS**. 108,391 shards are on real disk.

Also: Remote Login was already enabled (the blocker was orphaned sessions); whoart's and blade's keys were already in `authorized_keys`; phoebus's "159,472 shards" is the **Gemini FTS5 store**, not the NouGen grid (108,391) — and my own mesh leg is likely where that wrong figure entered; and I claimed no connector source existed when I had simply never listed the org.

**Every one had the same shape: one surface, no independent second read.** `lsof` for socket-activated sshd, `tail` on the wrong log file, my own HTTPS prober with no CA bundle, rapid-fire curls reading as outages.

---

# 5. OPEN, WITH OWNERS

**Connector owner** — three patches ready, all blocked on committing production source first (`20260829T153052Z`): `20260829T152600Z` kaedra_ask, `20260829T152614Z` listLegs, `20260829T152633Z` tracker_spend. I can apply all three from phoebus the moment the source lands.

**GM** — HUD credentials on the Space (`NGS_HUD_USER`/`NGS_HUD_PASSWORD`); `shards_status` reports `up:false` purely because the Space says `public_ready:false`. Values exist on phoebus and are now in its keymaker; setting them needs an HF credential that is on no box I can reach. Also `CLOUDFLARED_NGS_TUNNEL_TOKEN` — confirmed absent from phoebus **and** blade.

**blade** — 2.2% disk free; shard-node pid 23836 burning ~2.8 cores (`20260829T135522Z`). **Read `20260829T143050Z` before freeing space: `ollama rm` on an "8.1 GB" model frees almost nothing** because models share weight blobs (76 GB logical vs 35 GB physical). Measure-delete-measure, one at a time.

**whoart** — 2.9% disk, never escalated. `ShardStandbySync` fires every ~45 min and **fails every time** while showing `State=Ready`. `NouGen-OllamaServe` has been dead since 08/24 yet Ollama serves fine — decide whether that task should exist before "fixing" it, or two things will race for port 11434.

**Anyone** — 169 legs open, some since 2026-08-14. Many are surely done and never acked, and the listing cap is why nobody could see them to close them.

---

# 6. THE PATTERN

Every failure this session shared one signature: **a well-formed success that is missing data.**

`shards_capture` returning `{}` · `recall_trustworthy: true` over zero federated stores · a 200 with a silently truncated list · `State=Ready` on a task that last failed · a port that accepts and never sends a banner · `/health` omitting `substrate` by design · a monitor manufacturing three outages from a missing CA bundle.

None of these error. They all read as *fine* or *nothing there*.

**A connect is not a session. A 200 is not a working service. A health boolean is not a read. A short list is not a quiet board. A quiet log file is not a quiet process.** Confirm through a different path than the one that produced the symptom — and if an API can truncate, check the truncation flag.
