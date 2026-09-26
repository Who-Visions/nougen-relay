"""The baton, end to end, against a real git repo.

This is the contract other machines rely on: a leg is `open` until somebody
takes it, every event appends to a trail instead of overwriting, and two
machines writing at once never collide on a filename.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from _env import cli_env

SRC = str(Path(__file__).resolve().parents[1] / "src")


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


def load_one(repo):
    paths = records(repo)
    assert len(paths) == 1, [p.name for p in paths]
    return json.loads(paths[0].read_text(encoding="utf-8"))


def leg_id(repo):
    """A leg is identified by its filename stem; records carry no id field."""
    paths = records(repo)
    assert len(paths) == 1, [p.name for p in paths]
    return paths[0].stem


def test_a_new_leg_starts_open(repo):
    """Nobody has taken the baton yet, and the record must say so."""
    assert relay(repo, "create", "-g", "wire the sidecar", "-m", "stubbed").returncode == 0
    rec = load_one(repo)
    assert rec["status"] == "open"
    assert rec["machine"] == "boxa"
    assert rec["agent"] == "lane1"
    assert rec["goal"] == "wire the sidecar"


def test_a_leg_is_written_as_json_plus_a_readable_twin(repo):
    relay(repo, "create", "-g", "goal", "-m", "body")
    stems = {p.stem for p in (repo / ".handoffs").glob("*")}
    assert len(stems) == 1
    stem = stems.pop()
    assert (repo / ".handoffs" / f"{stem}.json").is_file()
    assert (repo / ".handoffs" / f"{stem}.md").is_file()


def test_the_record_names_the_machine_and_agent_that_wrote_it(repo):
    """Filenames carry identity so two machines never write the same path."""
    relay(repo, "create", "-g", "g", "-m", "m", machine="phoebus", agent="claude-cli")
    name = records(repo)[0].name
    assert "phoebus" in name and "claude-cli" in name


def test_concurrent_legs_from_two_machines_do_not_collide(repo):
    """The reason there is no shared index file: an index conflicts on every
    concurrent write, which is exactly when coordination matters most."""
    relay(repo, "create", "-g", "a", "-m", "a", machine="boxa", agent="lane1")
    relay(repo, "create", "-g", "b", "-m", "b", machine="boxb", agent="lane2")
    assert len(records(repo)) == 2


def test_acking_takes_the_baton_and_names_the_taker(repo):
    relay(repo, "create", "-g", "g", "-m", "m", machine="boxa", agent="lane1")
    leg = leg_id(repo)
    relay(repo, "relay", "ack", "--id", leg, "-m", "picking this up",
          machine="boxb", agent="lane2")
    rec = load_one(repo)
    assert rec["status"] == "acked"
    assert "boxb" in json.dumps(rec)


def test_completing_closes_the_leg(repo):
    relay(repo, "create", "-g", "g", "-m", "m")
    leg = leg_id(repo)
    relay(repo, "relay", "ack", "--id", leg, "-m", "mine", machine="boxb", agent="lane2")
    relay(repo, "relay", "complete", "--id", leg, "-m", "done", machine="boxb", agent="lane2")
    assert load_one(repo)["status"] == "complete"


def test_every_event_appends_rather_than_overwrites(repo):
    """A leg's history has to survive completion — otherwise 'what happened'
    is only answerable while the work is still in flight."""
    relay(repo, "create", "-g", "g", "-m", "m")
    leg = leg_id(repo)
    relay(repo, "relay", "ack", "--id", leg, "-m", "taking it", machine="boxb", agent="lane2")
    relay(repo, "relay", "checkpoint", "--id", leg, "--state", "blocked",
          "-m", "waiting on a key", machine="boxb", agent="lane2")
    relay(repo, "relay", "complete", "--id", leg, "-m", "unblocked and done",
          machine="boxb", agent="lane2")

    trail = json.dumps(load_one(repo))
    for moment in ("taking it", "waiting on a key", "unblocked and done"):
        assert moment in trail, moment


# `relay open` reads the REMOTE, not the working copy — a leg only exists for
# another machine once it is published. Those cases live in test_two_machines.py,
# where there is a real remote to publish to.


def test_writing_a_record_never_needs_a_remote(repo):
    """A record must survive an offline machine. Publishing is best-effort;
    losing the handoff because the network was down is not acceptable."""
    out = relay(repo, "create", "-g", "offline", "-m", "no remote here")
    assert out.returncode == 0
    assert load_one(repo)["goal"] == "offline"
