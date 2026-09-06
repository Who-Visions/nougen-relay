"""Retry history must survive lease reclaims (2026-08-31 thrash incident).

acquire_lease used to build every reclaimed lease with retry_count 0, so
record_leg_failure never accumulated attempts, dead_letter was unreachable,
and one leg was claimed 45 times (148 retry_pending vs 17 complete since
08-30, each claim commit firing CI on an exhausted Actions budget).
"""

import json

import pytest

from nougen_relay import core


@pytest.fixture
def relay_root(tmp_path, monkeypatch):
    monkeypatch.setenv("NOUGEN_RELAY_MAX_RETRIES", "3")
    monkeypatch.setenv("NOUGEN_MACHINE", "testbox")
    return tmp_path


def _fail_then_elapse(root, leg_id, monkeypatch):
    """Record a failure, then rewind next_retry_utc so backoff has elapsed."""
    core.record_leg_failure(root, leg_id, "boom")
    lease_file = core.leases_dir(root) / f"{leg_id}.lease.json"
    rec = json.loads(lease_file.read_text(encoding="utf-8"))
    if rec.get("next_retry_utc"):
        rec["next_retry_utc"] = "2000-01-01T00:00:00+00:00"
        lease_file.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    return rec


def test_retry_count_survives_reclaim(relay_root, monkeypatch):
    leg = "leg-carry-1"
    assert core.acquire_lease(relay_root, leg, agent="t", goal="g") is not None
    _fail_then_elapse(relay_root, leg, monkeypatch)

    second = core.acquire_lease(relay_root, leg, agent="t", goal="g")
    assert second is not None
    assert second["retry_count"] == 1, "reclaim must carry retry history, not reset it"


def test_leg_dead_letters_after_max_retries_across_reclaims(relay_root, monkeypatch):
    leg = "leg-carry-2"
    statuses = []
    for _ in range(3):
        lease = core.acquire_lease(relay_root, leg, agent="t", goal="g")
        assert lease is not None
        rec = _fail_then_elapse(relay_root, leg, monkeypatch)
        statuses.append(rec["status"])
    assert statuses[-1] == "dead_letter", f"3rd failure must dead-letter, got {statuses}"

    # An exhausted leg is not claimable again without force.
    assert core.acquire_lease(relay_root, leg, agent="t", goal="g") is None


def test_backoff_window_blocks_early_reclaim(relay_root):
    leg = "leg-carry-3"
    assert core.acquire_lease(relay_root, leg, agent="t", goal="g") is not None
    core.record_leg_failure(relay_root, leg, "boom")  # next_retry in the future
    assert core.acquire_lease(relay_root, leg, agent="t", goal="g") is None, (
        "retry_pending inside its backoff window must not be reclaimable")


def test_fresh_leg_still_starts_at_zero(relay_root):
    lease = core.acquire_lease(relay_root, "leg-fresh", agent="t", goal="g")
    assert lease is not None
    assert lease["retry_count"] == 0
