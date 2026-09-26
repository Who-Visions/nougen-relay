"""The relay watcher is optional infrastructure, so it has to fail quietly and alone.

Two properties matter more than its triage output: exactly one daemon may run
against a state DB (they share a SQLite ledger, and two writers double every lag
alert), and every path it uses has to be discovered rather than baked in, because
the same file runs from Sol-Ai/tools on blade and from tools/ in this repo.
"""

import datetime
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

relay_daemon = pytest.importorskip("relay_daemon")

RelayDaemon = relay_daemon.RelayDaemon
SingletonLock = relay_daemon.SingletonLock
TriageResult = relay_daemon.TriageResult


@pytest.fixture
def relay_env(tmp_path, monkeypatch):
    """A throwaway relay dir + state DB, wired through the env vars the daemon reads."""
    relay_dir = tmp_path / "NouGenRelay"
    handoffs = relay_dir / ".handoffs"
    handoffs.mkdir(parents=True)
    db_path = tmp_path / "state" / "daemon.db"

    stale = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=900)
    (handoffs / "20260823T000000Z__test__agent.json").write_text(
        json.dumps(
            {
                "id": "20260823T000000Z__test__agent",
                "machine": "test",
                "agent": "agent",
                "goal": "verify the watcher sees an open leg",
                "status": "open",
                "created_utc": stale.isoformat(),
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("NOUGEN_RELAY_DIR", str(relay_dir))
    monkeypatch.setenv("NOUGEN_DAEMON_DB", str(db_path))
    return relay_dir, db_path


def _daemon(relay_dir, db_path):
    return RelayDaemon(relay_dir=relay_dir, db_path=db_path, machine_name="test")


def test_open_legs_are_read_straight_off_disk(relay_env):
    """No import of the shards package: the watcher must run in a bare clone."""
    relay_dir, db_path = relay_env
    legs = _daemon(relay_dir, db_path).get_open_handoffs()
    assert [leg["id"] for leg in legs] == ["20260823T000000Z__test__agent"]


def test_auto_shard_refuses_a_later_explicit_correction(relay_env):
    relay_dir, db_path = relay_env
    handoffs = relay_dir / ".handoffs"
    source_id = "20260904T142512Z__claude-app__agent"
    (handoffs / f"{source_id}.json").write_text(json.dumps({
        "id": source_id,
        "created_utc": "2026-09-04T14:25:12Z",
        "goal": "initial finding",
    }), encoding="utf-8")
    correction_id = "20260904T142715Z__claude-app__agent"
    (handoffs / f"{correction_id}.json").write_text(json.dumps({
        "id": correction_id,
        "created_utc": "2026-09-04T14:27:15Z",
        "goal": f"CORRECTING my earlier finding in {source_id}",
    }), encoding="utf-8")

    daemon = _daemon(relay_dir, db_path)
    assert daemon._superseding_relay_ids(source_id, "2026-09-04T14:25:12Z") == [correction_id]
    assert daemon.auto_capture_shard(
        "must not write", "old claim", handoff_id=source_id,
        created_utc="2026-09-04T14:25:12Z",
    ) is False


def test_auto_shard_does_not_treat_an_unrelated_correction_as_supersession(relay_env):
    relay_dir, db_path = relay_env
    handoffs = relay_dir / ".handoffs"
    source_id = "20260904T142512Z__claude-app__agent"
    (handoffs / "later.json").write_text(json.dumps({
        "id": "later",
        "created_utc": "2026-09-04T14:27:15Z",
        "goal": "CORRECTION: unrelated service finding",
    }), encoding="utf-8")

    assert _daemon(relay_dir, db_path)._superseding_relay_ids(
        source_id, "2026-09-04T14:25:12Z"
    ) == []


def test_lag_is_measured_against_the_threshold(relay_env):
    relay_dir, db_path = relay_env
    daemon = _daemon(relay_dir, db_path)
    leg = daemon.get_open_handoffs()[0]

    lag_seconds, is_lagging = daemon.calculate_lag(leg)

    assert lag_seconds > 800
    assert is_lagging is True


def test_second_daemon_is_refused_while_the_first_lives(tmp_path):
    lock_path = tmp_path / "state.lock"
    first = SingletonLock(lock_path)
    second = SingletonLock(lock_path)

    assert first.acquire() is True
    assert second.acquire() is False
    assert second.holder_pid == os.getpid()


def test_a_lock_left_by_a_dead_process_is_reclaimed(tmp_path):
    """A hard kill skips atexit, so the lock outlives its holder. It must not wedge."""
    lock_path = tmp_path / "state.lock"
    dead_pid = _a_pid_that_is_not_running()
    lock_path.write_text(json.dumps({"pid": dead_pid}), encoding="utf-8")

    assert SingletonLock(lock_path).acquire() is True
    assert json.loads(lock_path.read_text(encoding="utf-8"))["pid"] == os.getpid()


def test_a_corrupt_lock_file_is_reclaimed_not_fatal(tmp_path):
    lock_path = tmp_path / "state.lock"
    lock_path.write_text("{ not json", encoding="utf-8")

    assert SingletonLock(lock_path).acquire() is True


def test_release_leaves_another_holders_lock_alone(tmp_path):
    lock_path = tmp_path / "state.lock"
    lock = SingletonLock(lock_path)
    assert lock.acquire() is True

    lock_path.write_text(json.dumps({"pid": os.getpid() + 1}), encoding="utf-8")
    lock.release()

    assert lock_path.exists()


def test_racing_starts_produce_exactly_one_winner(tmp_path):
    """The bug this replaced: check-then-write let two processes both claim the lock.

    The children have to keep holding after they answer -- a winner that exits
    immediately leaves a lock whose PID is genuinely dead, and reclaiming that is
    correct behaviour, not a second winner.
    """
    lock_path = tmp_path / "state.lock"
    script = (
        "import sys, time;"
        f"sys.path.insert(0, {str(TOOLS)!r});"
        "import relay_daemon;"
        f"won = relay_daemon.SingletonLock({str(lock_path)!r}).acquire();"
        "print('WON' if won else 'REFUSED', flush=True);"
        "time.sleep(10) if won else None"
    )
    procs = [
        subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for _ in range(6)
    ]
    try:
        # Read until the verdict, not just the first line. relay_daemon can emit
        # import-time diagnostics (e.g. "WARN using fallback watchtower root"
        # wherever ~/Watchtower is absent -- which includes a clean CI runner),
        # and a bare readline() consumes that warning instead of WON/REFUSED,
        # scoring every racer as neither. The lock was always correct; the
        # harness was reading the wrong line.
        def _verdict(proc):
            for _ in range(20):
                line = proc.stdout.readline().strip()
                if line in ("WON", "REFUSED"):
                    return line
                if not line:
                    break
            return "NO-VERDICT"

        verdicts = [_verdict(p) for p in procs]
    finally:
        for p in procs:
            p.kill()
            p.wait()

    assert verdicts.count("WON") == 1, verdicts


def test_dispatch_reports_a_missing_agy_binary_instead_of_raising(relay_env, monkeypatch):
    relay_dir, db_path = relay_env
    monkeypatch.setattr(relay_daemon.shutil, "which", lambda _name: None)
    monkeypatch.setattr(relay_daemon, "run_dav1d_agy", None)
    triage = _triage("agy version")

    result = _daemon(relay_dir, db_path).dispatch_execution(triage)

    assert result["status"] == "error"
    assert result["exit_code"] == 127


def test_dry_run_never_shells_out(relay_env, monkeypatch):
    relay_dir, db_path = relay_env

    def _explode(*_args, **_kwargs):  # pragma: no cover - only runs on regression
        raise AssertionError("dry-run dispatched a subprocess")

    monkeypatch.setattr(relay_daemon.subprocess, "run", _explode)
    triage = _triage("agy mcp list")

    assert _daemon(relay_dir, db_path).dispatch_execution(triage, dry_run=True)["status"] == "dry_run"


def test_paths_come_from_the_environment_not_a_constant(relay_env):
    """Rule 0.2: a machine path baked into the file breaks the moment it moves."""
    relay_dir, db_path = relay_env
    source = (TOOLS / "relay_daemon.py").read_text(encoding="utf-8")

    assert "C:\\Users" not in source
    assert relay_daemon._resolve_relay_dir() == relay_dir
    assert str(db_path) == os.environ["NOUGEN_DAEMON_DB"]


def test_registry_merge_preserves_local_ack_and_remote_events():
    """A stale gateway projection must not erase a local acknowledgement."""
    local = {
        "id": "leg-1",
        "status": "acked",
        "goal": "ship the fix",
        "relay": [
            {"event": "create", "at": "2026-08-28T17:00:00Z", "agent": "claude"},
            {"event": "ack", "at": "2026-08-28T17:01:00Z", "agent": "codex", "note": "taken"},
        ],
    }
    remote = {
        "id": "leg-1",
        "status": "open",
        "goal": "ship the fix",
        "relay": [
            {"event": "create", "at": "2026-08-28T17:00:00Z", "agent": "claude"},
            {"event": "triage", "at": "2026-08-28T17:00:30Z", "agent": "relay-watch"},
        ],
    }

    merged = relay_daemon._merge_relay_records(local, remote)

    assert merged["status"] == "acked"
    assert {(event["event"], event["agent"]) for event in merged["relay"]} == {
        ("create", "claude"),
        ("triage", "relay-watch"),
        ("ack", "codex"),
    }


def test_registry_merge_never_regresses_terminal_state():
    local = {
        "id": "leg-2",
        "status": "complete",
        "relay": [{"event": "complete", "at": "2026-08-28T17:02:00Z", "agent": "codex"}],
    }
    remote = {
        "id": "leg-2",
        "status": "open",
        "relay": [{"event": "create", "at": "2026-08-28T17:00:00Z", "agent": "claude"}],
    }

    merged = relay_daemon._merge_relay_records(local, remote)

    assert merged["status"] == "complete"
    assert len(merged["relay"]) == 2


def test_registry_merge_never_reactivates_a_released_claim():
    local = {"status": "active", "scope": "relay:leg-3"}
    remote = {
        "status": "released",
        "scope": "relay:leg-3",
        "released_utc": "2026-08-28T21:00:00+00:00",
    }

    merged = relay_daemon._merge_relay_records(local, remote)

    assert merged["status"] == "released"
    assert merged["released_utc"] == remote["released_utc"]


def test_sync_merges_registry_projection_without_checkout_overwrite(tmp_path, monkeypatch):
    """The daemon must preserve local events while importing remote legs."""
    relay_dir = tmp_path / "NouGenRelay"
    handoffs = relay_dir / ".handoffs"
    handoffs.mkdir(parents=True)
    (relay_dir / ".git").mkdir()
    db_path = tmp_path / "state" / "daemon.db"
    leg_id = "20260828T000000Z__remote__agent"
    local = {
        "id": leg_id,
        "status": "acked",
        "goal": "preserve the baton",
        "relay": [{"event": "ack", "at": "2026-08-28T00:01:00Z", "agent": "codex"}],
    }
    remote = {
        "id": leg_id,
        "status": "open",
        "goal": "preserve the baton",
        "relay": [{"event": "create", "at": "2026-08-28T00:00:00Z", "agent": "claude"}],
    }
    (handoffs / f"{leg_id}.json").write_text(json.dumps(local, indent=2) + "\n", encoding="utf-8")
    (handoffs / f"{leg_id}.md").write_text("local brief\n", encoding="utf-8")

    commands = []

    def fake_run(argv, **kwargs):
        commands.append(argv)
        if "fetch" in argv:
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "ls-tree" in argv:
            return subprocess.CompletedProcess(
                argv, 0,
                f".handoffs/{leg_id}.json\n.handoffs/{leg_id}.md\n",
                "",
            )
        if argv[-1] == f"origin/main:.handoffs/{leg_id}.json":
            return subprocess.CompletedProcess(argv, 0, json.dumps(remote) + "\n", "")
        if argv[-1] == f"origin/main:.handoffs/{leg_id}.md":
            return subprocess.CompletedProcess(argv, 0, "remote brief\n", "")
        raise AssertionError(f"unexpected git command: {argv}")

    monkeypatch.setattr(relay_daemon.subprocess, "run", fake_run)
    daemon = _daemon(relay_dir, db_path)
    monkeypatch.setattr(daemon, "_registry_branch", lambda: "main")
    daemon.sync_relay_repo()

    merged = json.loads((handoffs / f"{leg_id}.json").read_text(encoding="utf-8"))
    assert merged["status"] == "acked"
    assert {event["event"] for event in merged["relay"]} == {"create", "ack"}
    assert (handoffs / f"{leg_id}.md").read_text(encoding="utf-8") == "local brief\n"
    assert not any("checkout" in argv for argv in commands)


def test_ollama_bind_all_address_is_dialled_on_loopback(monkeypatch):
    """OLLAMA_HOST is a bind address; 0.0.0.0 is not a destination."""
    monkeypatch.setenv("OLLAMA_HOST", "0.0.0.0:11436")

    assert relay_daemon._resolve_ollama_url() == "http://127.0.0.1:11436"


def test_ready_handoffs_retries_a_seen_leg_after_backoff(relay_env):
    relay_dir, db_path = relay_env
    daemon = _daemon(relay_dir, db_path)
    leg = daemon.get_open_handoffs()[0]
    daemon.record_triage(leg, _triage("first attempt"), {"status": "error"})
    lease_dir = relay_daemon.leases_dir(relay_dir)
    lease_dir.mkdir(parents=True)
    (lease_dir / f"{leg['id']}.lease.json").write_text(
        json.dumps(
            {
                "leg_id": leg["id"],
                "status": "retry_pending",
                "retry_count": 1,
                "max_retries": 3,
                "next_retry_utc": "2000-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    assert daemon._ready_handoffs([leg]) == [leg]


def test_ready_handoffs_respects_an_active_lease(relay_env):
    relay_dir, db_path = relay_env
    daemon = _daemon(relay_dir, db_path)
    leg = daemon.get_open_handoffs()[0]
    daemon.record_triage(leg, _triage("already running"), {"status": "error"})
    lease_dir = relay_daemon.leases_dir(relay_dir)
    lease_dir.mkdir(parents=True)
    (lease_dir / f"{leg['id']}.lease.json").write_text(
        json.dumps(
            {
                "leg_id": leg["id"],
                "status": "active",
                "leased_utc": datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat(),
                "ttl_minutes": 30,
            }
        ),
        encoding="utf-8",
    )

    assert daemon._ready_handoffs([leg]) == []


def test_upstream_claim_is_fleet_visible_and_per_leg(relay_env, monkeypatch):
    relay_dir, db_path = relay_env
    daemon = _daemon(relay_dir, db_path)
    leg = daemon.get_open_handoffs()[0]
    written = {}
    def read(path):
        if path.startswith(".handoffs/claims/"):
            return {}, {}
        return {"sha": "leg"}, {"status": "open"}  # live leg still open

    monkeypatch.setattr(daemon, "_registry_read_json", read)

    def capture(path, record, message, sha=None):
        written.update(path=path, record=record, message=message, sha=sha)
        return True

    monkeypatch.setattr(daemon, "_registry_write_json", capture)

    assert daemon.claim_leg_upstream(
        leg, {"ttl_minutes": 30, "idempotency_key": "key-1"}
    ) is True
    assert written["path"].endswith(
        f"{leg['id']}__autonomous.json"
    )
    assert written["record"]["status"] == "active"
    assert written["record"]["scope"] == f"relay:{leg['id']}"
    assert written["record"]["ttl_hours"] == pytest.approx(0.5)


def test_foreign_upstream_claim_fences_dispatch(relay_env, monkeypatch):
    relay_dir, db_path = relay_env
    daemon = _daemon(relay_dir, db_path)
    leg = daemon.get_open_handoffs()[0]
    foreign = {
        "machine": "other-box",
        "agent": "worker",
        "status": "active",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "ttl_hours": 1,
    }
    monkeypatch.setattr(
        daemon, "_registry_read_json", lambda _path: ({"sha": "old"}, foreign)
    )
    monkeypatch.setattr(
        daemon,
        "_registry_write_json",
        lambda *_args, **_kwargs: pytest.fail("foreign active claim was overwritten"),
    )

    assert daemon.claim_leg_upstream(leg, {"ttl_minutes": 30}) is False


def test_verified_ack_is_reconciled_without_redispatch(relay_env, monkeypatch):
    relay_dir, db_path = relay_env
    daemon = _daemon(relay_dir, db_path)
    leg = daemon.get_open_handoffs()[0]
    result = {
        "status": "success",
        "verified": True,
        "verify_evidence": "tests passed",
        "acked_upstream": False,
    }
    daemon.record_triage(leg, _triage("ship it"), result)
    released = []
    monkeypatch.setattr(daemon, "ack_leg_upstream", lambda *_args: True)
    monkeypatch.setattr(
        daemon,
        "release_upstream_claim",
        lambda leg_id, outcome, evidence="": released.append(
            (leg_id, outcome, evidence)
        ) or True,
    )
    monkeypatch.setattr(relay_daemon, "release_lease", lambda *_args, **_kwargs: True)

    assert daemon.reconcile_verified_acks() == 1
    assert released == [(leg["id"], "complete", "tests passed")]
    with sqlite3.connect(db_path) as conn:
        stored = json.loads(
            conn.execute(
                "SELECT execution_result FROM triage_events WHERE handoff_id=?",
                (leg["id"],),
            ).fetchone()[0]
        )
    assert stored["acked_upstream"] is True
    assert "reconciled_utc" in stored


def test_cycle_claims_before_dispatch_and_releases_after_ack(relay_env, monkeypatch):
    relay_dir, db_path = relay_env
    daemon = _daemon(relay_dir, db_path)
    leg = daemon.get_open_handoffs()[0]
    order = []
    monkeypatch.setattr(daemon, "sync_relay_repo", lambda: None)
    monkeypatch.setattr(daemon, "reconcile_verified_acks", lambda: 0)
    monkeypatch.setattr(
        daemon, "check_ollama_health", lambda: (True, 1.0, ["local-model"])
    )
    monkeypatch.setattr(
        relay_daemon,
        "acquire_lease",
        lambda *_args, **_kwargs: order.append("local-lease")
        or {"ttl_minutes": 30, "idempotency_key": "key-1"},
    )
    monkeypatch.setattr(
        relay_daemon,
        "release_lease",
        lambda *_args, **_kwargs: order.append("local-release") or True,
    )
    monkeypatch.setattr(
        daemon,
        "claim_leg_upstream",
        lambda *_args: order.append("upstream-claim") or True,
    )
    monkeypatch.setattr(
        daemon,
        "triage_with_ollama",
        lambda _handoff: TriageResult(
            handoff_id=leg["id"],
            task_type="EXECUTION_RUN",
            action="run the task",
            requires_harness_wake=True,
            confidence=1.0,
            reasoning="test",
            lag_seconds=0.0,
            is_lagging=False,
        ),
    )
    monkeypatch.setattr(
        daemon,
        "dispatch_execution",
        lambda *_args, **_kwargs: order.append("dispatch")
        or {"status": "success", "exit_code": 0, "stdout": "tests pass"},
    )
    monkeypatch.setattr(
        daemon,
        "dav1d_probe_verify",
        lambda *_args: order.append("verify")
        or {"verified": True, "evidence": "tests pass"},
    )
    monkeypatch.setattr(
        daemon,
        "ack_leg_upstream",
        lambda *_args: order.append("ack") or True,
    )
    monkeypatch.setattr(
        daemon,
        "release_upstream_claim",
        lambda *_args: order.append("upstream-release") or True,
    )
    monkeypatch.setattr(daemon, "auto_capture_shard", lambda **_kwargs: True)

    result = daemon.run_cycle()

    assert result["triaged_count"] == 1
    assert order.index("local-lease") < order.index("upstream-claim")
    assert order.index("upstream-claim") < order.index("dispatch")
    assert order.index("dispatch") < order.index("ack")
    assert order.index("ack") < order.index("upstream-release")


def test_unverified_cycle_records_retry_and_releases_fleet_claim(relay_env, monkeypatch):
    relay_dir, db_path = relay_env
    daemon = _daemon(relay_dir, db_path)
    leg = daemon.get_open_handoffs()[0]
    outcomes = []
    monkeypatch.setattr(daemon, "sync_relay_repo", lambda: None)
    monkeypatch.setattr(daemon, "reconcile_verified_acks", lambda: 0)
    monkeypatch.setattr(daemon, "check_ollama_health", lambda: (False, -1.0, []))
    monkeypatch.setattr(
        relay_daemon,
        "acquire_lease",
        lambda *_args, **_kwargs: {"ttl_minutes": 30},
    )
    monkeypatch.setattr(relay_daemon, "release_lease", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(daemon, "claim_leg_upstream", lambda *_args: True)
    monkeypatch.setattr(
        daemon,
        "triage_with_ollama",
        lambda _handoff: TriageResult(
            handoff_id=leg["id"],
            task_type="EXECUTION_RUN",
            action="run the task",
            requires_harness_wake=True,
            confidence=1.0,
            reasoning="test",
            lag_seconds=0.0,
            is_lagging=False,
        ),
    )
    monkeypatch.setattr(
        daemon,
        "dispatch_execution",
        lambda *_args, **_kwargs: {"status": "error", "exit_code": 1},
    )
    monkeypatch.setattr(
        daemon,
        "dav1d_probe_verify",
        lambda *_args: {"verified": False, "evidence": "exit 1"},
    )
    monkeypatch.setattr(
        relay_daemon,
        "record_leg_failure",
        lambda *_args: {"status": "retry_pending", "retry_count": 1},
    )
    monkeypatch.setattr(
        daemon,
        "release_upstream_claim",
        lambda _leg_id, outcome, evidence="": outcomes.append((outcome, evidence))
        or True,
    )

    result = daemon.run_cycle()

    execution = result["triages"][0]["execution"]
    assert execution["retry_status"] == "retry_pending"
    assert execution["retry_count"] == 1
    assert outcomes == [("retry_pending", "exit 1")]


def _triage(action: str) -> "TriageResult":
    return TriageResult(
        handoff_id="20260823T000000Z__test__agent",
        task_type="STATUS_CHECK",
        action=action,
        requires_harness_wake=False,
        confidence=0.9,
        reasoning="test",
        lag_seconds=900.0,
        is_lagging=True,
    )


def _a_pid_that_is_not_running() -> int:
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait()
    return proc.pid
