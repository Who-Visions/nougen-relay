"""A relay commit must never absorb the operator's staged work.

Measured on 2026-08-01: a `claim release` committed a source fix, its tests and
a new tool alongside the claim record, under the subject "claim(whoart):
release". Nothing was lost and the code was correct — which is precisely why it
is dangerous. A commit that fails announces itself; a commit that quietly
describes itself wrong is believed by the next person to read `git log`.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from _env import cli_env

SRC = str(Path(__file__).resolve().parents[1] / "src")


def git(*args, cwd, check=True):
    return subprocess.run(["git", *args], cwd=cwd, check=check,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def relay(repo, *args, machine="boxa", agent="lane-a"):
    return subprocess.run(
        [sys.executable, "-m", "nougen_relay.cli", *args],
        cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        env=cli_env(NOUGEN_MACHINE=machine, NOUGEN_AGENT=agent),
    )


@pytest.fixture()
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    (r / "app.py").write_text("original\n", encoding="utf-8")
    git("init", "-q", ".", cwd=r)
    git("config", "user.email", "t@example.com", cwd=r)
    git("config", "user.name", "t", cwd=r)
    git("add", ".", cwd=r)
    git("commit", "-qm", "init", cwd=r)
    return r


def subject(repo, ref="HEAD"):
    return git("log", "-1", "--format=%s", ref, cwd=repo).stdout.strip()


def files_in(repo, ref="HEAD"):
    out = git("show", "--name-only", "--format=", ref, cwd=repo).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


def test_a_claim_does_not_commit_the_operators_staged_work(repo):
    """The exact incident: unrelated work sitting in the index, then a claim."""
    (repo / "app.py").write_text("my unrelated fix\n", encoding="utf-8")
    git("add", "app.py", cwd=repo)

    # Exit code is deliberately nonzero here: there is no remote, and the CLI
    # says so rather than pretending an unpublished claim protects anything.
    # What matters for this test is what it committed.
    relay(repo, "claim", "take", "-s", "src/lib", "-g", "something")

    assert "app.py" not in files_in(repo), (
        f"the claim commit swallowed unrelated work: {files_in(repo)}"
    )
    assert "claim" in subject(repo).lower()


def test_the_staged_work_is_still_staged_afterwards(repo):
    """Not merely excluded — left exactly as the operator had it, so their next
    `git commit` behaves as they expect."""
    (repo / "app.py").write_text("my unrelated fix\n", encoding="utf-8")
    git("add", "app.py", cwd=repo)

    relay(repo, "claim", "take", "-s", "src/lib", "-g", "something")

    staged = git("diff", "--cached", "--name-only", cwd=repo).stdout.split()
    assert "app.py" in staged, "the operator's staged file was un-staged from under them"


def test_release_is_equally_scoped(repo):
    """`release` is where it actually bit."""
    relay(repo, "claim", "take", "-s", "src/lib", "-g", "something")
    (repo / "app.py").write_text("more unrelated work\n", encoding="utf-8")
    git("add", "app.py", cwd=repo)

    relay(repo, "claim", "release", "-s", "src/lib")

    assert "app.py" not in files_in(repo)
    assert "app.py" in git("diff", "--cached", "--name-only", cwd=repo).stdout.split()


def test_the_claim_record_itself_is_still_committed(repo):
    """Scoping the commit must not stop it doing its job."""
    relay(repo, "claim", "take", "-s", "src/lib", "-g", "something")
    committed = files_in(repo)
    assert any(".handoffs" in f and "claims" in f for f in committed), committed
