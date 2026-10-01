"""Two machines, one bare remote — the contract as it actually runs.

Everything here goes through a real git remote, because that is the transport.
A leg only exists for another machine once it is published, and `relay open`
reads the remote for exactly that reason.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from nougen_relay import core
from _env import cli_env

SRC = str(Path(__file__).resolve().parents[1] / "src")


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def relay(repo, *args, machine, agent="claude-cli"):
    env = cli_env(NOUGEN_MACHINE=machine, NOUGEN_AGENT=agent)
    return subprocess.run([sys.executable, "-m", "nougen_relay.cli", *args],
                          cwd=repo, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


@pytest.fixture()
def fleet(tmp_path):
    """A bare 'origin' plus two working copies standing in for two machines."""
    bare = tmp_path / "origin.git"
    git("init", "-q", "--bare", "-b", "main", str(bare), cwd=tmp_path)

    seed = tmp_path / "seed"
    git("clone", "-q", str(bare), str(seed), cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=seed)
    git("config", "user.name", "t", cwd=seed)
    (seed / "f.txt").write_text("x\n", encoding="utf-8")
    git("add", ".", cwd=seed)
    git("commit", "-qm", "init", cwd=seed)
    git("push", "-q", "origin", "main", cwd=seed)

    boxa, boxb = tmp_path / "boxa", tmp_path / "boxb"
    for path in (boxa, boxb):
        git("clone", "-q", str(bare), str(path), cwd=tmp_path)
        git("config", "user.email", "t@example.com", cwd=path)
        git("config", "user.name", "t", cwd=path)
    return boxa, boxb


def legs(repo):
    return sorted((repo / ".handoffs").glob("*.json"))


def publish(repo, message="handoff"):
    """Push whatever the CLI left uncommitted.

    `claim` and `ack` publish themselves; `create` deliberately does not, so
    this is a no-op in the first case and the actual publish in the second.
    """
    subprocess.run(["git", "add", ".handoffs"], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-qm", message], cwd=repo, capture_output=True)
    subprocess.run(["git", "push", "-q", "origin", "HEAD"], cwd=repo,
                   capture_output=True)


def test_a_published_leg_is_visible_to_the_other_machine(fleet):
    boxa, boxb = fleet
    assert relay(boxa, "create", "-g", "wire the sidecar", "-m", "stubbed",
                 machine="boxa").returncode == 0
    publish(boxa)

    out = relay(boxb, "relay", "open", machine="boxb")
    assert "boxa" in out.stdout
    assert out.returncode != 0, "an unacked leg must be detectable by exit code"


def test_a_delayed_publish_is_delivered_on_the_receivers_next_poll(fleet):
    """A locally written leg remains recoverable while publication is delayed."""
    boxa, boxb = fleet
    goal = "recover a delayed relay after the publisher reconnects"
    assert relay(boxa, "create", "-g", goal, "-m", "queued locally",
                 machine="boxa").returncode == 0

    before = relay(boxb, "open", machine="boxb")
    assert before.returncode == 0
    assert goal not in before.stdout

    publish(boxa, "publish after temporary loss")
    after = relay(boxb, "open", machine="boxb")
    assert after.returncode != 0
    assert goal in after.stdout


def test_malformed_record_does_not_hide_a_legacy_schema_neighbor(fleet):
    """The receiver skips a truncated packet and still decodes older records."""
    boxa, boxb = fleet
    handoffs = boxa / ".handoffs"
    handoffs.mkdir(exist_ok=True)
    (handoffs / "20260828T000001Z__boxa__broken.json").write_text(
        '{"id":"20260828T000001Z__boxa__broken","status":"open"',
        encoding="utf-8",
    )
    legacy_id = "20260828T000002Z__boxa__legacy"
    legacy = {
        "schema_version": 1,
        "machine": "boxa",
        "agent": "lane1",
        "goal": "legacy payload without embedded id or status",
        "created_utc": "2026-08-28T00:00:02Z",
        "future_extension": {"trace": "kept"},
    }
    (handoffs / f"{legacy_id}.json").write_text(json.dumps(legacy), encoding="utf-8")
    publish(boxa, "publish mixed schema records")
    git("fetch", "-q", "origin", cwd=boxb)

    records = core._remote_handoffs(boxb, "origin/main")
    assert [record["_file"] for record in records] == [f"{legacy_id}.json"]
    assert core.record_id(records[0]) == legacy_id
    assert core.relay_status(records[0]) == "open"
    assert records[0]["future_extension"] == {"trace": "kept"}


def test_your_own_leg_is_not_a_leg_you_need_to_take(fleet):
    """`relay open` answers 'what is waiting for me', not 'what exists'."""
    boxa, _ = fleet
    relay(boxa, "create", "-g", "g", "-m", "m", machine="boxa")
    publish(boxa)
    out = relay(boxa, "relay", "open", machine="boxa")
    assert out.returncode == 0


def test_remote_handoffs_are_read_in_one_git_batch(fleet, monkeypatch):
    boxa, boxb = fleet
    directory = boxa / ".handoffs"
    directory.mkdir()
    for index in range(40):
        record = {
            "machine": "boxa",
            "agent": "lane1",
            "goal": f"batch-{index:02d}",
            "status": "open",
            "created_utc": f"2026-01-01T00:00:{index:02d}+00:00",
        }
        (directory / f"leg-{index:02d}.json").write_text(
            json.dumps(record), encoding="utf-8"
        )
    claims = directory / "claims"
    claims.mkdir()
    (claims / "nested.json").write_text("{}", encoding="utf-8")
    publish(boxa, "batch handoffs")
    git("fetch", "-q", "origin", cwd=boxb)

    calls = []
    real_run = core.subprocess.run

    def tracking_run(command, *args, **kwargs):
        if command[:2] == ["git", "show"]:
            raise AssertionError("remote JSON reads must not spawn git show per file")
        if command[:2] == ["git", "archive"]:
            calls.append(command)
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(core.subprocess, "run", tracking_run)
    records = core._remote_handoffs(boxb, "origin/main")

    assert len(records) == 40
    assert records[0]["_file"] == "leg-00.json"
    assert records[-1]["_file"] == "leg-39.json"
    assert len(calls) == 1


def test_the_ack_travels_back_to_the_originator(fleet):
    """The whole point of the third verb: boxa can tell the baton was taken."""
    boxa, boxb = fleet
    relay(boxa, "create", "-g", "g", "-m", "m", machine="boxa")
    publish(boxa)

    git("pull", "-q", "--rebase", "origin", "main", cwd=boxb)
    leg = legs(boxb)[0].stem
    assert relay(boxb, "relay", "ack", "--id", leg, "-m", "picking this up",
                 machine="boxb").returncode == 0
    publish(boxb, "ack")

    git("pull", "-q", "--rebase", "origin", "main", cwd=boxa)
    rec = json.loads(legs(boxa)[0].read_text(encoding="utf-8"))
    assert rec["status"] == "acked"
    assert any(e.get("machine") == "boxb" for e in rec.get("relay", []))

    assert relay(boxa, "relay", "open", machine="boxa").returncode == 0


def test_an_acked_leg_stops_waiting_for_everyone(fleet):
    boxa, boxb = fleet
    relay(boxa, "create", "-g", "g", "-m", "m", machine="boxa")
    publish(boxa)
    git("pull", "-q", "--rebase", "origin", "main", cwd=boxb)
    relay(boxb, "relay", "ack", "--id", legs(boxb)[0].stem, "-m", "mine",
          machine="boxb")
    publish(boxb, "ack")

    out = relay(boxb, "relay", "open", machine="boxb")
    assert out.returncode == 0


def test_both_machines_writing_at_once_merge_without_conflict(fleet):
    """Concurrent legs are the normal case, not the edge case: one file per
    leg, named by machine, so git never has to reconcile a shared index."""
    boxa, boxb = fleet
    relay(boxa, "create", "-g", "a-side", "-m", "a", machine="boxa")
    relay(boxb, "create", "-g", "b-side", "-m", "b", machine="boxb")

    publish(boxa)
    git("add", ".handoffs", cwd=boxb)
    git("commit", "-qm", "handoff", cwd=boxb)
    git("pull", "-q", "--rebase", "origin", "main", cwd=boxb)  # must not conflict
    git("push", "-q", "origin", "HEAD", cwd=boxb)

    git("pull", "-q", "--rebase", "origin", "main", cwd=boxa)
    goals = {json.loads(p.read_text(encoding="utf-8"))["goal"] for p in legs(boxa)}
    assert goals == {"a-side", "b-side"}


def test_a_claim_blocks_an_overlapping_claim_from_the_other_machine(fleet):
    """The half of the protocol that runs before work starts."""
    boxa, boxb = fleet
    assert relay(boxa, "claim", "take", "-s", "src/lib/twitch.ts",
                 "-g", "oauth", machine="boxa").returncode == 0
    publish(boxa, "claim")

    blocked = relay(boxb, "claim", "take", "-s", "src/lib/twitch.ts",
                    "-g", "same file", machine="boxb")
    assert blocked.returncode != 0
    assert "boxa" in (blocked.stdout + blocked.stderr)


def test_a_claim_does_not_block_unrelated_work(fleet):
    boxa, boxb = fleet
    relay(boxa, "claim", "take", "-s", "src/lib/twitch.ts", "-g", "oauth",
          machine="boxa")
    publish(boxa, "claim")

    ok = relay(boxb, "claim", "take", "-s", "docs/RELAY.md", "-g", "docs",
               machine="boxb")
    assert ok.returncode == 0


def test_releasing_a_claim_frees_the_scope(fleet):
    boxa, boxb = fleet
    relay(boxa, "claim", "take", "-s", "src/lib", "-g", "work", machine="boxa")
    publish(boxa, "claim")
    relay(boxa, "claim", "release", "-s", "src/lib", machine="boxa")
    publish(boxa, "release")

    ok = relay(boxb, "claim", "take", "-s", "src/lib", "-g", "my turn",
               machine="boxb")
    assert ok.returncode == 0
