# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Build NouGen CLI as a polished terminal cockpit with semantic UI and live fleet observability
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T04:39:21.020Z

---
LONG FORM CLI UX SPEC FROM CHATGPT SESSION

VISION
NouGen CLI should feel like a terminal operating environment and fleet cockpit, not a collection of scripts or raw log commands. It must remain terminal-native, fast, composable, scriptable, accessible, and automation-safe, while providing a polished human-facing control surface when attached to a TTY.

CORE PRINCIPLE
The CLI is itself a first-class NouGen client. It should expose the same capability substrate that external AI clients receive: fleet status, recall, relay, ledger, routing, models, topology, diagnostics, and eventually direct natural-language interaction with the fleet.

FIRST-RUN EXPERIENCE
`nougen init` should have ceremony only on first install. Begin with a compact NOUGEN banner and thesis such as `Your infrastructure. One fleet.` Then adaptive onboarding:
1. What should NouGen call you?
2. What should this fleet/instance be called?
3. What are you primarily using NouGen for?
4. What should NouGen optimize for: speed, privacy, cost, quality, balance?
5. How much autonomy should NouGen have?
Then request permission to inspect the machine.

DISCOVERY EXPERIENCE
Use real spinners and phase labels while discovering:
* hardware: CPU, RAM, GPU, VRAM, OS, architecture
* runtimes: Ollama, Docker, Python, Node, Git, LM Studio, llama.cpp, vLLM, etc.
* local models and their sizes/states
* optional inference probe with real latency/tokens-per-second
* local network NouGen nodes
* cloud/provider connections

Never fake progress. Progress bars only when progress is actually measurable. Spinners map to actual phases.

CAPABILITY MAP
After discovery, render a concise map grouped into COMPUTE, LOCAL AI, CLOUD AI, INFRASTRUCTURE, MEMORY, RELAY, LEDGER, MCP. Show discovered capabilities as healthy, missing, or uninitialized. NouGen then proposes a compiled profile based on answers and discovered infrastructure: privacy preference, cost policy, cloud escalation, memory persistence, failure learning, provenance strictness, ledger, MCP, multi-node routing, etc. User accepts/edits/views before construction.

BUILD PHASE
Render deterministic setup phases, e.g.:
[01/09] NouGen home
[02/09] identity
[03/09] Shards
[04/09] Relay
[05/09] Ledger
[06/09] capability registry
[07/09] router
[08/09] MCP gateway
[09/09] diagnostics
Each phase reports actual subchecks. End with `FLEET ONLINE`, counts of machines/providers/models/routes/memory substrate, health, and immediately ask what the user wants to accomplish first. Do not end with a dead `Setup complete.`

SEMANTIC VISUAL GRAMMAR
Color must mean the same thing everywhere. Suggested semantic roles:
* green: healthy, success, ready
* amber: warning, degraded, partial capability
* red: failure
* cyan: network/discovery/cloud activity
* violet: model/AI activity
* dim gray: secondary metadata
* normal/bright foreground: current action
Do not hardwire scattered ANSI codes. Build a centralized UI abstraction, e.g. ui.success(), ui.warn(), ui.error(), ui.info(), ui.spinner(), ui.progress(), ui.table(), ui.panel(), ui.tree(), ui.banner().

MOTION
Animations must communicate state, not decorate. Use spinners for active probes, model warming, network negotiation, shard operations, MCP tests. Keep routine commands instant. First install may have a sub-second node illumination animation ending in `Fleet Online`; do not replay a long intro on every invocation.

`nougen status`
Should be a beautiful fleet dashboard, not JSON. Show fleet name, owner, online state, version, aggregate health, nodes with hardware/load/model counts, providers, memory shard count/database mount/recall status/latest activity, relay active agents/open legs/claims/latest handoff, ledger daily invocations/input/output/cache, routing local-vs-cloud split/cache efficiency, MCP gateway/health/tool count/authentication. Human can understand entire fleet at a glance.

`nougen doctor`
Must explain failures architecturally. Run installation, hardware, local AI, network, Shards, Relay, Ledger, MCP tests with real latency/state. Include end-to-end probes where safe: shard write/search/recall/provenance, relay read/write/identity, MCP discovery/invocation. Summary gives passed/warnings/failures.

