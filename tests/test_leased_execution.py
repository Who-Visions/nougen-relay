"""Tests for leased execution, wake signal triggering, idempotency, routing heuristics, and retry backoff."""

import hashlib
import json
from datetime import datetime, timedelta, timezone

import pytest

from nougen_relay import core

FROZEN = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    """Freeze clock for deterministic TTL and backoff calculations."""
    monkeypatch.setattr(core, "_now", lambda: FROZEN)


@pytest.fixture()
def test_repo(tmp_path, monkeypatch):
    """Initialize a test repo for relay operations."""
    root = tmp_path / "repo"
    root.mkdir(parents=True, exist_ok=True)
    (root / ".handoffs").mkdir(parents=True, exist_ok=True)
    (root / ".relay").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(core, "repo_root", lambda: root)
    monkeypatch.setenv("NOUGEN_MACHINE", "testbox")
    monkeypatch.setenv("NOUGEN_AGENT", "testlane")
    return root


# --- 1. Atomic Claim / Lease Expiration Tests -------------------------------

def test_default_lease_ttl_is_15_minutes():
    assert core._lease_ttl_minutes() == 15.0


def test_acquire_lease_and_check_active(test_repo):
    leg_id = "20260828T120000Z__boxa__lane1"
    lease = core.acquire_lease(test_repo, leg_id, machine="boxa", agent="lane1", goal="build worker")
    assert lease is not None
    assert lease["leg_id"] == leg_id
    assert lease["status"] == "active"
    assert lease["ttl_minutes"] == 15.0
    assert core.lease_is_active(lease) is True


def test_concurrent_worker_cannot_acquire_active_lease(test_repo):
    leg_id = "20260828T120000Z__boxa__lane1"
    lease1 = core.acquire_lease(test_repo, leg_id, machine="boxa", agent="lane1")
    assert lease1 is not None

    # Another worker on different machine/agent tries to acquire active lease
    lease2 = core.acquire_lease(test_repo, leg_id, machine="boxb", agent="lane2")
    assert lease2 is None


def test_same_worker_can_reenter_and_renew_lease(test_repo):
    leg_id = "20260828T120000Z__boxa__lane1"
    lease1 = core.acquire_lease(test_repo, leg_id, machine="boxa", agent="lane1", ttl_minutes=15.0)
    assert lease1 is not None

    # Same machine & agent renews
    renewed = core.acquire_lease(test_repo, leg_id, machine="boxa", agent="lane1", ttl_minutes=30.0)
    assert renewed is not None
    assert renewed["ttl_minutes"] == 30.0


def test_expired_lease_is_automatically_reclaimed(test_repo, monkeypatch):
    leg_id = "20260828T120000Z__boxa__lane1"
    # Worker 1 acquired lease at T0 with 15m TTL
    lease1 = core.acquire_lease(test_repo, leg_id, machine="boxa", agent="lane1", ttl_minutes=15.0)
    assert lease1 is not None

    # Advance time by 16 minutes (lease expired)
    future = FROZEN + timedelta(minutes=16)
    monkeypatch.setattr(core, "_now", lambda: future)

    assert core.lease_is_active(lease1) is False

    # Worker 2 on boxb can now atomically reclaim the expired lease from dead worker
    lease2 = core.acquire_lease(test_repo, leg_id, machine="boxb", agent="lane2", ttl_minutes=15.0)
    assert lease2 is not None
    assert lease2["machine"] == "boxb"
    assert lease2["agent"] == "lane2"
    assert core.lease_is_active(lease2) is True


def test_release_lease(test_repo):
    leg_id = "20260828T120000Z__boxa__lane1"
    core.acquire_lease(test_repo, leg_id, machine="boxa", agent="lane1")
    assert core.release_lease(test_repo, leg_id) is True

    # After release, lease is no longer active
    leases = core.active_leases(test_repo, active_only=True)
    assert len(leases) == 0


# --- 2. Idempotency Check (SHA-256 Fingerprint) Tests -----------------------

