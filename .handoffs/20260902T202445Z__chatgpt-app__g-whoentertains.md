# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: P0 tonight: bring first-class Hugging Face lane online end-to-end
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T20:24:45.986Z

---
# P0 TONIGHT — Hugging Face lane must be live

**Owner intent:** Dave wants a real Hugging Face provider lane online tonight (2026-09-02 ET), using the SAME canonical NouGen MCP door: `https://shards.nougenai.com/mcp`.

## Current evidence
HuggingChat already accepts the NouGenShards custom MCP server and reaches it. Its Health Check currently fails with: **Authentication required. Provide appropriate Authorization headers in the server configuration.** That is positive transport evidence. Do not misdiagnose this as reachability failure.

## Hard architecture rules
- DO NOT create `huggingface.nougenai.com` or any provider-specific public MCP fork.
- DO NOT weaken the canonical gateway's auth.
- DO NOT paste a fleet/root token into HuggingChat.
- Create a **scoped, revocable Hugging Face/HuggingChat credential/identity**.
- First lane should be READ-ONLY until attribution and revocation are proven.
- Lane attribution must never silently fall back to `claude-app` or another provider.
- Preserve identity fields separately: `provider=huggingface`, `client=huggingchat|responses-api|claude-code|codex`, `fleet_lane=huggingface-app`, `model`, `downstream_provider`, `routing_policy`, `reasoning_effort`, `machine`, `source_node`.
- All examples below use placeholders. Secrets come from Keymaker/env only.

## Official HF sources used
- https://huggingface.co/docs/inference-providers/index
- https://huggingface.co/docs/inference-providers/guides/responses-api
- https://huggingface.co/docs/inference-providers/integrations/index
- https://huggingface.co/docs/inference-providers/integrations/claude-code
- https://huggingface.co/docs/inference-providers/integrations/codex
- https://huggingface.co/docs/chat-ui/en/configuration/mcp-tools

## 1. HuggingChat / Chat UI MCP configuration
HF Chat UI documents `headers` as an optional MCP server field. The intended shape is:

```json
[
  {
    "name": "NouGenShards",
    "url": "https://shards.nougenai.com/mcp",
    "headers": {
      "Authorization": "Bearer ${NOUGEN_HF_MCP_TOKEN}"
    }
  }
]
```

If the hosted HuggingChat UI exposes a custom-header editor, use the scoped HF lane token there. If it does NOT expose headers in the hosted UI, do not hack around it. Determine whether the canonical MCP OAuth flow is supported by HuggingChat and fix the server-side auth handshake cleanly.

Self-hosted Chat UI reference shape:

```bash
MCP_SERVERS='[
  {"name":"NouGenShards","url":"https://shards.nougenai.com/mcp","headers":{"Authorization":"Bearer '${NOUGEN_HF_MCP_TOKEN}'"}}
]'
```

HF also documents optional HF-user-token forwarding for self-hosted Chat UI:

```bash
MCP_FORWARD_HF_USER_TOKEN=true
```

Do NOT turn that on by default for NouGen until we explicitly want Hugging Face user tokens to become an identity source. Prefer our own scoped NouGen credential unless there is a designed token-exchange path.

## 2. Hugging Face token for Inference Providers
HF requires a fine-grained token with `Make calls to Inference Providers` permission.

```bash
export HF_TOKEN="${HF_TOKEN}"
```

Never write `hf_...` into repo files, relays, tests, screenshots, or logs.

## 3. Responses API basic client
HF exposes OpenAI-compatible Responses at `https://router.huggingface.co/v1`.

```python
import os
from openai import OpenAI

hf = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

resp = hf.responses.create(
    model="openai/gpt-oss-120b:fastest",
    instructions="You are a NouGen worker. Preserve provenance.",
    input="Return exactly: HF_LANE_OK",
)
print(resp.output_text)
```

Provider routing variants to test:

```python
MODELS = [
    "openai/gpt-oss-120b:fastest",
    "openai/gpt-oss-120b:cheapest",
    "openai/gpt-oss-120b:preferred",
    "openai/gpt-oss-120b:groq",
]
```

HF default behavior without a suffix is fastest/auto selection. Record the ACTUAL downstream provider if exposed. Do not infer it from the requested suffix when auto/fallback is in play.

