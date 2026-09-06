# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: gateway security audit done on blade: 2 bugs fixed+verified, cross-lane leak refuted, go-live gated on connector-auth choice
**Branch**: `main` @ `57d52d0`
**Stack**: (undetected)
**When**: 2026-08-06T00:31:01.254335+00:00

---
# Gateway security audit done on blade; 2 real bugs fixed + verified; go-live gated on connector-auth choice

Pre-exposure adversarial audit of `Watchtower/local_search_mcp.py` SSE gateway (mcp.nougenai.com target). Both external review lanes were DOWN (codex = deactivated_workspace/402; gemini = invalid GOOGLE_API_KEY — the same plaintext-key rot already flagged). Audit rests on direct read + an empirical pentest agent that ran live attacks on port 8799 against a DB copy, cleaned up.

## Findings
- **Cross-lane profile leak under concurrency: REFUTED (safe).** 0/40 leaks across 80 interleaved fleet+claude-client calls; CURRENT_LANE is captured per-SSE-connection. No fix needed.
- **Allowlist fail-open: FIXED.** `_record_denied` (~L265) nested the `allowed_categories` check inside "category present", so uncategorized records bypassed any allowlist profile. Now fail-CLOSED: no/mismatched category under an allowlist → denied. Re-tested: allowlist keeps only allowed cat.
- **Recursive filter corrupting envelopes: FIXED.** `apply_gateway_scope` (~L293) treated every nested dict as a droppable record, nulling metadata dicts. Added `record_position` flag: only top-level object + list elements are record positions; dict values are envelope fields (recursed, never nulled). Re-tested: status/summary preserved, results still filtered, standalone denied record (shard_get style) still nulled.
- **?token= hygiene: FIXED.** uvicorn `access_log=False` (keeps token out of access logs) + deprecation warning on query-string auth. Header auth is the real path.
- Residual (accepted): dropping list items can leave a sibling count/total field stale — reveals existence (not content) of a hidden record; audit lane records true counts; not auto-rewritten to avoid corrupting legit totals.
- Legacy shared `.gateway_token` RETIRED (→ .gateway_token.retired-20260805); only per-lane tokens (fleet 14c93e5133aa, claude-client 6eec914cb9f3) remain.

## Live verification (patched, 127.0.0.1:8766, then stopped)
/health 200; no token 401; bad token 401; valid bearer 200; X-NouGen-Lane mismatch 403. Bind loopback-only confirmed. mesh 8765 untouched.

## Go-live gate (needs GM)
claude.ai custom connectors: OAuth 2.0 is standard; static-bearer/header auth is a BETA ("request headers authentication", header allowlist incl. `authorization`), slowly rolled out. Our gateway speaks `Authorization: Bearer`. So: (A) if GM's claude.ai has the header beta → add connector with Request Header, works now; (B) else front with Cloudflare Access (zero-trust, strictly safer, our bearer as defense-in-depth) — needs GM's allowed identity. ?token= will NOT work for claude.ai connectors (POST /messages URL won't carry it). Tunnel NOT brought up.
