"""mcp_server shells out to the CLI; pin the argv each tool builds and the
error-as-text contract of `_run`."""

import subprocess
import sys
from types import SimpleNamespace

import pytest

pytest.importorskip("mcp")

from nougen_relay import mcp_server as m  # noqa: E402


@pytest.fixture
def calls(monkeypatch, tmp_path):
    seen = []

    def fake_run(argv, **kw):
        seen.append((argv, kw))
        return SimpleNamespace(stdout="out\n", stderr="", returncode=0)

    monkeypatch.setattr(m.subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    return seen


def _args(calls):
    argv = calls[-1][0]
    assert argv[:3] == [sys.executable, "-m", "nougen_relay.cli"]
    return argv[3:]


def test_run_returns_stripped_output(calls):
    assert m._run(["check"]) == "out"


def test_run_combines_stderr(monkeypatch, tmp_path):
    monkeypatch.setattr(
        m.subprocess, "run",
        lambda *a, **k: SimpleNamespace(stdout="a", stderr="b", returncode=1),
    )
    assert m._run(["x"], str(tmp_path)) == "ab"


def test_run_no_output_reports_exit_code(monkeypatch, tmp_path):
    monkeypatch.setattr(
        m.subprocess, "run",
        lambda *a, **k: SimpleNamespace(stdout="", stderr="", returncode=3),
    )
    assert m._run(["x"], str(tmp_path)) == "(no output, exit 3)"


def test_run_bad_repo_is_text_not_exception(tmp_path):
    missing = str(tmp_path / "nope")
    assert m._run(["check"], missing) == f"error: not a directory: {missing}"


def test_run_timeout_is_text_not_exception(monkeypatch, tmp_path):
    def boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd="relay", timeout=m.TIMEOUT)

    monkeypatch.setattr(m.subprocess, "run", boom)
    out = m._run(["claim", "list"], str(tmp_path))
    assert out == f"error: `relay claim list` timed out after {m.TIMEOUT}s"


def test_run_uses_repo_as_cwd_and_utf8_env(calls, tmp_path):
    m._run(["check"], str(tmp_path))
    kw = calls[-1][1]
    assert kw["cwd"] == str(tmp_path)
    assert kw["env"]["PYTHONIOENCODING"] == "utf-8"
    assert kw["timeout"] == m.TIMEOUT


@pytest.mark.parametrize("call,expected", [
    (lambda: m.relay_whoami(), ["whoami"]),
    (lambda: m.relay_check(), ["check"]),
    (lambda: m.relay_open(), ["relay", "open"]),
    (lambda: m.relay_claim_list(), ["claim", "list"]),
    (lambda: m.relay_claim_take("src/a", "fix"),
     ["claim", "take", "-s", "src/a", "-g", "fix"]),
    (lambda: m.relay_claim_release("src/a"), ["claim", "release", "-s", "src/a"]),
    (lambda: m.relay_create("g", "msg"), ["create", "-g", "g", "-m", "msg"]),
    (lambda: m.relay_create("g", "msg", parent_leg_id="L1"),
     ["create", "-g", "g", "-m", "msg", "--parent", "L1"]),
    (lambda: m.relay_summarize("L1", "done"),
     ["summarize", "--id", "L1", "-m", "done"]),
    (lambda: m.relay_summarize("L1", "done", goal="g"),
     ["summarize", "--id", "L1", "-m", "done", "-g", "g"]),
    (lambda: m.relay_ack("L1", "mine"), ["relay", "ack", "--id", "L1", "-m", "mine"]),
    (lambda: m.relay_shards(), ["shards"]),
    (lambda: m.relay_shards(dry=True), ["shards", "--dry"]),
])
def test_tool_argv(calls, call, expected):
    assert call() == "out"
    assert _args(calls) == expected