## 4. Responses API -> NouGen Remote MCP
HF's Responses API supports server-hosted MCP with `server_url`, `allowed_tools`, and `require_approval`.

Start with a read-only role:

```python
import os
from openai import OpenAI

hf = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

nougen_read_tools = [
    "shards_status",
    "shards_recall",
    "shards_search",
    "shards_window",
    "shards_coverage",
    "ask_griot",
]

resp = hf.responses.create(
    model="openai/gpt-oss-120b:fastest",
    input="Use NouGenShards to recall Dave. Cite source-node provenance in your answer.",
    tools=[
        {
            "type": "mcp",
            "server_label": "nougenshards",
            "server_url": "https://shards.nougenai.com/mcp",
            "allowed_tools": nougen_read_tools,
            "require_approval": "never",
        }
    ],
)

for item in resp.output:
    print(item)
```

**Auth blocker to resolve:** HF's public Remote MCP example does not show an arbitrary custom-header field. Do not assume it exists. Test whether HF follows the canonical MCP OAuth challenge/metadata flow. If the Responses implementation cannot send our required auth today, document the exact protocol gap and keep HuggingChat + HF-backed harness routes progressing independently. Do NOT expose an unauthenticated NouGen endpoint just to make the demo green.

## 5. Role-specific MCP tool belts
Prototype policy in code, not prose-only:

```python
ROLE_TOOLS = {
    "historian": [
        "shards_status", "shards_recall", "shards_search",
        "shards_window", "shards_coverage", "ask_griot",
    ],
    "relay_reader": [
        "relay_open", "relay_read", "relay_latest", "relay_claim_list",
    ],
    "memory_curator": [
        "shards_recall", "shards_search", "shards_mark",
        "shards_capture", "shards_amend",
    ],
}
```

First HuggingFace lane MUST use the historian/read-only set. Prove write tools are absent or denied before widening scope.

## 6. Reasoning effort as scheduler knob
HF Responses supports reasoning effort on compatible open reasoning models:

```python
resp = hf.responses.create(
    model="openai/gpt-oss-120b:groq",
    input="Audit this relay for contradictions.",
    reasoning={"effort": "low"},
)
```

Bench the same task across `low`, `medium`, `high`. Record latency, token usage if returned, correctness, tool behavior, and final judge score.

## 7. Streaming / tool-event observability
Use Responses streaming to inspect tool orchestration rather than only final prose:

```python
stream = hf.responses.create(
    model="openai/gpt-oss-120b:fastest",
    input="Recall the latest NouGen federation milestone.",
    stream=True,
)

for event in stream:
    print(event)
```

We need telemetry hooks around `response.created`, tool events, deltas, completion, errors, and retries/fallbacks where exposed.

## 8. Claude Code backed by Hugging Face
Official HF integration supports Claude Code as the HARNESS while HF/open models are the BRAIN.

Recommended extension path:

```bash
export HF_TOKEN="${HF_TOKEN}"
hf extensions install hf-claude
hf claude
```

Manual path:

```bash
export ANTHROPIC_BASE_URL="https://router.huggingface.co"
export ANTHROPIC_AUTH_TOKEN="${HF_TOKEN}"
export ANTHROPIC_API_KEY="${HF_TOKEN}"
export ANTHROPIC_DEFAULT_OPUS_MODEL="zai-org/GLM-5.1"
export ANTHROPIC_DEFAULT_SONNET_MODEL="zai-org/GLM-5.1"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="zai-org/GLM-5.1"
export CLAUDE_CODE_SUBAGENT_MODEL="zai-org/GLM-5.1"
claude
```

Treat `harness=claude-code` and `model=zai-org/GLM-5.1` as separate telemetry fields. A Claude Code shell running GLM through HF is NOT an Anthropic-model inference event.

## 9. Codex backed by Hugging Face
In `~/.codex/config.toml`:

```toml
[model_providers.huggingface]
name = "Hugging Face"
base_url = "https://router.huggingface.co/v1"
env_key = "HF_TOKEN"
wire_api = "responses"
```

In `~/.codex/huggingface.config.toml`:

```toml
model_provider = "huggingface"
model = "openai/gpt-oss-120b:fastest"
```

Launch:

```bash
export HF_TOKEN="${HF_TOKEN}"
codex --profile huggingface
```

One-shot regression probe:

```bash
codex exec --profile huggingface "Return HF_CODEX_OK and identify your configured model provider."
```

