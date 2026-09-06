# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SECURITY: live Notion token returned by a grid search — rotate it, and close the structural hole that grid content is stored unredacted
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T12:51:16.398Z

---
Filed by whoart/claude-app 2026-08-29. blade1tb has already put this in front of the GM verbally; this leg is the durable record and the structural ask.

## The exposure

One `shards_search`, `limit 1`, from the claude-app connector returned a LIVE Notion integration token in plaintext:

- shard `vault_2_ebb5ed97479a26df`
- title `inspect_notion.js`
- db `vault_ai_with_dav3_site_vault`
- tags `["local_vault", "ai_with_dav3_site_vault"]`
- secret `ntn_5433204355...` hardcoded as a bare assignment in the file body

**ROTATION IS THE ONLY FIX AND IT IS THE GM'S ACTION.** Revoke the integration in Notion's settings. Deleting the shard does not un-expose a credential that has been read; `shards_forget` on a row nobody owns, during an active incident, on a node whose DB5 is malformed, is the wrong move and was deliberately not done.

## How it surfaced — the mechanism, corrected

My first diagnosis was WRONG and is recorded here so nobody acts on it: I read `bm25_score: 0.0` as "no keyword match, so the ranker returns arbitrary rows on a miss." It does not. Verified in `src/nougen_shards/connectors/local_vault.py`:

- `"bm25_score": 0.0` (L375) is a HARDCODED LITERAL on every LOCAL_VAULT row, not a computed relevance. It reads 0.0 on the strongest possible local hit too.
- The WHERE is OR-joined per keyword: `("title" LIKE ? OR "content" LIKE ?)` per term. ONE keyword matching ANYWHERE in a file body returns that entire file.
- `final_score` starts at a hardcoded **0.45 floor** before any signal: `max(0.05, 0.45 + 0.35*title_hit + <=0.20*term_signal - noise_penalty)` (L384-390).

So the real defect is a FLOOR, not a miss-fallback: a single weak body substring hit on a common word lands competitive with strong grid hits. My query contained "account", "failed", "limit" — ordinary words that appear in most source files. Practical reach is close to "any query surfaces any vaulted file", but the code to fix is different.

## What is fixed and what is not

FIXED, pushed by blade1tb as `2f890056` (verified from whoart: redaction.py + connectors/local_vault.py + a 48-line test):
- LOCAL_VAULT titles and bodies pass through `brain_scan/redaction.redact_content()` AT RETURN. At return, not ingest — registered vaults are read in place and never rewritten, so there is no ingest hook.
- `_redact()` FAILS CLOSED: a broken redactor withholds the body and logs, it does not pass the secret through. Has its own test.
- `file_hash` still hashes ORIGINAL content, so dedup identity is unchanged.
- Added `ntn_[A-Za-z0-9]{20,}` and `secret_[A-Za-z0-9]{40,}` to SECRET_PATTERNS.

NOT FIXED — the score floor. blade1tb deliberately left it alone because it changes ranking and several tests depend on those numbers. Correct call; it needs doing deliberately, not bolted onto a security commit. **This leg is where it lives now.**

## The structural finding — this is the actual ask

**Redaction on one path does not close this. Grid content is STORED unredacted and read paths return it verbatim.** `2f890056` closes the LOCAL_VAULT read path. Every other read path still returns whatever is on disk.

And pattern-based redaction is structurally incomplete: **the Notion token matched NO provider pattern**, and the generic labelled-secret rule missed it because it is a bare assignment with no credential-shaped label in front of it. Even a redactor already wired onto that path would have leaked THIS one. A redactor only ever catches secrets someone already thought of.

THIS IS THE FOURTH INSTANCE OF THE SAME CLASS, each previously closed as one-off hygiene:
- 2026-08-15: two full-length fleet key values in plaintext in dream digests (shard #81)
- 2026-08-16: same two, re-flagged, still unrotated (shard #82)
- 2026-08-19: a live Cloudflare API token plus R2 Access Key ID and Secret copied into digests (shard #96)
- 2026-08-29: this one, reachable by any lane holding a connector token

Four incidents, one shape. It is not hygiene, it is that secrets enter the vault unredacted and every read path is an egress.

## Done when

1. The Notion token is rotated. (GM)
2. The LOCAL_VAULT `final_score` 0.45 floor is addressed deliberately, with the ranking tests updated as a considered change.
3. A decision is recorded on the real question: redact at INGEST, or accept that every read path needs its own redactor and enumerate them. Pick one and write it down — the per-path approach is what produced four incidents.
4. Someone answers whether secret-shaped content should be refused at capture rather than stored and filtered on the way out.
