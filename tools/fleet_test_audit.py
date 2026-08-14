#!/usr/bin/env python3
"""Ask the fleet to grade this repo's tests against current practice.

The author of a test suite is the worst judge of it. This sends the real files
to independent routes and tallies concrete, checkable claims — then a human
verifies them, because a unanimous fleet was two-thirds wrong the last time it
was asked a question here.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\super\Outpost\NouGen\tools")
from fleet import Fleet  # noqa: E402

TESTS = Path(r"C:\Users\super\Outpost\NouGenRelay\tests")


def sample() -> str:
    """Two contrasting files: a pure-logic suite and a real-IO suite."""
    picks = ["test_claim_expiry.py", "test_two_machines.py"]
    out = []
    for name in picks:
        p = TESTS / name
        if p.exists():
            body = p.read_text(encoding="utf-8")[:5000]
            out.append(f"===== {name} =====\n{body}")
    return "\n\n".join(out)


PROMPT = f"""You are auditing a Python test suite against CURRENT best practice.
Be specific and critical. Do not praise.

The suite has 165 tests over a CLI that coordinates several machines through
git. It runs on CI for Python 3.9/3.11/3.13. It has NO runtime dependencies by
design, and dev dependencies are limited to pytest.

{sample()}

Answer ONLY in this format, no preamble:

GRADE: A, B, C, D or F
MISSING: <the single most valuable testing practice this suite lacks, one line>
WEAKEST: <the concrete weakest thing in the code shown, one line, cite a test name>
FLAKE_RISK: <a specific way one of these tests could fail intermittently, or NONE>"""


def main() -> int:
    f = Fleet()
    f.probe(verbose=False)
    n = min(len(f.healthy), 10)
    if not n:
        print("no healthy routes")
        return 1
    print(f"grading across {n} independent routes...", flush=True)
    results = f.map([PROMPT] * n)

    rows, grades = [], []
    for _idx, name, res in results:
        text = (res or "").strip() if isinstance(res, str) else str(res).strip()
        if not text:
            rows.append({"route": name, "status": "no-answer"})
            continue
        got = {}
        for line in text.splitlines():
            for key in ("GRADE", "MISSING", "WEAKEST", "FLAKE_RISK"):
                if line.strip().upper().startswith(key):
                    got[key] = line.split(":", 1)[-1].strip()
        if got.get("GRADE"):
            grades.append(got["GRADE"][:1].upper())
        rows.append({"route": name, **got})

    analysis = Path(r"C:\Users\super\Outpost\NouGenRelay\analysis")
    analysis.mkdir(exist_ok=True)
    (analysis / "fleet-audit-tests.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8")

    from collections import Counter
    print("\nGRADES:", dict(Counter(grades)))
    for field in ("MISSING", "WEAKEST", "FLAKE_RISK"):
        print(f"\n--- {field} ---")
        seen = set()
        for r in rows:
            v = (r.get(field) or "").strip()
            if v and v.lower() not in seen and v.upper() != "NONE":
                seen.add(v.lower())
                print(f"  [{r['route'][:22]:22}] {v[:150]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
