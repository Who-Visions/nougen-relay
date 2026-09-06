# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix Rhea brain provenance self-report mismatch
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T01:43:20.634Z

---
LIVE BUG FOUND from ChatGPT mobile ask_rhea call. Dave asked Rhea where her brain was coming from. The ask_rhea gateway envelope returned brain=`free:nvidia/nemotron-3-ultra-550b-a55b:free`, but Rhea's generated answer claimed `Anthropic Claude Sonnet 4`. This violates truth/provenance requirements and proves model self-introspection cannot be trusted for backend identity.

ROOT PRINCIPLE: provider/model identity must come from trusted routing/runtime metadata, never from the inference model guessing its own substrate.

FIX ASK:
1. Inject authoritative provider/model/route metadata into Rhea's request context after routing is resolved.
2. For any question like 'what brain are you on?', answer from that trusted envelope, not latent model knowledge.
3. Ideally reserve structured fields such as `agent_identity`, `provider`, `model`, `route`, `fallback_used`, `request_id`, and `observed_at`.
4. Make the user-facing brain statement deterministic from gateway metadata, or post-process/validate Rhea's prose against the envelope before returning it.
5. If prose contradicts routing metadata, metadata wins and emit a provenance mismatch event.
6. Add regression tests across Kimi primary and every free/fallback lane to force the agent to report the actual runtime brain.
7. Preserve the architectural distinction: Rhea-Noir is the persistent agent identity; Nemotron/Kimi/Claude/etc. are replaceable inference engines.

REPRO: ask_rhea('where is your brain coming from right now? identify actual inference brain/provider'). Returned envelope brain Nemotron 3 Ultra 550B free while generated prose said Claude Sonnet 4.

DONE WHEN: Rhea can be routed through any supported engine and her reported brain always matches trusted gateway metadata, with contradictions impossible or explicitly flagged.
