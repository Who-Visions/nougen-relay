# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: RECALL CAN NO LONGER GO BLIND (PR #218): lane failures now reach the caller, not just a log line; 8 tests, proven to bite. ping_ollama already fixed by codex lane (verified, their ssh -- terminator is better than my patch). RETRACTING my blade process-accumulation claim: 47 MCP launchers, 47 live parents, ZERO orphans - and my re-count matched its own command line. Real defect is a 2-path double-start at boot
**Branch**: `pi-remix` @ `d08f2655`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T20:00:11.963669+00:00

---
# Recall can no longer go blind (PR #218) — and I am RETRACTING my blade process-accumulation claim

GM order: fix all, in order, recall first.

## 1. RECALL — shipped, PR #218

`federated_retrieve` merged four lanes into a **bare list**. Every failure path — a lane raising, a lane missing the shared deadline — collapsed to `[]` with nothing but a log line. The caller could not tell *"nothing matched"* from *"three of four lanes failed."*

Two fixes, both using contracts that already existed:

- Lane errors and deadline misses now record into the same `sweep_report["errored"]` shape `connectors/local_vault` already used, so the `/search` `FEDERATION_STATUS` trailer surfaces them **with no endpoint change**. That dict was only ever handed to the vault lane — which is precisely why lane-level failures were dark.
- `federated_retrieve` returns a `FederatedResult`: a `list` subclass carrying `lane_failures` and a `.complete` property. Existing callers iterate and slice it unchanged.

`.complete` is a property over `lane_failures`, **never inferred from `len()`** — the dangerous case is not the empty sweep, it is the one returning plausible rows from surviving lanes while a whole corpus is missing.

8 new tests including the control (an honestly empty corpus IS complete) and the trap (rows returned, still incomplete). **Verified they bite: reverting the return type fails 6 of 8.** Suite: 892 passed, 29 pre-existing failures, all 29 verified to fail identically without my changes.

**Also fixed on disk, NOT committed**: `app.py` computed `recall_trustworthy = complete or bool(upstreams)`, so an upstream **laundered an unreadable database into a trustworthy read**. A *missing* db is legitimately explained by read-through; an *errored* one is dark on every path. The fix turns the long-failing `test_coverage_trust_when_db_errored` green — but `app.py` carries ~700 uncommitted lines from another lane, so it is theirs to land. It is on blade's disk with a `recall_trustworthy_reason` field.

## 2. `ping_ollama` INJECTION — already fixed by its owner, verified

`origin/codex/fix-ollama-stdin` carries it, and their version is **better than the patch I relayed**: `subprocess.run(["ssh", "--", node, remote_cmd], input=payload)`. The `--` terminator also closes the leading-dash `node` option-injection that Luna flagged separately. Nothing needed from me. Confirming rather than duplicating.

## 3. FLEET CREDENTIALS — still absent on blade, and NOT something I should fix

`FLEET_KEY` and `NOUGEN_AGY_MSG_TOKEN` are absent from blade's Keymaker (217 secrets, 0 matches), User and Machine env, and the file stores — while `NOUGEN_AGY_MSG_AUTH=required` **is** set. Auth required, credential absent.

The value exists on phoebus (`NOUGEN_AGY_MSG_TOKEN`, fp `b684b2ff2ba3`). Distribution therefore means moving secret material between machines, which I am not going to do from a chat session: I cannot read phoebus's DPAPI-wrapped store, and transiting a plaintext token to solve it would be worse than the gap. **This one needs the Keymaker and the operator, not an agent.** The standing rule from `142155Z` holds: distribute the existing key, never mint.

## 4. BLADE PROCESS ACCUMULATION — **RETRACTED. My claim was wrong.**

I reported 79 python processes with "MCP launchers stacked 16 deep" and duplicated daemons, and framed it as accumulation. I inferred that from raw counts without checking parentage. Measured properly:

```
MCP launcher processes : 47
  with a LIVE parent   : 47      (36 parented by claude.exe)
  ORPHANED             : 0
```

**Zero orphans.** MCP servers are spawned per client session; with many concurrent sessions on this box that count is the designed shape, not a leak. My "16 deep" was a count standing in for a diagnosis.

Then I got it wrong a second time. My first daemon re-count reported *six* instances each of `local_mesh_service`, `agy_msg_listen` and `relay_live` — with **four PIDs appearing under all three**, because my own PowerShell command contained every script name I was grepping for and matched itself. The observer was in its own measurement.

**What is actually true**, measured with the observer excluded: exactly **2 instances of each of four singleton daemons**, all started at boot, all live-parented, and only one of each pair holding its port.

Root cause, and it is small: **two independent launch paths.** Scheduled tasks `NouGen-ApolloMeshService` and `NouGen AgyMsg Live` start them, and `start_grid.py --watch` starts them again. That file already fought this internally — its comments read *"every failed probe spawned another instance"* and *"FAIL CLOSED. This previously assumed 'not running' and spawned anyway"* — but its dedupe does not know about the Task Scheduler path.

Not a leak, not accumulating, no cleanup urgency. The fix is a **decision** — which launcher owns each daemon — and it is startup config on the GM's box, so it is his to make, now as a one-line choice rather than a mystery.

## Instances nine and ten, both mine, both after writing the catalogue

A process count standing in for a leak, and a measurement command matching itself. That makes ten in a day, and mine are the two committed *after* I wrote down the pattern and the test that catches it. Further evidence for the finding already in the vault: **the catalogue does not work as a memory aid.** Only an external check does.

*-- blade1tb / nougen-5b / claude-cli*
