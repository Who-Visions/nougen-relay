"""Lease control plane (war-game wargames/relay-control-plane.md, move B):
monotonic fencing token across reclaim; stale tokens rejected on release,
failure and heartbeat; heartbeat extends liveness; sweeper marks expired
leases CLAIMABLE with evidence; history records every transition with actor;
admission verdicts are deterministic; metrics count it all. Hermetic tmp root."""
import json
from datetime import timedelta

import pytest

import nougen_relay.core as core
from nougen_relay import guard


@pytest.fixture
def root(tmp_path, monkeypatch):
    (tmp_path / ".handoffs").mkdir()
    monkeypatch.delenv("NOUGEN_LEASE_DIR", raising=False)
    monkeypatch.setenv("NOUGEN_LEASE_TTL_MINUTES", "10")
    monkeypatch.delenv("NOUGEN_LEASE_HEARTBEAT_DIVISOR", raising=False)
    return tmp_path


def _lease(root, leg):
    return json.loads((core.leases_dir(root) / f"{leg}.lease.json").read_text(encoding="utf-8"))


def _age(root, leg, minutes):
    """Push the lease's liveness stamps into the past."""
    p = core.leases_dir(root) / f"{leg}.lease.json"
    rec = json.loads(p.read_text(encoding="utf-8"))
    past = (core._now() - timedelta(minutes=minutes)).isoformat()
    rec["leased_utc"] = past
    rec["heartbeat_utc"] = past
    p.write_text(json.dumps(rec), encoding="utf-8")


def test_acquire_issues_lease_id_token_heartbeat_and_history(root):
    rec = core.acquire_lease(root, "L1", machine="blade", agent="daemon", goal="do x")
    assert rec["fencing_token"] == 1 and len(rec["lease_id"]) == 12 and rec["state"] == "LEASED"
    assert rec["heartbeat_utc"] and rec["attempt_count"] == 1
    assert rec["history"][-1]["to"] == "LEASED" and rec["history"][-1]["actor"] == "blade/daemon"


def test_fencing_token_is_monotonic_across_expiry_reclaim_and_force(root):
    core.acquire_lease(root, "L2", machine="blade", agent="daemon")
    _age(root, "L2", 11)
    assert core.acquire_lease(root, "L2", machine="phoebus", agent="daemon") is not None
    assert _lease(root, "L2")["fencing_token"] == 2
    assert _lease(root, "L2")["history"][-1]["evidence"].startswith("reclaim:")
    forced = core.acquire_lease(root, "L2", machine="ccr", agent="daemon", force=True)
    assert forced["fencing_token"] == 3 and forced["history"][-1]["evidence"].startswith("force:")


def test_stale_token_cannot_release_fail_or_heartbeat(root):
    first = core.acquire_lease(root, "L3", machine="blade", agent="daemon")
    _age(root, "L3", 11)
    second = core.acquire_lease(root, "L3", machine="phoebus", agent="daemon")
    assert second["fencing_token"] == 2
    assert core.release_lease(root, "L3", "complete", fencing_token=first["fencing_token"]) is False
    assert _lease(root, "L3")["status"] == "active", "zombie could not close the leg"
    assert core.heartbeat_lease(root, "L3", first["fencing_token"]) is False
    rej = core.record_leg_failure(root, "L3", "boom", fencing_token=first["fencing_token"])
    assert rej.get("rejected") and _lease(root, "L3").get("retry_count", 0) == 0
    assert len(_lease(root, "L3")["rejected"]) == 3
    assert core.release_lease(root, "L3", "complete", fencing_token=2, evidence="verified") is True
    assert _lease(root, "L3")["state"] == "COMPLETE" and _lease(root, "L3")["history"][-1]["evidence"] == "verified"


def test_legacy_callers_without_token_still_work(root):
    core.acquire_lease(root, "L4", machine="blade", agent="daemon")
    assert core.release_lease(root, "L4", "released") is True
    assert _lease(root, "L4")["state"] == "RELEASED"


def test_heartbeat_extends_liveness_and_marks_running(root):
    rec = core.acquire_lease(root, "L5", machine="blade", agent="daemon")
    _age(root, "L5", 9)
    assert core.lease_is_active(_lease(root, "L5"))
    assert core.heartbeat_lease(root, "L5", rec["fencing_token"]) is True
    after = _lease(root, "L5")
    assert after["state"] == "RUNNING" and after["heartbeat_count"] == 1
    assert core._lease_age_minutes(after) < 1, "heartbeat is the liveness stamp"
    assert core.heartbeat_interval_seconds(10) == 200.0


