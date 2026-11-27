"""Wrong-shape leg files must not disable or crash the dedup check.

json.loads only guards syntax: a leg file holding a list, string, number or
null, or a leg whose goal is not a string, is valid JSON of the wrong shape.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import relay_dedup as rd

GOAL = "Build autonomous completion reconciliation for the relay"


@pytest.fixture
def handoffs(tmp_path, monkeypatch):
    monkeypatch.setenv("NOUGEN_HANDOFFS_DIR", str(tmp_path))
    monkeypatch.setattr(rd, "_embed", lambda _t: None)  # degraded, no network
    (tmp_path / "20260828T000002Z__b__y.json").write_text(json.dumps(
        {"goal": GOAL, "agent": "y", "machine": "m", "status": "open"}),
        encoding="utf-8")
    return tmp_path


BAD_FILES = [
    ("list", [1, 2]),
    ("string", "open"),
    ("number", 7),
    ("null", None),
    ("goal_list", {"goal": ["a", "b"], "agent": "x", "status": "open"}),
    ("goal_number", {"goal": 42, "agent": "x", "status": "open"}),
    ("goal_dict", {"goal": {"t": GOAL}, "agent": "x", "status": "open"}),
]


@pytest.mark.parametrize("payload", [p for _, p in BAD_FILES],
                         ids=[n for n, _ in BAD_FILES])
def test_load_legs_skips_wrong_shape(handoffs, payload):
    (handoffs / "20260828T000001Z__a__x.json").write_text(
        json.dumps(payload), encoding="utf-8")
    legs = rd.load_legs()
    assert [leg["_id"] for leg in legs] == ["20260828T000002Z__b__y"]


@pytest.mark.parametrize("payload", [p for _, p in BAD_FILES],
                         ids=[n for n, _ in BAD_FILES])
def test_check_dedup_still_catches_duplicate(handoffs, payload):
    """One bad leg used to turn the verdict into "skipped" (leg written with no
    dedup) or raise; the real duplicate must still be found."""
    (handoffs / "20260828T000001Z__a__x.json").write_text(
        json.dumps(payload), encoding="utf-8")
    verdict, leg_id, _ = rd.check_dedup(GOAL, directory=handoffs)
    assert verdict == "exact"
    assert leg_id == "20260828T000002Z__b__y"
