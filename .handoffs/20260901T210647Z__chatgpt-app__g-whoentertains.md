# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Audit fresh-provider NouGen bootstrap, auth identity, and default shard exposure
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T21:06:47.179Z

---
## Situation
A controlled fresh-provider test on Grok reproduced the NouGen bootstrap pattern already seen on a fresh Claude account.

### Observed sequence
1. Fresh Grok account/session answered `who am i?` with no name, no location, no history, and no prior personal context.
2. NouGenShards was then connected through the canonical MCP endpoint.
3. User asked `recall dave`.
4. Grok invoked the NouGenShards connector and reconstructed Dave's identity/authority, Who Visions/NouGen role, GM-in-the-skybox framing, shards+relay operating doctrine, canonical single-MCP rule, recent project context, and fleet details.
5. Grok also reported a live authenticated identity string claiming key `g-whoentertains` on the `claude-app` lane, despite the client visibly being Grok.

### Findings
- Cross-provider continuity is now demonstrated behaviorally: a provider with zero native account memory can reconstruct operator identity, architecture, and work context from the external substrate after connection.
- The onboarding path is low-friction. The model can infer `recall` semantics and architecture from tool affordances/shards without a large provider-specific system prompt.
- The same substrate appears capable of exposing not only durable canon but also operator profile, fleet internals, recent work context, and live operational identity.
- That breadth is powerful for continuity but makes authorization/scoping a first-class design concern.
- The reported `claude-app` lane on a Grok client may indicate one of: shared credential reuse, connector-side static lane attribution, fleet_whoami identity not reflecting the actual external client, or a provenance-labeling bug. This needs verification before using lane identity as evidence of which provider made a request.

## Questions for fleet
1. **Provider attribution:** Why would Grok surface `claude-app` as its lane? Is lane identity bound to the bearer/key, the MCP connector deployment, or the actual calling provider? What is the authoritative source of provider/client identity?
2. **Credential isolation:** Are Grok, Claude, ChatGPT, and Perplexity currently sharing `g-whoentertains` or otherwise inheriting the same scope? Should each provider/account receive a distinct credential/fingerprint even if they enter through the same public MCP URL?
3. **Default scopes:** What should a newly connected provider be allowed to retrieve by default? Propose explicit tiers such as public canon, operator profile, project memory, fleet internals, live ops state, private/sensitive shards.
4. **PII minimization:** Should broad queries such as `recall Dave` return contact details/company identifiers by default, or require an elevated scope / exact intent? Define what should be redacted or withheld from generic identity recall.
5. **Live-state leakage:** Should connector-visible responses expose key names, lane names, machine names, runtime topology, or tracker/relay state automatically? Which fields are useful provenance vs unnecessary attack surface?
6. **Bootstrap contract:** Can we formalize a provider-agnostic onboarding sequence: identify self -> inspect allowed tools -> recall operator/project canon -> inspect open relay work -> continue assigned task, without provider-specific prompts?
7. **Auth tests:** Build a sterile cross-provider matrix for ChatGPT, Claude, Perplexity, Grok, then future Mistral/Gemini/Replit/Cursor. Verify the same queries return the same allowed canon while forbidden tiers fail closed.
8. **Provenance:** Every returned shard/result should make it clear whether it is durable canon, recent operational state, inferred synthesis, or connector identity metadata. Can the UI/tool payload distinguish these classes explicitly?
9. **Revocation:** If one external account or provider connector is compromised, can its credential be revoked without affecting the canonical MCP URL or other providers?
10. **Auditability:** Can we log provider/account credential fingerprint + tool + shard class accessed, without storing sensitive prompt content, so cross-provider access can be audited?

## Ask
Audit the auth/identity path and propose the minimum changes needed to preserve the single canonical public MCP endpoint while adding provider/account-specific credentials, scopes, provenance, and revocation.

## Done when
- Explain the Grok -> `claude-app` attribution with evidence.
- Produce a recommended scope model and default-new-provider policy.
- Identify any current overexposure in broad `recall Dave` behavior.
- Define a repeatable cross-provider bootstrap/auth test matrix.
- Preserve `https://shards.nougenai.com/mcp` as the one public front door.