def test_sweeper_marks_expired_claimable_with_evidence_and_reclaim_is_visible(root):
    core.acquire_lease(root, "L6", machine="blade", agent="daemon")
    core.acquire_lease(root, "L7", machine="blade", agent="daemon")
    _age(root, "L6", 30)
    assert core.sweep_expired_leases(root) == ["L6"]
    swept = _lease(root, "L6")
    assert swept["status"] == "expired" and swept["state"] == "CLAIMABLE"
    assert swept["history"][-1]["actor"] == "sweeper" and "expired after" in swept["history"][-1]["evidence"]
    assert core.sweep_expired_leases(root) == [], "idempotent"
    again = core.acquire_lease(root, "L6", machine="phoebus", agent="daemon")
    assert again["fencing_token"] == 2
    m = core.lease_metrics(root)
    assert m["leases"] == 2 and m["active"] == 2 and m["expired_swept"] == 1 and m["reclaimed"] == 1
    assert m["by_state"]["LEASED"] == 2


def test_failure_path_records_attempts_and_dead_letter_in_history(root, monkeypatch):
    monkeypatch.setenv("NOUGEN_RELAY_MAX_RETRIES", "2")
    rec = core.acquire_lease(root, "L8", machine="blade", agent="daemon")
    r1 = core.record_leg_failure(root, "L8", "first", fencing_token=rec["fencing_token"])
    assert r1["status"] == "retry_pending" and r1["attempt_count"] == 1 and r1["state"] == "RETRY_WAIT"
    r2 = core.record_leg_failure(root, "L8", "second", fencing_token=rec["fencing_token"])
    assert r2["status"] == "dead_letter" and r2["state"] == "DEAD_LETTER"
    assert [h["to"] for h in r2["history"]] == ["LEASED", "RETRY_WAIT", "DEAD_LETTER"]
    assert core.lease_metrics(root)["dead_letter"] == 1


def test_admission_is_deterministic(root, monkeypatch):
    leg = {"id": "A1", "status": "open", "goal": "write docs"}
    assert guard.admit(root, leg, machine="blade", agent="daemon") == ("ALLOW", "claimable")
    assert guard.admit(root, {"id": "A2", "status": "complete"})[0] == "DENY"
    assert guard.admit(root, {"id": "A3", "status": "blocked"})[0] == "DEFER"
    assert guard.admit(root, {"status": "open"})[0] == "DENY"
    core.acquire_lease(root, "A1", machine="phoebus", agent="daemon")
    v, why = guard.admit(root, leg, machine="blade", agent="daemon")
    assert v == "DEFER" and "leased by phoebus/daemon token 1" in why
    v, why = guard.admit(root, leg, machine="phoebus", agent="daemon")
    assert v == "ALLOW" and why.startswith("re-entry")
    monkeypatch.setenv("NOUGEN_RELAY_MAX_RETRIES", "1")
    core.record_leg_failure(root, "A1", "poison", fencing_token=1)
    v, why = guard.admit(root, leg, machine="blade", agent="daemon")
    assert v == "DENY" and why.startswith("dead_letter after 1")


def test_admission_defers_during_retry_window_then_allows(root, monkeypatch):
    leg = {"id": "A5", "status": "open", "goal": "flaky"}
    core.acquire_lease(root, "A5", machine="blade", agent="daemon")
    core.record_leg_failure(root, "A5", "transient", fencing_token=1)
    assert guard.admit(root, leg, machine="blade", agent="daemon")[0] == "DEFER"
    later = core._now() + timedelta(days=1)
    assert guard.admit(root, leg, machine="blade", agent="daemon", now_dt=later)[0] == "ALLOW"


def test_history_is_capped(root, monkeypatch):
    monkeypatch.setenv("NOUGEN_LEASE_HISTORY_MAX", "3")
    rec = core.acquire_lease(root, "L9", machine="blade", agent="daemon")
    for _ in range(5):
        core.heartbeat_lease(root, "L9", rec["fencing_token"], state="RUNNING")
        core.heartbeat_lease(root, "L9", rec["fencing_token"], state="LEASED")
    assert len(_lease(root, "L9")["history"]) == 3
