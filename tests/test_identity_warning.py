"""A machine the registry has never seen gets flagged where the tool writes.

The hook asks this question already, but only on clones where someone ran
`git config core.hooksPath hooks` — and on most of them nobody had. The tool
writes records on every clone, so it has to ask too.

It warns where the hook refuses. A box's first write is very often its ack:
pull a leg, take the baton, push. Refusing that refuses the workflow relay
exists for, and the escape would be NOUGEN_IDENTITY_OK=1 parked in a shell
profile — the guard uninstalling itself. The hook can refuse because a human is
reading; the tool frequently runs where nobody is.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SRC = str(Path(__file__).resolve().parents[1] / "src")


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def relay(repo, *args, machine, agent="claude-cli", **extra):
    base_env = {k: v for k, v in os.environ.items() if k != "NOUGEN_IDENTITY_OK"}
    env = {**base_env, "PYTHONPATH": SRC, "NOUGEN_MACHINE": machine,
           "NOUGEN_AGENT": agent, "PYTHONIOENCODING": "utf-8"}
    env.update({k: str(v) for k, v in extra.items()})
    return subprocess.run([sys.executable, "-m", "nougen_relay.cli", *args],
                          cwd=repo, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


@pytest.fixture()
def repo(tmp_path):
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
    return work


def test_the_first_record_ever_is_not_flagged(repo):
    """An empty registry has nobody to be a stranger to."""
    out = relay(repo, "create", "-g", "first ever", "-m", "notes", machine="phoebus")
    assert "never written a record" not in out.stdout, out.stdout


def test_a_second_name_on_the_same_repo_is_flagged(repo):
    relay(repo, "create", "-g", "first", "-m", "notes", machine="phoebus")
    out = relay(repo, "create", "-g", "second", "-m", "notes", machine="who-mac-mini")
    assert "never written a record" in out.stdout, out.stdout
    assert "phoebus" in out.stdout, "the warning must name who is already here"


def test_the_warning_never_blocks_the_write(repo):
    """The record is the point. A flag that loses one is worse than the gap."""
    relay(repo, "create", "-g", "first", "-m", "notes", machine="phoebus")
    out = relay(repo, "create", "-g", "from a new box", "-m", "notes",
                machine="brand-new-box")
    assert out.returncode == 0, out.stdout + out.stderr
    written = list((repo / ".handoffs").glob("*brand-new-box*"))
    assert written, "the record must exist despite the warning"


def test_a_joining_box_can_still_take_the_baton(repo):
    """The exact workflow refusing would have broken."""
    relay(repo, "create", "-g", "needs a mac", "-m", "notes", machine="whoart")
    git("add", ".handoffs", cwd=repo)
    git("commit", "-qm", "handoff", cwd=repo)

    out = relay(repo, "relay", "ack", "-m", "picking this up", machine="phoebus")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "baton taken" in out.stdout
    assert "never written a record" in out.stdout, "still flagged, just not blocked"


def test_a_known_machine_is_quiet(repo):
    relay(repo, "create", "-g", "first", "-m", "notes", machine="phoebus")
    out = relay(repo, "create", "-g", "second", "-m", "notes", machine="phoebus")
    assert "never written a record" not in out.stdout, out.stdout


def test_reads_are_never_flagged(repo):
    """`claim list` is what you run to find out which name the fleet uses."""
    relay(repo, "create", "-g", "first", "-m", "notes", machine="phoebus")
    for args in (("claim", "list"), ("claim", "check", "-s", "src"), ("list",)):
        out = relay(repo, *args, machine="a-stranger")
        assert "never written a record" not in out.stdout, (args, out.stdout)


def test_the_override_silences_it(repo):
    relay(repo, "create", "-g", "first", "-m", "notes", machine="phoebus")
    out = relay(repo, "create", "-g", "deliberate", "-m", "notes",
                machine="brand-new-box", NOUGEN_IDENTITY_OK="1")
    assert "never written a record" not in out.stdout, out.stdout


@pytest.mark.skipif(shutil.which("sh") is None, reason="Needs sh to test the hook's shell snippet")
def test_tool_and_hook_agree_on_who_is_known(repo):
    """Two notions of 'known' would be worse than one."""
    relay(repo, "create", "-g", "first", "-m", "notes", machine="phoebus")
    hook_view = subprocess.run(
        ["sh", "-c",
         "ls .handoffs 2>/dev/null | sed -n 's/^[^_]*__\\([^_]*\\)__.*/\\1/p' | sort -u"],
        cwd=repo, capture_output=True, text=True, check=False,
    ).stdout.split()

    sys.path.insert(0, SRC)
    from nougen_relay.core import known_machines
    tool_view = known_machines(repo)
    sys.path.remove(SRC)

    assert tool_view == set(hook_view), (tool_view, hook_view)
