"""The install contract the README makes.

pip only *warns* when it cannot write a console-script launcher, so a broken
entry point looks like a successful install and fails later as "command not
found". These assert the two things that must hold regardless of whether the
launcher was written.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = str(ROOT / "src")
TARGET = "nougen_relay.cli:main"


def test_console_script_is_declared_and_points_somewhere_real():
    """`relay` must resolve to an importable callable — if this drifts, every
    install produces a launcher that fails at runtime.

    Read from the checkout rather than from installed metadata: a contributor
    who has not run `pip install -e .` still has to be told when the entry
    point drifts, and a suite that goes red on an uninstalled clone teaches
    everyone to ignore it.
    """
    declaration = f'relay = "{TARGET}"'
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "[project.scripts]" in pyproject, "no console scripts declared at all"
    assert declaration in pyproject, f"pyproject.toml no longer declares `{declaration}`"

    out = subprocess.run(
        [sys.executable, "-c",
         "import importlib,sys;m,f=sys.argv[1].split(':');"
         "sys.exit(0 if callable(getattr(importlib.import_module(m),f,None)) else 1)",
         TARGET],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={"PYTHONPATH": SRC},
    )
    assert out.returncode == 0, f"`{TARGET}` is not an importable callable: {out.stderr}"


def test_module_invocation_works_without_a_launcher():
    """The documented fallback. A machine whose Scripts/bin directory is not
    writable never gets a launcher, so this path has to carry the CLI."""
    out = subprocess.run([sys.executable, "-m", "nougen_relay.cli", "--help"],
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace", env={"PYTHONPATH": SRC, "PATH": ""})
    assert out.returncode == 0, out.stderr
    for verb in ("claim", "create", "relay", "check"):
        assert verb in out.stdout, f"{verb} missing from --help"
