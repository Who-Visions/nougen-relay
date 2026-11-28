"""`relay fail` retry limit: env fallback and the per-leg stored limit.

The CLI used to default --max-retries to the constant 3, so record_leg_failure
never consulted NOUGEN_RELAY_MAX_RETRIES on the CLI path, and a limit set on
an earlier failure (`fail --max-retries 5`) was overwritten by 3 on the next
plain `fail`, dead-lettering the leg early.
"""
import json
from pathlib import Path

import pytest

from nougen_relay import core


@pytest.fixture
def relay_root(tmp_path, monkeypatch):
    (tmp_path / ".handoffs").mkdir()
    monkeypatch.delenv("NOUGEN_RELAY_MAX_RETRIES", raising=False)
    monkeypatch.setattr(core, "_touch_record", lambda *a, **k: None)
    return tmp_path


def _fail(root: Path, argv: list) -> dict:
    args = core.build_parser().parse_args(["fail", "--id", "leg1", "-m", "boom", *argv])
    return core.record_leg_failure(root, args.id, args.message, max_retries=args.max_retries)


def _lease(root: Path) -> dict:
    return json.loads((core.leases_dir(root) / "leg1.lease.json").read_text(encoding="utf-8"))


def test_cli_default_is_unset_so_fallbacks_apply():
    args = core.build_parser().parse_args(["fail", "--id", "x"])
    assert args.max_retries is None


def test_cli_fail_honours_env_limit(relay_root, monkeypatch):
    monkeypatch.setenv("NOUGEN_RELAY_MAX_RETRIES", "5")
    for _ in range(3):
        res = _fail(relay_root, [])
    assert res["status"] == "retry_pending"
    assert res["max_retries"] == 5


def test_later_plain_fail_keeps_the_legs_stored_limit(relay_root):
    assert _fail(relay_root, ["--max-retries", "5"])["max_retries"] == 5
    for _ in range(2):
        res = _fail(relay_root, [])
    assert res["retry_count"] == 3
    assert res["status"] == "retry_pending"
    assert _lease(relay_root)["max_retries"] == 5
    _fail(relay_root, [])
    assert _fail(relay_root, [])["status"] == "dead_letter"


def test_explicit_limit_still_overrides_stored(relay_root):
    _fail(relay_root, ["--max-retries", "5"])
    res = _fail(relay_root, ["--max-retries", "2"])
    assert res["status"] == "dead_letter"
    assert res["max_retries"] == 2


@pytest.mark.parametrize("stored", [None, "junk", 0, -1, [3]])
def test_bad_stored_limit_falls_back_to_default(relay_root, stored):
    ldir = core.leases_dir(relay_root)
    ldir.mkdir(parents=True, exist_ok=True)
    (ldir / "leg1.lease.json").write_text(
        json.dumps({"leg_id": "leg1", "retry_count": 0, "max_retries": stored}), encoding="utf-8")
    res = _fail(relay_root, [])
    assert res["max_retries"] == core.DEFAULT_MAX_RETRIES
