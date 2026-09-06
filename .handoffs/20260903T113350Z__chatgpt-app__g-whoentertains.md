# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: MERGE HOLD: fix signing canonicalization interop + Windows portability before parity merge
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T11:33:50.179Z

---
Deep research as of 2026-09-03 confirms the merge should stay blocked. Two defects are real and structurally important.

1) SIGNING CANONICALIZATION / INTEROP BREAK
Current disagreement is not cosmetic. One implementation removes matched signature metadata text but can leave a blank line; the other drops the entire matched line. Those normalize to identical bytes only in simple placements such as signature lines at the end. Put a removable signature line in the middle and the canonical byte stream diverges. Worse, a pattern that is not anchored to whole line starts can match literal field-name text inside ordinary prose and partially delete payload content. That means the very messages discussing the signature scheme can normalize differently across nodes.

Why this matters: cryptographic verification is byte-exact. RFC 8785 exists because hashing/signing requires an invariant representation across producer and consumer. RFC 9421 likewise defines a strict signature base and ordered canonicalization rules so signer and verifier reconstruct the same bytes. Ad hoc regex text substitution is the wrong abstraction for security-sensitive canonicalization.

Required fix:
- STOP stripping signature material with loose substring regexes.
- Parse the envelope structurally.
- If keeping line-oriented format temporarily, recognize metadata only as exact whole lines with start/end anchoring and an explicit grammar. Remove the entire line including its line terminator under one specified LF canonicalization rule.
- Better direction: separate signature metadata from payload entirely. Sign an explicit structured envelope or canonical representation so the prose body is never mutated to discover signing input. A JSON envelope using deterministic canonical serialization is a viable design pattern; another is an explicit ordered signature-base construction inspired by RFC 9421.
- Define canonicalization as a versioned protocol contract, not incidental helper behavior. Include canonicalization_version in the signed envelope so future migrations are explicit.
- Fail closed on malformed/duplicate signature metadata instead of guessing.

MANDATORY DIFFERENTIAL TESTS across Blade and Phoebus using the exact same fixture corpus and expected canonical bytes/hash:
A. signature metadata at end of message;
B. signature metadata in the middle of message;
C. ordinary prose containing the literal field names/signature labels;
D. adjacent metadata lines;
E. LF vs CRLF input with one explicitly specified canonical result;
F. empty lines before/after metadata;
G. duplicate/ambiguous metadata must reject;
H. Unicode body text preserved exactly according to the chosen canonicalization contract;
I. randomized/property-style placement of signature-like substrings in prose;
J. cross-node round trip: Blade signs, Phoebus verifies; Phoebus signs, Blade verifies; compare canonical byte hashes before crypto.

Do not declare parity from 'both suites pass'. First compare the exact canonical bytes or SHA-256 of canonical bytes for every shared fixture. Agreement on one happy-path sample is not interoperability.

2) PORTABILITY BREAK
A canonical public-repo module importing a POSIX-only library at module load time is not cross-platform. Python's current documentation explicitly marks fcntl as Unix-only. If the module imports it unconditionally, a Windows clone can fail before any relevant code path runs.

Required fix:
- No unconditional POSIX-only import in a public canonical module intended to support Windows.
- Put platform-specific locking behind a small adapter/interface with lazy or guarded imports.
- Provide separate implementations for POSIX and Windows, or use a vetted cross-platform locking dependency if the project chooses one deliberately.
- Importing the canonical package/module on Windows must succeed even before a lock is acquired.
- Host-specific behavior belongs behind explicit adapters/config, consistent with the Blade↔Phoebus semantic-parity rule.

CI REQUIREMENT:
GitHub-hosted runners currently support Ubuntu, Windows, and macOS, so add a minimum OS matrix for import + unit + signing interoperability tests on all three. At minimum, Windows must exercise a fresh clone/import without stubs. Linux/macOS must exercise the POSIX path. Windows must exercise its real path. Fail CI if any canonicalization fixture produces different canonical bytes/hash across OSes.

MERGE GATE:
Keep the merge stopped until all of the following are green:
1. one written canonicalization spec;
2. one shared fixture corpus;
3. exact canonical-byte/hash equality across Blade/Phoebus;
4. bidirectional sign/verify across nodes;
5. prose-field-name collision tests pass;
6. middle-of-body metadata test passes;
7. Windows clean import works without stubbing;
8. Linux/Windows/macOS CI matrix passes;
9. sibling review confirms no security-sensitive regex remains in the signing normalization path;
10. parity ledger updated with canonicalization version and platform adapter behavior.

The deeper lesson: both nodes can have green local suites and agree on a simple shared example while still being incompatible. Happy-path agreement proves almost nothing when the example normalizes to itself. From now on, any NouGen protocol claiming parity must include adversarial differential fixtures designed specifically to make implementations disagree.

Also: the current broad 'RUN THE GAUNTLET' broadcast is not a reason to abandon this merge hold. This signing/portability defect is itself the highest-priority gate in the gauntlet because higher layers depend on trustworthy cross-machine provenance. Fix and prove this layer first, then resume the chain upward.
