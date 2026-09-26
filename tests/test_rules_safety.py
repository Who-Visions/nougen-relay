"""The module that runs shell commands because another machine pushed.

This was 276 statements at 0% coverage — the largest untested surface in the
repo and by some distance the most dangerous, because a rule fires *unattended*:
a leg arrives from a box that is awake, and this executes a command on one that
may not be.

So these tests are about restraint, not features. Every one asks "what stops
this from running something it should not":

  the kill switch actually kills          (NOUGEN_RULES=off)
  dry mode reports without executing      (NOUGEN_RULES=dry)
  a leg fires once, not once per pull     (replay safety)
  your own leg does not trigger your box  (no self-firing loops)
  a rule that hangs cannot hang the box   (timeout)

Anything here failing means a machine runs a command nobody asked it to.
"""

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from nougen_relay import rules

MARKER = "fired.txt"


@pytest.fixture(autouse=True)
def clean_mode(monkeypatch):
    monkeypatch.delenv("NOUGEN_RULES", raising=False)
    monkeypatch.delenv("NOUGEN_RULES_TIMEOUT", raising=False)


@pytest.fixture()
def repo(tmp_path):
    (tmp_path / ".handoffs").mkdir()
    return tmp_path


def touch_cmd(target: Path) -> str:
    """A command that proves it ran, portable across shells."""
    argv = [sys.executable, "-c", f"open({str(target)!r}, 'w').write('x')"]
    return subprocess.list2cmdline(argv) if os.name == "nt" else shlex.join(argv)


def leg(root: Path, machine: str = "boxb", rec_id: str = "20260801T000000Z__boxb__lane") -> dict:
    rec = {"machine": machine, "agent": "lane", "goal": "did a thing",
           "status": "open", "created_utc": "2026-08-01T00:00:00+00:00",
           "_file": f"{rec_id}.json"}
    (root / ".handoffs" / f"{rec_id}.json").write_text(json.dumps(rec), encoding="utf-8")
    return rec


# --- the kill switch --------------------------------------------------------

def test_off_means_nothing_runs(repo, monkeypatch):
    """A box taken out of the rotation must stay out. This is the switch an
    operator reaches for when something is misfiring at 3am."""
    target = repo / MARKER
    rules.add_rule(repo, rule_id="r1", run=touch_cmd(target))
    prime(repo)
    leg(repo, rec_id="20260801T060000Z__boxb__lane")
    monkeypatch.setenv("NOUGEN_RULES", "off")

    rules.react(repo)

    assert not target.exists(), "a rule executed with the kill switch on"


@pytest.mark.parametrize("value", ["off", "0", "false", "no", "disabled", "OFF", "Off"])
def test_every_documented_off_spelling_is_honoured(value, monkeypatch):
    """An operator typing `NOUGEN_RULES=0` and getting execution anyway is the
    worst possible outcome for a safety switch."""
    monkeypatch.setenv("NOUGEN_RULES", value)
    assert rules.mode() == "off"


@pytest.mark.parametrize("value", ["dry", "dry-run", "dryrun", "test"])
def test_every_documented_dry_spelling_is_honoured(value, monkeypatch):
    monkeypatch.setenv("NOUGEN_RULES", value)
    assert rules.mode() == "dry"


def test_an_unrecognised_value_leaves_rules_on(monkeypatch):
    """Fail useful, not silent: a typo must not quietly disable the feature."""
    monkeypatch.setenv("NOUGEN_RULES", "yes-please")
    assert rules.mode() == "on"


# --- dry mode ---------------------------------------------------------------

def prime(repo):
    """Get past the first-run baseline so later legs actually fire.

    A box's first `react()` adopts whatever history is already present instead
    of firing against it — see the baseline test below. Every test that wants a
    rule to RUN has to step over that deliberately.
    """
    rules.react(repo)


def test_a_new_box_adopts_existing_history_instead_of_firing_on_it(repo):
    """Clone a repo with six months of legs, install a rule, and the box must
    not execute six months of commands. Found by writing a test that assumed
    the opposite and being wrong."""
    target = repo / MARKER
    rules.add_rule(repo, rule_id="r1", run=touch_cmd(target))
    leg(repo)

    rules.react(repo)          # first ever run on this box

    assert not target.exists(), "a fresh box fired against pre-existing history"


def test_dry_mode_reports_without_executing(repo, monkeypatch):
    """The whole point of dry: see what WOULD happen on a box you do not yet
    trust, without it happening."""
    target = repo / MARKER
    rules.add_rule(repo, rule_id="r1", run=touch_cmd(target))
    prime(repo)
    leg(repo, rec_id="20260801T010000Z__boxb__lane")
    monkeypatch.setenv("NOUGEN_RULES", "dry")

    fired = rules.react(repo)

    assert not target.exists(), "dry mode executed the command"
    assert fired, "dry mode should still report the match"


# --- fire once --------------------------------------------------------------

