"""Tests for tools/local_relay_worker.py (Ollama is always stubbed)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import local_relay_worker as w


@pytest.fixture(autouse=True)
def no_ollama(monkeypatch):
    monkeypatch.setattr(w, "inspect_with_local_e2b", lambda _t: "all good")
    monkeypatch.setattr(w.time, "sleep", lambda _s: None)


def _leg(tmp_path, name, **meta):
    p = tmp_path / f"{name}.json"
    p.write_text(json.dumps(meta), encoding="utf-8")
    return p


def test_open_leg_is_completed_with_ack(tmp_path):
    p = _leg(tmp_path, "20260829-a", id="a", goal="g", status="open")
    assert w.process_single_leg(str(p)) is True
    meta = json.loads(p.read_text(encoding="utf-8"))
    assert meta["status"] == "complete"
    assert meta["relay"][-1]["event"] == "ack"
    assert "all good" in meta["relay"][-1]["note"]


def test_non_open_leg_is_untouched(tmp_path):
    p = _leg(tmp_path, "20260829-b", id="b", status="complete")
    before = p.read_text(encoding="utf-8")
    assert w.process_single_leg(str(p)) is False
    assert p.read_text(encoding="utf-8") == before


def test_long_finding_is_truncated(tmp_path, monkeypatch):
    monkeypatch.setattr(w, "inspect_with_local_e2b", lambda _t: "x" * 500)
    p = _leg(tmp_path, "20260829-c", id="c", status="open")
    w.process_single_leg(str(p))
    note = json.loads(p.read_text(encoding="utf-8"))["relay"][-1]["note"]
    assert note.endswith("...")
    assert len(note) <= len("[Local-Worker] ") + 160


def test_ollama_failure_falls_back(tmp_path, monkeypatch):
    def boom(_t):
        raise OSError("down")
    monkeypatch.setattr(w, "inspect_with_local_e2b", boom)
    p = _leg(tmp_path, "20260829-d", id="d", status="open")
    assert w.process_single_leg(str(p)) is True


def test_advance_batch_survives_corrupt_leg(tmp_path, monkeypatch):
    """A corrupt JSON file must be skipped, not crash the batch."""
    monkeypatch.setattr(w.os.path, "dirname", lambda _p: str(tmp_path / "tools"))
    handoffs = tmp_path / ".handoffs"
    handoffs.mkdir()
    (handoffs / "20260829-bad.json").write_text("{not json", encoding="utf-8")
    good = handoffs / "20260829-good.json"
    good.write_text(json.dumps({"id": "g", "status": "open"}), encoding="utf-8")
    w.advance_batch("20260829")
    assert json.loads(good.read_text(encoding="utf-8"))["status"] == "complete"
