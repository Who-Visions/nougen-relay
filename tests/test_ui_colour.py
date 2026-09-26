"""Colour must be invisible to everything that is not a human terminal.

This CLI's stdout is an interface. The Antigravity guard parsed `claim list`
output and broke on box-drawing glyphs alone — escape codes in a pipe would be
that same failure with a prettier cause. So the contract is stronger than "looks
nice": when stdout is not a tty, the bytes are exactly what they were before
colour existed.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from nougen_relay import ui

SRC = str(Path(__file__).resolve().parents[1] / "src")


@pytest.fixture(autouse=True)
def fresh(monkeypatch):
    for var in ("NO_COLOR", "FORCE_COLOR", "TERM"):
        monkeypatch.delenv(var, raising=False)
    ui.reset_cache()
    yield
    ui.reset_cache()


def test_no_escape_codes_when_not_a_tty(monkeypatch):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    ui.reset_cache()
    assert ui.machine("whoart") == "whoart"
    assert "\033" not in ui.good("done")


def test_no_color_env_wins_over_a_real_tty(monkeypatch):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setenv("NO_COLOR", "1")
    ui.reset_cache()
    assert ui.bad("nope") == "nope"


def test_force_color_paints_even_when_piped(monkeypatch):
    """CI log viewers render ANSI; let someone ask for it."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    ui.reset_cache()
    assert "\033[" in ui.good("done")


def test_dumb_terminals_get_plain_text(monkeypatch):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setenv("TERM", "dumb")
    ui.reset_cache()
    assert ui.warn("careful") == "careful"


def test_painted_text_still_contains_the_text(monkeypatch):
    """Colour wraps, never replaces — greps on the message keep working."""
    monkeypatch.setenv("FORCE_COLOR", "1")
    ui.reset_cache()
    painted = ui.machine("whoart")
    assert "whoart" in painted and painted.endswith("\033[0m")


def test_every_style_closes_what_it_opens(monkeypatch):
    monkeypatch.setenv("FORCE_COLOR", "1")
    ui.reset_cache()
    for fn in (ui.machine, ui.lane, ui.ident, ui.good, ui.warn, ui.bad,
               ui.head, ui.dim):
        out = fn("x")
        assert out.count("\033[0m") == 1, f"{fn.__name__} leaks its style"


def test_empty_string_is_never_decorated(monkeypatch):
    """An escape-code-only string would be invisible padding in a table."""
    monkeypatch.setenv("FORCE_COLOR", "1")
    ui.reset_cache()
    assert ui.machine("") == ""


def test_the_real_cli_emits_no_escapes_when_piped():
    """End to end, the way another program would actually call it."""
    out = subprocess.run(
        [sys.executable, "-m", "nougen_relay.cli", "whoami"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={"PATH": __import__("os").environ.get("PATH", ""),
             "PYTHONPATH": SRC, "PYTHONIOENCODING": "utf-8",
             "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", "")},
    )
    assert "\033[" not in out.stdout, "escape codes leaked into a pipe"
