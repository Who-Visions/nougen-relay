# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build Who Visions Universe and photography operating rhythm this week
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T20:57:56.492Z

---
## Mission
Turn the 70,000+ image Who Visions archive into an agent-native, geographically navigable photography knowledge graph while restarting active photography as the upstream source of new canonical material.

## Core doctrine
Do not build a spam engine. Build narrative gravity. Every real image should become a trustworthy node connected to people, places, dates, shoots, events, stories, rights, and related frames so humans and agents naturally keep traversing the archive.

Dave's metaphor: the site is a spider on the net casting a web. The agent should not hit one flat page and leave. It should discover legitimate semantic paths deeper into the Who Visions world.

## Proposed substrate
Evaluate a dedicated Who Visions 9DB style cluster, separate from NouGen operational memory but cross-linkable to it. Photography retrieval needs its own schema and indexes.

Suggested primary entity classes:
1. Image
2. Person / model / collaborator
3. Shoot / session
4. Event
5. Place / venue / geographic point
6. Project / series / gallery
7. Publication / page
8. Rights / license / release record
9. Story / shard / narrative context

Each image should be able to resolve relationships among these classes.

## Canonical image record
At minimum, normalize:
creator, copyright, credit line, license URL, canonical image URL, source asset id, file hash, capture date/time, place, GPS where appropriate, subject identities where authorized, shoot/session, event, project, camera/lens when useful, visible concept/wardrobe, neighboring frames, caption, alt text, provenance, edit status, AI-assisted status where applicable, model/property release references, publication URLs, related shard/story ids, embedding/vector fields, and confidence/provenance for inferred metadata.

## Publication surfaces
Generate from one canonical record rather than hand-authoring separately:
IPTC/XMP metadata in exports
JSON-LD / ImageObject and related entity structured data
accurate alt text and captions
image sitemap entries
canonical URLs
entity pages for people, places, events, shoots, and series
internal semantic links
geographic/time navigation
rights/licensing surfaces
machine-readable APIs or feeds where useful

## Geographic experience
Prototype a map/time interface where a user or agent can enter through geography and follow Who Visions history across years. A possible traversal:
photo -> model -> shoot -> location -> event -> year -> gallery -> story/shard -> another photo.

## This week's execution plan
PARALLELOGRAM this work into independent lanes where safe.

Lane A: Archive census
Count assets, formats, current metadata coverage, duplicate rate, folder/date structure, Cloudinary/library mappings, and what percentage has usable EXIF/IPTC/GPS.

Lane B: Schema + 9DB design
Draft the Who Visions entity model, relationship types, provenance rules, confidence handling, rights/privacy boundaries, and candidate shard/database partition strategy. Do not blindly copy NouGen's schema.

Lane C: Metadata pipeline
Build a small ingestion proof of concept: source image + shoot record + existing shards -> normalized canonical record -> IPTC/XMP + JSON-LD + alt/caption + sitemap payload. Human-review uncertain fields.

Lane D: Geographic graph
Choose a small real historical slice and render it as map + timeline + entity traversal. Prove that place and time can drive discovery.

Lane E: Website integration
Design stable canonical image pages and entity pages that fit the existing Who Visions web stack. Prefer durable URLs and progressive enhancement. Avoid making SEO-only pages with no human value.

Lane F: Retrieval / agent test
Have multiple agents enter through one image and measure whether the graph gives them enough grounded paths to answer questions without external search. Log traversal paths and dead ends.

Lane G: Photography restart
The archive cannot become a mausoleum. Establish a recurring field workflow that produces new shoots and immediately feeds the graph.

## Photography operating rhythm proposal
Daily or shoot-day loop:
CAPTURE -> INGEST -> BACKUP -> SELECT -> CANONICALIZE -> ENRICH -> PUBLISH -> SHARD.

Weekly rhythm:
1. One dedicated photography field block or planned shoot.
2. One archive ingestion / cleanup block.
3. One metadata enrichment block.
4. One publishing block.
5. One graph quality audit: broken links, orphan images, weak metadata, rights conflicts, geographic gaps.
6. One agent traversal test from a random image.

Monthly rhythm:
Review coverage by year, city, person, event, and project. Pick one under-documented cluster and restore it into full graph quality. Measure indexed pages, image discovery, crawl health, agent retrieval quality, conversion/traffic, and licensing inquiries without resorting to keyword stuffing.

## Guardrails
No hidden keyword stuffing, cloaking, fake entities, fabricated captions, or metadata unrelated to the actual image. Preserve model/privacy rights. GPS should be suppressed or generalized when location disclosure could be sensitive. Search performance is a consequence of a truthful, dense archive, not the sole objective.

## Durable canon created
1. `Who Visions Universe: Agent Native Photography Knowledge Graph`
2. `Who Visions Spiderweb Doctrine: Narrative Gravity for Agents`

## Done when for this week's first milestone
We have a written schema, archive census, one working ingestion pipeline, one small geographic/time prototype, and a repeatable photography-to-publish routine tested on a real shoot or historical session.
