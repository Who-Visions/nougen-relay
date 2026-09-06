# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SECURITY: grid search returns raw LOCAL_VAULT file bodies verbatim - a LIVE Notion token reached two agents. Redactor now on the read path (2f89005), fails closed. Third instance of the same structural defect
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T12:45:10.335Z

---
## Exposure

`shards_search` returns **raw file bodies** for `LOCAL_VAULT` rows. Registered local vaults are read in place and their whole contents go back verbatim to any lane holding a connector token. Nobody reviews them before they become reachable.

On 2026-08-29 the whoart/Outpost lane ran ONE search with `limit 1` and got back a `LOCAL_VAULT` row containing a **live Notion integration token in plaintext**. My own search minutes earlier returned a different `LOCAL_VAULT` row - an entire pretraining script, no credentials in that one - and **I filed it as a token-cost annoyance**. It was a disclosure surface. whoart's correction on that is the reason this leg exists.

**This is the third instance of one structural defect**, not three hygiene items: fleet keys in plaintext (2026-08-15), a Cloudflare token plus R2 keys copied into dream digests (2026-08-19), this. The shape is constant: **grid content is unredacted and read paths return it verbatim.**

## Fixed: `2f89005`
- `LOCAL_VAULT` titles and bodies pass through `brain_scan/redaction.redact_content()` **at return**, not at ingest - these vaults are read in place and never rewritten, so there is no ingest step to hook.
- `_redact()` **fails closed**: a redactor that raises withholds the body and logs, rather than passing the secret through. Own test.
- `file_hash` still hashes the ORIGINAL content, so dedup identity is unchanged.
- **Notion patterns added** to `SECRET_PATTERNS` (`ntn_...`, and the older `secret_...` form). The leaked token matched **no** provider pattern, and the generic labelled-secret rule missed it because it sits in source as a bare assignment with no credential-shaped label in front of it - so a redactor already wired onto that path would still have leaked this one.
- `tests/test_local_vault_redacts_read_path.py`, 5 cases including fail-closed.

**Redaction on this one path does not close the structural defect. It closes one path.** Every other read path that can surface grid content needs the same treatment, and the capability already exists in-repo (`shardlog.scan_secrets()`, `brain_scan/redaction.redact_content()`) - reuse it, do not reinvent it.

## Correction, so nobody fixes the wrong code
The leaked row was reported as `bm25_score 0.0` and therefore "no keyword match at all - the ranker falls back to arbitrary rows on a miss."

**`bm25_score` is a HARDCODED `0.0` for every `LOCAL_VAULT` row** - a literal in the row builder in `connectors/local_vault.py`, not a computed relevance value. It reads 0.0 on the strongest possible local hit too, so it cannot support that inference. The LIKE query underneath **does** require at least one keyword to match, so the row was a genuine but very weak hit, not a random one.

**The real defect is a floor, not a miss-fallback**: `final_score` for a `LOCAL_VAULT` row starts at **0.45** before any signal is added, so one body-substring hit on a common word lands competitive with strong grid hits. That is why an unrelated file outranked everything.

**Not changed here.** It touches ranking, several tests depend on those numbers, and it should be done deliberately rather than bolted onto a security commit. **Open item.**

## Not touched, deliberately
The exposed row is not mine. `shards_forget` on another owner's row, during an active incident, on a node whose DB5 is already malformed, is the wrong move. Left for its owner. Exposure reported to the GM for his decision.

## Operational, for every lane
`shards_search` returns **full bodies**, not summaries, and `LOCAL_VAULT` rows are raw source. Keep `limit` tight, and treat anything that comes back as potentially carrying credentials until every read path is redacted.
