"""Some claim writers stamped `scope` as a JSON list instead of a string
(e.g. `.handoffs/claims/blade1tb__agy.json` on the live registry). Any reader
that hashes `(machine, scope)` as a dict key — `foreign_claims` chief among
them — crashed with `TypeError: unhashable type: 'list'` the moment one such
record was active in the same directory, taking `claim list --all` down for
the whole fleet.

`_read_claims_from` is the single funnel both `foreign_claims` and the local
`claim` commands read through, so normalizing there is enough to fix every
caller at once.
"""
import json

from nougen_relay import core


def _write_claim(root, name, scope, *, machine="blade1tb", status="released"):
    claims = root / ".handoffs" / "claims"
    claims.mkdir(parents=True, exist_ok=True)
    (claims / f"{name}.json").write_text(
        json.dumps({
            "machine": machine,
            "agent": "claude-cli",
            "scope": scope,
            "status": status,
            "created_utc": "2026-08-28T06:37:47Z",
            "ttl_hours": 8.0,
        }),
        encoding="utf-8",
    )


def test_list_scope_is_normalized_to_a_string(tmp_path):
    _write_claim(tmp_path, "legacy", ["src/nougen_shards/keymaker.py"])
    recs = core._read_claims_from(tmp_path, None)
    assert recs[0]["scope"] == "src/nougen_shards/keymaker.py"


def test_list_scope_does_not_crash_dict_keying(tmp_path):
    """Regression for the `foreign_claims` TypeError: build the same
    (machine, scope) key it builds, over records that mix list and string
    scopes, exactly like the live registry does."""
    _write_claim(tmp_path, "legacy-a", ["src/nougen_shards/keymaker.py"])
    _write_claim(tmp_path, "legacy-b", [".handoffs/**"])
    _write_claim(tmp_path, "normal", "docs/RELAY.md")

    recs = core._read_claims_from(tmp_path, None)
    keyed = {(r.get("machine"), r.get("scope")): r for r in recs}
    assert len(keyed) == 3
