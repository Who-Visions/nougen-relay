"""The hook runs on every box in the fleet, so it must be POSIX everywhere.

`prepare-commit-msg` is the one file that executes on Windows (git-bash, GNU
userland), macOS (BSD userland) and Linux alike. A GNU-only construct in it is
green on two of those and silently wrong on the third — and "silently wrong"
here means a machine commits under a name the registry has never seen, which
the guard then refuses.

That is not hypothetical. `sed 's/\\.\\(local\\|lan\\)$//'` shipped and passed
on Windows: `\\|` alternation is a GNU extension, BSD sed matches it literally,
so the suffix strip no-opped and every Mac commit was refused as an unknown
machine. The behavioural test could not catch it, because it only fails on a
box whose real hostname carries a suffix.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "prepare-commit-msg"


def test_the_hook_uses_no_gnu_only_sed_alternation():
    """`\\|` in a sed expression is a GNU extension; BSD sed takes it literally."""
    body = HOOK.read_text(encoding="utf-8")
    offenders = [
        line.strip()
        for line in body.splitlines()
        if re.search(r"sed\s+[^|]*\\\|", line) and not line.strip().startswith("#")
    ]
    assert not offenders, (
        "GNU-only sed alternation found — use a POSIX `case` statement instead:\n  "
        + "\n  ".join(offenders)
    )


def test_the_hook_uses_no_gnu_only_sed_flags():
    """-i without an argument, -r and -E-by-default differ across seds too."""
    body = HOOK.read_text(encoding="utf-8")
    offenders = [
        line.strip()
        for line in body.splitlines()
        if re.search(r"sed\s+(-i\s|-r\s)", line) and not line.strip().startswith("#")
    ]
    assert not offenders, "GNU-only sed flag found:\n  " + "\n  ".join(offenders)


@pytest.mark.skipif(sys.platform == "win32", reason="PATH shim needs a POSIX shell")
def test_a_suffixed_hostname_is_stripped_whatever_the_box(tmp_path):
    """Force the hostname rather than depending on the one this box happens to have.

    The existing behavioural test only exercises the strip on a machine whose
    real hostname ends in `.local`, so it is dead weight on Windows and Linux.
    Shimming `hostname` makes every box run the same case.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "core.hooksPath", str(HOOK.parent)], cwd=repo, check=True)

    shim = tmp_path / "bin"
    shim.mkdir()
    fake = shim / "hostname"
    fake.write_text("#!/bin/sh\necho probe-box.local\n", encoding="utf-8")
    fake.chmod(0o755)

    env = {**os.environ, "PATH": f"{shim}{os.pathsep}{os.environ['PATH']}",
           "NOUGEN_AGENT": "claude-cli",
           # This box is deliberately new to the registry; the guard's job is
           # tested elsewhere, what matters here is the name it settles on.
           "NOUGEN_IDENTITY_OK": "1"}
    env.pop("NOUGEN_MACHINE", None)

    (repo / "a.txt").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True, env=env)
    done = subprocess.run(["git", "commit", "-qm", "probe"], cwd=repo, env=env,
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr

    message = subprocess.run(["git", "log", "-1", "--format=%B"], cwd=repo,
                             capture_output=True, text=True, check=True).stdout
    assert "Machine: probe-box" in message, message
    assert "probe-box-local" not in message, (
        "the network suffix survived — the strip is not portable: " + message
    )


@pytest.mark.skipif(sys.platform == "win32", reason="PATH shim needs a POSIX shell")
def test_a_real_fqdn_keeps_its_domain(tmp_path):
    """`build.corp.example.com` -> `build` would collide across domains."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "core.hooksPath", str(HOOK.parent)], cwd=repo, check=True)

    shim = tmp_path / "bin"
    shim.mkdir()
    fake = shim / "hostname"
    fake.write_text("#!/bin/sh\necho build.corp.example.com\n", encoding="utf-8")
    fake.chmod(0o755)

    env = {**os.environ, "PATH": f"{shim}{os.pathsep}{os.environ['PATH']}",
           "NOUGEN_AGENT": "claude-cli", "NOUGEN_IDENTITY_OK": "1"}
    env.pop("NOUGEN_MACHINE", None)

    (repo / "a.txt").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True, env=env)
    subprocess.run(["git", "commit", "-qm", "probe"], cwd=repo, env=env,
                   capture_output=True, text=True, check=True)

    message = subprocess.run(["git", "log", "-1", "--format=%B"], cwd=repo,
                             capture_output=True, text=True, check=True).stdout
    assert "Machine: build-corp-example-com" in message, message