Pinned provider / policy variants:

```toml
model_provider = "huggingface"
model = "openai/gpt-oss-120b:groq"
```

or

```toml
model_provider = "huggingface"
model = "openai/gpt-oss-120b:cheapest"
```

## 10. OpenAI-compatible chat endpoint baseline
Useful as a boring control before agent/MCP complexity:

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

out = client.chat.completions.create(
    model="openai/gpt-oss-120b:fastest",
    messages=[{"role": "user", "content": "Return HF_CHAT_OK"}],
)
print(out.choices[0].message.content)
```

Raw HTTP control:

```bash
curl -sS https://router.huggingface.co/v1/chat/completions \
  -H "Authorization: Bearer ${HF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "model":"openai/gpt-oss-120b:fastest",
    "messages":[{"role":"user","content":"Return HF_CURL_OK"}]
  }'
```

## 11. Model catalog adapter
HF documents `/v1/models` as exposing available models and, when available, per-provider pricing/context/latency/throughput. Build a catalog snapshotter.

```python
import os, requests

r = requests.get(
    "https://router.huggingface.co/v1/models",
    headers={"Authorization": f"Bearer {os.environ['HF_TOKEN']}"},
    timeout=30,
)
r.raise_for_status()
models = r.json()
print(type(models), len(models.get("data", [])))
```

Persist normalized scheduler fields, not raw provider blobs only:

```python
candidate = {
    "fabric": "huggingface",
    "model": model_id,
    "provider": provider_id,
    "context_length": context_length,
    "latency_ms": latency_ms,
    "throughput_tps": throughput_tps,
    "input_price": input_price,
    "output_price": output_price,
    "supports_tools": supports_tools,
    "supports_responses": supports_responses,
    "observed_at": observed_at,
}
```

## 12. Provenance event shape
Every HF inference path should be capable of emitting something equivalent to:

```json
{
  "provider": "huggingface",
  "client": "huggingchat",
  "fleet_lane": "huggingface-app",
  "fabric": "hf-inference-providers",
  "model": "openai/gpt-oss-120b",
  "downstream_provider": "groq",
  "routing_policy": "fastest",
  "reasoning_effort": null,
  "mcp_server": "https://shards.nougenai.com/mcp",
  "mcp_scope": "read-only",
  "source_nodes": ["blade", "phoebus"],
  "complete": true
}
```

Do not fake unknown downstream-provider/source-node values. Unknown must stay unknown.

## 13. Tonight's acceptance tests
1. **HuggingChat auth:** Health Check on `https://shards.nougenai.com/mcp` goes green using a scoped HF/HuggingChat credential or standards-compliant OAuth flow.
2. **Identity:** `fleet_whoami` / equivalent provider identity shows a first-class HF lane, target name `huggingface-app`, never `claude-app` fallback.
3. **Read test:** fresh HuggingChat asks `recall Dave` and receives real shard evidence.
4. **Federation:** when fan-out is healthy, response can surface Blade + Phoebus provenance. If Phoebus misses grace or errors, `complete:false` is visible, never hidden.
5. **Write denial:** first HF/HuggingChat identity cannot call `shards_capture`, `shards_amend`, `relay_create`, etc. until scope is intentionally widened.
6. **Responses baseline:** one plain HF Responses call succeeds.
7. **Responses MCP:** attempt direct Remote MCP against canonical NouGen. If auth unsupported, capture exact response/protocol limitation rather than weakening NouGen.
8. **HF-backed harness:** get at least one of Claude Code-over-HF or Codex-over-HF to return a verified probe; ideally both.
9. **Provenance:** logs distinguish harness vs fabric vs model vs downstream provider vs lane vs source node.
10. **Regression artifact:** add a small repeatable probe/test so tomorrow we can prove the HF lane still exists without relying on screenshots.

## Suggested order tonight
P0a HuggingChat scoped auth -> P0b first-class lane attribution -> P0c read-only recall -> P0d provenance + write-denial -> P1 Responses baseline -> P1 Remote MCP auth experiment -> P1 Claude Code/Codex HF harness probes -> P2 model catalog + routing/eval matrix.

**Done when:** Hugging Face is no longer merely an inference vendor in NouGen. It is a named, attributable, revocable, provider-native lane that can enter through the canonical MCP door and participate in the same Shards/Relay world without provider-specific forks.
