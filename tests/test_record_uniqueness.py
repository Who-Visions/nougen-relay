"""Two records from one machine in the same second must not share a name.

Flagged by phoebus while porting the trigger layer: ids are second-granular.
The consequence is worse than a duplicate label — the second write lands on the
first one's filename and DESTROYS it, and if the first was already reacted to,
the survivor carries an id `react` has seen and never fires a rule for. A
registry that exists to stop lost work was losing it.

These force the collision instead of racing the clock: a test that only fails
when two subprocess spawns happen to land in the same second is not a
regression test.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from nougen_relay.core import unique_record_name

SRC = str(Path(__file__).resolve().parents[1] / "src")
STAMP = datetime(2026, 7, 31, 23, 30, 15, tzinfo=timezone.utc)
BASE = "20260731T233015Z__blade1tb__claude-cli"


def test_an_empty_directory_gives_the_plain_name(tmp_path):
    """Every id already in circulation keeps resolving — the counter appears
    only when it has to."""
    assert unique_record_name(tmp_path, STAMP, "blade1tb", "claude-cli") == BASE


def test_a_taken_name_gets_a_counter(tmp_path):
    (tmp_path / f"{BASE}.json").write_text("{}", encoding="utf-8")
    assert (unique_record_name(tmp_path, STAMP, "blade1tb", "claude-cli")
            == "20260731T233015Z-2__blade1tb__claude-cli")


def test_the_counter_keeps_climbing(tmp_path):
    (tmp_path / f"{BASE}.json").write_text("{}", encoding="utf-8")
    (tmp_path / "20260731T233015Z-2__blade1tb__claude-cli.json").write_text("{}", encoding="utf-8")
    assert (unique_record_name(tmp_path, STAMP, "blade1tb", "claude-cli")
            == "20260731T233015Z-3__blade1tb__claude-cli")


def test_a_markdown_body_alone_still_counts_as_taken(tmp_path):
    """Records are a .json/.md pair. Checking only one half would overwrite
    the other."""
    (tmp_path / f"{BASE}.md").write_text("x", encoding="utf-8")
    assert unique_record_name(tmp_path, STAMP, "blade1tb", "claude-cli") != BASE


def test_identity_segments_survive_disambiguation(tmp_path):
    """The counter goes inside the timestamp segment because the commit hook
    and the registry both parse identity back out of these filenames."""
    (tmp_path / f"{BASE}.json").write_text("{}", encoding="utf-8")
    name = unique_record_name(tmp_path, STAMP, "blade1tb", "claude-cli")
    _stamp, machine, agent = name.split("__")
    assert (machine, agent) == ("blade1tb", "claude-cli")


def test_another_machine_never_collides(tmp_path):
    """What already worked, and must keep working: same instant, different box,
    different name — that is why this registry merges without conflicts."""
    (tmp_path / f"{BASE}.json").write_text("{}", encoding="utf-8")
    assert (unique_record_name(tmp_path, STAMP, "phoebus", "claude-cli")
            == "20260731T233015Z__phoebus__claude-cli")


# --- end to end --------------------------------------------------------------

def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def relay(repo, *args, **env_extra):
    env = {**os.environ, "PYTHONPATH": SRC, "NOUGEN_AGENT": "claude-cli",
           "NOUGEN_MACHINE": "blade1tb", "PYTHONIOENCODING": "utf-8"}
    env.update({k: str(v) for k, v in env_extra.items()})
    return subprocess.run([sys.executable, "-m", "nougen_relay.cli", *args],
                          cwd=repo, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


@pytest.fixture()
def repo(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    git("init", "-q", "-b", "main", ".", cwd=work)
    git("config", "user.email", "t@example.com", cwd=work)
    git("config", "user.name", "t", cwd=work)
    (work / "f.txt").write_text("x\n", encoding="utf-8")
    git("add", ".", cwd=work)
    git("commit", "-qm", "init", cwd=work)
    return work


def occupy_the_next_few_seconds(directory, machine="blade1tb", agent="claude-cli"):
    """Claim every name the next write could want, so the collision is certain
    rather than a race the test might lose."""
    directory.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    taken = []
    for offset in range(6):
        stamp = now.replace(microsecond=0).timestamp() + offset
        name = datetime.fromtimestamp(stamp, timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = directory / f"{name}__{machine}__{agent}.json"
        path.write_text(json.dumps({"id": path.stem, "machine": machine}), encoding="utf-8")
        taken.append(path)
    return taken


def test_a_leg_never_lands_on_an_existing_record(repo):
    taken = occupy_the_next_few_seconds(repo / ".handoffs")
    before = {p: p.read_text(encoding="utf-8") for p in taken}

    out = relay(repo, "create", "-g", "the new leg", "-m", "body")
    assert out.returncode == 0, out.stdout + out.stderr

    for path, content in before.items():
        assert path.read_text(encoding="utf-8") == content, f"{path.name} was overwritten"

    written = [p for p in (repo / ".handoffs").glob("*.json") if p not in before]
    assert len(written) == 1, f"expected exactly one new record, got {written}"
    record = json.loads(written[0].read_text(encoding="utf-8"))
    assert record["id"] == written[0].stem, "the embedded id drifted from the filename"
    assert record["goal"] == "the new leg"
    assert (written[0].with_suffix(".md")).exists(), "the markdown body lost its pair"


def test_a_claim_never_lands_on_an_existing_claim(repo):
    taken = occupy_the_next_few_seconds(repo / ".handoffs" / "claims")
    before = {p: p.read_text(encoding="utf-8") for p in taken}

    out = relay(repo, "claim", "take", "-s", "src/lib", "-g", "work",
                "--no-push", "--no-fetch")
    assert out.returncode == 0, out.stdout + out.stderr

    for path, content in before.items():
        assert path.read_text(encoding="utf-8") == content, f"{path.name} was overwritten"
    written = [p for p in (repo / ".handoffs" / "claims").glob("*.json") if p not in before]
    assert len(written) == 1, f"expected exactly one new claim, got {written}"
