"""Two sessions on one lane, and the release that took the wrong claim.

Identity is machine+lane, which was enough while a lane meant one session. On
2026-08-02 two agent sessions ran on `whoart` under `claude-cli` at the same
time. They were invisible to each other's claims, and a bare `claim release` in
one released the other's while it was still working.

The fix has to be honest about what it can know. A `relay` invocation is a fresh
process, so pid and ppid say nothing about which session drove it — there is no
ambient answer, only one a harness supplies. So `NOUGEN_SESSION` is read when
set and the field is OMITTED when it is not, because "a different session" and
"nobody recorded one" need different answers and a discriminator that guesses
would be worse than none.

Which makes the regression test the important one here: a fleet that sets
nothing must behave exactly as it did before.
"""
import itertools
import json
import subprocess

import pytest

from nougen_relay import core as gh


def _run(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    root = tmp_path / "work"
    root.mkdir()
    _run("git", "init", "-q", "-b", "main", cwd=root)
    _run("git", "config", "user.email", "t@example.com", cwd=root)
    _run("git", "config", "user.name", "Test", cwd=root)
    (root / ".handoffs" / "claims").mkdir(parents=True)
    monkeypatch.setenv("NOUGEN_MACHINE", "whoart")
    monkeypatch.setenv("NOUGEN_AGENT", "claude-cli")
    for var in gh._SESSION_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.chdir(root)
    gh._AGENT_CACHE = None
    return root


class _Release:
    action = "release"
    scope = ""
    no_push = True
    all_sessions = False

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


_SEQ = itertools.count()


def _write_claim(root, scope, *, session=None, machine="whoart", status="active"):
    """One claim file, guaranteed distinct from the last one.

    The sequence number is not decoration. Windows' clock granularity is coarse
    enough that two calls in a row produce an identical timestamp, so a
    timestamp-only filename silently OVERWROTE the previous claim — and a test
    asserting "both were released" then passed while examining one file twice.
    """
    outdir = root / ".handoffs" / "claims"
    stamp = gh._now()
    rec = {"machine": machine, "agent": "claude-cli", "goal": "g", "scope": scope,
           "status": status, "branch": "main", "sha": "0" * 7,
           "created_utc": stamp.isoformat(), "ttl_hours": 8.0}
    if session:
        rec["session"] = session
    name = f"{stamp.strftime('%Y%m%dT%H%M%S')}-{next(_SEQ):04d}Z__{machine}__claude-cli.json"
    path = outdir / name
    path.write_text(json.dumps(rec), encoding="utf-8")
    return path


def _status_of(path):
    return json.loads(path.read_text(encoding="utf-8"))["status"]


def test_a_session_only_releases_its_own_claim(repo, monkeypatch, capsys):
    """The 2026-08-02 failure, as a test."""
    mine = _write_claim(repo, "a.py", session="alpha")
    theirs = _write_claim(repo, "b.py", session="beta")
    monkeypatch.setenv("NOUGEN_SESSION", "alpha")

    gh.cmd_claim(_Release())

    assert _status_of(mine) == "released"
    assert _status_of(theirs) == "active", "a sibling's claim was released mid-work"
    assert "another session" in capsys.readouterr().out


def test_all_sessions_takes_them_anyway(repo, monkeypatch):
    theirs = _write_claim(repo, "b.py", session="beta")
    monkeypatch.setenv("NOUGEN_SESSION", "alpha")
    gh.cmd_claim(_Release(all_sessions=True))
    assert _status_of(theirs) == "released"


def test_a_fleet_that_sets_nothing_behaves_exactly_as_before(repo):
    """The regression that matters: three machines are running this today."""
    one = _write_claim(repo, "a.py")
    two = _write_claim(repo, "b.py")
    gh.cmd_claim(_Release())
    assert _status_of(one) == "released"
    assert _status_of(two) == "released"


def test_a_sessionless_claim_is_still_released_by_a_session(repo, monkeypatch):
    """Claims written before this change must not become unreleasable."""
    legacy = _write_claim(repo, "a.py")
    monkeypatch.setenv("NOUGEN_SESSION", "alpha")
    gh.cmd_claim(_Release())
    assert _status_of(legacy) == "released"


def test_a_session_claim_is_released_by_a_sessionless_caller(repo):
    """The other direction: an operator on a plain shell must not be locked out."""
    held = _write_claim(repo, "a.py", session="alpha")
    gh.cmd_claim(_Release())
    assert _status_of(held) == "released"


def test_scope_still_narrows_a_release(repo, monkeypatch):
    a = _write_claim(repo, "a.py", session="alpha")
    b = _write_claim(repo, "b.py", session="alpha")
    monkeypatch.setenv("NOUGEN_SESSION", "alpha")
    gh.cmd_claim(_Release(scope="a.py"))
    assert _status_of(a) == "released"
    assert _status_of(b) == "active"


def test_another_machines_claim_is_untouched_either_way(repo, monkeypatch):
    theirs = _write_claim(repo, "a.py", machine="phoebus", session="alpha")
    monkeypatch.setenv("NOUGEN_SESSION", "alpha")
    gh.cmd_claim(_Release(all_sessions=True))
    assert _status_of(theirs) == "active"


def test_the_harness_session_id_is_used_without_configuration(repo, monkeypatch):
    """The reason this works at all: nobody had NOUGEN_SESSION set.

    Both sessions that collided ran with it unset, and so did the session that
    wrote the first version of the fix — which then had its own claim released
    a second time. A mitigation that requires configuration nobody applied
    prevents nothing, so relay reads the id the harness already exports.
    """
    monkeypatch.delenv("NOUGEN_SESSION", raising=False)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "c158477b-5697-4318-b9fc-69d3d38931b7")
    assert gh.resolve_session() == "c158477b-5697-4318-b9fc-69d3d38931b7"


def test_an_explicit_session_overrides_the_harness(repo, monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "from-harness")
    monkeypatch.setenv("NOUGEN_SESSION", "chosen")
    assert gh.resolve_session() == "chosen"


def test_resolve_session_is_empty_rather_than_invented(repo, monkeypatch):
    for var in gh._SESSION_VARS:
        monkeypatch.delenv(var, raising=False)
    assert gh.resolve_session() == ""
    monkeypatch.setenv("NOUGEN_SESSION", "  ")
    assert gh.resolve_session() == ""
    monkeypatch.setenv("NOUGEN_SESSION", "Alpha Session/1")
    assert gh.resolve_session() == "alpha-session-1"


def test_a_claim_without_a_session_omits_the_field_entirely(repo):
    """Absent must be distinguishable from empty, or the reader cannot tell
    "nobody recorded one" from "recorded as nothing"."""
    rec = json.loads(_write_claim(repo, "a.py").read_text(encoding="utf-8"))
    assert "session" not in rec
