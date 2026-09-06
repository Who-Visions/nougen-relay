# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Complete arXiv scanner contract with API access policy, enrichment lane, and attribution safeguards
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T18:39:57.837Z

---
Use RSS as the low-cost discovery heartbeat and arXiv API as targeted enrichment/retrieval. Official API access page requires reviewing API Terms, API Basics, and User Manual; independent/open-access projects should acknowledge arXiv data usage with: “Thank you to arXiv for use of its open access interoperability.” Do not brand NouGen in a way that implies arXiv endorsement or use arXiv names/logos/colors as project branding. For any commercialized NouGen product using arXiv APIs, review arXiv commercial/public API and bulk pipeline guidance before launch. Architecture: RSS discovers new/replacement/cross-list events; API resolves targeted metadata/search and fills gaps; cache aggressively; dedup by canonical arXiv id/version; rate-limit; backoff; maintain provenance and request telemetry. Add configuration for user agent/contact, attribution text, request budget, API fallback health, and API/Bulk mode selection. Acceptance: scanner can run daily RSS without API spam, enrich only scored papers, survive API outage using queued enrichment, and expose compliance/attribution status in telemetry.
