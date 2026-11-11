"""Cross-language parity tests between Python `nougen_relay.core` and Go `gorelay`."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from nougen_relay import core

ROOT = Path(__file__).resolve().parents[1]
GORELAY_DIR = ROOT / "gorelay"
FIXTURES_DIR = GORELAY_DIR / "testdata" / "protocol"


@pytest.fixture(scope="module")
def gorelay_bin(tmp_path_factory):
    go_exe = shutil.which("go")
    if not go_exe:
        pytest.skip("go toolchain unavailable")
    out_dir = tmp_path_factory.mktemp("gorelay-bin")
    bin_path = out_dir / ("gorelay.exe" if os.name == "nt" else "gorelay")
    subprocess.run(
        [go_exe, "build", "-o", str(bin_path), "."],
        cwd=str(GORELAY_DIR),
        check=True,
    )
    return bin_path


def _run_go(bin_path: Path, *args: str, env: dict | None = None, check: bool = True):
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        [str(bin_path), *args],
        capture_output=True,
        text=True,
        env=merged_env,
        check=check,
    )


def test_gorelay_binary_is_gitignored():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "gorelay/gorelay" in [line.strip() for line in gitignore]


def test_phase0_golden_vectors_match_python(gorelay_bin):
    vectors = json.loads((FIXTURES_DIR / "vectors.json").read_text(encoding="utf-8"))
    for row in vectors["idempotency_keys"]:
        assert core.compute_idempotency_key(row["leg_id"], row["goal"]) == row["expected_sha256"]
    for row in vectors["scope_normalization"]:
        assert core._normalize_scope(row["raw"]) == row["tokens"]
    for row in vectors["scope_overlap"]:
        assert core._scopes_overlap(row["a"], row["b"]) == row["expected_overlap"]


def test_gorelay_open_and_ack_parity_with_fencing(tmp_path, gorelay_bin, monkeypatch):
    monkeypatch.setenv("NOUGEN_LEASE_DIR", str(tmp_path / ".relay" / "leases"))
    monkeypatch.setenv("NOUGEN_IDEMPOTENCY_DIR", str(tmp_path / ".relay" / "idempotency"))

    hdir = tmp_path / ".handoffs"
    hdir.mkdir()
    leg_name = "20261111T172801Z__node-b__worker.json"
    shutil.copyfile(FIXTURES_DIR / "handoffs" / "open_explicit.json", hdir / leg_name)

    res_open = _run_go(
        gorelay_bin,
        "open",
        "--dir",
        str(hdir),
        "--machine",
        "node-a",
        "--strict",
        check=False,
    )
    assert res_open.returncode == 3
    assert "node-b/worker" in res_open.stdout

    # Python issues fenced lease (token=1); Go respects token=1 and rejects stale token=2.
    lease = core.acquire_lease(
        tmp_path,
        "20261111T172801Z__node-b__worker",
        machine="node-a",
        agent="runner",
        goal="Add ack and claim to gorelay",
    )
    assert lease["fencing_token"] == 1

    stale = _run_go(
        gorelay_bin,
        "ack",
        "--root",
        str(tmp_path),
        "--id",
        "20261111T172801Z__node-b__worker",
        "--machine",
        "node-a",
        "--agent",
        "runner",
        "--fencing-token",
        "2",
        check=False,
    )
    assert stale.returncode != 0
    assert core.lease_metrics(tmp_path)["fencing_rejections"] == 1

    ok = _run_go(
        gorelay_bin,
        "ack",
        "--root",
        str(tmp_path),
        "--id",
        "20261111T172801Z__node-b__worker",
        "--machine",
        "node-a",
        "--agent",
        "runner",
        "-m",
        "taking via parity test",
        "--fencing-token",
        "1",
    )
    assert ok.returncode == 0
    doc = json.loads((hdir / leg_name).read_text(encoding="utf-8"))
    assert doc["status"] == "acked"
    assert doc["branch"] == "feat/example"
    assert doc["relay"][-1]["idempotency_key"] == lease["idempotency_key"]
    assert core.is_duplicate_execution(tmp_path, "20261111T172801Z__node-b__worker", doc["goal"]) is False

    # Replay is idempotent and does not append a second ack entry.
    replay = _run_go(
        gorelay_bin,
        "ack",
        "--root",
        str(tmp_path),
        "--id",
        "20261111T172801Z__node-b__worker",
        "--machine",
        "node-a",
        "--agent",
        "runner",
        "--fencing-token",
        "1",
    )
    assert replay.returncode == 0
    assert "idempotent" in replay.stdout
    assert len(json.loads((hdir / leg_name).read_text(encoding="utf-8"))["relay"]) == 1


def test_gorelay_claim_parity_with_python_reader(tmp_path, gorelay_bin, monkeypatch):
    monkeypatch.setenv("NOUGEN_MACHINE", "node-b")
    monkeypatch.setenv("NOUGEN_AGENT", "py-worker")
    monkeypatch.setenv("NOUGEN_SESSION", "py-sess")

    claims_dir = tmp_path / ".handoffs" / "claims"
    claims_dir.mkdir(parents=True)
    # Seed legacy list-typed claim fixture matching real registry format.
    shutil.copyfile(FIXTURES_DIR / "claims" / "active_list_scope.json", claims_dir / "legacy_list.json")

    # Go detects Python/fixture active list-typed claim overlap on self="node-a".
    chk = _run_go(
        gorelay_bin,
        "claim",
        "check",
        "--root",
        str(tmp_path),
        "--scope",
        "src\\pkg\\legacy.py",
        "--machine",
        "node-a",
        check=False,
    )
    assert chk.returncode == 3

    # Go claims a new disjoint scope with fenced lease; Python reads it cleanly via foreign_claims.
    res = _run_go(
        gorelay_bin,
        "claim",
        "take",
        "--root",
        str(tmp_path),
        "--scope",
        "gorelay/claim.go",
        "--goal",
        "Parity claim test",
        "--machine",
        "node-a",
        "--agent",
        "go-worker",
        "--session",
        "go-sess",
        "--leg",
        "L-PARITY-1",
    )
    assert res.returncode == 0
    recs = core._read_claims_from(tmp_path, None)
    active = [r for r in recs if core.claim_is_active(r) and r.get("machine") == "node-a"]
    assert any(core._scopes_overlap("gorelay/claim.go", r["scope"]) for r in active)
    metrics = core.lease_metrics(tmp_path)
    assert metrics["leases"] == 1 and metrics["active"] == 1
    lease = json.loads((tmp_path / ".relay" / "leases" / "L-PARITY-1.lease.json").read_text(encoding="utf-8"))
    assert lease["fencing_token"] == 1
    assert len(lease["lease_id"]) == 12
    assert lease["idempotency_key"] == core.compute_idempotency_key("L-PARITY-1", "Parity claim test")
