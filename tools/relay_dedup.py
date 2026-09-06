"""Catch duplicate relay legs BEFORE they are written.

Three duplicate pairs landed on 2026-08-28 alone: two reconciliation TODOs
filed from different surfaces, and a split-brain diagnosis restated 107s after
the original. Every one was a lane doing work another lane had already done.
The relay race exists to stop exactly that, so the check belongs at write
time, not in a cleanup pass afterwards.

Semantic, not textual: two agents describing the same defect rarely reuse the
same words. Embeddings come from nomic-embed-text on the local fleet -- free,
fast, already installed. If that lane is unreachable the check DEGRADES to
token overlap rather than failing open silently, because a dedup check that
vanishes when a dependency is down is worse than none: it teaches the fleet to
trust something absent.

Usage:
    python tools/relay_dedup.py                 # scan open legs, report pairs
    python tools/relay_dedup.py --check "goal"  # would this new leg duplicate?
    python tools/relay_dedup.py --all --since 20260828
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

DEFAULT_THRESHOLD = 0.86
DEFAULT_DEDUP_EXACT = 0.96
DEFAULT_DEDUP_NEAR = 0.85
DEFAULT_EMBED_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "nomic-embed-text"
DEFAULT_TIMEOUT_SEC = 5.0


def resolve_host() -> str:
    return (os.environ.get("NOUGEN_EMBED_URL")
            or os.environ.get("OLLAMA_HOST_URL")
            or os.environ.get("NOUGEN_OLLAMA_URL")
            or DEFAULT_EMBED_URL).rstrip("/")


def resolve_model() -> str:
    return os.environ.get("NOUGEN_DEDUP_MODEL", DEFAULT_MODEL)


def resolve_threshold() -> float:
    return float(os.environ.get("NOUGEN_DEDUP_THRESHOLD", DEFAULT_THRESHOLD))


def resolve_exact_threshold() -> float:
    raw = os.environ.get("NOUGEN_DEDUP_EXACT")
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    return DEFAULT_DEDUP_EXACT


def resolve_near_threshold() -> float:
    raw = os.environ.get("NOUGEN_DEDUP_NEAR")
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    return DEFAULT_DEDUP_NEAR


def resolve_timeout() -> float:
    raw = os.environ.get("NOUGEN_EMBED_TIMEOUT")
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    return DEFAULT_TIMEOUT_SEC


def resolve_handoffs(root: Optional[Path] = None) -> Path:
    env = os.environ.get("NOUGEN_HANDOFFS_DIR") or os.environ.get("NOUGEN_GIT_HANDOFF_DIR")
    if env:
        p = Path(env).expanduser()
        return p if p.is_absolute() or root is None else root / p
    if root is not None:
        return root / ".handoffs"
    return Path(__file__).resolve().parent.parent / ".handoffs"


def _embed(text: str) -> Optional[List[float]]:
    body = json.dumps({"model": resolve_model(), "prompt": text}).encode()
    req = urllib.request.Request(f"{resolve_host()}/api/embeddings", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=resolve_timeout()) as r:
            return (json.loads(r.read()) or {}).get("embedding")
    except (urllib.error.URLError, OSError, ValueError):
        return None


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return num / (na * nb) if na and nb else 0.0


_STOP = {"the", "a", "an", "and", "or", "to", "for", "of", "in", "on", "is",
         "are", "be", "that", "this", "it", "with", "as", "at", "by", "from"}


def _tokens(s: str) -> set:
    return {w for w in re.findall(r"[a-z0-9_]+", s.lower())
            if len(w) > 2 and w not in _STOP}


def _jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


class Similarity:
    """Embeddings when the lane answers, token overlap when it does not.
    `degraded` is reported to the caller -- never hide which mode ran."""

    def __init__(self) -> None:
        self.degraded = _embed("probe") is None
        self._cache: Dict[str, Optional[List[float]]] = {}

    def score(self, a: str, b: str) -> float:
        if self.degraded:
            return min(1.0, _jaccard(a, b) * 1.6)
        for t in (a, b):
            if t not in self._cache:
                self._cache[t] = _embed(t)
        va, vb = self._cache[a], self._cache[b]
        if va is None or vb is None:
            return min(1.0, _jaccard(a, b) * 1.6)
        return _cosine(va, vb)


def load_legs(only_open: bool = True, since: str = "", directory: Optional[Path] = None) -> List[dict]:
    out = []
    target_dir = directory or resolve_handoffs()
    for p in sorted(target_dir.glob("*.json")):
        if since and p.stem < since:
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if only_open and d.get("status") not in (None, "", "open"):
            continue
        if d.get("goal"):
            d["_id"] = p.stem
            out.append(d)
    return out


def check_dedup(
    goal: str,
    directory: Optional[Path] = None,
    exact_threshold: Optional[float] = None,
    near_threshold: Optional[float] = None,
    report: Optional[dict] = None,
) -> Tuple[str, Any, float]:
    """Check a candidate goal against open legs.

    Returns:
        ("exact", leg_id, score): exact duplicate found (similarity >= exact_threshold)
        ("near", [leg_ids], max_score): near duplicates found (similarity >= near_threshold)
        ("ok", None, 0.0): no duplicates found
        ("skipped", reason_str, 0.0): check could not run at all

    `report`, when given, receives {"mode": "embeddings"|"token-overlap",
    "degraded": bool, "legs_compared": int} so the caller can say which method
    produced the verdict. An unreachable embed lane is no longer "skipped": it
    downgrades the method, not the guarantee.
    """
    cleaned_goal = (goal or "").strip()
    if not cleaned_goal:
        return ("ok", None, 0.0)

    try:
        sim = Similarity()
    except Exception as exc:
        return ("skipped", str(exc), 0.0)
    # NOT a bail-out when the embed lane is down. Similarity already implements
    # the token-overlap fallback this module's docstring promises ("DEGRADES to
    # token overlap rather than failing open silently") - it was simply never
    # reached, because this function returned "skipped" first and cmd_create
    # writes the leg on "skipped".
    #
    # Measured cost of that gap, 2026-09-04: two CLOSED legs 41s apart, same
    # work, both delivered fleet-wide. Every session on every node woke for the
    # second one. Measured value of the fallback on that exact pair:
    #
    #     the duplicate pair          jaccard*1.6 = 1.000
    #     three distinct real legs    jaccard*1.6 = 0.000 / 0.178 / 0.094
    #
    # The separation is wide enough that the embedding thresholds hold in
    # degraded mode unchanged; softening them would only reintroduce the
    # escape. `report` carries which mode actually ran, because a check that
    # silently changes method is the same failure one level up.
    if report is not None:
        report["mode"] = "token-overlap" if sim.degraded else "embeddings"
        report["degraded"] = bool(sim.degraded)
        if sim.degraded:
            report["reason"] = f"embed lane unreachable ({resolve_host()})"

    try:
        legs = load_legs(only_open=True, directory=directory)
    except Exception as exc:
        return ("skipped", str(exc), 0.0)

    if report is not None:
        report["legs_compared"] = len(legs)
    if not legs:
        return ("ok", None, 0.0)

    t_exact = exact_threshold if exact_threshold is not None else resolve_exact_threshold()
    t_near = near_threshold if near_threshold is not None else resolve_near_threshold()

    exact_match = None
    highest_exact = 0.0
    near_matches = []

    for leg in legs:
        leg_goal = (leg.get("goal") or "").strip()
        if not leg_goal:
            continue
        try:
            score = sim.score(cleaned_goal, leg_goal)
        except Exception:
            continue

        if score >= t_exact:
            if score > highest_exact:
                highest_exact = score
                exact_match = leg
        elif score >= t_near:
            near_matches.append((leg, score))

    if exact_match is not None:
        leg_id = exact_match.get("id") or exact_match.get("_id")
        return ("exact", leg_id, highest_exact)

    if near_matches:
        near_matches.sort(key=lambda item: item[1], reverse=True)
        similar_ids = [leg.get("id") or leg.get("_id") for leg, _ in near_matches]
        return ("near", similar_ids, near_matches[0][1])

    return ("ok", None, 0.0)


def find_pairs(legs: List[dict], threshold: float,
               sim: "Similarity") -> List[Tuple[float, dict, dict]]:
    pairs = []
    for i in range(len(legs)):
        for j in range(i + 1, len(legs)):
            a, b = legs[i], legs[j]
            if a.get("agent") == b.get("agent") and a.get("machine") == b.get("machine"):
                continue
            s = sim.score(a["goal"], b["goal"])
            if s >= threshold:
                pairs.append((s, a, b))
    return sorted(pairs, key=lambda t: -t[0])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--since", default="")
    ap.add_argument("--threshold", type=float, default=resolve_threshold())
    args = ap.parse_args()

    legs = load_legs(only_open=not args.all, since=args.since)
    sim = Similarity()
    mode = "token-overlap (DEGRADED)" if sim.degraded else f"embeddings ({resolve_model()})"
    print(f"mode: {mode}   threshold: {args.threshold}   legs: {len(legs)}")

    if args.check:
        hits = [(sim.score(args.check, leg["goal"]), leg) for leg in legs]
        hits = [(s, leg) for s, leg in hits if s >= args.threshold]
        if not hits:
            print("\nno duplicate found - safe to create")
            return 0
        print("\nDUPLICATE - ack one of these instead of creating a new leg:")
        for s, leg in sorted(hits, key=lambda t: -t[0]):
            print(f"  {s:.3f}  {leg['_id']}\n         {leg['goal'][:100]}")
        return 1

    pairs = find_pairs(legs, args.threshold, sim)
    print(f"\nduplicate pairs: {len(pairs)}")
    for s, a, b in pairs:
        print(f"\n  {s:.3f}")
        print(f"    A {a['_id']}  [{a.get('agent')}]\n      {a['goal'][:96]}")
        print(f"    B {b['_id']}  [{b.get('agent')}]\n      {b['goal'][:96]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
