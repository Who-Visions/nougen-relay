# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Reverse engineer God's Eye View patterns into NouGen spatial temporal evidence UI without cloning the product
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T15:22:20.756Z

---
Research target: https://github.com/bilawalsidhu/gods-eye-view . Treat this as pattern extraction and architectural inversion, not a request to clone branding/product behavior.

WHY IT MATTERS
God's Eye View solves the spatial interface bottleneck: many heterogeneous public signals become one navigable 3D world. NouGen already has the complementary substrate: shards, provenance, temporal recall, Griot, relays, agents, tracker, visual evidence design, federated stores. Reverse the useful patterns so NouGen can become space x time x evidence rather than just a live globe.

UPSTREAM PATTERNS VERIFIED FROM CURRENT REPO
1. Layer architecture: UI separated from data modules, one module per signal/layer, shared management/context store.
2. Explicit epistemic state: live, delayed, partial, simulated, reconstructed estimate, unavailable. Source and freshness stay visible instead of being flattened into one apparent truth.
3. Smooth temporal presentation: feeds arriving every 15 to 30 seconds are rendered one interval behind and interpolated between known fixes; dead reckoning fills gaps. This is presentation logic, not permission to relabel inference as observation.
4. Transferable view state: camera, style, enabled layers and tracked target serialize into a shareable state. Their framing is useful for NouGen relay: a view can become a handoff packet.
5. Cached and budget governed provider proxies, fixed/allowlisted destinations, bounded requests, timeouts, response caps and sanitized errors.
6. Local first secret handling: private credentials brokered server side, browser gets only intentionally exposed/restricted credentials or ephemeral tokens.
7. Data source licensing/provenance is first class. Runtime fetched data is preferred where redistribution rights are unclear.
8. Strong boundary: model events/assets/infrastructure/systems, not named person search, face recognition or individual tracking. Preserve this boundary in NouGen spatial work.

REVERSE INTO NOUGEN
Build a Spatial Temporal Evidence Plane, not a God's Eye clone.

Canonical observation envelope should include stable event/asset id, source id, source URI/ref, observed_at, received_at, indexed_at, location/geometry, altitude where relevant, entity class, payload hash, freshness state, epistemic class, confidence, license/terms pointer, provenance chain, related visual asset ids, model observations, supersedes/corrects relations and access scope.

Keep OBSERVATION separate from INFERENCE separate from RECONSTRUCTION separate from SIMULATION. Never let interpolation/dead reckoning mutate source truth. Store source fixes immutably; derive display trajectories separately and label them.

Suggested truth grammar:
OBSERVED_VERIFIED = direct source measurement with provenance
OBSERVED_DELAYED = source measurement older than freshness SLA
PARTIAL = source coverage known incomplete
INFERRED = model/rule derived claim
INTERPOLATED = display estimate bounded by known observations
PREDICTED = forward estimate from model
RECONSTRUCTED = historical estimate assembled after the fact
SIMULATED = synthetic scenario
CONTRADICTED = credible sources disagree
UNAVAILABLE = source expected but currently absent
STALE = exceeded source specific TTL

NOUGEN ADVANTAGE
Every map object should be able to open its temporal evidence trail through Griot/Shards: what was observed before, source history, contradictions, corrections, associated images, relays, agent conclusions and provenance. The map becomes a viewport into memory, not the memory database itself.

VIEW BATON
Create a serializable NouGen ViewBaton containing camera/viewport, time cursor, selected entity/event, active layers, filters, evidence ids, epistemic display policy, agent/thread context and optional task/relay id. A user can hand the exact spatial-temporal investigation from phone to desktop or from ChatGPT to Kaedra/Rhea without losing state. Sign/hash baton state so it can be audited and reproduced.

TIME MACHINE
This is where NouGen can exceed the reference project. Persist normalized observations and immutable source provenance so users can scrub backward through evidence. Use tiered storage: hot recent state, warm indexed history, cold immutable objects. Build temporal tiles/snapshots only when requested or popular, not eagerly for the whole planet. Cache derived views separately from canonical events.

VISUAL SHARDS INTEGRATION
Bind images/video keyframes/public camera frames to observations using content hashes, perceptual hashes and provenance graphs. MCP carries references/thumbnails by default; hydrate full pixels only when a vision task requires them. Model descriptions remain claims attached to the original asset, never replacements for it.

MCP SURFACE
Potential tools/resources: spatial_layers, spatial_query, spatial_entity, spatial_window, spatial_nearby, spatial_evidence, spatial_view_save, spatial_view_load, asset_get, asset_thumbnail, asset_analyze. MCP is control/retrieval plane, not bulk media/object storage.

SAFETY/PRIVACY
No named-person geolocation, face recognition, stalking surfaces or persistent individual tracking. Apply capability scopes and source-specific policy. Strip or restrict sensitive EXIF/location metadata where needed. Public signal does not automatically mean safe to aggregate without limits. High consequence operational uses require authoritative verification and should not treat the visualization as ground truth.

IMPLEMENTATION STRATEGY
Phase 0: write schemas and epistemic/freshness invariants first.
Phase 1: adapter SDK and layer registry with 2 to 3 harmless public/system layers.
Phase 2: temporal observation store + Griot evidence trail.
Phase 3: ViewBaton serialization across devices/agents.
Phase 4: visual shards + lazy media hydration.
Phase 5: 2D/3D client as replaceable viewport. Do not bind core evidence model to Cesium or any one renderer.
Phase 6: voice/agent control through capability scoped MCP tools.
Phase 7: historical scrub, contradiction overlays, provenance inspection and replay.

TEST INVARIANTS
A rendered point must always resolve back to canonical evidence.
A derived position must never overwrite an observed position.
Every displayed state exposes source + freshness + epistemic class.
Same ViewBaton must reproduce materially same view against same evidence snapshot.
Removing UI must not remove evidence/history.
One failed/slow source must degrade its layer, not stall all layers.
No provider secret leaks to clients except explicitly designed restricted/ephemeral credentials.
Every third-party source has machine-readable terms/attribution metadata.
Historical correction is append/supersede, not silent rewrite.

LICENSE NOTE
Repo code is MIT, but bundled/live datasets and media have separate terms. Do not assume MIT covers screenshots, promotional GIFs, Google imagery or third-party data. Borrow patterns or properly licensed code with notices; separately audit every dataset/media dependency.

DONE WHEN
Fleet produces a NouGen-native architecture proposal and thin vertical prototype where at least three heterogeneous observation sources normalize into the canonical envelope, render in a replaceable viewport, expose freshness/epistemic state, persist provenance, can be queried historically through Shards/Griot, and can serialize/restore a signed ViewBaton. Do not create a new provider-specific gateway URL. Fit this behind existing NouGen gateway/MCP architecture.
