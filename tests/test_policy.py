"""Every leg gets exactly one deterministic disposition; nothing in the
policy names a lane, a person, or a project."""
from datetime import datetime, timedelta, timezone

from nougen_relay import policy

OLD = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat().replace("+00:00", "Z")


def _reg(ids=None, lanes=None):
    return policy.Registry(lanes=set(lanes or []), ids=dict(ids or {}))


def _rec(goal, **kw):
    return {"goal": goal, "status": "open", "created_utc": OLD, **kw}


def test_route_to_a_known_lane_from_arrow_form():
    reg = _reg(lanes={"blade1tb", "antigravity", "claude-app"})
    d = policy.decide(_rec("[-> @blade] restart the node"), "## Ask\nrestart\n", reg)
    assert d.action == "route" and d.target == "blade1tb"


def test_route_to_agent_name_in_prose_arrow():
    reg = _reg(lanes={"xoah", "claude-app"})
    d = policy.decide(_rec("[-> Xoah lane] archive populated"), "", reg)
    assert d.action == "route" and d.target == "xoah"


def test_addressed_to_unknown_lane_holds():
    reg = _reg(lanes={"blade1tb"})
    d = policy.decide(_rec("[-> @nobody] do a thing"), "", reg)
    assert d.action == "hold" and "no lane" in d.reason


def test_already_routed_is_a_noop():
    reg = _reg(lanes={"blade1tb"})
    d = policy.decide(_rec("[-> @blade] x", target_agent="blade1tb", routed_utc="2026"), "", reg)
    assert d.action == "none"


def test_resolve_closes_the_referenced_open_leg():
    reg = _reg(ids={"20260914T112826Z__claude-app__g": "open", "20260914T000000Z__x__y": "acked"})
    d = policy.decide(_rec("DONE leg 112826Z: six tools live on the worker"), "", reg, self_id="me")
    assert d.action == "resolve" and d.resolves == ("20260914T112826Z__claude-app__g",)


def test_short_reference_must_be_unique():
    reg = _reg(ids={"20260914T112826Z__a__b": "open", "20260913T112826Z__c__d": "open"})
    d = policy.decide(_rec("DONE leg 112826Z: shipped"), "", reg)
    assert d.action == "ack" and not d.resolves


def test_reference_to_already_complete_leg_is_plain_ack():
    reg = _reg(ids={"20260914T112826Z__a__b": "complete"})
    d = policy.decide(_rec("DONE leg 112826Z: shipped"), "", reg)
    assert d.action == "ack"


def test_status_only_report_acks():
    d = policy.decide(_rec("phoebus /msg FIXED end-to-end"), "## Situation\nfine\n", _reg())
    assert d.action == "ack"


def test_ask_holds():
    d = policy.decide(_rec("EchoVault next steps"), "## Ask\n1. write the eval\n", _reg())
    assert d.action == "hold"


def test_non_open_is_none():
    d = policy.decide(dict(_rec("x"), status="acked"), "", _reg())
    assert d.action == "none"


def test_decision_is_deterministic():
    reg = _reg(lanes={"blade1tb"}, ids={"20260914T112826Z__a__b": "open"})
    rec, body = _rec("[-> @blade] DONE leg 112826Z"), "## Ask\nrestart\n"
    assert policy.decide(rec, body, reg) == policy.decide(dict(rec), body, reg)


def test_stamp_at_birth_sets_disposition_and_target(tmp_path):
    d = tmp_path / ".handoffs"
    d.mkdir()
    (d / "20260914T000000Z__blade1tb__antigravity.json").write_text('{"status":"acked"}')
    rec = {"goal": "[-> @blade] restart node", "status": "open"}
    policy.stamp_at_birth(rec, "## Ask\nrestart\n", tmp_path)
    assert rec["disposition"]["action"] == "route"
    assert rec["target_agent"] == "blade1tb" and rec["target"] == "blade1tb"


def test_stamp_at_birth_marks_reports_as_ack(tmp_path):
    (tmp_path / ".handoffs").mkdir()
    rec = {"goal": "[auto] repo@main: session ended with 2 uncommitted file(s)", "status": "open"}
    policy.stamp_at_birth(rec, "", tmp_path)
    assert rec["disposition"]["action"] == "ack" and "target_agent" not in rec
