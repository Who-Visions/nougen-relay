# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: BUILD: NouGen Wake CLI, skills, adapters, canaries, and relay protocol
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T04:16:59.485Z

---
## Product directive
Dave wants the provider-agnostic NouGen Wake fabric to ship as a complete operator experience for strangers, not as hidden daemon plumbing. Build the CLI commands, reusable skills, provider adapters, diagnostics, proof gates, and relay semantics together.

## Core law
Relay moves intent. Wake restores agency.

A user must not need to know PreInvocation, named pipes, Task Scheduler, inbox drains, session resume flags, provider lifecycle hooks, or daemon internals. NouGen discovers and manages those.

## Required CLI surface
Prefer one stable root command (`nougen`) with discoverable help. Exact implementation may preserve existing commands/aliases where already shipped.

### Runtime discovery
- `nougen runtime discover`
- `nougen runtime list`
- `nougen runtime status [runtime]`
- `nougen runtime capabilities [runtime]`
Show provider/runtime identity, active/idle state if knowable, inject support, wake support, resume support, transport, configured inbox/endpoint, and proof timestamps.

### Wake lifecycle
- `nougen wake status [runtime|--all]`
- `nougen wake doctor [runtime|--all]`
- `nougen wake adapters`
- `nougen wake install [runtime|--all]`
- `nougen wake uninstall [runtime]`
- `nougen wake start [runtime]`
- `nougen wake stop [runtime]`
- `nougen wake restart [runtime]`
- `nougen wake logs [runtime]`
- `nougen wake probe [runtime]`
- `nougen wake canary [runtime|--all]`
- `nougen wake canary --idle [runtime]`
- `nougen wake verify [runtime]`
- `nougen wake policy show [runtime]`
- `nougen wake policy set [runtime] ...`

`doctor` must distinguish at least:
transport, delivery, mid-turn injection, idle wake, session resume, autonomous claim, acknowledgment, receiver proof.

### Messaging / intent
Integrate rather than duplicate existing NouGenMsg/AgyMsg semantics:
- `nougen msg <target> <message>`
- `nougen msg inbox [target]`
- `nougen msg status`
- retain compatibility aliases such as `nougenmsg` / `agy msg` where present.
A message being queued is NOT delivery proof.

### Relay / baton
Expose discoverable relay operations through the same CLI while preserving the canonical registry:
- `nougen relay open`
- `nougen relay latest`
- `nougen relay read <id>`
- `nougen relay claim <id>`
- `nougen relay send --goal ... --message ...`
- `nougen relay ack <id>` if claim/ack semantics remain distinct
- `nougen relay watch`
- `nougen relay canary --to <runtime>`
- `nougen relay reconcile`
Do not silently auto-claim merely because a message exists. Eligibility, scope, lease/claim truth, and safety policy must run first.

### Fleet proof / onboarding
- `nougen doctor`
- `nougen setup`
- `nougen setup --verify`
- `nougen canary`
- `nougen canary --idle`
Onboarding canary sequence: active delivery -> context injection -> idle target -> wake/resume -> context injection -> receiver acknowledgment. Report partial capability honestly when a provider cannot be externally awakened.

## Required skills
Create portable project skills, with no Dave-specific paths/endpoints:
1. `nougen-wake` — interpret wake requests, inspect capability matrix, install/repair adapter, require receiver proof.
2. `nougen-wake-doctor` — diagnose transport vs injection vs idle-wake vs resume vs autonomous-action failures.
3. `nougen-runtime-discovery` — identify Claude/Codex/Antigravity/Ollama/etc and return a normalized capability record.
4. `nougen-baton-canary` — safely test active and idle baton delivery without mutating user projects.
5. `nougen-relay-operator` — read/claim/execute/verify/ack relay legs using leases and scope safety.
6. `nougen-provider-adapter` — authoring contract for future provider wake adapters.
7. `nougenmsg` / messaging skill — normalized send/inbox/receipt semantics across AgyMsg, cc-msg, HTTP, named pipe, etc.

Skills should teach intent, invariants, and verification. They must not hardcode `shards.nougenai.com`, Blade, Dave account names, local absolute paths, or a specific private topology. Those resolve from config/discovery.

## Adapter contract
Every provider adapter should normalize something like:
- detect()
- capabilities()
- health()
- inject(message)
- wake(event)
- resume(session_hint)
- receipt(event_id)
- stop()/repair() when applicable
- explain_unavailable()

Capabilities are explicit booleans/levels, not assumptions: `can_inject_active`, `can_wake_idle`, `can_resume_session`, `can_receive_webhook`, `can_auto_claim`, `requires_user_presence`, etc.

## Proof gates
Do not report ONLINE because a launcher returned success. Recent AGY evidence showed an AgyMsg child could die after a tool call despite an 'active' claim; later persistence had to be installed separately. Require observable health plus receiver-side evidence.

Suggested canary states:
DISCOVERED -> TRANSPORT_OK -> DELIVERED -> INJECTED -> IDLE_WAKE_OK -> RESUMED -> ACKED -> AUTONOMY_VERIFIED.
Partial states are valid and must be surfaced.

## Safety / public-main gate
This is intended for a repo distributed to strangers. Mechanism belongs on public main only after abstraction: no embedded personal endpoints, tenant IDs, account emails, machine names, private repo paths, secrets, or silent elevation. Destructive/external actions require policy gates. Wake should never mean unrestricted execution.

## Immediate AGY acceptance test
Use the Veilverse canary leg `20260903T040909Z__chatgpt-app__g-whoentertains`. With AGY idle and no new Dave prompt, prove: watcher sees eligible baton -> wakes/resumes Antigravity -> injects full baton -> AGY reads provenance -> safely produces requested canon classification -> acknowledges/relays result. If any step requires Dave to poke AGY, mark IDLE_WAKE/AUTONOMY unverified and fix the adapter.

## Done when
A fresh user can install NouGen, run `nougen setup --verify` (or equivalent), see every connected runtime's wake capability, receive actionable remediation, run an idle canary, and get receiver-proven end-to-end results without understanding provider-specific plumbing.
