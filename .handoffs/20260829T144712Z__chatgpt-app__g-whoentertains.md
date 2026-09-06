# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Design NouGen Visual Evidence Plane: top-tier multimodal MCP architecture for images, provenance, retrieval and safe agent use
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T14:47:12.553Z

---
RESEARCH PASS — 2026-08-29

Objective: move NouGen from text/code memory into a first-class multimodal evidence system without turning MCP into a dumb base64 pipe.

CURRENT STANDARD GROUNDING

The current MCP 2026-07-28 resource specification explicitly supports uniquely addressed resources by URI and binary resource contents. MCP tool results can carry mixed content including text, image, audio, resource links and embedded resources. This means images are protocol-native, but protocol support does not imply that large binary blobs should traverse every agent hop. The correct production architecture is to use MCP as the control plane and selective delivery plane while preserving original media in a durable object plane.

TOP .01% DESIGN: NOUGEN VISUAL EVIDENCE PLANE

1. ORIGINAL BYTES ARE THE WITNESS
Never make a caption, OCR result, embedding or vision-model description the canonical asset. The original file is immutable evidence. Every derivative is linked to it as a child artifact with its own identity and provenance.

2. CONTENT-ADDRESSED IDENTITY
On ingest calculate a cryptographic digest over canonical bytes, preferably SHA-256 or stronger approved equivalent. Asset identity should be digest-derived, not filename-derived. Store original filename only as metadata. This gives exact dedupe, tamper detection, deterministic cross-machine identity and safe rename/move behavior.

Recommended identity family:
asset_id = sha256(original_bytes)
blob_uri = nougen://asset/<sha256>
Each derivative gets its own digest plus parent_asset_id and transformation record.

3. HARD + SOFT BINDINGS
Adopt the same conceptual split used by C2PA. Hard binding = cryptographic hash proving exact bytes. Soft binding = perceptual fingerprint that can recover resized, recompressed, cropped or otherwise near-duplicate media. Maintain both. Exact hash answers 'is this the same file?' Perceptual hash/embedding answers 'is this visually the same underlying media?'

4. PROVENANCE GRAPH, NOT FLAT METADATA
C2PA 2.4 formalizes signed claims, assertions, manifests, content bindings, derived/composed assets, and provenance history. NouGen should make provenance a graph: original capture -> import -> edit -> crop -> export -> AI analysis -> publication. Keep actor, machine, timestamp, software/tool, transformation, parent hashes, confidence and signature/attestation status. Where Content Credentials are present, validate and preserve them instead of stripping them. Where absent, NouGen can still maintain its own internal append-only lineage.

5. OBJECT PLANE + MCP CONTROL PLANE
Do not base64 multi-megabyte originals through every MCP call. Store media in local/content-addressed object storage or another durable asset store. MCP carries lightweight resource links, descriptors, thumbnails and signed/authorized fetch references. Transfer original pixels only when the receiving model actually requires them.

Suggested MCP surface:
asset_ingest
asset_get
asset_head
asset_search
asset_similar
asset_thumbnail
asset_derivatives
asset_analyze
asset_provenance
asset_verify
asset_link_shard
asset_extract_frames
asset_redact

MCP resources can expose nougen://asset/<digest> and rendition URIs. A tool result can return image content directly when small enough or when a client requires pixels, but references should be preferred for ordinary orchestration.

6. MULTI-RESOLUTION DELIVERY
Generate safe deterministic derivatives on ingest: tiny preview, UI thumbnail, model-sized rendition, and original. Agents should receive the minimum fidelity needed. A classification agent rarely needs a 45 MP RAW. This reduces latency, bandwidth, vision-token cost and accidental sensitive-detail exposure. Preserve original independently.

7. NATIVE MULTIMODAL RETRIEVAL
Do not reduce every image to text. Current multimodal retrieval practice maps text and images into shared embedding spaces, allowing text-to-image and image-to-image retrieval while preserving visual information that captions or OCR lose. Index multiple representations:
exact hash
perceptual hash
multimodal embedding
OCR text when useful
vision caption/scene graph
EXIF/time/location where authorized
human tags/project/session links
objects/faces only when policy and consent allow

Use late fusion or weighted hybrid retrieval rather than trusting one vector. Query can combine semantic similarity + exact metadata + temporal constraints + provenance trust + shard utility.

8. DERIVED INTERPRETATIONS ARE CLAIMS
Every model observation must record model/provider/version, prompt or analysis policy, timestamp, confidence, source asset hash and transformation/rendition used. Never store 'there is X in this image' as bare truth. Store 'model M observed X from asset A at time T with confidence C.' Human corrections append and supersede; they do not erase historical inference.

9. SHARDS SHOULD POINT TO EVIDENCE
A visual shard should be a compact durable knowledge object linked to one or more asset IDs. Retrieval returns the shard plus evidence handles. Griot can narrate the interpretation, but an agent can pull the pixels or provenance graph when it needs to verify. This prevents text memory from becoming detached from source evidence.

