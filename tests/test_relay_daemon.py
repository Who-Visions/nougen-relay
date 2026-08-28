"""The relay watcher is optional infrastructure, so it has to fail quietly and alone.

Two properties matter more than its triage output: exactly one daemon may run
against a state DB (they share a SQLite ledger, and two writers double every lag
alert), and every path it uses has to be discovered rather than baked in, because
the same file runs from Sol-Ai/tools on blade and from tools/ in this repo.
"""

import datetime
import json
import os
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
            env={
                **os.environ,
                "NOUGEN_WATCHTOWER_ROOT": str(tmp_path),
                "NOUGEN_RELAY_DIR": str(tmp_path / "relay"),
            },
        )
        for _ in range(6)
    ]
    try:
        verdicts = [p.stdout.readline().strip() for p in procs]
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


def test_ollama_bind_all_address_is_dialled_on_loopback(monkeypatch):
    """OLLAMA_HOST is a bind address; 0.0.0.0 is not a destination."""
    monkeypatch.setenv("OLLAMA_HOST", "0.0.0.0:11436")

    assert relay_daemon._resolve_ollama_url() == "http://127.0.0.1:11436"


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
