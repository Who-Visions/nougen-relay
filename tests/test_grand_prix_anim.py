"""Tests for the pure helpers in tools/relay_grand_prix_anim.py."""
import sqlite3
import sys
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")
pytest.importorskip("numpy")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import relay_grand_prix_anim as gp  # noqa: E402


def _make_db(path):
    conn = sqlite3.connect(str(path))
    conn.execute(
        "CREATE TABLE daemon_pulses (pulse_number INT, timestamp_utc TEXT, "
        "ollama_status TEXT, ollama_latency_ms REAL, open_handoffs_count INT, "
        "lag_alerts_count INT, status TEXT)"
    )
    conn.execute(
        "CREATE TABLE triage_events (id INTEGER PRIMARY KEY, handoff_id TEXT, "
        "task_type TEXT, action TEXT, status TEXT)"
    )
    for i in range(1, 51):
        conn.execute(
            "INSERT INTO daemon_pulses VALUES (?,?,?,?,?,?,?)",
            (i, f"2026-01-01T00:00:{i % 60:02d}+00:00", "healthy", 10.0, 5, 0, "ok"),
        )
    for t in ["A", "A", "B", None]:
        conn.execute(
            "INSERT INTO triage_events (handoff_id, task_type, action, status) "
            "VALUES ('h', ?, 'x', 's')",
            (t,),
        )
    conn.commit()
    conn.close()


def test_missing_db_returns_demo_data(tmp_path):
    data = gp.fetch_telemetry_data(tmp_path / "nope.db")
    assert len(data["pulses"]) == 14
    assert data["recent_batons"] == []
    assert data["triage_counts"]["EXECUTION_RUN"] == 12


def test_reads_latest_40_pulses_in_order(tmp_path):
    db = tmp_path / "s.db"
    _make_db(db)
    data = gp.fetch_telemetry_data(db)
    nums = [p["pulse_number"] for p in data["pulses"]]
    assert len(nums) == 40
    assert nums == sorted(nums) and nums[-1] == 50


def test_triage_counts_and_null_type(tmp_path):
    db = tmp_path / "s.db"
    _make_db(db)
    data = gp.fetch_telemetry_data(db)
    assert data["triage_counts"] == {"A": 2, "B": 1, "UNKNOWN": 1}
    assert len(data["recent_batons"]) == 4


def test_unreadable_db_degrades_to_empty(tmp_path, capsys):
    db = tmp_path / "bad.db"
    db.write_bytes(b"not a sqlite database at all" * 10)
    data = gp.fetch_telemetry_data(db)
    assert data == {"pulses": [], "triage_counts": {}, "recent_batons": []}
    assert "SQLite read warning" in capsys.readouterr().out


def test_resolve_default_db_prefers_env(tmp_path, monkeypatch):
    f = tmp_path / "x.db"
    f.write_text("")
    monkeypatch.setenv("NOUGEN_DAEMON_DB", str(f))
    assert gp._resolve_default_db() == f


def test_resolve_default_db_falls_back_to_home(tmp_path, monkeypatch):
    monkeypatch.setenv("NOUGEN_DAEMON_DB", str(tmp_path / "missing.db"))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    assert gp._resolve_default_db() == tmp_path / "Watchtower" / "Sol-Ai" / "relay_daemon_state.db"


def test_wrap_html_embeds_snippet():
    out = gp._wrap_responsive_html("<div id='SNIP'></div>")
    assert out.startswith("<!DOCTYPE html>")
    assert "<div id='SNIP'></div>" in out
