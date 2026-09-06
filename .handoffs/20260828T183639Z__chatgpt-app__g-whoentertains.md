# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: TOP 0.01% arXiv scanner rebuild: event-driven RSS ingest with idempotency, version lineage, scoring, and autonomous research handoff
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T18:36:39.496Z

---
Rebuild the arXiv scanner as a production research ingestion lane using arXiv's official RSS contract. Source: https://info.arxiv.org/help/rss_specifications.html

Official feed semantics to honor:
1. Channel has lastBuildDate, pubDate, skipDays. Empty weekends/holidays are normal, not failures.
2. Each item exposes title, abstract link, description, guid, one or more category values, item pubDate, arxiv:announce_type, dc:rights, optional arxiv:DOI, optional arxiv:journal_reference, dc:creator.
3. The description itself includes canonical arXiv id + version and announce type text.
4. arxiv:announce_type differentiates new, replacement/update, cross-list, and combined states such as replace-cross.
5. guid example: oai:arXiv.org:2203.01250v3. Treat GUID as event identity, while canonical paper identity is version-stripped arXiv id.

Architecture:
A. FETCHER
- Poll configured category feeds over HTTPS with conditional GET support if available.
- Timeouts, exponential backoff + jitter, circuit breaker, User-Agent naming NouGen research scanner.
- Persist fetch ledger: feed_url, fetched_at_utc, http_status, content_hash, lastBuildDate, pubDate, item_count, parser_version.
- Respect skipDays and do not page on empty weekend feeds.

B. PARSER
- Namespace-aware XML parser. Never regex the XML body.
- Normalize each item into a typed object:
  event_id = guid
  paper_id = base arXiv id with version removed
  version = integer parsed from vN
  title
  abstract_url
  abstract_text
  announce_type
  categories[]
  authors[]
  announced_at
  rights_url
  doi nullable
  journal_reference nullable
  source_feed
  ingested_at
  raw_item_hash
- Validate required fields. Dead-letter malformed items instead of silently dropping them.

C. IDEMPOTENCY + LINEAGE
- Unique constraint on event_id / GUID.
- Separate paper entity from paper-version event.
- New v1 => create paper + version event.
- Replacement vN => append version event to same paper_id. Never overwrite historical versions.
- Cross-list => attach category announcement event without duplicating paper identity.
- replace-cross => append version lineage and category announcement in one atomic processing transaction.
- Safe replay: processing same XML 1,000 times produces one logical event per GUID.

D. CHECKPOINTING
- Do not checkpoint merely because fetch succeeded.
- Commit checkpoint only after parse + durable event write succeeds.
- Track per-feed last successful build timestamp plus content hash and max seen event sequence/time.
- On restart replay from last safe checkpoint.

E. RESEARCH SCORING
Build a deterministic first-pass score before spending cloud tokens. Suggested weighted dimensions:
- memory / continual learning / retrieval / temporal reasoning
- agent systems / orchestration / planning / world models
- uncertainty / calibration / metacognition
- interpretability / provenance / causal reasoning
- multi-agent coordination
- human cognition / affect / social reasoning
- embeddings / indexing / compression / efficient inference
- multimodal perception relevant to NouGen Art
- infrastructure relevant to relay, shards, daemons, observability
Score 0-100 with explicit feature contributions. Store score_version so rankings are reproducible.

F. TWO-STAGE SUMMARIZATION
Stage 1 local/free model: title + abstract triage, relevance score, predicted NouGen subsystem, novelty estimate, reasons to skip.
Stage 2 expensive model only for high-value papers: structured research memo with:
- problem addressed
- core method
- what is actually novel
- assumptions / limits
- implementation hooks
- NouGen subsystem mapping
- estimated engineering effort
- risks
- 3 concrete experiments
- whether to SHARD, RELAY, BOTH, or IGNORE
Never spend expensive inference on low-value duplicates/cross-lists unless the version changed materially.

G. VERSION DIFFING
For replacement papers, retrieve prior stored abstract/metadata and compute semantic + textual delta.
- If change is metadata-only, avoid full re-analysis.
- If abstract/method claims materially change, reopen research review.
- Persist diff summary and changed_fields.

H. SHARD / RELAY POLICY
- SHARD durable findings, methods, validated architectural implications, and corrected beliefs.
- RELAY actionable engineering experiments, scanner fixes, or papers requiring implementation.
- BOTH when a durable insight also creates work.
- Do not shard raw abstracts as memory spam. Store provenance pointer + distilled finding.
- Every shard/relay must include arXiv paper_id, version, source URL, announced_at, scanner timestamp, and confidence.

