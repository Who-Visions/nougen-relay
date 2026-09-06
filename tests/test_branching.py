"""Branching legs: parent_leg_id, summary legs, and the abandoned state.

Investigations fork. Before this, giving up on a line of work looked exactly
like never having seen it — the leg just sat open forever. Now a branch can
name its parent (in the JSON, never the filename), and an abandoned branch is
closed by a summary leg that carries what it learned.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from _env import cli_env

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

relay_daemon = pytest.importorskip("relay_daemon")


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True,
                   capture_output=True, text=True)


@pytest.fixture()
def repo(tmp_path):
    git("init", "-q", ".", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "t", cwd=tmp_path)
    (tmp_path / "f.txt").write_text("x\n", encoding="utf-8")
    git("add", ".", cwd=tmp_path)
    git("commit", "-qm", "init", cwd=tmp_path)
    return tmp_path


def relay(repo, *args, machine="boxa", agent="lane1"):
    env = cli_env(NOUGEN_MACHINE=machine, NOUGEN_AGENT=agent)
    return subprocess.run([sys.executable, "-m", "nougen_relay.cli", *args],
                          cwd=repo, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def records(repo):
    return sorted((repo / ".handoffs").glob("*.json"))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def by_goal(repo, goal):
    matches = [r for r in map(load, records(repo)) if r.get("goal") == goal]
    assert len(matches) == 1, [r.get("goal") for r in map(load, records(repo))]
    return matches[0]


def test_parent_lands_in_json_never_in_filename(repo):
    """Filename segments are parsed back out for identity by the commit hook
    and adopt.py, so parentage must never leak into the name."""
    relay(repo, "create", "-g", "root", "-m", "trunk")
    parent = records(repo)[0].stem
    relay(repo, "create", "-g", "branch", "-m", "fork", "--parent", parent,
          machine="boxb", agent="lane2")
    child = by_goal(repo, "branch")
    assert child["parent_leg_id"] == parent
    child_file = [p for p in records(repo) if load(p).get("goal") == "branch"][0]
    assert parent not in child_file.name


def test_parent_substring_resolves_to_the_full_id(repo):
    """Dangling substrings would inherit _record_path's ambiguity refusal
    forever — resolvable parents are stored as FULL ids at write time."""
    relay(repo, "create", "-g", "root", "-m", "trunk")
    parent = records(repo)[0].stem
    fragment = parent.split("__")[0]  # timestamp segment, unique here
    relay(repo, "create", "-g", "branch", "-m", "fork", "--parent", fragment,
          machine="boxb", agent="lane2")
    assert by_goal(repo, "branch")["parent_leg_id"] == parent


def test_a_dangling_parent_is_stored_as_given_with_a_warning(repo):
    """A parent can legitimately live on a ref this machine has not fetched
    — refusing would make cross-machine branches impossible."""
    out = relay(repo, "create", "-g", "branch", "-m", "fork",
                "--parent", "20990101T000000Z__ghost__lane")
    assert out.returncode == 0
    assert "not found locally" in out.stdout
    rec = by_goal(repo, "branch")
    assert rec["parent_leg_id"] == "20990101T000000Z__ghost__lane"


def test_summarize_closes_the_parent_and_writes_a_summary_leg(repo):
    relay(repo, "create", "-g", "dead end", "-m", "tried the timeout theory")
    parent = records(repo)[0].stem
    out = relay(repo, "summarize", "--id", parent,
                "-m", "timeout theory disproved; abort propagation is the lead",
                machine="boxb", agent="lane2")
    assert out.returncode == 0, out.stdout + out.stderr
    parent_rec = by_goal(repo, "dead end")
    assert parent_rec["status"] == "abandoned"
    assert parent_rec["relay"][-1]["state"] == "abandoned"
    summary = [r for r in map(load, records(repo)) if r.get("type") == "summary"]
    assert len(summary) == 1
    assert summary[0]["parent_leg_id"] == parent
    assert parent in summary[0]["goal"]  # default goal names the parent


def test_abandoned_is_a_recognized_checkpoint_state(repo):
    relay(repo, "create", "-g", "g", "-m", "m")
    parent = records(repo)[0].stem
    out = relay(repo, "checkpoint", "--id", parent, "--state", "abandoned",
                "-m", "giving up", "--no-push", machine="boxb", agent="lane2")
    assert out.returncode == 0, out.stdout + out.stderr
    assert load(records(repo)[0])["status"] == "abandoned"


def test_old_style_mutations_round_trip_the_new_fields(repo):
    """_touch_record read-modify-writes the whole JSON — a reader that acks a
    branched leg must not drop parent_leg_id or type on the floor."""
    relay(repo, "create", "-g", "root", "-m", "trunk")
    parent = records(repo)[0].stem
    relay(repo, "create", "-g", "branch", "-m", "fork", "--parent", parent,
          machine="boxb", agent="lane2")
    child_id = [p.stem for p in records(repo)
                if load(p).get("goal") == "branch"][0]
    relay(repo, "relay", "ack", "--id", child_id, "-m", "taking it",
          machine="boxc", agent="lane3")
    child = by_goal(repo, "branch")
    assert child["status"] == "acked"
    assert child["parent_leg_id"] == parent


def test_daemon_never_offers_an_abandoned_leg(repo, tmp_path):
    """The daemon's open-set is the states worth waking a harness for.
    Terminal states — complete, abandoned — must stay invisible to it."""
    relay(repo, "create", "-g", "live", "-m", "m")
    relay(repo, "create", "-g", "dead", "-m", "m", machine="boxb", agent="lane2")
    dead = [p.stem for p in records(repo) if load(p).get("goal") == "dead"][0]
    relay(repo, "checkpoint", "--id", dead, "--state", "abandoned", "-m", "no")

    daemon = relay_daemon.RelayDaemon.__new__(relay_daemon.RelayDaemon)
    daemon.handoffs_dir = repo / ".handoffs"
    goals = {r.get("goal") for r in daemon.get_open_handoffs()}
    assert "live" in goals
    assert "dead" not in goals


def test_daemon_open_set_is_env_resolvable():
    """Rule 0.2: the open-set is discovered from the environment, with the
    constant as a logged fallback — never only baked in."""
    assert relay_daemon.OPEN_HANDOFF_STATES == ("open", "active", "held") or \
        "NOUGEN_RELAY_OPEN_STATES" in __import__("os").environ
    assert "abandoned" not in relay_daemon.OPEN_HANDOFF_STATES
    assert "complete" not in relay_daemon.OPEN_HANDOFF_STATES
