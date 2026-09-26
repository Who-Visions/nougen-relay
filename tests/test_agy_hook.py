"""The Antigravity PreToolUse guard.

This is the only piece of the system that can actually STOP a lane, so its
failure modes matter more than its success path: a guard that blocks wrongly
gets ripped out, and a guard that silently allows everything is worse than none
because it looks like protection.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SRC = str(Path(__file__).resolve().parents[1] / "src")


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   text=True, encoding="utf-8", errors="replace")


def decide(payload, machine="boxa"):
    env = {**os.environ, "PYTHONPATH": SRC, "NOUGEN_MACHINE": machine,
           "NOUGEN_AGENT": "lane1", "PYTHONIOENCODING": "utf-8"}
    out = subprocess.run([sys.executable, "-m", "nougen_relay.agy_hook"],
                         input=json.dumps(payload) if isinstance(payload, dict) else payload,
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace", env=env)
    assert out.returncode == 0, f"hook must always exit 0: {out.stderr}"
    return json.loads(out.stdout)


@pytest.fixture()
def repo(tmp_path):
    git("init", "-q", ".", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "t", cwd=tmp_path)
    (tmp_path / "f.txt").write_text("x\n", encoding="utf-8")
    git("add", ".", cwd=tmp_path)
    git("commit", "-qm", "init", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "lib.py").write_text("x\n", encoding="utf-8")
    return tmp_path


def claim(repo, scope, goal, machine):
    env = {**os.environ, "PYTHONPATH": SRC, "NOUGEN_MACHINE": machine,
           "NOUGEN_AGENT": "lane1", "PYTHONIOENCODING": "utf-8"}
    subprocess.run([sys.executable, "-m", "nougen_relay.cli", "claim", "take",
                    "-s", scope, "-g", goal], cwd=repo, env=env,
                   capture_output=True, text=True, encoding="utf-8")


def edit(repo, rel):
    return {"toolCall": {"name": "write_to_file",
                         "args": {"TargetFile": str(Path(repo) / rel)}},
            "workspacePaths": [str(repo)]}


# --- it must actually block ------------------------------------------------

def test_another_machines_claim_blocks_the_edit(repo):
    claim(repo, "src/lib.py", "refactor", machine="boxb")
    out = decide(edit(repo, "src/lib.py"), machine="boxa")
    assert out["decision"] == "deny"
    assert "boxb" in out["reason"], "the reason must name who holds it"


def test_a_directory_claim_blocks_a_file_inside_it(repo):
    claim(repo, "src", "working the whole dir", machine="boxb")
    assert decide(edit(repo, "src/lib.py"), machine="boxa")["decision"] == "deny"


def test_windows_separators_do_not_defeat_the_match(repo):
    """Claims are written with forward slashes and Windows hands the hook
    backslashes. Unnormalised, the tokens never match and the guard gates
    nothing while appearing to work."""
    claim(repo, "src/lib.py", "mine", machine="boxb")
    payload = {"toolCall": {"name": "write_to_file",
                            "args": {"TargetFile": str(Path(repo) / "src" / "lib.py")}},
               "workspacePaths": [str(repo)]}
    assert decide(payload, machine="boxa")["decision"] == "deny"


# --- it must not block the wrong things ------------------------------------

def test_your_own_claim_lets_you_through(repo):
    claim(repo, "src/lib.py", "mine", machine="boxa")
    assert decide(edit(repo, "src/lib.py"), machine="boxa")["decision"] == "allow"


def test_an_unclaimed_edit_asks_rather_than_denies(repo):
    """A nudge, not a wall. Denying unclaimed work trains the operator to
    remove the hook, and a removed hook protects nothing.

    The registry directory has to exist for the repo to count as coordinated —
    a repo nobody shares is deliberately not gated at all.
    """
    (repo / ".handoffs").mkdir(exist_ok=True)
    out = decide(edit(repo, "src/lib.py"), machine="boxa")
    assert out["decision"] == "ask"
    assert "relay_claim_take" in out["reason"]


def test_an_unrelated_claim_does_not_block(repo):
    claim(repo, "docs/README.md", "docs", machine="boxb")
    assert decide(edit(repo, "src/lib.py"), machine="boxa")["decision"] == "ask"


def test_read_only_tools_are_none_of_its_business(repo):
    payload = {"toolCall": {"name": "view_file",
                            "args": {"AbsolutePath": str(repo / "src" / "lib.py")}},
               "workspacePaths": [str(repo)]}
    assert decide(payload)["decision"] == "allow"


# --- it must fail open ------------------------------------------------------

def test_unparseable_input_allows(repo):
    assert decide("not json at all")["decision"] == "allow"


def test_a_repo_with_no_registry_is_not_gated(tmp_path):
    git("init", "-q", ".", cwd=tmp_path)
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    payload = {"toolCall": {"name": "write_to_file",
                            "args": {"TargetFile": str(tmp_path / "a.txt")}},
               "workspacePaths": [str(tmp_path)]}
    assert decide(payload)["decision"] == "allow"


def test_a_missing_target_does_not_crash_the_session(repo):
    payload = {"toolCall": {"name": "write_to_file", "args": {}},
               "workspacePaths": [str(repo)]}
    assert decide(payload)["decision"] in {"allow", "ask"}
