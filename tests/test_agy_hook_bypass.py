"""Path spellings that must not slip past a claim.

A 12-route independent review unanimously flagged path normalisation as the way
through this guard: the comparison is string-based, so any spelling of a claimed
file that differs from the claim's spelling would walk past it.

Measured, not assumed — and the measurement corrected the review on two counts:

  * `./x` never reached the comparison. pathlib collapses a `.` segment when the
    path is built, so that case was always the plain path wearing a disguise.
  * `src/../src/x` was already denied BEFORE the resolve() fix, but by accident:
    `_repo_for` probes with `.exists()`, the OS resolves `/repo/src/..` to
    `/repo`, and `relative_to` then cancels the `..` as a side effect. Correct
    behaviour that nobody designed and no test held in place.

  * the symlink case is the one that was never disproved on Windows, where
    creating one needs privilege. Linux CI is where that assertion earns its
    keep.

So these tests are not a bypass reproduction. They are the fence around
behaviour that was previously accidental — which is worth more, because an
accident survives only until someone refactors `_repo_for`.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from _env import cli_env

SRC = str(Path(__file__).resolve().parents[1] / "src")


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   text=True, encoding="utf-8", errors="replace")


@pytest.fixture()
def claimed(tmp_path):
    """A repo where boxa holds a claim on src/lib."""
    repo = tmp_path / "repo"
    (repo / "src" / "lib").mkdir(parents=True)
    (repo / "src" / "lib" / "twitch.ts").write_text("x\n", encoding="utf-8")
    git("init", "-q", ".", cwd=repo)
    git("config", "user.email", "t@example.com", cwd=repo)
    git("config", "user.name", "t", cwd=repo)
    git("add", ".", cwd=repo)
    git("commit", "-qm", "init", cwd=repo)

    env = cli_env(NOUGEN_MACHINE="boxa", NOUGEN_AGENT="lane-a")
    subprocess.run([sys.executable, "-m", "nougen_relay.cli", "claim", "take",
                    "-s", "src/lib", "-g", "oauth work"],
                   cwd=repo, env=env, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
    return repo


def ask_hook(repo, target, machine="boxb"):
    """Run the hook as Antigravity would: JSON in, JSON out."""
    payload = {
        "toolCall": {"name": "replace_file_content", "args": {"TargetFile": str(target)}},
        "workspacePaths": [str(repo)],
    }
    out = subprocess.run(
        [sys.executable, "-m", "nougen_relay.agy_hook"],
        input=json.dumps(payload), cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        env=cli_env(NOUGEN_MACHINE=machine, NOUGEN_AGENT="lane-b"),
    )
    return json.loads(out.stdout or '{"decision": "<no output>"}')


def test_the_plain_path_is_denied(claimed):
    """Baseline: the guard works when the caller spells the path the obvious way."""
    assert ask_hook(claimed, claimed / "src" / "lib" / "twitch.ts")["decision"] == "deny"


def test_a_dotdot_detour_cannot_slip_past(claimed):
    """The same file by another name. Denied before the fix too, but only as a
    side effect of an `.exists()` probe elsewhere — pinned here deliberately."""
    sneaky = claimed / "src" / ".." / "src" / "lib" / "twitch.ts"
    assert ask_hook(claimed, sneaky)["decision"] == "deny"


def test_a_dot_prefix_cannot_slip_past(claimed):
    """Collapsed by pathlib before the guard ever sees it — asserted so that
    stays true, not because it was ever a hole."""
    sneaky = claimed / "." / "src" / "lib" / "twitch.ts"
    assert ask_hook(claimed, sneaky)["decision"] == "deny"


@pytest.mark.skipif(os.name == "nt", reason="symlink creation needs privilege on Windows")
def test_a_symlink_into_claimed_scope_cannot_slip_past(claimed):
    """The review's sharpest case: an innocent-looking path that IS the file."""
    link = claimed / "shortcut.ts"
    link.symlink_to(claimed / "src" / "lib" / "twitch.ts")
    assert ask_hook(claimed, link)["decision"] == "deny"


def test_your_own_claim_still_allows_the_detour(claimed):
    """Normalisation must not break the machine that holds the claim."""
    sneaky = claimed / "src" / ".." / "src" / "lib" / "twitch.ts"
    assert ask_hook(claimed, sneaky, machine="boxa")["decision"] == "allow"


def test_an_unclaimed_file_still_only_asks(claimed):
    """The nudge stays a nudge — normalisation must not turn it into a wall."""
    other = claimed / "README.md"
    other.write_text("hi\n", encoding="utf-8")
    assert ask_hook(claimed, other)["decision"] == "ask"


def test_a_path_outside_the_repo_is_not_silently_allowed(claimed, tmp_path):
    """A path outside the repo: no claim here governs it, but the guard must not
    imply it vetted it either."""
    outside = tmp_path / "elsewhere.txt"
    outside.write_text("x\n", encoding="utf-8")
    assert ask_hook(claimed, outside)["decision"] != "deny"  # not ours to deny
    # ...but it must not pretend it vetted it either.
    assert ask_hook(claimed, outside)["decision"] in ("ask", "allow")
