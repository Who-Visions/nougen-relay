# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build NouGen dynamic documentation compiler from relays, shards, and repo truth
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T23:35:20.031Z

---
Full arc proposal: create a Python driven documentation system inside NouGen that continuously converts operational memory into public documentation without letting generated prose outrank source truth.

CORE IDEA
NouGen already produces three classes of evidence every day: source code and config, relay traffic, and durable shards. The README updater should fuse those into a documentation compiler.

Hierarchy of truth:
1. Repository source, config, schemas, tests, live interfaces, manifests. These define current hard facts.
2. Relay registry. These explain what changed operationally, what was attempted, what failed, what was handed off, and what remains unresolved.
3. Shards. These provide durable decisions, lessons, historical context, design rationale, terminology, corrections, and lessons learned.

The system should never let a fuzzy memory overwrite something the repo can prove. Source truth wins. Relays explain transition. Shards explain meaning.

PROPOSED SCRIPT
Create something like tools/readme_sync.py or tools/nougen_docs.py at the NouGen root. It should support multiple modes:

python tools/nougen_docs.py --check
python tools/nougen_docs.py --dry-run
python tools/nougen_docs.py --write
python tools/nougen_docs.py --changelog
python tools/nougen_docs.py --repo <name>
python tools/nougen_docs.py --all-public
python tools/nougen_docs.py --since <timestamp>
python tools/nougen_docs.py --explain

PUBLIC REPO MANIFEST
Maintain a central repo manifest that declares every public NouGen repository, local path, canonical README sections, changelog path, source-of-truth files, and which relay/shard tags belong to that repo. Example fields:

repos:
  nougenshards:
    public: true
    path: ../nougenshards
    readme: README.md
    changelog: CHANGELOG.md
    relay_tags: [shards, mcp, gateway, memory]
    shard_tags: [shards, gateway, connector]
    generated_sections: [status, architecture, tools, endpoints, install, recent_changes]

  nougentracker:
    public: true
    path: ../nougentracker
    relay_tags: [tracker, cost, telemetry]
    shard_tags: [tracker, billing, token-usage]

README STRUCTURE
Human narrative remains human controlled. Generated sections are fenced with explicit markers so the script updates only owned regions:

<!-- NOUGEN:AUTO:STATUS:START -->
...
<!-- NOUGEN:AUTO:STATUS:END -->

<!-- NOUGEN:AUTO:ARCHITECTURE:START -->
...
<!-- NOUGEN:AUTO:ARCHITECTURE:END -->

<!-- NOUGEN:AUTO:RECENT_CHANGES:START -->
...
<!-- NOUGEN:AUTO:RECENT_CHANGES:END -->

The system must never blindly rewrite the entire README.

RELAY SCAN
The updater should scan relay history since the last documentation checkpoint. From each relay it should extract structured signals such as:

repo or subsystem
created time
agent or lane
status
problem
change attempted
result
unresolved work
done-when condition
important terminology
public-facing impact
breaking change signal

Relays are particularly valuable because they encode the actual operational arc, including failures and pivots. They can become the raw material for CHANGELOG entries.

Example transformation:
Relay: tracker daily endpoint returns 404, existing path must be repaired, do not spawn another provider-specific endpoint.

Generated changelog candidate:
Fixed tracker daily routing and preserved the canonical endpoint strategy rather than introducing provider-specific URL fragmentation.

SHARD SCAN
The updater should scan durable shards relevant to each repo for the same period. It should use shards for:

design decisions
architecture rationale
canonical terminology
important failures and lessons
historical context
public concepts
corrections and retractions

Important: retracted or amended shards must be respected. A retracted belief must never be generated as current documentation. Amended shards should contribute only the latest valid interpretation while preserving historical context in the changelog if useful.

CHANGELOG COMPILER
This is the big extension. Generate or update CHANGELOG.md from the operational memory stream.

Pipeline:
relay events + shard decisions + git diff/source inspection -> candidate events -> deduplicate -> classify -> verify -> render changelog

Suggested categories:
Added
Changed
Fixed
Recovered
Deprecated
Security
Infrastructure
Documentation
Known Issues

NouGen-specific category worth considering:
Learned

That category could surface important recursive lessons that materially changed system behavior without pretending they are code releases.

Every generated changelog entry should carry internal provenance metadata in a sidecar state file even if the public markdown stays clean. Example state:

{
  "entry_id": "ngdoc_20260828_001",
  "repo": "nougenshards",
  "sources": {
    "relays": ["20260828T..."],
    "shards": [1234, 1277],
    "git": ["abc123"]
  },
  "confidence": 0.96,
  "verified": true
}

This prevents duplicate changelog entries and lets the compiler explain exactly why a line exists.

SOURCE VERIFICATION
Before a relay or shard can change a hard-fact README section, verify it against the repository.

Examples:
If a shard says 25 tools, count the registered public tools.
If a relay says an endpoint moved, inspect the route table or schema.
If a relay says Python 3.12 is required, inspect pyproject.toml, setup metadata, or CI.
If a shard says a provider is supported, inspect current adapters or manifests.

If memory and source disagree, source wins and the discrepancy should be surfaced as a documentation conflict rather than silently merged.

