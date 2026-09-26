"""Tests for relay create CLI semantic deduplication (arXiv 2608.26225 - Agent Mesh).

Validates:
1. Exact duplicate idempotent return: no second leg written, exits 0, prints existing leg ID.
2. Near duplicate: writes second leg, prints warning naming similar leg ID(s), records similar_to in JSON.
3. Embed lane down passthrough: advisory dedup skips with log, create succeeds, never write-blocking.
4. Env thresholds override: NOUGEN_DEDUP_EXACT, NOUGEN_DEDUP_NEAR, NOUGEN_EMBED_URL.
5. Distinct goals: clean creation without similar_to field.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from _env import cli_env
from nougen_relay import cli

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


def relay(repo, *args, machine="boxa", agent="lane1", **extra_env):
    env = cli_env(NOUGEN_MACHINE=machine, NOUGEN_AGENT=agent, **extra_env)
    return subprocess.run([sys.executable, "-m", "nougen_relay.cli", *args],
                          cwd=repo, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def records(repo):
    return sorted((repo / ".handoffs").glob("*.json"))


def load_record(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_exact_dupe_idempotent_return(repo):
    """An exact duplicate must not write a second leg; it must print the existing leg id and exit 0."""
    goal = "Build autonomous completion reconciliation for the relay"
    r1 = relay(repo, "create", "-g", goal, "-m", "original leg")
    assert r1.returncode == 0, r1.stderr
    recs = records(repo)
    assert len(recs) == 1
    existing_id = recs[0].stem

    # Attempt to create an exact duplicate
    r2 = relay(repo, "create", "-g", goal, "-m", "duplicate attempt")
    assert r2.returncode == 0, r2.stderr
    assert existing_id in r2.stdout
    assert "duplicate leg already exists" in r2.stdout

    # Verify no second leg file was created
    recs2 = records(repo)
    assert len(recs2) == 1
    assert recs2[0].stem == existing_id


def test_near_dupe_warning_and_similar_to_field(repo):
    """A near duplicate must write the leg, print a warning, and record similar_to in JSON."""
    g1 = "Add temporal provenance evidence model to shards for Griot chronology"
    g2 = "Add full temporal provenance to shards so Griot can reconstruct chronology"

    r1 = relay(repo, "create", "-g", g1, "-m", "first leg")
    assert r1.returncode == 0, r1.stderr
    recs1 = records(repo)
    assert len(recs1) == 1
    first_id = recs1[0].stem

    # Second leg is a near duplicate
    r2 = relay(repo, "create", "-g", g2, "-m", "second leg")
    assert r2.returncode == 0, r2.stderr
    assert "⚠️ near duplicate open leg(s) detected:" in r2.stdout
    assert first_id in r2.stdout

    recs2 = records(repo)
    assert len(recs2) == 2

    # Second leg should contain similar_to with first_id
    second_rec = next(load_record(path) for path in recs2 if path.stem != first_id)
    assert "similar_to" in second_rec
    assert first_id in second_rec["similar_to"]


def test_embed_lane_down_passthrough(repo):
    """When the embed lane is unreachable, create must SUCCEED with a logged skip or token-overlap mode."""
    goal = "Fix the keymaker cross-tenant vault write escape"
    unreachable_url = "http://127.0.0.1:9"  # port 9 discard, immediately unreachable/refused

    r1 = relay(repo, "create", "-g", goal, "-m", "first", NOUGEN_EMBED_URL=unreachable_url)
    assert r1.returncode == 0, r1.stderr
    assert ("ℹ️ dedup check skipped: embed lane unreachable" in r1.stdout or
            "⚠️ dedup ran in token-overlap mode" in r1.stdout)
    assert len(records(repo)) == 1

    # Second write with distinct goal while embed lane is down must still succeed (passthrough)
    goal2 = "Add temporal provenance evidence model to shards for Griot chronology"
    r2 = relay(repo, "create", "-g", goal2, "-m", "second", NOUGEN_EMBED_URL=unreachable_url)
    assert r2.returncode == 0, r2.stderr
    assert ("ℹ️ dedup check skipped: embed lane unreachable" in r2.stdout or
            "⚠️ dedup ran in token-overlap mode" in r2.stdout)
    assert len(records(repo)) == 2


def test_thresholds_env_override(repo):
    """NOUGEN_DEDUP_EXACT and NOUDUP_NEAR override defaults dynamically."""
    g1 = "Add temporal provenance evidence model to shards for Griot chronology"
    g2 = "Add full temporal provenance to shards so Griot can reconstruct chronology"

    r1 = relay(repo, "create", "-g", g1, "-m", "first leg")
    assert r1.returncode == 0, r1.stderr
    first_id = records(repo)[0].stem

    # Lower exact threshold so g2 qualifies as an EXACT duplicate (embedding ~0.937, token-overlap ~0.873)
    r2 = relay(repo, "create", "-g", g2, "-m", "attempt with lower threshold",
               NOUGEN_DEDUP_EXACT="0.85")
    assert r2.returncode == 0, r2.stderr
    assert first_id in r2.stdout
    assert "duplicate leg already exists" in r2.stdout
    assert len(records(repo)) == 1


def test_distinct_goal_creates_without_similar_to(repo):
    """A distinct goal creates cleanly without similar_to field."""
    r1 = relay(repo, "create", "-g", "Fix the keymaker cross-tenant vault write escape", "-m", "m1")
    assert r1.returncode == 0
    r2 = relay(repo, "create", "-g", "Render an animated terminal race card from daemon heartbeats", "-m", "m2")
    assert r2.returncode == 0

    recs = records(repo)
    assert len(recs) == 2
    rec2 = load_record(recs[1])
    assert "similar_to" not in rec2


def test_cli_exports_dedup_functions():
    """Verify cli module re-exports the required dedup symbols and constants."""
    assert hasattr(cli, "check_leg_dedup")
    assert hasattr(cli, "resolve_dedup_exact")
    assert hasattr(cli, "resolve_dedup_near")
    assert hasattr(cli, "resolve_embed_url")
    assert hasattr(cli, "DEFAULT_DEDUP_EXACT")
    assert hasattr(cli, "DEFAULT_DEDUP_NEAR")
    assert hasattr(cli, "DEFAULT_EMBED_URL")
    assert cli.DEFAULT_DEDUP_EXACT == 0.96
    assert cli.DEFAULT_DEDUP_NEAR == 0.85
    assert cli.DEFAULT_EMBED_URL == "http://127.0.0.1:11434"
