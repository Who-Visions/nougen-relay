"""One place that builds the environment for a spawned CLI.

Every test that runs the CLI as a subprocess needs `src` importable — and each
file was setting `PYTHONPATH` outright, which quietly discarded anything the
parent had put there. That is how the coverage instrumentation in `conftest.py`
came to be exported and then thrown away by the very tests it was meant to
measure.

Appending is the whole point. Kept here rather than repeated per file so it is
one decision instead of five copies that drift.
"""

import os
from pathlib import Path

SRC = str(Path(__file__).resolve().parents[1] / "src")


def cli_env(**overrides) -> dict:
    """Parent environment + src on PYTHONPATH + whatever the test needs."""
    existing = os.environ.get("PYTHONPATH", "")
    pythonpath = f"{SRC}{os.pathsep}{existing}" if existing else SRC
    env = {**os.environ, "PYTHONPATH": pythonpath, "PYTHONIOENCODING": "utf-8"}
    env.update({k: v for k, v in overrides.items() if v is not None})
    return env