When broken, report WHAT broke, WHERE, IMPACT, and ACTION. Example identity mismatch: expected chatgpt-app, received claude-app; runtime healthy but ledger degraded; explain token/provider/provenance impact; recommend repairing identity resolution while preserving working endpoint/data path. Do not lead with opaque stack traces. Verbose mode can expose internals.

`nougen topology`
Render an ASCII/Unicode topology tree showing machines -> local runtimes/models; cloud -> providers; both feeding NouGen Router -> Shards/Relay/Ledger -> MCP Gateway -> external clients. This screen should explain the product visually and be screenshot-worthy.

`nougen models`
Human table of local models by node, size, ready/cold state, speed where measured; cloud providers and status; routing policy such as simple=local, coding=local then cloud, reasoning=best available, embeddings=local, bulk=cheapest capable.

`nougen shards`
Make memory tangible: prominent total shard count, per-database counts and health, coverage earliest/latest, recall/search/federation health, today's captures/amends/retractions/useful recalls if available.

`nougen recall <query>`
Visualize actual stages: semantic recall, keyword search, temporal evidence, provenance verification. Return chronological memories with confidence/source/db and a synthesized earliest/strongest answer. Never fake stage completion.

`nougen relay`
Air-traffic-control feel. Show active agents, machines, tasks, age, open handoffs, sender/status/age. When an agent takes a baton, update visibly. Relay is fleet motion made visible.

`nougen watch`
Live second-monitor mode. Streaming event table with time/lane/model/event, token activity, recalls, shard captures, relay reads, inference, routing/cache hits. Persistent footer with today's tokens, active agents/jobs/nodes/providers and system health. Keyboard controls for pause/filter/details/exit. Motion should be subtle and readable from across a room.

ERROR UX
Errors must have calm operational personality, not cute failure text. Example provider timeout should show provider/model/attempt/ledger id, impact, whether fallback is allowed, the recovery action, and final result. Preserve original failure in ledger. Core philosophy: failure becomes information. Human sees what happened, what it affected, what NouGen did, and whether recovery succeeded. Raw trace available under `--verbose`.

INTERACTIVE HOME
Running `nougen` with no args should open an interactive home screen when TTY is present. Header: fleet name, health, owner, node/model/provider/shard counts. Menu: Ask the fleet, Recall something, View status, View agents, View models, View memory, Run diagnostics, Configure NouGen. Keyboard navigation and search/help/quit. `Ask the fleet` accepts natural language and visibly consults grid/relay/etc. This makes CLI itself a full NouGen client.

AUTOMATION / ACCESSIBILITY CONTRACT
Pretty output can never compromise scripts, CI, logging, screen readers, or piping. Required modes:
* --json for machine-readable output
* --plain for stable text
* --quiet where appropriate
* --verbose for diagnostic internals
* NO_COLOR=1
* NOUGEN_PLAIN=1
* NOUGEN_LOG_LEVEL
Detect TTY. Interactive terminal gets rich rendering. Pipe/redirect gets stable structured/plain output. CI gets no animation. Avoid spinner line rewriting in accessibility/plain modes. ASCII fallback for Unicode tree/arrow glyphs.

DESIGN RESTRAINT
One meaningful spinner feels alive; a wall of simultaneous motion is noise. Use color/motion to encode state. Routine commands should have near-zero startup ceremony.

PRODUCT DOCTRINE
The terminal is the cockpit for whatever computational world the user already owns. A small laptop gets a small cockpit. A multi-machine system with local models, cloud models and provider integrations gets a starship bridge. Both run the same NouGen architecture. The CLI should make that scaling visible without changing the mental model.

IMPLEMENTATION ASK
Turn this into a reusable terminal UI system rather than one-off pretty-print code. Prefer a mature terminal rendering library appropriate to the CLI language, with semantic theme tokens, capability detection, no-color/plain modes, deterministic snapshots/tests, and separation between domain events and presentation. Commands emit structured events/data; renderer decides rich/plain/json representation.

DONE WHEN
1. `nougen init` provides adaptive onboarding + real capability discovery + compiled profile + construction + first useful action.
2. status/doctor/topology/models/shards/recall/relay/watch share one semantic visual grammar.
3. UI degrades cleanly for non-TTY/CI/accessibility.
4. No fake progress, fake health, or decorative misleading animations.
5. Errors explain location, impact, recovery and provenance.
6. CLI can function as a first-class interactive NouGen client.
7. Public repo allows a stranger to reproduce this experience using their own infrastructure.