def test_compute_idempotency_key():
    key1 = core.compute_idempotency_key("leg123", "fix auth bug")
    expected = hashlib.sha256(b"leg123:fix auth bug").hexdigest()
    assert key1 == expected

    # Same inputs produce identical key
    key2 = core.compute_idempotency_key("leg123", "fix auth bug")
    assert key1 == key2

    # Different goal produces different key
    key3 = core.compute_idempotency_key("leg123", "fix database bug")
    assert key1 != key3


def test_record_and_check_duplicate_execution(test_repo):
    leg_id = "20260828T120000Z__boxa__lane1"
    goal = "compile binary"
    assert core.is_duplicate_execution(test_repo, leg_id, goal) is False

    # Record completion
    core.record_idempotency(test_repo, leg_id, goal, metadata={"exit_code": 0})

    # Now duplicate execution is detected
    assert core.is_duplicate_execution(test_repo, leg_id, goal) is True


# --- 3. Autonomous Wake Signal Triggering Tests -----------------------------

def test_emit_and_pending_wake_signals(test_repo):
    leg_id = "20260828T120000Z__boxa__lane1"
    rec = {"machine": "boxa", "agent": "lane1", "goal": "sync fleet state"}
    sig_path = core.emit_wake_signal(test_repo, leg_id, rec)
    assert sig_path.is_file()

    signals = core.pending_wake_signals(test_repo)
    assert len(signals) == 1
    assert signals[0]["leg_id"] == leg_id
    assert signals[0]["goal"] == "sync fleet state"


def test_consume_wake_signal(test_repo):
    leg_id = "20260828T120000Z__boxa__lane1"
    core.emit_wake_signal(test_repo, leg_id, {"goal": "test task"})
    assert len(core.pending_wake_signals(test_repo)) == 1

    assert core.consume_wake_signal(test_repo, leg_id) is True
    assert len(core.pending_wake_signals(test_repo)) == 0


def test_acquire_lease_automatically_consumes_wake_signal(test_repo):
    leg_id = "20260828T120000Z__boxa__lane1"
    core.emit_wake_signal(test_repo, leg_id, {"goal": "run tests"})
    assert len(core.pending_wake_signals(test_repo)) == 1

    core.acquire_lease(test_repo, leg_id, machine="boxa", agent="lane1")
    # Wake signal is consumed once lease is claimed
    assert len(core.pending_wake_signals(test_repo)) == 0


# --- 4. Capability / Tag Routing Heuristics Tests ---------------------------

def test_explicit_target_agent_routing():
    leg_claude = {"goal": "refactor router", "target_agent": "claude-cli"}
    assert core.is_lane_eligible("claude-cli", leg_claude) is True
    assert core.is_lane_eligible("codex", leg_claude) is False

    leg_codex = {"goal": "write tests", "target_lane": "codex"}
    assert core.is_lane_eligible("codex", leg_codex) is True
    assert core.is_lane_eligible("sol-ai", leg_codex) is False


def test_explicit_tags_routing():
    leg_diag = {"goal": "run health diagnostics", "tags": ["diagnostic", "status"]}
    assert core.is_lane_eligible("sol-ai", leg_diag) is True
    assert core.is_lane_eligible("dav1d", leg_diag) is True

    leg_coding = {"goal": "implement algorithm", "tags": ["coding"]}
    assert core.is_lane_eligible("codex", leg_coding) is True
    assert core.is_lane_eligible("claude-cli", leg_coding) is True


def test_goal_keyword_heuristic_routing():
    # Coding keywords
    leg_bug = {"goal": "fix null pointer exception in auth handler"}
    assert core.is_lane_eligible("codex", leg_bug) is True
    assert core.is_lane_eligible("claude-cli", leg_bug) is True

    # Triage / status keywords
    leg_status = {"goal": "check fleet sync status and report triage"}
    assert core.is_lane_eligible("sol-ai", leg_status) is True
    assert core.is_lane_eligible("dav1d", leg_status) is True


def test_filter_eligible_legs():
    legs = [
        {"id": "1", "goal": "fix broken test", "target_agent": "codex"},
        {"id": "2", "goal": "fleet heartbeat status check", "tags": ["status"]},
        {"id": "3", "goal": "general documentation review"},
    ]
    codex_legs = core.filter_eligible_legs(legs, "codex")
    assert any(leg["id"] == "1" for leg in codex_legs)

    solai_legs = core.filter_eligible_legs(legs, "sol-ai")
    assert any(leg["id"] == "2" for leg in solai_legs)
    assert not any(leg["id"] == "1" for leg in solai_legs)


