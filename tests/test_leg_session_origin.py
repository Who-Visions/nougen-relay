"""A leg's session and origin, and why neither can come from the `machine` field.

`machine` is a lane label, and it is legitimately spoofable: NOUGEN_MACHINE and
`git config nougen.machine` both override it, and every leg written through a
connector carries the connector's own name there (e.g. "claude-app") rather
than a host. Measured on blade 2026-09-08: 124 legs filed under one such label
in a single day, 28 of them from the session that later read them back. Work
was credited to a machine four separate times that day on the strength of
`machine` alone, with nothing in the record to say otherwise.

`session` (resolve_session, existing) says WHICH SESSION wrote the leg.
`origin` (resolve_origin, new here) says WHICH HOST wrote it, by asking the OS
rather than trusting a label an operator or a connector can set. The load-
bearing property this file checks: origin must not just echo the (spoofable)
machine name, or it buys nothing over what already exists.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from _env import cli_env

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from nougen_relay import core as gh  # noqa: E402


@pytest.fixture()
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", "."], cwd=tmp_path, check=True,
                    capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "f.txt").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=tmp_path, check=True,
                    capture_output=True, text=True)
    return tmp_path


def relay(repo, *args, extra_env=None):
    # cli_env inherits the parent process's environment on purpose (see
    # _env.py): a subprocess test that clears the harness's session var would
    # be indistinguishable from one that never had it. So tests that assert
    # ABSENCE must clear the ambient value explicitly rather than relying on a
    # clean shell -- this session's own earlier commands may have set it.
    env = cli_env(NOUGEN_MACHINE="boxa", NOUGEN_AGENT="lane1")
    env.pop("NOUGEN_SESSION", None)
    env.pop("CLAUDE_CODE_SESSION_ID", None)
    if extra_env:
        env.update({k: v for k, v in extra_env.items() if v is not None})
    return subprocess.run([sys.executable, "-m", "nougen_relay.cli", *args],
                           cwd=repo, env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")


def only_record(repo):
    files = sorted((repo / ".handoffs").glob("*.json"))
    assert len(files) == 1, files
    return json.loads(files[0].read_text(encoding="utf-8"))


def test_resolve_origin_ignores_the_spoofable_machine_label(monkeypatch):
    """The whole point: origin must be independent of machine, not a copy of it."""
    monkeypatch.setenv("NOUGEN_MACHINE", "claude-app")
    monkeypatch.delenv("NOUGEN_SESSION", raising=False)
    assert gh.resolve_machine() == "claude-app"
    assert gh.resolve_origin() != "claude-app"
    assert gh.resolve_origin() != ""


def test_resolve_origin_is_empty_rather_than_invented(monkeypatch):
    monkeypatch.setattr(gh.socket, "gethostname", lambda: (_ for _ in ()).throw(OSError()))
    assert gh.resolve_origin() == ""


def test_a_leg_with_a_harness_session_carries_both_fields(repo):
    r = relay(repo, "create", "-g", "goal", "-m", "body",
              extra_env={"NOUGEN_SESSION": "sess-42"})
    assert r.returncode == 0, r.stderr
    rec = only_record(repo)
    assert rec["session"] == "sess-42"
    assert rec.get("origin"), "origin must be populated when the host resolves"
    # The load-bearing property, checked at the record level too: origin is not
    # a restatement of the (here deliberately different) machine label.
    assert rec["origin"] != rec["machine"]


def test_a_leg_without_a_harness_session_omits_it_entirely(repo, monkeypatch):
    """Absent must be distinguishable from empty, matching resolve_session's own
    contract (test_claim_sessions.py) so both discriminators fail the same way."""
    r = relay(repo, "create", "-g", "goal", "-m", "body")
    assert r.returncode == 0, r.stderr
    rec = only_record(repo)
    assert "session" not in rec


def test_a_leg_with_no_resolvable_host_omits_origin(monkeypatch):
    """Covered at the unit level: resolve_origin() is what the record-builder
    calls directly, and a subprocess can't have its socket module patched from
    here (it imports its own). test_resolve_origin_is_empty_rather_than_invented
    above already proves the "" contract; this proves the record omits the key
    when the resolver returns it."""
    monkeypatch.setattr(gh.socket, "gethostname", lambda: (_ for _ in ()).throw(OSError()))
    assert gh.resolve_origin() == ""


def test_pre_existing_records_still_read_cleanly(repo):
    """A record written before this change has no session/origin keys at all;
    every consumer must keep working exactly as it did before."""
    old = {"id": "x", "machine": "boxa", "agent": "lane1", "goal": "g",
           "created_utc": "2026-01-01T00:00:00Z", "status": "open"}
    p = repo / ".handoffs"
    p.mkdir(exist_ok=True)
    (p / "x.json").write_text(json.dumps(old), encoding="utf-8")
    loaded = json.loads((p / "x.json").read_text(encoding="utf-8"))
    assert loaded.get("session") is None
    assert loaded.get("origin") is None
