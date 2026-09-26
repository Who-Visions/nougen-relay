"""Tests for the leg dedup check.

None of these require the embed lane to be up: the degraded path is exercised
deliberately, because that is the mode that runs when the fleet is down and it
is the mode most likely to rot unnoticed.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import relay_dedup as rd


@pytest.fixture
def degraded(monkeypatch):
    """Force the no-embed-lane path."""
    monkeypatch.setattr(rd, "_embed", lambda _t: None)
    return rd.Similarity()


def test_reports_degraded_mode_rather_than_hiding_it(degraded):
    """A dedup check that silently stops working is worse than none -- callers
    must be able to see which mode produced a score."""
    assert degraded.degraded is True


def test_degraded_still_scores_near_identical_goals_above_threshold(degraded):
    a = "Add full temporal provenance to shards so Griot can reconstruct chronology"
    b = "Add temporal provenance evidence model to shards for Griot chronology"
    assert degraded.score(a, b) >= rd.DEFAULT_THRESHOLD


def test_unrelated_goals_stay_below_threshold(degraded):
    a = "Fix the keymaker cross-tenant vault write escape"
    b = "Render an animated terminal race card from daemon heartbeats"
    assert degraded.score(a, b) < rd.DEFAULT_THRESHOLD


def test_stopwords_do_not_manufacture_similarity(degraded):
    """Two unrelated goals share 'the/of/to'. If stopwords counted, short goals
    would collide constantly and the check would cry wolf."""
    assert degraded.score("the state of the node", "the end of the war") < 0.5


def _leg(tmp, stem, goal, agent, machine="m", status="open"):
    (tmp / f"{stem}.json").write_text(json.dumps(
        {"goal": goal, "agent": agent, "machine": machine, "status": status}),
        encoding="utf-8")


def test_same_agent_restating_itself_is_not_flagged(tmp_path, monkeypatch, degraded):
    """A lane repeating itself is noise, not duplicated WORK. Only cross-agent
    overlap means two lanes are about to do the same job twice."""
    monkeypatch.setenv("NOUGEN_HANDOFFS_DIR", str(tmp_path))
    g = "Build autonomous completion reconciliation for the relay"
    _leg(tmp_path, "20260828T000001Z__a__codex", g, "codex")
    _leg(tmp_path, "20260828T000002Z__a__codex", g, "codex")
    legs = rd.load_legs()
    assert len(legs) == 2
    assert rd.find_pairs(legs, rd.DEFAULT_THRESHOLD, degraded) == []


def test_cross_agent_duplicate_is_flagged(tmp_path, monkeypatch, degraded):
    monkeypatch.setenv("NOUGEN_HANDOFFS_DIR", str(tmp_path))
    g = "Build autonomous completion reconciliation for the relay"
    _leg(tmp_path, "20260828T000001Z__a__codex", g, "codex", machine="ccr")
    _leg(tmp_path, "20260828T000002Z__b__agy", g, "antigravity", machine="blade")
    pairs = rd.find_pairs(rd.load_legs(), rd.DEFAULT_THRESHOLD, degraded)
    assert len(pairs) == 1 and pairs[0][0] >= rd.DEFAULT_THRESHOLD


def test_acked_legs_are_excluded_by_default(tmp_path, monkeypatch):
    """An acked leg has an owner. Flagging it would push a lane to re-ack work
    already being carried."""
    monkeypatch.setenv("NOUGEN_HANDOFFS_DIR", str(tmp_path))
    _leg(tmp_path, "20260828T000001Z__a__x", "goal one", "x", status="open")
    _leg(tmp_path, "20260828T000002Z__b__y", "goal two", "y", status="acked")
    assert len(rd.load_legs(only_open=True)) == 1
    assert len(rd.load_legs(only_open=False)) == 2


def test_since_filters_by_leg_id_prefix(tmp_path, monkeypatch):
    monkeypatch.setenv("NOUGEN_HANDOFFS_DIR", str(tmp_path))
    _leg(tmp_path, "20260801T000001Z__a__x", "old", "x")
    _leg(tmp_path, "20260828T000001Z__a__x", "new", "x")
    assert [leg["goal"] for leg in rd.load_legs(since="20260828")] == ["new"]


def test_corrupt_leg_is_skipped_not_fatal(tmp_path, monkeypatch):
    """One unreadable leg must not blind the check to every other leg."""
    monkeypatch.setenv("NOUGEN_HANDOFFS_DIR", str(tmp_path))
    (tmp_path / "20260828T000001Z__a__x.json").write_text("{not json", encoding="utf-8")
    _leg(tmp_path, "20260828T000002Z__b__y", "a real goal", "y")
    assert len(rd.load_legs()) == 1


def test_threshold_is_env_overridable(monkeypatch):
    monkeypatch.setenv("NOUGEN_DEDUP_THRESHOLD", "0.42")
    assert rd.resolve_threshold() == 0.42
