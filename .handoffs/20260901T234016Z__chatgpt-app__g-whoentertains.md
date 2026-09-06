# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Implement provider-native multi-agent specialization loop
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T23:40:16.595Z

---
Dave wants each conversational turn to improve NouGen's multi-agent routing by what each provider actually supports, with useful deltas sharded and actionable work relayed. Start from the just-captured provider-native specialization v0.1 decision.

Implement a capability/policy-aware scheduler model with identity fields kept separate: provider, account, model, NouGen lane, machine. Do not treat multiple email addresses as quota aggregation where provider terms disallow multiple accounts. Current official-doc findings checked 2026-09-01: Ollama Free includes local models and starter cloud usage; Ollama says one account per person, so schedule local Ollama by machine/hardware, not account multiplication. OpenRouter Free advertises 25+ free models, 4 free providers, 50 requests/day and supports model fallbacks/provider routing; OpenRouter terms prohibit multiple accounts per user, so use one compliant account scope and BYOK only within provider terms. Hugging Face Inference Providers Free currently gives $0.10 monthly credits and spans text/tool calling, embeddings/RAG, classification, NER, summarization, image/video/speech; use it as specialist/eval/modality lane, not assumed bulk-free text pool. HF multi-account policy remains unverified and must be checked before any pooling logic.

Proposed first role map: local Ollama = bulk digestion/shard distillation/classification/regression/recursive cheap passes; OpenRouter = heterogeneous model scout + fallback/router + comparative judges; Hugging Face = embeddings/RAG/classifiers/multimodal/specialist experiments; premium first-party lanes = promoted high-stakes/strong-reasoning/native-tool tasks.

Ask: create a machine-readable provider capability registry and routing score skeleton that includes capability match, policy eligibility, current quota/credits, latency, cost, cache affinity, reliability, and model quality/eval score. Add a hard gate so policy_unknown cannot participate in quota pooling. Preserve provenance for every dispatch.

Done when: one representative task can be classified and routed among these lanes with an explicit reason code, no cross-account quota-circumvention behavior, and the routing decision is emitted to telemetry/shards for later eval feedback.
