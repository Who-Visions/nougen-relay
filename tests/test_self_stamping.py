"""The tool stamps the commits it writes, without help from a hook.

A hook is per-clone configuration: `git config core.hooksPath hooks`, run by
hand, on every machine, in every checkout. It was missed on most of them — of
the first twenty commits on this repo's main, every unstamped one was a claim
or relay record written by this tool, on a box where that step had not been
run. The tool resolves machine and agent to write the record; it should not
then depend on a hook to say so.

These tests run with hooks deliberately NOT configured, which is the state the
gap actually occurred in.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

SRC = str(Path(__file__).resolve().parents[1] / "src")
HOOKS = Path(__file__).resolve().parents[1] / "hooks"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def relay(repo, *args, machine="phoebus", agent="claude-cli", **extra):
    env = {**os.environ, "PYTHONPATH": SRC, "NOUGEN_MACHINE": machine,
           "NOUGEN_AGENT": agent, "PYTHONIOENCODING": "utf-8"}
    env.update({k: str(v) for k, v in extra.items()})
    return subprocess.run([sys.executable, "-m", "nougen_relay.cli", *args],
                          cwd=repo, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def trailers(repo, key, ref="HEAD"):
    out = git("log", "-1", f"--format=%(trailers:key={key},valueonly=true)", ref,
              cwd=repo).stdout
    return out.strip()


@pytest.fixture()
def repo(tmp_path):
    """A clone with a remote and, deliberately, no hooks configured."""
    bare = tmp_path / "origin.git"
    git("init", "-q", "--bare", "-b", "main", str(bare), cwd=tmp_path)
    work = tmp_path / "work"
    git("clone", "-q", str(bare), str(work), cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=work)
    git("config", "user.name", "t", cwd=work)
    (work / "f.txt").write_text("x\n", encoding="utf-8")
    git("add", ".", cwd=work)
    git("commit", "-qm", "init", cwd=work)
    git("push", "-q", "origin", "main", cwd=work)
    # The state the gap occurred in: a clone nobody ran the hook setup on.
    hooks_path = subprocess.run(["git", "config", "--get", "core.hooksPath"],
                                cwd=work, capture_output=True, text=True)
    assert not hooks_path.stdout.strip(), "fixture must start without hooks"
    return work


def test_a_claim_is_stamped_without_any_hook(repo):
    out = relay(repo, "claim", "take", "-s", "src/lib", "-g", "oauth fix")
    assert "claimed" in out.stdout, out.stdout + out.stderr
    assert trailers(repo, "Machine") == "phoebus"
    assert trailers(repo, "Agent") == "claude-cli"


def test_a_release_is_stamped_without_any_hook(repo):
    relay(repo, "claim", "take", "-s", "src/lib", "-g", "oauth fix")
    relay(repo, "claim", "release", "-s", "src/lib")
    assert git("log", "-1", "--format=%s", cwd=repo).stdout.strip().endswith("release")
    assert trailers(repo, "Machine") == "phoebus"
    assert trailers(repo, "Agent") == "claude-cli"


def test_the_ack_of_a_leg_is_stamped_without_any_hook(repo):
    relay(repo, "create", "-g", "left off here", "-m", "notes")
    git("add", ".handoffs", cwd=repo)
    git("commit", "-qm", "handoff", cwd=repo)

    # A different box takes the baton.
    out = relay(repo, "relay", "ack", "-m", "picking this up", machine="blade1tb")
    assert "baton taken" in out.stdout, out.stdout + out.stderr
    assert trailers(repo, "Machine") == "blade1tb"
    assert trailers(repo, "Agent") == "claude-cli"


def test_an_unset_agent_is_recorded_as_such_not_omitted(repo):
    """Half an answer that looks authoritative is worse than an honest gap."""
    env_free = {**os.environ, "PYTHONPATH": SRC, "NOUGEN_MACHINE": "phoebus",
                "PYTHONIOENCODING": "utf-8"}
    env_free.pop("NOUGEN_AGENT", None)
    subprocess.run([sys.executable, "-m", "nougen_relay.cli",
                    "claim", "take", "-s", "src/lib", "-g", "anonymous lane"],
                   cwd=repo, env=env_free, capture_output=True, text=True)
    assert trailers(repo, "Machine") == "phoebus"
    assert trailers(repo, "Agent") == "unknown-agent"


def test_stamping_does_not_duplicate_when_the_hook_is_installed(repo):
    """interpret-trailers is idempotent and the hook uses the same keys."""
    git("config", "core.hooksPath", str(HOOKS), cwd=repo)
    relay(repo, "claim", "take", "-s", "src/lib", "-g", "both paths active")
    body = git("log", "-1", "--format=%B", cwd=repo).stdout
    assert body.count("Machine:") == 1, body
    assert body.count("Agent:") == 1, body
    assert "phoebus" in body


def test_whoami_reports_a_missing_hook(repo):
    out = relay(repo, "whoami")
    assert "not installed in this clone" in out.stdout, out.stdout
    assert "core.hooksPath" in out.stdout

    git("config", "core.hooksPath", str(HOOKS), cwd=repo)
    out = relay(repo, "whoami")
    assert "not installed in this clone" not in out.stdout, out.stdout
