"""The dedup check must not fail open when the embed lane is down.

Measured 2026-09-04: two CLOSED legs describing the same NouGenTracker
rollout were filed 41 seconds apart and both delivered fleet-wide, waking
every session on every node. The check that exists to prevent exactly this
returned "skipped" because the embed lane was unreachable, and cmd_create
writes the leg on "skipped".

`Similarity` already implemented the token-overlap fallback the module
docstring promises. `check_dedup` returned before ever calling it. That is the
gap under test: not "is the fallback correct" but "is the fallback reached".
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import relay_dedup as rd  # noqa: E402

DUP_A = "CLOSED: NouGenTracker passive live status, security gate, and fleet rollout"
DUP_B = "CLOSED: NouGenTracker passive live status and fleet rollout"
DISTINCT = "Restore Phoebus shard path and direct capture/recall"


@pytest.fixture()
def legs(tmp_path):
    import json
    for i, goal in enumerate((DUP_A, DISTINCT)):
        (tmp_path / f"2026090{i}T000000Z__phoebus__claude-cli.json").write_text(
            json.dumps({"goal": goal, "status": "open"}))
    return tmp_path


@pytest.fixture()
def embed_lane_down(monkeypatch):
    """Force the exact production condition: the embed lane does not answer."""
    monkeypatch.setattr(rd, "_embed", lambda *a, **k: None)


def test_duplicate_is_still_caught_with_the_embed_lane_down(legs, embed_lane_down):
    report = {}
    status, payload, score = rd.check_dedup(
        DUP_B, directory=legs, exact_threshold=0.96, near_threshold=0.86,
        report=report)
    assert status == "exact", f"failed open: {status} {payload} {score}"
    assert score >= 0.96
    assert report["degraded"] is True
    assert report["mode"] == "token-overlap"


def test_a_distinct_leg_is_not_refused_in_degraded_mode(legs, embed_lane_down):
    """The cost of over-refusing is worse than a duplicate: a legitimate leg
    that never lands is coordination the fleet silently loses."""
    status, _, score = rd.check_dedup(
        "Wire the arXiv lane marker into the fast greeting probe",
        directory=legs, exact_threshold=0.96, near_threshold=0.86)
    assert status == "ok", f"false positive at {score}"


def test_the_mode_is_reported_when_the_lane_is_healthy(legs, monkeypatch):
    monkeypatch.setattr(rd, "_embed", lambda t, *a, **k: [1.0, 0.0, 0.0])
    report = {}
    rd.check_dedup(DUP_B, directory=legs, report=report)
    assert report["degraded"] is False
    assert report["mode"] == "embeddings"
    assert report["legs_compared"] == 2


def test_skipped_now_means_the_check_could_not_run_at_all(legs, monkeypatch):
    def boom():
        raise RuntimeError("no similarity backend at all")
    monkeypatch.setattr(rd, "Similarity", boom)
    status, payload, _ = rd.check_dedup(DUP_B, directory=legs)
    assert status == "skipped"
