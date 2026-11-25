"""Handoff/claim record files holding valid non-object JSON (list, string,
number, null) parse fine under json.loads, so a bare try/except around the
parse does not protect the following `.get()` / item assignment. One such file
used to crash `_read_claims_from`, `_record_path` (every id lookup) and
`_touch_record`. These readers must skip it, like they skip unparseable files.
"""
import json

import pytest

from nougen_relay import core

BAD_PAYLOADS = ["[1, 2]", '"text"', "42", "null"]


@pytest.fixture
def root(tmp_path, monkeypatch):
    monkeypatch.delenv("NOUGEN_GIT_HANDOFF_DIR", raising=False)
    return tmp_path


def _handoff(root, name, payload):
    d = core.handoff_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{name}.json"
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")
    return p


def test_load_record_obj(tmp_path):
    good = tmp_path / "g.json"
    good.write_text('{"a": 1}', encoding="utf-8")
    assert core._load_record_obj(good) == {"a": 1}
    for i, payload in enumerate(BAD_PAYLOADS + ["{not json"]):
        p = tmp_path / f"b{i}.json"
        p.write_text(payload, encoding="utf-8")
        assert core._load_record_obj(p) is None
    assert core._load_record_obj(tmp_path / "missing.json") is None


@pytest.mark.parametrize("payload", BAD_PAYLOADS)
def test_read_claims_skips_non_object(root, payload):
    claims = core.claims_dir(root)
    claims.mkdir(parents=True)
    (claims / "bad.json").write_text(payload, encoding="utf-8")
    (claims / "ok.json").write_text(
        json.dumps({"machine": "m", "scope": "x", "status": "active"}), encoding="utf-8"
    )
    out = core._read_claims_from(root, None)
    assert [r["_file"] for r in out] == ["ok.json"]


@pytest.mark.parametrize("payload", BAD_PAYLOADS)
def test_record_path_skips_non_object(root, payload):
    _handoff(root, "aaa-bad", payload)
    good = _handoff(root, "zzz-file", {"id": "wanted-id", "status": "open"})
    assert core._record_path(root, "wanted-id") == good


@pytest.mark.parametrize("payload", BAD_PAYLOADS)
def test_touch_record_non_object_returns_none(root, payload):
    _handoff(root, "leg-bad", payload)
    called = []
    assert core._touch_record(root, "leg-bad", lambda r: called.append(r)) is None
    assert called == []


def test_touch_record_still_mutates_object(root):
    p = _handoff(root, "leg-ok", {"id": "leg-ok", "status": "open"})
    rec = core._touch_record(root, "leg-ok", lambda r: r.update(status="done"))
    assert rec["status"] == "done"
    assert json.loads(p.read_text(encoding="utf-8"))["status"] == "done"
