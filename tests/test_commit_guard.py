"""The commit-time identity guard.

Documentation was already there and it still did not hold: a box committed to
this repo as `kushboygroups-mac-mini-local` / `unknown-agent`, read the
onboarding note, and corrected itself one commit too late. These assert that
the hook now refuses at the only moment the mistake is still fixable.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "prepare-commit-msg"


def git(*args, cwd, env=None, check=True):
    return subprocess.run(["git", *args], cwd=cwd, check=check,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          env=env)


@pytest.fixture()
def repo(tmp_path):
    """A repo with the hook installed the way the README installs it."""
    work = tmp_path / "work"
    work.mkdir()
    git("init", "-q", "-b", "main", ".", cwd=work)
    git("config", "user.email", "t@example.com", cwd=work)
    git("config", "user.name", "t", cwd=work)

    hooks = work / "hooks"
    hooks.mkdir()
    shutil.copy(HOOK, hooks / "prepare-commit-msg")
    os.chmod(hooks / "prepare-commit-msg", 0o755)
    git("config", "core.hooksPath", "hooks", cwd=work)
    return work


def commit(repo, name, **env_extra):
    """Stage a new file and commit it, returning the completed process."""
    (repo / name).write_text("x\n", encoding="utf-8")
    git("add", name, cwd=repo)
    env = {**os.environ, **{k: str(v) for k, v in env_extra.items()}}
    env.pop("NOUGEN_MACHINE", None)
    env.pop("NOUGEN_AGENT", None)
    env.pop("NOUGEN_IDENTITY_OK", None)
    env.update({k: str(v) for k, v in env_extra.items()})
    return git("commit", "-qm", f"add {name}", cwd=repo, env=env, check=False)


def record(repo, machine, agent="claude-cli"):
    """Put a record in the registry so the repo has a known machine."""
    directory = repo / ".handoffs"
    directory.mkdir(exist_ok=True)
    (directory / f"20260731T000000Z__{machine}__{agent}.md").write_text("x\n", encoding="utf-8")


def last_message(repo):
    return git("log", "-1", "--format=%B", cwd=repo).stdout


def test_an_unset_agent_is_refused_before_it_reaches_history(repo):
    out = commit(repo, "a.txt", NOUGEN_MACHINE="blade1tb")
    assert out.returncode != 0, "an anonymous commit must not land"
    assert "unknown-agent" in out.stderr
    # The refusal must tell you how to fix it — but not in one fixed spelling.
    # `relay init --agent` became the recommended remedy when the lane moved
    # into git config, and asserting the literal env var name made a message
    # improvement look like a regression.
    assert any(hint in out.stderr for hint in ("NOUGEN_AGENT", "relay init")),         "the refusal has to say what to set"


def test_a_first_commit_still_works_in_an_empty_registry(repo):
    """Bootstrapping a repo that has no records yet cannot be blocked — there
    is no known-machine list to check against, only an agent to name."""
    out = commit(repo, "a.txt", NOUGEN_MACHINE="brand-new-box", NOUGEN_AGENT="claude-cli")
    assert out.returncode == 0, out.stderr
    assert "Machine: brand-new-box" in last_message(repo)
    assert "Agent: claude-cli" in last_message(repo)


def test_a_machine_the_registry_already_knows_commits_normally(repo):
    record(repo, "blade1tb")
    out = commit(repo, "a.txt", NOUGEN_MACHINE="blade1tb", NOUGEN_AGENT="claude-cli")
    assert out.returncode == 0, out.stderr
    assert "Machine: blade1tb" in last_message(repo)


def test_a_name_the_registry_has_never_seen_is_refused(repo):
    """The exact failure: the Mac mini's hostname, not the name the fleet uses."""
    record(repo, "blade1tb")
    record(repo, "whoart")
    out = commit(repo, "a.txt",
                 NOUGEN_MACHINE="kushboygroups-mac-mini-local", NOUGEN_AGENT="claude-cli")
    assert out.returncode != 0, "a second identity for one box must not land silently"
    assert "kushboygroups-mac-mini-local" in out.stderr
    assert "blade1tb" in out.stderr and "whoart" in out.stderr, "show what the fleet calls itself"
    assert any(hint in out.stderr for hint in ("NOUGEN_MACHINE", "relay init"))


def test_the_override_lets_a_genuinely_new_box_introduce_itself(repo):
    record(repo, "blade1tb")
    out = commit(repo, "a.txt", NOUGEN_MACHINE="phoebus", NOUGEN_AGENT="claude-cli",
                 NOUGEN_IDENTITY_OK="1")
    assert out.returncode == 0, out.stderr
    assert "Machine: phoebus" in last_message(repo)


def test_the_override_is_the_only_way_past_an_unset_agent(repo):
    out = commit(repo, "a.txt", NOUGEN_MACHINE="blade1tb", NOUGEN_IDENTITY_OK="1")
    assert out.returncode == 0, out.stderr
    assert "Agent: unknown-agent" in last_message(repo), (
        "an override still records the truth — it does not invent an identity"
    )


