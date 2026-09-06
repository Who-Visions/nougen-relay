# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Use cs.AI recent listing as scanner verification and relevance benchmark
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T18:43:18.409Z

---
The human-facing https://arxiv.org/list/cs.AI/recent should be used as an independent verification surface against RSS/API ingestion. As of Fri Aug 28 2026 it shows 196 cs.AI entries for the day and 1195 recent entries total, paginated 50 per page. Cross-check scanner counts, dates, canonical ids, titles, subjects, comments, HTML/PDF availability, and ordering against this page. High-value NouGen-relevant papers visible today include: arXiv:2608.27454 WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution; arXiv:2608.27260 What Makes Good Agentic Data?; arXiv:2608.27167 Calibrated Enough to Know, Not Calibrated to Act; arXiv:2608.27146 When Tool Outputs Become Commands: Separating Action Induction from Runtime Authorization; arXiv:2608.27086 A Contract-Centered Architecture for Scalable and Manageable Agentic Runtimes; arXiv:2608.26983 GraphMemix: Query-Aware Evidence Forests for Long-Term Multimodal Agent Memory; arXiv:2608.26867 BekchiAI: Measuring, Observing, and Controlling LLM Agents in One Click. Treat the list page as verification/fallback only, not the primary ingestion path. Done when RSS/API/list counts and IDs reconcile deterministically and mismatches raise telemetry instead of silently drifting.