# --- 5. Retry Backoff & Dead-Letter Logic Tests -----------------------------

def test_exponential_backoff_calculation():
    # Base = 5.0s, Factor = 2.0
    assert core.calculate_backoff_seconds(1) == 5.0
    assert core.calculate_backoff_seconds(2) == 10.0
    assert core.calculate_backoff_seconds(3) == 20.0
    assert core.calculate_backoff_seconds(4) == 40.0


def test_transient_failure_and_retry_backoff(test_repo, monkeypatch):
    leg_id = "20260828T120000Z__boxa__lane1"
    core.acquire_lease(test_repo, leg_id)

    # First transient failure (attempt 1)
    res1 = core.record_leg_failure(test_repo, leg_id, "connection timeout", max_retries=3)
    assert res1["status"] == "retry_pending"
    assert res1["retry_count"] == 1
    assert "next_retry_utc" in res1

    # Right now at T0, not retryable yet due to backoff
    assert core.is_leg_retryable(res1, now_dt=FROZEN) is False

    # After backoff time (5s), it becomes retryable
    after_backoff = FROZEN + timedelta(seconds=6)
    assert core.is_leg_retryable(res1, now_dt=after_backoff) is True


def test_dead_letter_status_after_max_retries(test_repo):
    leg_id = "20260828T120000Z__boxa__lane1"
    core.acquire_lease(test_repo, leg_id)

    # Attempt 1
    res1 = core.record_leg_failure(test_repo, leg_id, "error 1", max_retries=3)
    assert res1["status"] == "retry_pending"

    # Attempt 2
    res2 = core.record_leg_failure(test_repo, leg_id, "error 2", max_retries=3)
    assert res2["status"] == "retry_pending"

    # Attempt 3 (Max retries reached -> dead_letter)
    res3 = core.record_leg_failure(test_repo, leg_id, "error 3", max_retries=3)
    assert res3["status"] == "dead_letter"
    assert res3["retry_count"] == 3
    assert core.is_leg_retryable(res3) is False


# --- 6. CLI Command Integration Tests ---------------------------------------

def test_cli_lease_commands(test_repo):
    import argparse
    # Test acquire
    ns_acq = argparse.Namespace(action="acquire", id="leg100", goal="test lease", ttl=20.0, force=False)
    assert core.cmd_lease(ns_acq) == core.EXIT_OK

    # Test list
    ns_list = argparse.Namespace(action="list", all=False)
    assert core.cmd_lease(ns_list) == core.EXIT_OK

    # Test release
    ns_rel = argparse.Namespace(action="release", id="leg100")
    assert core.cmd_lease(ns_rel) == core.EXIT_OK


def test_cli_wake_commands(test_repo):
    import argparse
    # Test emit
    ns_emit = argparse.Namespace(action="emit", id="leg200", goal="test wake")
    assert core.cmd_wake(ns_emit) == core.EXIT_OK

    # Test list
    ns_list = argparse.Namespace(action="list")
    assert core.cmd_wake(ns_list) == core.EXIT_OK

    # Test consume
    ns_con = argparse.Namespace(action="consume", id="leg200")
    assert core.cmd_wake(ns_con) == core.EXIT_OK


def test_cli_route_command(test_repo):
    import argparse
    # Create test record file
    rec = {
        "id": "leg300",
        "machine": "testbox",
        "agent": "testlane",
        "goal": "fix auth bug",
        "status": "open",
    }
    (test_repo / ".handoffs" / "leg300.json").write_text(json.dumps(rec), encoding="utf-8")

    ns_route = argparse.Namespace(id="leg300")
    assert core.cmd_route(ns_route) == core.EXIT_OK


def test_cli_fail_command(test_repo):
    import argparse
    core.acquire_lease(test_repo, "leg400")
    ns_fail = argparse.Namespace(id="leg400", message="timeout error", max_retries=3)
    assert core.cmd_fail(ns_fail) == core.EXIT_OK