I. DATABASE MODEL SKETCH
feeds(id, url UNIQUE, category, enabled, last_build_at, last_success_at, last_content_hash, failure_count)
papers(paper_id PRIMARY KEY, first_seen_at, latest_version, primary_category, canonical_url)
paper_events(event_id PRIMARY KEY, paper_id FK, version, announce_type, announced_at, source_feed_id, raw_hash, payload_json, ingested_at)
paper_categories(paper_id, category, first_seen_event_id, PRIMARY KEY(paper_id, category))
research_scores(event_id PRIMARY KEY, score, score_version, features_json, scored_at)
research_memos(event_id PRIMARY KEY, model, prompt_version, memo_json, created_at)
scanner_dead_letters(id, feed_id, event_hint, error_class, error_text, raw_hash, created_at, resolved_at)
scanner_runs(run_id PRIMARY KEY, started_at, finished_at, feeds_polled, items_seen, new_events, duplicates, failures, tokens_local, tokens_cloud)

J. PYTHON IMPLEMENTATION SKELETON
Use stdlib + requests/httpx + feedparser or defusedxml/lxml. Typed dataclasses or Pydantic. SQLite first if local footprint is priority; WAL mode, foreign_keys=ON, busy_timeout, explicit transactions. Design repository interface so SQLite can later swap to Postgres without changing scanner logic.

Pseudo-code:

async def scan_feed(feed):
    response = await fetch(feed)
    channel = parse_channel(response.body)
    with db.transaction():
        run = begin_run(feed, channel)
        for raw_item in channel.items:
            try:
                item = normalize(raw_item)
                if db.event_exists(item.event_id):
                    run.duplicates += 1
                    continue
                db.upsert_paper_identity(item.paper_id, item)
                db.insert_event(item)
                score = scorer.score(item)
                db.insert_score(item.event_id, score)
                if score >= LOCAL_TRIAGE_THRESHOLD:
                    memo1 = local_triage(item, score)
                    db.save_memo(item.event_id, memo1)
                    if memo1.requires_deep_review:
                        queue_deep_review(item.event_id)
                run.new_events += 1
            except Exception as exc:
                db.dead_letter(feed, raw_item, exc)
                run.failures += 1
        if run.failures == 0 or policy_allows_partial_checkpoint(run):
            db.advance_feed_checkpoint(feed, channel.last_build_date, hash(response.body))
        finish_run(run)

Deep review worker:

def review_event(event_id):
    event = db.get_event(event_id)
    previous = db.get_previous_version(event.paper_id, event.version)
    delta = diff_versions(previous, event)
    memo = deep_model_review(event, delta)
    db.save_memo(event_id, memo)
    if memo.decision in {'SHARD','BOTH'}:
        shards_capture(... provenance-rich distilled finding ...)
    if memo.decision in {'RELAY','BOTH'}:
        relay_create(... concrete implementation experiment ...)

K. CRASH SAFETY / CHAOS TESTS
Must pass:
- process killed after fetch before DB write
- killed mid-item transaction
- killed after event insert before score insert
- duplicate fetches
- feed delivered out of order
- replacement arrives before local v1 exists
- malformed XML item
- network timeout / 429 / 500
- empty weekend feed
- same paper cross-listed across categories
- concurrent scanner workers
- DB locked temporarily
- local model unavailable
- cloud model quota exhausted
Expected behavior: no duplicate logical events, no lost committed events, deterministic replay, no silent memory corruption.

L. OBSERVABILITY
Expose scanner HUD / Pulse spans:
feed_fetch latency/status
items_seen
new_events
duplicates
replacements
cross_lists
dead_letters
score distribution
local inference latency/tokens
cloud inference latency/tokens/cost
shards_captured
relays_created
checkpoint lag
last successful scan
Per run trace id should follow fetch -> parse -> score -> review -> shard/relay.

M. SECURITY / QUALITY
- XML entity expansion protections.
- Sanitize logs so paper text cannot become terminal control sequences.
- Bound item/abstract sizes.
- Schema-version every persisted JSON payload.
- Provenance is mandatory, never let model-generated analysis masquerade as arXiv metadata.
- Treat paper claims as claims, not facts, until independently validated when consequential.

N. ACCEPTANCE CRITERIA
1. Replaying identical feed creates zero duplicate events.
2. v1/v2/v3 form one paper lineage with three immutable events.
3. Cross-list does not create duplicate paper identity.
4. Weekend empty feed is healthy.
5. Crash at any persistence boundary recovers deterministically.
6. A high relevance paper automatically produces a provenance-rich research memo and appropriate shard/relay without Dave manually prompting it.
7. A low relevance paper incurs near-zero cloud cost.
8. HUD shows scanner health and research throughput.
9. All emitted memory has paper id/version/source/time/confidence.
10. Scanner can resume after machine reboot with no manual babysitting.

Done when: scanner runs unattended, consumes official arXiv RSS correctly, preserves version history, spends cloud tokens selectively, and turns high-value research into reproducible NouGen memory + actionable fleet work.
