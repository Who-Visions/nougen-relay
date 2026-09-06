# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: dav1d:e2b self-ID fixed and verified; audit the other persona modelfiles for the same two defects
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-22T21:45:50.127Z

---
## Done on Blade

`dav1d:e2b` no longer claims to be a cloud model.

**Before**: `DAV1D48 The Gemini Cloud Assist model in Lane Alpha answered this query.`
**After** (fresh token DAV1D49, post-rebuild): `DAV1D49 dav1d:e2b on the local ollama lane answered.`

Root cause was in its own SYSTEM prompt: `AUTHORITY FLEET` listed `Specialist Portals: Developer Knowledge API, Google Docs, Firebase ML, Gemini Cloud Assist` with nothing separating tools-it-calls from what-it-is, so asked to name itself the model grabbed the nearest model-shaped noun in its context.

New file `Sol-Ai/core/Dav1d.Modelfile` (none existed before, only `Solai.Modelfile`):
- IDENTITY block that self-ID answers must come from, with the exact sentence to return.
- Section retitled "AUTHORITY FLEET (tools you call, not identities you claim)".
- Removed a plaintext `GOOGLE_BIBLE_API_KEY` prefix that was sitting in the SYSTEM prompt. A key fragment inside a system prompt is echoable on request. It now resolves from Keymaker at call time.
- `FROM dav1d:e2b` instead of the absolute blob path, so the file is not pinned to one machine's ollama store.

Rollback: previous build kept as `dav1d:e2b-pre-selfid`.

## Ask for whoever picks this up

Both defects came out of one block, so they are likely copy-paste siblings across the other persona models on this box: `sol-ai:e4b`, `griot:e2b`, `rhea-noir:e2b`, `iris-ai:e4b`, `kaedra:e4b`, `DavOs`, `mrs-b`.

For each: `ollama show <tag> --modelfile` and check two things.
1. Vendor product names in a capabilities list with no identity boundary.
2. Embedded credential fragments of any length.

**Done when**: every persona model returns its own tag and lane when asked who answered, and no SYSTEM prompt in the fleet contains a key prefix.

## Still open from earlier this session

`ask_dav1d` and `dav1d_run` remain `Unknown tool` from the connector while being advertised in its tool list. That is unrelated to the modelfile and still needs the Worker tool set reconciled against repo HEAD. See leg `20260822T213030Z__claude-app__g-whoentertains`.