def test_a_rebase_does_not_reattribute_another_machines_commit(repo):
    """The measured failure. `git rebase` re-runs this hook on every replayed
    commit with the REBASING box's environment, and `--if-exists replace` used
    that to overwrite the author's own trailer — silently moving one machine's
    work onto another and losing the lane."""
    record(repo, "phoebus")
    record(repo, "blade1tb")
    assert commit(repo, "base.txt", NOUGEN_MACHINE="phoebus",
                  NOUGEN_AGENT="claude-cli").returncode == 0

    git("checkout", "-qb", "feat", cwd=repo)
    assert commit(repo, "feat.txt", NOUGEN_MACHINE="phoebus",
                  NOUGEN_AGENT="claude-cli").returncode == 0

    git("checkout", "-q", "main", cwd=repo)
    assert commit(repo, "main.txt", NOUGEN_MACHINE="blade1tb",
                  NOUGEN_AGENT="claude-cli").returncode == 0

    # The rebase runs on blade, in a shell that never exported phoebus's identity.
    git("checkout", "-q", "feat", cwd=repo)
    env = {k: v for k, v in os.environ.items() if not k.startswith("NOUGEN_")}
    env["NOUGEN_MACHINE"] = "blade1tb"
    rebase = git("rebase", "main", cwd=repo, env=env, check=False)
    assert rebase.returncode == 0, rebase.stderr

    message = last_message(repo)
    assert "Machine: phoebus" in message, "the rebasing box took the credit"
    assert "Agent: claude-cli" in message, "the lane was replaced by unknown-agent"


def test_a_replay_is_never_refused_partway(repo):
    """Refusing mid-rebase aborts it halfway, which is a worse failure than a
    wrong trailer — and there is nothing left to refuse, since the replayed
    commit keeps the identity it was written with."""
    record(repo, "phoebus")
    assert commit(repo, "base.txt", NOUGEN_MACHINE="phoebus",
                  NOUGEN_AGENT="claude-cli").returncode == 0
    git("checkout", "-qb", "feat", cwd=repo)
    assert commit(repo, "feat.txt", NOUGEN_MACHINE="phoebus",
                  NOUGEN_AGENT="claude-cli").returncode == 0
    git("checkout", "-q", "main", cwd=repo)
    assert commit(repo, "main.txt", NOUGEN_MACHINE="phoebus",
                  NOUGEN_AGENT="claude-cli").returncode == 0
    git("checkout", "-q", "feat", cwd=repo)

    # A stranger machine with no lane at all — the guard would refuse this if
    # it were a new commit.
    env = {k: v for k, v in os.environ.items() if not k.startswith("NOUGEN_")}
    env["NOUGEN_MACHINE"] = "a-box-nobody-knows"
    rebase = git("rebase", "main", cwd=repo, env=env, check=False)
    assert rebase.returncode == 0, f"the guard aborted a rebase: {rebase.stderr}"
    assert "Machine: phoebus" in last_message(repo)


@pytest.mark.skipif(sys.platform == "win32", reason="PATH shim needs a POSIX shell")
def test_a_probed_hostname_drops_its_network_suffix(repo, tmp_path):
    """Parity with core.resolve_machine(): `.local` says how the box is
    reachable, not which box it is, and the hook must not disagree with the
    tool about what this machine is called."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    (fake_bin / "hostname").write_text(
        "#!/bin/sh\necho KushBoyGroups-Mac-mini.local\n", encoding="utf-8")
    os.chmod(fake_bin / "hostname", 0o755)

    record(repo, "kushboygroups-mac-mini")
    out = commit(repo, "a.txt", NOUGEN_AGENT="claude-cli",
                 PATH=f"{fake_bin}{os.pathsep}{os.environ['PATH']}")
    assert out.returncode == 0, out.stderr
    assert "Machine: kushboygroups-mac-mini\n" in last_message(repo)


def test_an_explicit_name_is_passed_through_untouched(repo):
    """The other half of the same doctrine: a dotted name someone typed is
    their word on what the box is called, and the hook does not second-guess
    it any more than core.resolve_machine() does."""
    record(repo, "who-mac-mini-local")
    out = commit(repo, "a.txt", NOUGEN_MACHINE="Who-Mac-Mini.local",
                 NOUGEN_AGENT="claude-cli")
    assert out.returncode == 0, out.stderr
    assert "Machine: who-mac-mini-local\n" in last_message(repo)


def test_the_guard_follows_the_configured_registry_directory(repo):
    """The registry path is env-resolved, so the guard must resolve it too
    rather than assuming `.handoffs`."""
    directory = repo / "legs"
    directory.mkdir()
    (directory / "20260731T000000Z__blade1tb__claude-cli.md").write_text("x\n", encoding="utf-8")

    refused = commit(repo, "a.txt", NOUGEN_GIT_HANDOFF_DIR="legs",
                     NOUGEN_MACHINE="stranger", NOUGEN_AGENT="claude-cli")
    assert refused.returncode != 0, "the guard read the wrong directory"
    assert "blade1tb" in refused.stderr

    ok = commit(repo, "a.txt", NOUGEN_GIT_HANDOFF_DIR="legs",
                NOUGEN_MACHINE="blade1tb", NOUGEN_AGENT="claude-cli")
    assert ok.returncode == 0, ok.stderr
