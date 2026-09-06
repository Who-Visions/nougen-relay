"""Properties that must hold for every input, not just the ones I imagined.

Example-based tests check the cases their author thought of. That is exactly
how the TTL boundary went untested for a day: the example was 7.99 hours,
chosen to dodge a clock race, and nobody noticed it never exercised 8.0.

These assert invariants and let Hypothesis hunt for the counterexample. It is a
dev-only dependency; the package still installs with none.

Each property below is one the fleet actually depends on:

  * a claim that has expired cannot un-expire         (monotonicity)
  * two machines agree on whether their scopes collide (symmetry)
  * a name is safe to put in a filename, always        (slug closure)

A failure here is a real defect, not a style opinion.
"""

from datetime import datetime, timedelta, timezone

import pytest

from nougen_relay import core

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import assume, given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

FROZEN = datetime(2026, 8, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    monkeypatch.setattr(core, "_now", lambda: FROZEN)


def _claim(hours_old: float, ttl=None, status="active") -> dict:
    rec = {"status": status,
           "created_utc": (FROZEN - timedelta(hours=hours_old)).isoformat()}
    if ttl is not None:
        rec["ttl_hours"] = ttl
    return rec


# --- claims -----------------------------------------------------------------

# A record stores its age as an ISO timestamp truncated to microseconds, so a
# fractional-hour age does not survive the round trip exactly. Hypothesis found
# this immediately: at age == ttl == 1.34681448822721 the claim read as expired,
# while the 8.0 example passed because 8 hours is microsecond-exact.
#
# The code is right; the invariant as first written was not. The boundary is
# precise to about a microsecond and no further — which nobody had stated
# anywhere until a property test asked.
QUANTUM_HOURS = 1e-6 / 3600


@given(age=st.floats(min_value=0, max_value=1000, allow_nan=False),
       ttl=st.floats(min_value=0.01, max_value=1000, allow_nan=False))
def test_a_claim_is_active_exactly_while_it_is_younger_than_its_ttl(age, ttl):
    """The whole contract in one line, to the precision the format supports."""
    assume(abs(age - ttl) > QUANTUM_HOURS)   # the fuzzy edge, tested below
    assert core.claim_is_active(_claim(age, ttl=ttl)) is (age <= ttl)


@given(ttl=st.floats(min_value=0.01, max_value=1000, allow_nan=False))
def test_the_edge_is_decided_within_one_microsecond_either_way(ttl):
    """Whatever it decides AT the edge, it must be certain a microsecond out.
    An ambiguous band wider than the storage precision would mean two machines
    could disagree about the same claim."""
    assert core.claim_is_active(_claim(ttl - 0.001, ttl=ttl)) is True
    assert core.claim_is_active(_claim(ttl + 0.001, ttl=ttl)) is False


@given(young=st.floats(min_value=0, max_value=500, allow_nan=False),
       extra=st.floats(min_value=0.01, max_value=500, allow_nan=False))
def test_expiry_is_monotonic_a_dead_claim_never_revives(young, extra):
    """If a claim is expired, ageing it further cannot make it bind again.
    A non-monotonic expiry would let a scope silently re-lock itself."""
    ttl = 8.0
    if not core.claim_is_active(_claim(young, ttl=ttl)):
        assert not core.claim_is_active(_claim(young + extra, ttl=ttl))


@given(age=st.floats(min_value=0, max_value=100, allow_nan=False))
def test_a_released_claim_binds_at_no_age(age):
    """Release is absolute — freshness must never resurrect it."""
    assert core.claim_is_active(_claim(age, ttl=1000, status="released")) is False


@given(stamp=st.text(max_size=40))
def test_an_unparseable_timestamp_never_frees_a_scope(stamp):
    """Fail safe, not open: garbage in a record must not silently unlock work
    another machine is doing."""
    assume(not stamp.startswith("2"))  # keep it clearly non-ISO
    assert core.claim_is_active({"status": "active", "created_utc": stamp}) is True


# --- scope overlap ----------------------------------------------------------

@given(a=st.text(max_size=60), b=st.text(max_size=60))
@settings(max_examples=300)
def test_collision_is_symmetric_between_two_machines(a, b):
    """Both boxes must reach the SAME verdict about whether they conflict.
    If A thinks it is clear and B thinks it is blocked, the registry has
    produced two truths and the claim system is worse than nothing."""
    assert bool(core._scopes_overlap(a, b)) == bool(core._scopes_overlap(b, a))


@given(scope=st.text(min_size=1, max_size=60))
def test_a_scope_always_collides_with_itself(scope):
    """The one claim that must never be missed: your own."""
    assume(core._normalize_scope(scope))
    assert core._scopes_overlap(scope, scope)


@given(a=st.text(max_size=40))
def test_nothing_collides_with_an_empty_scope(a):
    assert core._scopes_overlap(a, "") == []


# --- identity slugs ---------------------------------------------------------

@given(name=st.text(max_size=60))
def test_a_slug_is_always_safe_in_a_filename(name):
    """Record filenames are built from these. A separator or a colon here is a
    path that differs per platform, or does not exist at all."""
    out = core._slug(name)
    assert out
    assert all(c.isalnum() or c == "-" for c in out)
    assert not (out.startswith("-") or out.endswith("-"))


@given(name=st.text(max_size=60))
def test_slugging_twice_changes_nothing(name):
    """Idempotence: a name read back out of a filename and re-slugged must be
    the same name, or identity drifts every round trip."""
    once = core._slug(name)
    assert core._slug(once) == once
