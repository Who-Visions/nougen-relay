"""Make the subprocess tests visible to coverage — actually, not nominally.

Most of this suite runs the CLI as a real subprocess, because a git transport
between two working copies is the behaviour worth testing. coverage.py traces
only the process it started, so those runs were invisible and core.py reported
21% while its CLI paths were exercised hard. A number that flatters a gap is
worse than no number.

Arming a child needs two things, and exporting COVERAGE_PROCESS_START alone —
the obvious first attempt — supplies only one. Something must also *call*
`coverage.process_startup()` inside the child before it imports anything. That
normally comes from a `.pth` in site-packages, which a test run has no business
writing to.

So: a throwaway `sitecustomize.py` is written to a temp directory and that
directory is prepended to PYTHONPATH. Python imports `sitecustomize`
automatically at interpreter startup, so every child arms itself, and nothing
outside this repo is touched.

Test helpers must APPEND to PYTHONPATH rather than replace it, or this is
silently undone. `tests/_env.py` exists so that is not something each file has
to remember.

Inert when coverage is not running.
"""

import os
import tempfile
from pathlib import Path

_RC = Path(__file__).parent / ".coveragerc"


def _under_coverage() -> bool:
    try:
        import coverage

        return coverage.Coverage.current() is not None
    except Exception:
        return False


def pytest_configure(config):
    if not _under_coverage() or not _RC.exists():
        return

    site_dir = Path(tempfile.mkdtemp(prefix="relay-cov-"))
    (site_dir / "sitecustomize.py").write_text(
        "import coverage\ncoverage.process_startup()\n", encoding="utf-8"
    )
    os.environ["COVERAGE_PROCESS_START"] = str(_RC)
    # Children run with cwd set to a throwaway repo, and coverage writes its
    # data file relative to cwd — so every child's measurements were landing in
    # a temp directory and being deleted with it. `combine` then reported
    # "skipped 2" and the totals never moved. Pin it to the project.
    os.environ["COVERAGE_FILE"] = str(Path(__file__).parent / ".coverage")
    existing = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = (
        f"{site_dir}{os.pathsep}{existing}" if existing else str(site_dir)
    )
    config._relay_cov_sitedir = site_dir