DOCUMENTATION DRIFT
Treat stale docs as a failing invariant.

CI command:
python tools/nougen_docs.py --check

Expected output on drift:
README DRIFT DETECTED
Repo: NouGenShards
Section: Connector Surface
README: 25 tools
Source: 27 tools
Relevant relays: ...
Relevant shards: ...
Run: python tools/nougen_docs.py --write

This makes stale documentation a detectable system state, not a human memory problem.

EXPLAIN MODE
Add --explain. It should narrate why docs would change:

WHY README CHANGED
27 MCP tools detected. Previous README documented 25.
New tools: shards_capture, shards_mark.
Evidence: tool registry, schema, relay X, shard Y.
Affected sections: Connector Surface, Tool Reference, Recent Changes.

WHY CHANGELOG CHANGED
Three relays described the same tracker routing repair. One shard captured the canonical endpoint rule. Git confirms the route changed. These were merged into one Fixed entry.

RECURSIVE FAILURE MODEL
Tie this directly into NouGen doctrine: we recursively learn through failure.

Failure should not disappear into terminal history. It should become structured operational memory, then documentation when it matters.

Flow:
failure -> relay -> attempted recovery -> pivot -> verified fix -> durable shard -> changelog -> README architecture/status update

That is the full knowledge circuit.

The docs therefore become downstream artifacts of the same recursive learning process as the codebase itself.

READMES AS CURRENT STATE
README should answer: what is this system right now, how do I use it, what interfaces exist, what architecture is current, what is stable, what is experimental.

CHANGELOG AS MEMORY OF TRANSITION
CHANGELOG should answer: what changed, why, what failed, what was repaired, and which user-visible or architectural behavior moved.

SHARDS AS DURABLE WHY
Shards answer: what did we learn and why does this decision still hold.

RELAYS AS MOTION
Relays answer: what was happening between one stable state and the next.

Together:
README = current truth
CHANGELOG = historical motion
RELAYS = operational motion
SHARDS = durable memory
SOURCE = executable truth

PUBLIC SAFETY AND REDACTION
Because relays and shards may contain internal-only details, credentials, machine names, private URLs, raw stack traces, user details, or sensitive infrastructure, never dump them directly into public docs. Add a sanitizer and policy layer:

allowlisted public concepts only
secret pattern detection
private host and path redaction
credential stripping
internal lane names optionally abstracted
no raw relay body publication
no shard publication without transformation

A public changelog entry should be a verified summary, not a memory dump.

STATE AND CHECKPOINTING
Keep a .nougen/docs-state.json file per repo or centrally. Track:
last relay timestamp processed
last shard timestamp/id processed
last git commit processed
rendered entry hashes
README section hashes
source provenance

This makes runs incremental and deterministic.

DEDUPLICATION
Multiple agents often relay the same incident. The compiler needs clustering based on repo, time window, file overlap, semantic similarity, and shared error signatures. Merge related relay events into one change arc rather than producing five noisy entries for one fix.

OPTIONAL AI LAYER
Use deterministic parsers first. AI can help summarize and cluster relays/shards, but generated claims must pass source verification when they concern technical facts. Use AI for wording and narrative compression, not authority.

GITHUB ACTIONS
Add a README/CHANGELOG drift workflow on push and PR. Potential modes:
1. check only on PR
2. optionally generate a patch artifact
3. optionally open a docs-only PR from a bot lane later

Do not auto-push public prose on day one. Start with check, dry-run, review, write. Once confidence is proven, graduate to automated docs PRs.

PUBLIC REPO ARC
Run this across every public NouGen repo. The goal is not identical READMEs. The goal is a shared documentation protocol so each repo derives its dynamic facts from its own source plus relevant NouGen memory.

DESIGN PRINCIPLES
Source truth outranks memory.
Human narrative outranks generated prose in human-owned sections.
Generated sections are bounded and reproducible.
Every generated change is explainable.
Every changelog entry has provenance.
Failures are retained as learning, not hidden.
Stale docs are bugs.
Public docs never expose raw private memory.
One canonical repo manifest controls the fleet.

LONG TERM
Eventually this becomes NouGen Docs, a first-class subsystem. A new agent or external developer could enter any public repo and see a README whose factual sections are synchronized with the code, a changelog reconstructed from actual development motion, and architecture notes backed by durable memory. Instead of documentation being the thing everyone forgets after shipping, documentation becomes a compiled view of the system's lived history.

This is especially aligned with NouGen because the system already has the raw material most documentation generators lack: relays encode work-in-motion, shards encode durable lessons, and the repositories encode executable truth.

Done when:
1. A proposed Python architecture exists.
2. It can map relays and shards to repos.
3. It can generate verified changelog candidates.
4. It can update bounded README sections.
5. It tracks provenance and checkpoints.
6. It sanitizes all public output.
7. It supports --check, --dry-run, --write, --changelog, --all-public, and --explain.
8. CI can fail on documentation drift.
9. At least one public NouGen repo is used as the pilot before fleet-wide rollout.

Core doctrine: NouGen should not merely remember that the system changed. It should compile the verified history of why it changed into the documentation humans actually read.
