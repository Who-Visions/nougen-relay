# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Harden arXiv API client around official Atom query contract
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T18:41:35.086Z

---
Source: official arXiv API Basics https://info.arxiv.org/help/api/basics.html

Implement scanner enrichment against the documented API query contract, not ad hoc scraping.

Key facts to encode:
1. Primary API is HTTP GET/POST to export.arxiv.org/api/query.
2. Search parameters are URL encoded, e.g. search_query=all:electron, start, max_results.
3. Responses are Atom 1.0 XML, not RSS. Parser must understand Atom namespace plus opensearch and arxiv extension namespaces.
4. Feed level fields include self link, query title/id, updated, opensearch:totalResults, startIndex, itemsPerPage.
5. Entry fields include id, published, updated, title, summary, author/name, arxiv:comment, arxiv:journal_ref, alternate HTML link, related PDF link, arxiv:primary_category, and category terms. Treat optional fields as optional.
6. Use canonical arXiv ID extracted from entry id as paper identity. Preserve returned versioned alternate/PDF links separately from base identity.
7. Build deterministic pagination from totalResults/startIndex/itemsPerPage and checkpoint pages. Never infer completion merely from one short page without inspecting metadata.
8. XML namespace handling must be explicit. Test against default Atom namespace plus opensearch=http://a9.com/-/spec/opensearch/1.1/ and arxiv=http://arxiv.org/schemas/atom.
9. API layer should enrich papers discovered through RSS, and also support targeted recovery/backfill searches. RSS remains discovery heartbeat, API is targeted query/enrichment.
10. Review and obey current arXiv API Terms before production traffic.

Suggested Python shape:

from dataclasses import dataclass
from urllib.parse import urlencode
import httpx
import xml.etree.ElementTree as ET

ATOM = 'http://www.w3.org/2005/Atom'
OPEN = 'http://a9.com/-/spec/opensearch/1.1/'
ARXIV = 'http://arxiv.org/schemas/atom'
NS = {'a': ATOM, 'o': OPEN, 'x': ARXIV}

@dataclass(frozen=True)
class ArxivQuery:
    search_query: str = ''
    id_list: str = ''
    start: int = 0
    max_results: int = 100
    sortBy: str | None = None
    sortOrder: str | None = None

    def params(self):
        out = {
            'search_query': self.search_query,
            'id_list': self.id_list,
            'start': self.start,
            'max_results': self.max_results,
        }
        if self.sortBy: out['sortBy'] = self.sortBy
        if self.sortOrder: out['sortOrder'] = self.sortOrder
        return out

async def query_arxiv(q: ArxivQuery, client: httpx.AsyncClient):
    url = 'https://export.arxiv.org/api/query?' + urlencode(q.params())
    r = await client.get(url, headers={'Accept':'application/atom+xml'})
    r.raise_for_status()
    root = ET.fromstring(r.content)
    total = int(root.findtext('o:totalResults', default='0', namespaces=NS))
    start = int(root.findtext('o:startIndex', default='0', namespaces=NS))
    per_page = int(root.findtext('o:itemsPerPage', default='0', namespaces=NS))
    entries = []
    for e in root.findall('a:entry', NS):
        raw_id = (e.findtext('a:id', default='', namespaces=NS) or '').strip()
        authors = [n.text.strip() for n in e.findall('a:author/a:name', NS) if n.text]
        categories = [c.attrib.get('term') for c in e.findall('a:category', NS) if c.attrib.get('term')]
        links = {ln.attrib.get('rel',''): ln.attrib.get('href') for ln in e.findall('a:link', NS)}
        pdf = next((ln.attrib.get('href') for ln in e.findall('a:link', NS) if ln.attrib.get('title') == 'pdf'), None)
        entries.append({
            'id_url': raw_id,
            'published': e.findtext('a:published', default=None, namespaces=NS),
            'updated': e.findtext('a:updated', default=None, namespaces=NS),
            'title': ' '.join((e.findtext('a:title', default='', namespaces=NS) or '').split()),
            'summary': ' '.join((e.findtext('a:summary', default='', namespaces=NS) or '').split()),
            'authors': authors,
            'comment': e.findtext('x:comment', default=None, namespaces=NS),
            'journal_ref': e.findtext('x:journal_ref', default=None, namespaces=NS),
            'primary_category': (e.find('x:primary_category', NS).attrib.get('term') if e.find('x:primary_category', NS) is not None else None),
            'categories': categories,
            'alternate_url': links.get('alternate'),
            'pdf_url': pdf,
        })
    return {'total': total, 'start': start, 'per_page': per_page, 'entries': entries, 'raw_sha256': __import__('hashlib').sha256(r.content).hexdigest()}

Production requirements:
- HTTP timeout, retry with bounded exponential backoff and jitter.
- Cache by normalized query plus pagination cursor.
- Persist raw response hash and fetch timestamp for provenance.
- Dedup by canonical paper id plus version/update semantics.
- Never overwrite old version history; append new version evidence.
- Unit tests with fixture Atom payloads, including missing optional arxiv fields, multiple authors/categories, zero results, malformed XML, duplicate entries, and pagination boundaries.
- Integration test against a tiny query max_results=1.
- Pulse metrics for request latency, HTTP status, parse failures, papers enriched, cache hit ratio, queue depth and last successful fetch.

Done when the scanner can discover via RSS, enrich via Atom API, restart mid-pagination without duplication or loss, and emit durable shard/relay candidates with full provenance.
