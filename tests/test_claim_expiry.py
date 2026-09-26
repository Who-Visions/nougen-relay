"""Claims expire on purpose.

A claim that never ages out becomes a tombstone: a machine that dies mid-task
blocks that scope forever, and the next agent either waits on nothing or learns
to ignore claims — which returns us to the duplicate work claims exist to stop.
"""

from datetime import datetime, timedelta, timezone

import pytest

from nougen_relay import core

# A fixed instant. Every age below is measured from here, so "7.99 hours old"
# means exactly that at assert time rather than "7.99 hours old, minus however
# long the test took to reach the assertion".
FROZEN = datetime(2026, 8, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    """Stop the TTL tests from racing the wall clock.

    `claim()` reads the clock to build a record and `claim_is_active()` reads it
    again to judge one. With a real clock those are different instants, so the
    boundary case was written as 7.99 hours against an 8 hour TTL — 36 seconds
    of slack, chosen to survive the gap rather than to test anything.

    That has two costs. It can flip on a loaded runner, and it means the actual
    boundary is never tested: 7.99 proves nothing about 8.0. Freezing the clock
    removes the race and lets the assertions below be exact.

    monkeypatch, not freezegun — a dependency is not worth it for one function.
    """
    monkeypatch.setattr(core, "_now", lambda: FROZEN)


def claim(hours_old, status="active", ttl=None):
    stamp = (core._now() - timedelta(hours=hours_old)).isoformat()
    rec = {"status": status, "created_utc": stamp}
    if ttl is not None:
        rec["ttl_hours"] = ttl
    return rec


def test_fresh_claim_binds():
    assert core.claim_is_active(claim(0.5)) is True


def test_claim_past_its_ttl_stops_binding():
    assert core.claim_is_active(claim(9)) is False


def test_the_boundary_itself_is_inclusive():
    """Exactly at the TTL still binds. Previously untestable: with a live clock
    an 8.0 would already have drifted past 8 by the time it was judged."""
    assert core.claim_is_active(claim(8.0)) is True


def test_one_second_past_the_boundary_stops_binding():
    """The other side of the same edge, to the second."""
    assert core.claim_is_active(claim(8.0 + 1 / 3600)) is False


def test_released_claim_never_binds_however_fresh():
    assert core.claim_is_active(claim(0.1, status="released")) is False


def test_per_claim_ttl_overrides_the_default():
    """Long-running work can hold a scope longer, explicitly."""
    assert core.claim_is_active(claim(9, ttl=24)) is True
    assert core.claim_is_active(claim(2, ttl=1)) is False


def test_unparseable_timestamp_keeps_binding(capsys):
    """Fail safe, not open: a corrupt stamp must not silently free a scope
    another machine is actively working in."""
    assert core.claim_is_active({"status": "active", "created_utc": "not-a-date"}) is True
    assert core.claim_is_active({"status": "active"}) is True


def test_default_ttl_is_configurable(monkeypatch):
    monkeypatch.setenv("NOUGEN_CLAIM_TTL_HOURS", "2")
    assert core.claim_is_active(claim(3)) is False
    assert core.claim_is_active(claim(1)) is True


def test_garbage_ttl_config_falls_back_to_the_default(monkeypatch):
    monkeypatch.setenv("NOUGEN_CLAIM_TTL_HOURS", "soon")
    assert core.claim_is_active(claim(1)) is True
    assert core.claim_is_active(claim(9)) is False
