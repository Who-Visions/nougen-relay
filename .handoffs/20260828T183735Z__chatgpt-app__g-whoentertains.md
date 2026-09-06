# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Extend arXiv scanner with official feed topology, category composition, scheduling, and RSS/ATOM fallback
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T18:37:35.316Z

---
Add these official arXiv feed behaviors to the scanner rebuild, grounded in https://info.arxiv.org/help/rss.html:

1. Support both RSS 2.0 and ATOM feeds for every active arXiv subject area. Treat ATOM as an alternate parser path and validation fallback, not a separate truth source.
2. Canonical feed bases:
   - RSS: https://rss.arxiv.org/rss/<category>
   - ATOM: https://rss.arxiv.org/atom/<category>
3. Support whole archives such as `cs`, individual subject classes such as `math.QA`, and multi category subscriptions joined with `+`, e.g. `cs.AI+q-bio.NC`.
4. Respect arXiv's documented multi category result ceiling of 2000 results. If the configured category bundle risks approaching this ceiling, split it into deterministic smaller feed groups and merge downstream by canonical paper identity.
5. Poll against arXiv's documented daily update cadence around midnight Eastern time, but do not assume a feed fetch is complete merely because wall clock passed midnight. Use feed metadata/checkpoints and retry with jitter around publication windows.
6. Build a declarative feed registry so NouGen can define research lanes such as cognition, memory, agents, continual learning, multimodal systems, robotics, HCI, affective computing, interpretability, causal reasoning, etc. without hardcoding URLs throughout the scanner.
7. Feed registry schema suggestion:
```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

class FeedFormat(str, Enum):
    RSS = "rss"
    ATOM = "atom"

@dataclass(frozen=True)
class ArxivFeed:
    name: str
    categories: tuple[str, ...]
    format: FeedFormat = FeedFormat.RSS
    enabled: bool = True
    priority: int = 50
    research_lane: str = "general"
    tags: tuple[str, ...] = field(default_factory=tuple)

    def url(self) -> str:
        joined = "+".join(self.categories)
        return f"https://rss.arxiv.org/{self.format.value}/{joined}"

FEEDS = [
    ArxivFeed(
        name="nougen_agents",
        categories=("cs.AI", "cs.MA", "cs.CL"),
        research_lane="agents",
        tags=("agents", "reasoning", "language"),
        priority=90,
    ),
    ArxivFeed(
        name="nougen_human_cognition",
        categories=("cs.HC", "q-bio.NC"),
        research_lane="human-cognition",
        tags=("hci", "cognition", "humanistic-ai"),
        priority=95,
    ),
]
```
8. Keep feed construction and paper identity separate. The same paper can arrive through multiple category feeds and cross lists. Dedup by canonical arXiv identity/GUID/version, while preserving every source feed/category as provenance.
9. Track feed-level state separately from paper-level state:
```sql
CREATE TABLE IF NOT EXISTS arxiv_feed_state (
    feed_key TEXT PRIMARY KEY,
    feed_url TEXT NOT NULL,
    last_build_date TEXT,
    last_poll_utc TEXT,
    last_success_utc TEXT,
    last_item_guid TEXT,
    etag TEXT,
    last_modified TEXT,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    parser_format TEXT NOT NULL,
    updated_utc TEXT NOT NULL
);
```
10. Conditional GET support where headers are available: persist ETag/Last-Modified and send `If-None-Match` / `If-Modified-Since`. A 304 should be a successful no-op, not an error.
11. Suggested fetch loop:
```python
import asyncio
import random
from datetime import datetime, timezone
import httpx

async def fetch_feed(client, feed, state):
    headers = {
        "User-Agent": "NouGenArxivScanner/2.0 (research indexing; contact configured locally)",
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9",
    }
    if state and state.etag:
        headers["If-None-Match"] = state.etag
    if state and state.last_modified:
        headers["If-Modified-Since"] = state.last_modified

    r = await client.get(feed.url(), headers=headers, timeout=30.0, follow_redirects=True)
    if r.status_code == 304:
        return {"changed": False, "status": 304, "body": None, "headers": r.headers}
    r.raise_for_status()
    return {"changed": True, "status": r.status_code, "body": r.content, "headers": r.headers}

async def poll_registry(feeds, state_store):
    limits = httpx.Limits(max_connections=4, max_keepalive_connections=2)
    async with httpx.AsyncClient(limits=limits) as client:
        for feed in sorted((f for f in feeds if f.enabled), key=lambda x: -x.priority):
            state = state_store.get(feed.name)
            try:
                result = await fetch_feed(client, feed, state)
                await process_result(feed, result, state_store)
            except Exception as exc:
                state_store.record_failure(feed.name, repr(exc))
            await asyncio.sleep(1.0 + random.random() * 2.0)
```
12. Do not poll aggressively. The official page states feeds update daily, so architect for reliability and correctness rather than high frequency hammering. Use a small number of scheduled checks around the expected publication window plus backoff/retry when feed status indicates delay.
13. Integrate the official arXiv feed status page as a health dependency. If feeds are delayed or degraded, surface `source_degraded` on Pulse instead of interpreting an empty feed as 'no papers today'.
14. Preserve a search API lane separately. The official RSS help page explicitly distinguishes news feeds from search-result access and points search use cases to the arXiv API. RSS should drive daily event discovery; API should be used for targeted enrichment/backfill/search, not as a substitute for the news feed semantics.
15. Acceptance tests:
   - construct RSS and ATOM URLs for archive, single class, and multi category cases
   - same paper from 3 feeds creates one paper identity with 3 provenance edges
   - 304 conditional fetch creates no duplicate work
   - empty weekend/holiday feed does not trip failure alarms
   - delayed arXiv feed raises source_degraded, not false 'zero relevant papers'
   - multi category feed over safe configured threshold is deterministically partitioned
   - RSS parser failure can be cross checked against ATOM for the same category before dead-lettering
   - restart after crash resumes from feed checkpoint with no duplicate shard/relay creation

Design principle: RSS is the daily event surface, the API is targeted query/enrichment, and NouGen's shard grid is durable cognitive memory. Keep those roles separate.
