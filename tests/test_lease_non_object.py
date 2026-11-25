"""A lease/leg file holding valid JSON that is not an object (e.g. a list from a
truncated or hand-edited file) must be treated like a corrupt file, not crash."""
import pytest

import nougen_relay.core as core
from nougen_relay import guard


@pytest.fixture
def root(tmp_path, monkeypatch):
    (tmp_path / ".handoffs").mkdir()
    monkeypatch.delenv("NOUGEN_LEASE_DIR", raising=False)
    monkeypatch.setenv("NOUGEN_LEASE_TTL_MINUTES", "10")
    return tmp_path


def _poison(root, leg, text):
    ldir = core.leases_dir(root)
    ldir.mkdir(parents=True, exist_ok=True)
    (ldir / f"{leg}.lease.json").write_text(text, encoding="utf-8")


@pytest.mark.parametrize("text", ["[1, 2]", '"oops"', "42"])
def test_read_lease_non_object_is_none(root, text):
    _poison(root, "L1", text)
    _, rec = core._read_lease(root, "L1")
    assert rec is None


@pytest.mark.parametrize("text", ["[1, 2]", '"oops"', "42"])
def test_acquire_reclaims_non_object_lease(root, text):
    _poison(root, "L2", text)
    rec = core.acquire_lease(root, "L2", machine="node-b", agent="daemon", goal="x")
    assert rec is not None and rec["fencing_token"] == 1


@pytest.mark.parametrize("text", ["[1, 2]", '"oops"', "42"])
def test_admit_ignores_non_object_lease(root, text):
    _poison(root, "L3", text)
    assert guard.admit(root, {"id": "L3", "status": "open"}) == ("ALLOW", "claimable")


@pytest.mark.parametrize("text", ["[1, 2]", '"oops"', "42"])
def test_release_failure_tolerate_non_object_lease(root, text):
    _poison(root, "L4", text)
    core.release_lease(root, "L4")