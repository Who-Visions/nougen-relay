"""Adoption has to be safe to run on a repo someone else configured.

The whole point is that it gets run across every repo the fleet works in,
mostly unattended, mostly on repos whose hook setup nobody remembers. So the
failure that matters is not "it did not install" — that is visible — it is "it
installed over something that was already working". NouGenTracker keeps its
hooks in `.githooks`; seizing `core.hooksPath` for `hooks/` would have disabled
the machine/agent trailers it already had, silently, in the same command that
claimed to improve its coverage.
"""
import os
import stat
import subprocess
from pathlib import Path

import pytest

from nougen_relay import adopt
from nougen_relay import core as gh

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


@pytest.fixture()
def bare(tmp_path, monkeypatch):
    root = tmp_path / "fresh"
    root.mkdir()
    _run("git", "init", "-q", "-b", "main", cwd=root)
    monkeypatch.chdir(root)
    gh._AGENT_CACHE = None
    return root


def test_the_shipped_hooks_match_this_repos_own(monkeypatch):
    """No drift between what adopt writes and what NouGenRelay runs on itself.

    The hooks are Python constants so they travel with an installed wheel,
    which means the checked-in copies are a second source of truth. This is the
    only thing keeping them one.
    """
    for name, content in adopt.HOOKS.items():
        on_disk = (REPO_ROOT / "hooks" / name)
        assert on_disk.exists(), f"hooks/{name} is missing from this repo"
        assert on_disk.read_text(encoding="utf-8") == content, (
            f"hooks/{name} has drifted from adopt.{name.replace('-', '_').upper()}")


def test_adoption_of_a_fresh_repo_installs_everything(bare):
    adopt.adopt(bare, agent="claude-cli")
    assert (bare / ".handoffs" / "claims").is_dir()
    assert (bare / ".handoffs" / ".gitkeep").exists()
    assert (bare / "hooks" / "prepare-commit-msg").exists()
    assert (bare / "hooks" / "pre-commit").exists()
    assert gh._git("config", "--get", "core.hooksPath") == "hooks"
    assert gh._git("config", "--get", "nougen.agent") == "claude-cli"


def test_adoption_is_idempotent(bare):
    adopt.adopt(bare, agent="claude-cli")
    second = adopt.adopt(bare, agent="claude-cli")
    assert all(status == "ok" for status, _ in second), second


def test_an_existing_hooks_path_is_respected_not_seized(bare):
    """NouGenTracker's `.githooks`, which already held a working hook."""
    (bare / ".githooks").mkdir()
    (bare / ".githooks" / "prepare-commit-msg").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    _run("git", "config", "core.hooksPath", ".githooks", cwd=bare)

    adopt.adopt(bare, agent="claude-cli")

    assert gh._git("config", "--get", "core.hooksPath") == ".githooks"
    assert (bare / ".githooks" / "pre-commit").exists()
    assert not (bare / "hooks").exists(), "adopt created a second, unused hooks dir"


def test_an_ignored_registry_is_reported_not_called_present(bare):
    """NouGen carried 130+ records under a .gitignore line since June.

    Every check said covered: the directory existed, adoption said "registry
    already present", and hooks were installed with nothing to publish into.
    `exists()` is a filesystem question; whether the fleet can read it is a git
    question, and nothing was asking it.
    """
    (bare / ".handoffs").mkdir()
    (bare / ".handoffs" / "20260615T000000Z__whoart__claude-cli.md").write_text("x", encoding="utf-8")
    (bare / ".gitignore").write_text(".handoffs/\n", encoding="utf-8")

    changes = adopt.adopt(bare, agent="claude-cli")

    ignored = [d for s, d in changes if s == "missing"]
    assert any("GITIGNORED" in d for d in ignored), changes


def test_an_unignored_but_untracked_registry_gets_a_gitkeep(bare):
    """Un-ignored and empty of tracked files is also invisible to everyone else."""
    (bare / ".handoffs").mkdir()
    adopt.adopt(bare, agent="claude-cli")
    assert (bare / ".handoffs" / ".gitkeep").exists()


def test_a_shared_registry_is_left_alone(bare):
    (bare / ".handoffs").mkdir()
    (bare / ".handoffs" / ".gitkeep").write_text("", encoding="utf-8")
    _run("git", "add", ".handoffs/.gitkeep", cwd=bare)
    _run("git", "-c", "user.email=t@e.com", "-c", "user.name=t",
         "-c", "core.hooksPath=", "commit", "-qm", "registry", cwd=bare)

    changes = adopt.adopt(bare, agent="claude-cli")
    assert any("present and shared" in d for _, d in changes), changes


def test_dry_run_changes_nothing(bare):
    changes = adopt.adopt(bare, agent="claude-cli", dry=True)
    assert changes
    assert not (bare / ".handoffs").exists()
    assert not (bare / "hooks").exists()
    assert not gh._git("config", "--get", "nougen.agent")


def test_a_repo_with_no_lane_is_reported_not_guessed(bare):
    changes = adopt.adopt(bare)
    assert any(status == "missing" for status, _ in changes)
    assert not gh._git("config", "--get", "nougen.agent")


def test_hooks_are_written_with_lf_endings(bare):
    """CRLF makes `#!/bin/sh` unparseable, with an error naming no cause."""
    adopt.adopt(bare, agent="claude-cli")
    raw = (bare / "hooks" / "pre-commit").read_bytes()
    assert b"\r\n" not in raw


@pytest.mark.skipif(os.name == "nt", reason="Windows has no executable bit; git does not need one")
def test_hooks_are_executable_where_that_means_something(bare):
    adopt.adopt(bare, agent="claude-cli")
    assert (bare / "hooks" / "pre-commit").stat().st_mode & stat.S_IXUSR


def test_the_pre_commit_hook_only_blocks_on_exit_three():
    """Anything other than a foreign claim — relay missing, a crash — must pass.

    A pre-commit hook that can wedge a repository gets uninstalled, and an
    uninstalled guard is worse than none because everyone believes it runs.
    """
    body = adopt.PRE_COMMIT
    assert 'STATUS" = "3"' in body
    assert body.rstrip().endswith("exit 0")


def test_the_pre_commit_hook_can_find_relay_without_the_console_script():
    """pip could not write relay.exe on whoart; the module path still worked."""
    assert "python -m nougen_relay.cli" in adopt.PRE_COMMIT


def test_the_commit_hook_reads_the_lane_from_git_config():
    """`relay init` stores it there and promised it survives new shells.

    The hook read only NOUGEN_AGENT, so the very next commit after a successful
    `relay init` was refused as unknown-agent. Two resolvers, one question.
    """
    assert "git config --get nougen.agent" in adopt.PREPARE_COMMIT_MSG
    assert "git config --get nougen.machine" in adopt.PREPARE_COMMIT_MSG
