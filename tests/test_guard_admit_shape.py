"""relay admit must survive lease/leg files holding valid but non-object JSON.

The parse sites only caught syntax errors, so a lease or leg file containing
a list, string or number raised AttributeError on .get() and crashed the
admission check. Non-object records are now treated like unreadable ones."""
import argparse
import json

import pytest

import nougen_relay.core as core
from nougen_relay import guard

BAD = ['[1, 2]', '"leased"', '7', 'true']


@pytest.fixture
def root(tmp_path, monkeypatch):
    (tmp_path / ".handoffs").mkdir()
    monkeypatch.delenv("NOUGEN_LEASE_DIR", raising=False)
    monkeypatch.setattr(guard.gh, "repo_root", lambda *a, **k: tmp_path)
    return tmp_path


@pytest.mark.parametrize("raw", BAD, ids=lambda r: r)
def test_admit_ignores_non_object_lease_file(root, raw):
    d = core.leases_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    (d / "S1.lease.json").write_text(raw, encoding="utf-8")
    assert guard.admit(root, {"id": "S1", "status": "open"}) == ("ALLOW", "claimable")


@pytest.mark.parametrize("raw", BAD, ids=lambda r: r)
def test_cmd_admit_falls_back_on_non_object_leg_file(root, raw, capsys):
    (root / ".handoffs" / "S2.json").write_text(raw, encoding="utf-8")
    args = argparse.Namespace(leg_id="S2", lane=None, status="complete")
    assert guard.cmd_admit(args) == 1
    out = json.loads(capsys.readouterr().out)
    assert out["verdict"] == "DENY" and out["reason"] == "leg status complete"
