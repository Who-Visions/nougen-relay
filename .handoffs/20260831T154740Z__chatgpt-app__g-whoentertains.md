# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Operationalize intent-to-action loop across every NouGen lane
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T15:47:40.563Z

---
# Coach directive: conversation is now the control surface

Dave's operating doctrine is now explicit: provider chats are not isolated endpoints. Human speech is the intent surface. NouGenShards is the durable memory substrate. NouGenRelay is the execution bus. Cloud and local models are field agents operating against the same canon.

## Required loop
1. Ground user intent against live fleet state and relevant shards before acting when project-specific truth matters.
2. Capture durable decisions, corrections, failures, and reusable architecture into shards.
3. Convert actionable work into relay legs instead of leaving it trapped in chat prose.
4. Let another capable lane claim the baton, execute, verify at the caller-visible boundary, and report evidence.
5. Feed outcomes back into shards so later lanes inherit the result without Dave re-explaining it.

## Behavioral rule
Do not make Dave manually carry context between Claude, ChatGPT, Perplexity, Gemini, or local Ollama agents when NouGen can carry it. Treat conversation as command input, not the final resting place of work.

## Guardrails
Preserve provenance. Distinguish verified state from claims. Do not duplicate open work. Check relay claims before overlapping execution. Fail visibly instead of returning plausible success. Prefer reversible actions where possible. Never promote ingestion time into original creation time without evidence.

## Done when
A fresh provider or local lane can receive a natural-language directive, recover the needed canon and topology from NouGen, create or claim the appropriate relay, execute the task, verify the result, and leave a durable shard or amended record without Dave manually restating the architecture.
