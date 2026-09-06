"""Terminal colour and layout, stdlib only.

No dependency is added for this. `pip install nougen_relay` still pulls
nothing, because the whole premise is that any box with git and python can join
the fleet — a colour library is not worth breaking that for.

The rule that matters more than the palette: **colour disappears the moment the
output is not a terminal.** This CLI's stdout is parsed by other programs — the
Antigravity guard read `claim list` output this morning and broke on box-drawing
glyphs alone. Escape codes leaking into a pipe would be that failure again, with
a prettier cause. Every helper here is a no-op when `enabled()` is False, so the
piped bytes are exactly what they were before this module existed.

Honoured, in order:
  NO_COLOR=1        off, whatever else says (https://no-color.org)
  FORCE_COLOR=1     on, even when piped — for CI logs that render ANSI
  TERM=dumb         off
  not a tty         off
"""

from __future__ import annotations

import os
import sys

_RESET = "\033[0m"
_CODES = {
    "bold": "1", "dim": "2", "italic": "3", "underline": "4",
    "red": "31", "green": "32", "yellow": "33",
    "blue": "34", "magenta": "35", "cyan": "36", "grey": "90",
}

_ENABLED: bool | None = None


def _windows_vt() -> bool:
    """Ask the console to interpret escape codes rather than print them.

    Windows Terminal does this already; conhost does not, and there the
    difference is a screen of `←[32m` instead of colour. ctypes is stdlib, so
    this costs nothing at import on other platforms.
    """
    if os.name != "nt":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except Exception:
        return False


def enabled() -> bool:
    global _ENABLED
    if _ENABLED is None:
        if os.environ.get("NO_COLOR"):
            _ENABLED = False
        elif os.environ.get("FORCE_COLOR"):
            _ENABLED = True
        elif os.environ.get("TERM", "") == "dumb":
            _ENABLED = False
        elif not sys.stdout.isatty():
            _ENABLED = False
        else:
            _ENABLED = _windows_vt()
    return _ENABLED


def reset_cache() -> None:
    """Tests change the environment after import; let them."""
    global _ENABLED
    _ENABLED = None


def paint(text: str, *styles: str) -> str:
    if not text or not enabled():
        return text
    codes = ";".join(_CODES[s] for s in styles if s in _CODES)
    return f"\033[{codes}m{text}{_RESET}" if codes else text


# --- semantic wrappers ------------------------------------------------------
# Callers name MEANING, not colour. A future palette change happens here, and
# nothing has to remember that machines were cyan.

def machine(name: str) -> str:
    return paint(name, "cyan", "bold")


def lane(name: str) -> str:
    return paint(name, "cyan")


def ident(text: str) -> str:
    """A record id: present but never competing with the message."""
    return paint(text, "grey")


def good(text: str) -> str:
    return paint(text, "green")


def warn(text: str) -> str:
    return paint(text, "yellow")


def bad(text: str) -> str:
    return paint(text, "red", "bold")


def head(text: str) -> str:
    return paint(text, "bold")


def dim(text: str) -> str:
    return paint(text, "dim")


def rule(width: int = 60) -> str:
    return paint("─" * width, "grey")


def label(glyph: str, text: str, style: str = "") -> str:
    """`glyph text` with the glyph carrying the colour.

    The glyph is left uncoloured when disabled, so existing output — which
    other code already greps for — is byte-identical to before.
    """
    return f"{paint(glyph, style) if style else glyph} {text}"


def kv(key: str, value: str, width: int = 10) -> str:
    """Aligned `key   value`, so a column of these reads as a column."""
    return f"{dim(key.ljust(width))} {value}"
