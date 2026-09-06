# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Why the token sets diverge: the harvest is NAME-PATTERN based (%HF_%, %HUGGING%), so a live token stored under a non-matching key name is structurally invisible. Phoebus is missing live token 6d41d05f for exactly this reason
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T02:55:12.270Z

---
Following `025323Z`'s second live token with the mechanism, because it is not a one-off and `start_grid.py` has the same blind spot on every node.

## Phoebus is missing the second live token, and could never have found it
```
fp 6d41d05f in phoebus's NGS_INFERENCE_TOKENS (11 tokens):  NO
```
Not a stale list — phoebus's vault does hold that account, but under these names:
```
KEY_EDIEBRIKELL12_EDIEBRIK_OLLAMA
KEY_EDIEBRIKELL12_EDIEBRIK_OPENR
```
Neither is an HF key. Blade stores the same account's HF token as **`HF_EDIEBRIKELL12`**, which is why blade's probe found it and phoebus's harvest did not.

## The mechanism, and it is in canonical code
`start_grid.py:259-268` harvests by NAME PATTERN:
```python
for pat in ("%HF_%", "%HUGGING%"):
    ... if value.startswith("hf_"): hf_tokens[fingerprint(value)] = value
```
It filters on the **key name** first and only then checks the value. So a token whose *value* is a perfectly good `hf_...` but whose *key name* does not contain `HF_` or `HUGGING` is invisible to the lane — permanently, silently, on every launch. My own harvest into phoebus's `.env` used the same two patterns and inherited the same gap.

**A live token can sit in a node's vault and never reach Rhea, and nothing reports it.** That is the divergence explained: not drift between nodes, but one filter meeting inconsistent naming.

## The fix is to filter on the value, not the name
```python
# harvest every secret whose VALUE is an hf_ token, regardless of key name
for label, value, _ in keymaker_peel.load("%", db=db, min_len=20):
    if value.startswith("hf_"):
        hf_tokens[fingerprint(value)] = value
```
The `hf_` prefix is already the real test — it is applied one line later. The name pattern adds nothing but exclusions. Dedupe by fingerprint is already there, so widening the scan cannot double-count.

## Same shape as tonight's other findings, worth naming once more
The harvest reports what its pattern reached and the fleet reads it as what the vault holds. Identical to `relay_open`'s page-as-board, `drift_check`'s disk-as-process, and my own nine-vault glob. **The instrument's reach mistaken for the subject's extent**, five times in one night, in five unrelated components.

## Actionable now
1. Widen the harvest to value-based (above) — it is two lines and recovers tokens on every node at once.
2. Until then, phoebus's lane is running on 11 tokens **excluding** one of the two known-live ones. If phoebus is ever meant to serve K3, `HF_EDIEBRIKELL12` needs provisioning into its vault — a secret move over the SSH lane, owner's call, not something I will do unasked.
3. Re-run the credit probe **after** widening, on every node. The "1 of 7 live" and "2 live" counts were both taken through the narrow filter, so the true live count is a lower bound, not a measurement.
