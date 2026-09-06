# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Validate live arXiv CS feed endpoint against scanner contract
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T18:38:50.531Z

---
User supplied the canonical live Computer Science RSS endpoint: https://rss.arxiv.org/rss/cs . Official arXiv docs confirm archive feeds are formed by appending the archive/category to https://rss.arxiv.org/rss/ and explicitly list this URL for Computer Science. The same docs confirm RSS 2.0 and ATOM feeds are updated daily at midnight Eastern, subject feeds use dotted classes, multi-category feeds use +, and multi-category responses are capped at 2000 results.

Observed integration quirk from this ChatGPT/web environment: direct fetch of the live RSS URL failed because the client rejected application/rss+xml as an unsupported content type. Treat this as a scanner test case: the NouGen scanner must use a raw HTTP client/XML parser rather than any HTML-only fetch abstraction, and should explicitly accept application/rss+xml, application/atom+xml, application/xml, and text/xml.

Implementation requirements:
1. Canonical source definition: archive=cs, rss_url=https://rss.arxiv.org/rss/cs, atom_url=https://rss.arxiv.org/atom/cs.
2. Fetch with a real HTTP client, timeout, compressed responses, redirects, ETag/If-None-Match, Last-Modified/If-Modified-Since, and an explicit NouGen User-Agent/contact string.
3. Accept and parse XML MIME types rather than treating non-HTML content as failure.
4. Parse channel/feed metadata before items so lastBuildDate/pubDate/updated become checkpoint evidence.
5. Preserve raw response hash and headers for provenance and replay debugging.
6. If RSS parse fails, retry once via ATOM for the same category and flag the source degradation rather than dropping the research day.
7. Keep discovery idempotent using GUID/arXiv identity and announce type/version lineage from the prior scanner spec.
8. Schedule shortly after arXiv midnight Eastern publication with jitter, not a tight poll loop. Empty weekends/holidays are normal.
9. Pulse metrics: fetch_status, mime_type, http_status, etag_hit, bytes, parse_ms, item_count, new_count, replacement_count, crosslist_count, duplicate_count, malformed_count, feed_age_seconds, fallback_used.
10. Acceptance test: raw fetch of /rss/cs succeeds under application/rss+xml; parser handles current live feed; simulated wrong content type does not silently pass; RSS outage falls back to ATOM; duplicate fetch yields zero duplicate shard creation.

Done when the live cs feed can be ingested end to end into the scanner without relying on browser/HTML fetch behavior and all provenance/checkpoint telemetry is visible.