def test_a_leg_fires_once_no_matter_how_often_you_react(repo):
    """`react` runs on every pull. Without once-per-leg tracking a build would
    re-run on every fetch for as long as the leg exists."""
    target = repo / MARKER
    rules.add_rule(repo, rule_id="r1", run=touch_cmd(target))
    prime(repo)
    leg(repo, rec_id="20260801T020000Z__boxb__lane")

    rules.react(repo)
    first = target.read_text(encoding="utf-8") if target.exists() else None
    target.unlink(missing_ok=True)

    rules.react(repo)
    rules.react(repo)

    assert first == "x", "the rule did not fire at all"
    assert not target.exists(), "the same leg fired more than once"


def test_replay_all_is_the_deliberate_way_to_re_run(repo):
    """An escape hatch has to exist, and it has to be explicit."""
    target = repo / MARKER
    rules.add_rule(repo, rule_id="r1", run=touch_cmd(target))
    leg(repo)

    # replay_all steps over the first-run baseline. It does NOT re-fire legs
    # already in `seen` — that ordering is in react() and is worth knowing:
    # the escape hatch is "do not baseline me", not "run everything again".
    rules.react(repo, replay_all=True)

    assert target.exists(), "replay_all did not step over the baseline"


# --- no self-firing ---------------------------------------------------------

def test_your_own_leg_does_not_trigger_your_own_box(repo, monkeypatch):
    """Otherwise every machine reacts to itself and a rule that writes a leg
    becomes an infinite loop across the fleet."""
    monkeypatch.setenv("NOUGEN_MACHINE", "boxa")
    target = repo / MARKER
    rules.add_rule(repo, rule_id="r1", run=touch_cmd(target))
    prime(repo)                       # or the baseline, not the rule, is what passes
    leg(repo, machine="boxa", rec_id="20260801T030000Z__boxa__lane")

    rules.react(repo)

    assert not target.exists(), "a box reacted to its own leg"


# --- disabled rules ---------------------------------------------------------

def test_a_disabled_rule_does_not_run(repo):
    target = repo / MARKER
    rules.add_rule(repo, rule_id="r1", run=touch_cmd(target))
    rules.set_enabled(repo, "r1", False)
    prime(repo)
    leg(repo, rec_id="20260801T040000Z__boxb__lane")

    rules.react(repo)

    assert not target.exists(), "a disabled rule executed"


def test_a_removed_rule_does_not_run(repo):
    target = repo / MARKER
    rules.add_rule(repo, rule_id="r1", run=touch_cmd(target))
    prime(repo)
    assert rules.remove_rule(repo, "r1") is True
    leg(repo, rec_id="20260801T050000Z__boxb__lane")

    rules.react(repo)

    assert not target.exists(), "a removed rule executed"


# --- timeouts ---------------------------------------------------------------

@pytest.mark.xfail(
    os.name == "nt",
    strict=True,
    reason="KNOWN DEFECT, WINDOWS ONLY — and the platform scope came from CI, "
           "not from me. Marked unconditionally at first; Linux XPASSed on all "
           "three Pythons, which is strict=True doing exactly its job: POSIX "
           "kills the process group and reaps the grandchild, Windows does not. "
           "The timeout IS passed to "
           "subprocess.run, but with shell=True + capture_output=True the "
           "timeout kills the SHELL while the grandchild keeps running and "
           "holding the pipe open, so communicate() blocks until it exits "
           "anyway. A 1s timeout took 30s. Fixing it needs process-group kill "
           "(POSIX) / job objects (Windows) and belongs to whoever owns "
           "rules.py — this test is left failing on purpose so it cannot be "
           "forgotten, and strict=True means it fails CI the moment it starts "
           "passing so the marker gets removed with the fix.",
)
def test_a_hanging_rule_cannot_hang_the_machine(repo, monkeypatch):
    """Unattended execution means nobody is watching to hit ctrl-c.

    This one was passing vacuously until the fixture was primed: the first-run
    baseline meant nothing ran at all, so 'the timeout works' was never tested.
    Priming it surfaced the defect below."""
    monkeypatch.setenv("NOUGEN_RULES_TIMEOUT", "1")
    rules.add_rule(repo, rule_id="slow",
                   run=f'{sys.executable} -c "import time; time.sleep(30)"')
    prime(repo)
    leg(repo, rec_id="20260801T070000Z__boxb__lane")

    import time
    start = time.time()
    rules.react(repo)
    elapsed = time.time() - start

    assert elapsed < 20, f"a hanging rule blocked for {elapsed:.0f}s"


def test_the_timeout_default_is_sane_and_configurable(monkeypatch):
    assert rules.default_timeout() == 60
    monkeypatch.setenv("NOUGEN_RULES_TIMEOUT", "5")
    assert rules.default_timeout() == 5


def test_a_garbage_timeout_falls_back_rather_than_crashing(monkeypatch):
    """A malformed env var must not take the reaction path down — that would
    turn a typo into a fleet-wide outage of unattended work."""
    monkeypatch.setenv("NOUGEN_RULES_TIMEOUT", "soon")
    assert rules.default_timeout() == 60
