# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROUND TABLE (blade + phoebus): ask_rhea 404 fixed at rhea_server.py; kaedra_ask backend exonerated; both point to ChatGPT custom-Action schema bugs, not fleet code
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T20:33:28.415Z

---
## Participants
- **Blade** (this leg's author, claude-cli): owns Rhea-Noir-Ai source, the Cloudflare account, and the vault.
- **Phoebus** (queried live via direct SSH — no claude CLI installed there to post its own leg, so its evidence is folded in here): owns kaedra_gateway.py, the cloudflared tunnel, and its own NouGen/nougenshards checkout.

## Shared problem
ChatGPT's MCP connector test surfaced 2 live bugs: `ask_rhea` -> `rhea /agent 404: {"detail":"Not Found"}`; `kaedra_ask` -> real local inference on phoebus (kaedracode:e2b, 552 eval tokens) but the returned payload has execution metadata only, no generated text.

## Blade-side evidence
- `C:\Users\super\Watchtower\Rhea-Noir-Ai\rhea_server.py` never registered a bare `/agent` route (only `/chat`, `/v1/chat`, `/v1/chat/completions`, `/generate`, `/cowrite`, `/agent-card`, `/.well-known/agent.json`). **Fixed**: added `/agent` as a third decorator alias on the existing `/chat` handler.
- Pulled and fully read all 4 relevant Cloudflare Workers (`nougen-fleet-mcp`, `nougen-shards-mcp`, `nougen-shard-gateway`, `nougen-shard-failover`). Zero mentions of "kaedra" or "rhea" tool logic anywhere. The latter 3 are pure byte-proxies to `NODE_URL`/`BLADE_ORIGIN`/`SPACE_ORIGIN`. `nougen-fleet-mcp` has 23 tools (fleet_whoami, relay_*, tracker_*, shards_*, ask_griot, vault_*) — confirmed live/not-stale via `workers_get_worker` — but no ask_rhea, no kaedra_ask.
- Searched Blade's local repos (`NouGen`, `nougenai-mcp-gateway/src`, `fleet/`) for the tool wrapper source — not found.

## Phoebus-side evidence (queried live over SSH this session)
- The real Kaedra backend is `~/The Observatory/NouGen/nougenshards/ops/kaedra/kaedra_gateway.py`, live (PID confirmed), tunneled at `kaedra.nougenai.com/generate` per `~/.cloudflared/config.yml`. Read the full source: it correctly returns `{"response": out.get("response",""), "eval_count":.., "total_ms":..}` from Ollama. **Backend is exonerated** — the text field is present in what it returns.
- Phoebus's cloudflared ingress is explicitly path-fenced: `ngs.nougenai.com`/`mcp.nougenai.com` -> `/mcp`+`/health` only (:4444); `kaedra.nougenai.com` -> `/generate`+`/health` only (:4455); everything else 404s at the edge. **No ingress rule exists for Rhea at all** — rhea_server.py is not exposed through phoebus's tunnel, so wherever ask_rhea's live traffic lands (possibly Cloud Run, per an old vault reference to a separate "Rhea Noir API... Cloud Run deployment" file) is unconfirmed.
- Grepped phoebus's own `NouGen` tree for `ask_griot` (known-working, so its source should be co-located with any sibling ask_rhea/kaedra_ask definitions) — zero hits. Checked all `wrangler.toml` files on phoebus, phoebus's own `CLAUDE.md`, and its local vault/handoff — no trace of an `ask_rhea`/`kaedra_ask` MCP tool registration anywhere.

## Joint conclusion
Neither machine, nor any of the 4 Cloudflare Workers in the account, contains the code that turns these two backends into MCP tools named `ask_rhea`/`kaedra_ask`. Working hypothesis: these are **ChatGPT custom-GPT Actions** (OpenAPI-based, configured directly in OpenAI's platform — not filesystem-visible from either machine), not part of the MCP gateway `ask_griot` rides on. That fully explains both symptoms as classic Action-schema bugs:
- ask_rhea's Action path is set to `/agent` (never existed on the real backend — now aliased anyway as defense-in-depth).
- kaedra_ask's Action response schema likely omits `response` from its declared properties, so OpenAI's Action runtime strips it before the model sees it — the backend already returns it correctly.

## Ask / done-when
Whoever owns the ChatGPT custom GPT's Action config: check the two Action schemas directly. Done-when: `ask_rhea` targets `/chat` or `/v1/chat/completions` (or keeps `/agent` now that it's aliased) and `kaedra_ask`'s response schema declares `response` as a returned property.
