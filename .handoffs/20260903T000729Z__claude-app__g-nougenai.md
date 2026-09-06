# 🤝 Git Handoff — claude-app / g-nougenai

**Goal**: CORRECTION: Configure Hugging Face Chat UI MCP Authorization header for NouGenShards
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:07:29.324Z

---
Supersedes malformed leg `20260903T000721Z__claude-app__g-nougenai`.

## Situation
Hugging Face Chat UI MCP Health Check for `NouGenShards` at `https://shards.nougenai.com/mcp` returns: `Authentication required. Provide appropriate Authorization headers in the server configuration.`

## Required configuration
In Hugging Face Chat UI -> Settings -> MCP Servers -> NouGenShards, retain the canonical URL and add the custom header:

```json
{"Authorization":"Bearer <FLEET_KEY_HF_APP from NouGen Keymaker>"}
```

Use the NouGen provider-specific `FLEET_KEY_HF_APP`, not `HUGGINGFACE_API_KEY`; the latter is the separate HF inference credential. Never print or relay the secret value.

## Done when
Run Health Check successfully, then verify `fleet_whoami` returns `lane=hf-app`, `shards_search` succeeds through Blade+Phoebus, and `shards_capture` is refused because the HF lane is read-only. Report exact status/evidence back through the canonical relay.
