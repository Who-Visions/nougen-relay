"""The guard has to be believed, so it has to be right in both directions.

A guard that blocks work nobody claimed gets --no-verify'd within a day, and
once that reflex exists the real block — another machine is already doing this —
gets skipped too. So the asymmetry is the design, and it is what these tests
pin: another machine's claim BLOCKS, a missing claim of your own WARNS, and a
repo with no registry says so instead of reporting all-clear.

That last one is the failure that produced this module. On 2026-08-01 a claim
was taken correctly in NouGenRelay for a file in NouGenTracker, which had no
registry, and the check answered "no active claim overlaps this scope" with
total confidence while another machine was already doing the work.
"""
import json
import subprocess

import pytest

from nougen_relay import core as gh
from nougen_relay import guard


def _run(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    """A real git repo with a registry, on this machine's identity."""
    root = tmp_path / "work"
    root.mkdir()
    _run("git", "init", "-q", "-b", "main", cwd=root)
    _run("git", "config", "user.email", "t@example.com", cwd=root)
    _run("git", "config", "user.name", "Test", cwd=root)
    (root / ".handoffs" / "claims").mkdir(parents=True)
    monkeypatch.setenv("NOUGEN_MACHINE", "whoart")
    monkeypatch.setenv("NOUGEN_AGENT", "claude-cli")
    monkeypatch.chdir(root)
    gh._AGENT_CACHE = None
    return root


def _claim(root, machine, scope, *, goal="work", status="active"):
    """Write a claim record the way `claim take` does, without the network."""
    outdir = root / ".handoffs" / "claims"
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = gh._now()
    rec = {
        "machine": machine, "agent": "claude-cli", "goal": goal, "scope": scope,
        "status": status, "branch": "main", "sha": "0" * 7,
        "created_utc": stamp.isoformat(), "ttl_hours": 8.0,
    }
    name = f"{stamp.strftime('%Y%m%dT%H%M%S')}Z__{machine}__claude-cli.json"
    (outdir / name).write_text(json.dumps(rec), encoding="utf-8")
    return rec


def _stage(root, relpath, content="x\n"):
    target = root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    _run("git", "add", relpath, cwd=root)


class _Args:
    def __init__(self, **kw):
        self.staged = kw.get("staged", True)
        self.path = kw.get("path", [])
        self.require_claim = kw.get("require_claim", False)
        self.strict = kw.get("strict", False)
        self.quiet = kw.get("quiet", True)


def test_another_machines_claim_blocks(repo, monkeypatch):
    _claim(repo, "phoebus", "token_tracker.py")
    _stage(repo, "token_tracker.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args()) == gh.EXIT_DIVERGED


def test_an_unrelated_claim_does_not_block(repo, monkeypatch):
    _claim(repo, "phoebus", "docs/RELAY.md")
    _claim(repo, "whoart", "token_tracker.py")
    _stage(repo, "token_tracker.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args()) == gh.EXIT_OK


def test_your_own_claim_never_blocks_you(repo, monkeypatch):
    _claim(repo, "whoart", "token_tracker.py")
    _stage(repo, "token_tracker.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args(require_claim=True)) == gh.EXIT_OK


def test_an_expired_claim_stops_blocking(repo, monkeypatch):
    rec = _claim(repo, "phoebus", "token_tracker.py")
    stale = gh._now().replace(year=gh._now().year - 1).isoformat()
    path = next((repo / ".handoffs" / "claims").glob("*.json"))
    rec["created_utc"] = stale
    path.write_text(json.dumps(rec), encoding="utf-8")
    _stage(repo, "token_tracker.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args()) == gh.EXIT_OK


def test_a_released_claim_stops_blocking(repo, monkeypatch):
    _claim(repo, "phoebus", "token_tracker.py", status="released")
    _stage(repo, "token_tracker.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args()) == gh.EXIT_OK


def test_unclaimed_work_warns_but_lets_the_commit_through(repo, monkeypatch, capsys):
    _stage(repo, "token_tracker.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args(quiet=False)) == gh.EXIT_OK
    assert "not covered by a claim" in capsys.readouterr().out


def test_require_claim_turns_that_warning_into_a_block(repo, monkeypatch):
    _stage(repo, "token_tracker.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args(require_claim=True)) == gh.EXIT_DIVERGED


def test_require_claim_can_be_switched_on_per_repo(repo, monkeypatch):
    _stage(repo, "token_tracker.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    _run("git", "config", "nougen.requireClaim", "true", cwd=repo)
    assert guard.cmd_guard(_Args()) == gh.EXIT_DIVERGED


def test_a_repo_without_a_registry_says_so_instead_of_all_clear(repo, monkeypatch, capsys):
    """The 2026-08-01 failure, as a test."""
    import shutil
    shutil.rmtree(repo / ".handoffs")
    _stage(repo, "token_tracker.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    guard.cmd_guard(_Args(quiet=False))
    out = capsys.readouterr().out
    assert "no .handoffs" in out and "relay adopt" in out
    assert "clear of other machines" not in out


def test_nothing_staged_is_not_a_finding(repo, monkeypatch):
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args()) == gh.EXIT_OK


def test_a_directory_claim_covers_files_beneath_it(repo, monkeypatch):
    _claim(repo, "phoebus", "fleet/")
    _stage(repo, "fleet/agy_usage.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args()) == gh.EXIT_DIVERGED


def test_a_windows_claim_matches_a_posix_path(repo, monkeypatch):
    """The separator bug, which the guard would otherwise inherit.

    git reports `src/lib.py`; a Windows lane claims `src\\lib.py`. Before
    _normalize_scope folded separators these shared no token, so the check
    reported all-clear on the exact collision it exists to catch.
    """
    _claim(repo, "phoebus", r"src\lib.py")
    _stage(repo, "src/lib.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args()) == gh.EXIT_DIVERGED


def test_scope_overlap_is_separator_blind_both_ways():
    assert gh._scopes_overlap(r"src\lib.py", "src/lib.py") == ["src/lib.py"]
    assert gh._scopes_overlap("src/lib.py", r"src\lib.py") == ["src/lib.py"]
    assert gh._scopes_overlap(r"NouGenTracker\fleet", "nougentracker/fleet/agy.py")


def test_the_registry_does_not_trip_the_guards_own_warning(repo, monkeypatch, capsys):
    """Otherwise every `relay create` ends in a complaint the guard produced.

    Handoff records are the protocol's own bookkeeping — written by relay,
    claimed by nobody, collided on by nobody. Warning about them is the
    cry-wolf failure this guard is weighted to avoid, self-inflicted.
    """
    _stage(repo, ".handoffs/20260802T000000Z__whoart__claude-cli.md")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args(quiet=False)) == gh.EXIT_OK
    assert "not covered by a claim" not in capsys.readouterr().out


def test_real_work_alongside_a_record_is_still_warned_about(repo, monkeypatch, capsys):
    """Exempting the registry must not exempt the commit that carries it."""
    _stage(repo, ".handoffs/20260802T000000Z__whoart__claude-cli.md")
    _stage(repo, "token_tracker.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    guard.cmd_guard(_Args(quiet=False))
    out = capsys.readouterr().out
    assert "not covered by a claim" in out
    assert "token_tracker.py" in out
    assert ".handoffs" not in out


def test_an_explicit_path_does_not_need_git(repo, monkeypatch):
    _claim(repo, "phoebus", "token_tracker.py")
    monkeypatch.setattr(gh, "watch_targets", lambda: [None])
    assert guard.cmd_guard(_Args(path=["token_tracker.py"], staged=False)) == gh.EXIT_DIVERGED