10. SECURITY GATE BEFORE DECODING
OWASP guidance is clear that MIME headers are spoofable and upload systems need defense in depth. NouGen ingest should validate allowlisted formats, magic/file signatures, size and dimensions, generate server-side filenames/IDs, quarantine untrusted inputs, scan where available, store outside webroot, authorize reads, and prevent parser abuse/decompression bombs. Treat SVG as active/risky content because current MCP schema guidance explicitly warns that SVG may contain executable JavaScript. Rasterize or sanitize before model/UI use when appropriate.

11. PRIVACY AND CAPABILITY SCOPING
Asset existence, metadata, thumbnails and originals should be separate capabilities. An agent may be allowed to know an asset exists without permission to receive full pixels or EXIF. Sensitive EXIF and location should be redactable at policy boundary. Build role/capability scopes such as asset:metadata, asset:preview, asset:original, asset:exif, asset:analyze, asset:export.

12. OBSERVABILITY AS A FIRST-CLASS EVENT STREAM
Instrument each image operation with trace_id/event_id using OpenTelemetry-style semantics: ingest duration, bytes transferred, decode time, derivative generation, embedding latency, model/provider, vision/token usage, cache hits, error class, provenance verification outcome and source/destination lane. This should feed the same canonical usage ledger being designed for tracker repair. A visual call cannot become another invisible Kaedra-style execution path.

13. IDEMPOTENCY + EXACTLY-ONCE SEMANTICS
Ingest must be safe to retry. Same bytes should resolve to same asset identity without duplicate storage. Transformation jobs need deterministic job IDs from parent digest + transform spec + version. This makes retries harmless and allows cross-machine cache reuse.

14. TIERED STORAGE AND LOCALITY
Keep hot thumbnails/embeddings close to agents, originals in authoritative object storage, and cold archives tiered. Use content digest for cache keys. Prefer compute-to-data for heavyweight media. Never bounce originals Phoebus -> Blade -> connector -> model if a signed resource fetch can let the authorized consumer retrieve the same immutable object directly.

15. VIDEO SHOULD BE THE SAME SYSTEM, NOT A SECOND SYSTEM
Treat video as an asset with timeline children: keyframes, scene boundaries, audio track, transcript, captions, embeddings and temporal observations. Retrieval should return exact time spans plus source hash. Audio follows the same provenance model. Build the asset abstraction once across image/audio/video/document media.

16. C2PA COMPATIBILITY WITHOUT DEPENDENCY
C2PA 2.4 provides strong concepts for authenticity, manifests, hard/soft bindings and derived/composed assets. NouGen should validate/preserve C2PA when available, map it into internal provenance, and optionally sign NouGen-generated derivatives later. Do not require every asset to have C2PA to enter the system.

17. ACTIONGATE FOR MEDIA SIDE EFFECTS
Reading/analyzing evidence differs from publishing, editing, deleting or externally transmitting it. Route destructive/export/publication actions through ActionGate. A vision model recognizing an image does not authorize posting, deleting, face-identifying, geolocating or sending it.

18. RECOMMENDED VISUAL SHARD SCHEMA
asset_id/hash
mime_verified
byte_size
width/height/duration
captured_at + confidence/source
imported_at
source_machine/lane
original_uri
renditions[]
parents[] / children[]
exact_hash
perceptual_hash(es)
embedding_refs[] with model/version
c2pa_status + manifest_ref
exif_policy/ref
project/session/entity links
observations[] with model/version/confidence
human_assertions[]
access_policy
provenance_events[]
created_event_id

19. RETRIEVAL RANKING
Recommended retrieval score should combine semantic relevance, temporal fit, provenance trust, exact metadata filters, perceptual similarity, human confirmation, shard utility, recency where relevant and contradiction state. The best answer is not simply nearest-vector wins.

20. FAILURE INVARIANTS
No asset is considered ingested until original bytes are durable and hash verified.
No derivative is canonical evidence.
No caption can overwrite the source.
No model observation is provenance-free.
No original pixels leave a trust boundary without authorization.
No aggregate usage path is allowed to omit vision inference.
No delete destroys audit history unless an explicit irreversible privacy/legal deletion path is invoked.

PHASED BUILD

P0: asset identity + immutable blob store + metadata DB + MCP asset_head/get/ingest + thumbnail pipeline + strict upload validation.
P1: visual shards + exact/perceptual dedupe + multimodal embeddings + provenance events + capability scopes.
P2: model observations with attribution + Griot evidence retrieval + ActionGate on exports/edits + OpenTelemetry usage envelopes.
P3: C2PA validation/preservation/signing + video/audio timeline children + cross-machine locality/cache + lineage-aware transformations.
P4: benchmark recall quality, bandwidth reduction, duplicate suppression, provenance recovery and end-to-end verification across ChatGPT/Claude/Gemini/Kaedra/Rhea.

DONE WHEN
A photo can enter on any NouGen machine, receive one deterministic identity, appear through the single MCP gateway, be found by text or visual similarity, be fetched at authorized resolution by any capable agent, retain cryptographic/perceptual provenance through derivatives, attach model claims without confusing them for fact, survive retries without duplication, expose full trace/usage telemetry, and allow Griot to trace every derived claim back to the original immutable media evidence.
