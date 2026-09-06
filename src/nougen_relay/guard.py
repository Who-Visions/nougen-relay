"""The half of the claim protocol that does not depend on anyone remembering.

`relay claim take` announces work before it starts. It only works if every lane
runs it, and on 2026-08-01 the fleet had duplicated the same work four times in
two days with the protocol documented, agreed, and skipped — plus once more
where it was followed correctly and still failed, because the claim was taken in
NouGenRelay while the work happened in NouGenTracker, which had no `.handoffs`
of its own and therefore no claims to overlap with.

So this asks the question at the one moment every lane passes through no matter
what harness or editor it drives: the commit.

    relay guard --staged      # what a pre-commit hook runs
    relay guard --path a.py   # ask about specific files

Two findings, deliberately weighted differently:

  SOMEONE ELSE HAS CLAIMED THIS  -> blocks. It is the duplicate-work failure
                                    happening in front of you, and the cost of
                                    a false positive (one --no-verify) is far
                                    below the cost of a false negative (two
                                    machines redoing the same work, which is
                                    what this repository exists to stop).

  YOU HAVE NOT CLAIMED THIS      -> warns by default. Blocking here would fire
                                    on every unclaimed typo fix and teach the
                                    fleet to pass --no-verify reflexively,
                                    which disarms the case above too. Opt in
                                    with --require-claim per repo.

A guard that cries wolf gets uninstalled, and an uninstalled guard is worth
less than no guard, because everyone believes it is running.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import List

from . import core as gh
from . import ui


def _adopt():
    """Imported lazily: adopt imports nothing from here, and this keeps it that way."""
    from . import adopt
    return adopt


def staged_paths() -> List[str]:
    """Repo-relative paths staged for commit, POSIX-separated (git's own form)."""
    out = gh._git("diff", "--cached", "--name-only", "--diff-filter=ACMRT")
    return [p.strip() for p in (out or "").splitlines() if p.strip()]


def changed_paths() -> List[str]:
    """Paths modified in the work tree, staged or not."""
    out = gh._git("diff", "--name-only")
    tracked = [p.strip() for p in (out or "").splitlines() if p.strip()]
    return sorted(set(tracked) | set(staged_paths()))


def _scope_of(paths: List[str]) -> str:
    return " ".join(paths)


def foreign_conflicts(root: Path, paths: List[str]) -> list:
    """(machine, record, shared tokens) for every active claim by another box."""
    scope = _scope_of(paths)
    conflicts = []
    for (other, claimed), rec in gh.foreign_claims(root).items():
        shared = gh._scopes_overlap(scope, claimed or "")
        if shared:
            conflicts.append((other, rec, shared))
    return conflicts


def own_cover(root: Path, paths: List[str]) -> tuple:
    """(covered, uncovered) split of `paths` against this machine's own claims.

    Answers "did I announce this before starting?" — the half of the protocol
    that has no other enforcement point at all.
    """
    machine = gh.resolve_machine()
    mine = []
    for target in gh.watch_targets():
        for rec in gh._read_claims_from(root, target):
            if rec.get("machine") != machine or not gh.claim_is_active(rec):
                continue
            mine.append(rec.get("scope") or "")
    covered, uncovered = [], []
    for path in paths:
        if any(gh._scopes_overlap(path, scope) for scope in mine):
            covered.append(path)
        else:
            uncovered.append(path)
    return covered, uncovered


def _require_claim_default() -> bool:
    """Per-repo opt-in to blocking on unclaimed work.

    Off by default and stored in git config rather than an env var, for the
    same reason `nougen.agent` is: a setting that must be exported in every
    shell is a setting that is unset in the shell that mattered.
    """
    if os.environ.get("NOUGEN_REQUIRE_CLAIM", "").strip():
        return os.environ["NOUGEN_REQUIRE_CLAIM"].strip().lower() in {"1", "true", "yes"}
    return (gh._git("config", "--get", "nougen.requireClaim") or "").strip().lower() in {
        "1", "true", "yes"}


def cmd_guard(args: argparse.Namespace) -> int:
    root = gh.repo_root()
    if root is None:
        print("✋ not inside a git work tree")
        return gh.EXIT_FAILURE

    if args.path:
        paths = list(args.path)
    elif args.staged:
        paths = staged_paths()
    else:
        paths = changed_paths()

    if not paths:
        if not args.quiet:
            print(ui.dim("relay guard: nothing to check"))
        return gh.EXIT_OK

    # A repo with no registry cannot answer the question, and saying "all
    # clear" would be the exact false assurance that produced the duplication
    # this guard was written for.
    registry_dir = gh.handoff_dir(root)
    complaint = None
    if not registry_dir.exists():
        complaint = f"{root.name} has no {registry_dir.name} — claims here are invisible to the fleet"
    elif _adopt().registry_is_ignored(root, registry_dir):
        # The worse version of no registry, because it looks like a registry.
        complaint = (f"{root.name}/{registry_dir.name} is GITIGNORED — every claim and leg "
                     f"written here stays on this machine")
    if complaint:
        print(ui.label("⚠️", complaint, "yellow"))
        print(ui.dim("   relay adopt   # give this repo a registry the fleet can read"))
        return gh.EXIT_OK if not args.strict else gh.EXIT_DIVERGED

    conflicts = foreign_conflicts(root, paths)
    if conflicts:
        print(ui.label("✋", ui.head(f"{len(conflicts)} active claim(s) cover files you are "
                                    f"committing:"), "red"))
        for other, rec, shared in conflicts:
            age = gh._claim_age_hours(rec)
            age_s = f"{age:.1f}h ago" if age is not None else "unknown age"
            print(f"  {ui.warn('•')} {ui.machine(str(other))}/{ui.lane(str(rec.get('agent')))} — "
                  f"\"{rec.get('goal') or '(no goal)'}\"")
            print(f"     {ui.dim('overlap:')} {', '.join(shared)} · {ui.dim('claimed')} {age_s}")
        print(ui.dim("   Coordinate first. To commit anyway: git commit --no-verify"))
        return gh.EXIT_DIVERGED

    # The registry is the protocol's own bookkeeping, written by relay itself.
    # Nobody claims a handoff record and nobody collides on one, so warning
    # about them means every single `relay create` ends in a complaint — the
    # cry-wolf failure this guard is weighted to avoid, produced by the guard
    # on its own output.
    registry = gh.handoff_dir(root).name
    authored = [p for p in paths if not p.replace("\\", "/").startswith(f"{registry}/")]
    covered, uncovered = own_cover(root, authored)
    if uncovered:
        require = args.require_claim or _require_claim_default()
        glyph, colour = ("✋", "red") if require else ("⚠️", "yellow")
        print(ui.label(glyph, f"{len(uncovered)} file(s) not covered by a claim of yours", colour))
        for path in uncovered[:8]:
            print(f"     {ui.dim(path)}")
        if len(uncovered) > 8:
            print(ui.dim(f"     … and {len(uncovered) - 8} more"))
        print(ui.dim(f'   relay claim take -s "{_scope_of(uncovered[:4])}" -g "<intent>"'))
        if require:
            return gh.EXIT_DIVERGED

    if not args.quiet:
        print(ui.label("✅", f"{len(paths)} path(s) clear of other machines' claims", "green"))
    return gh.EXIT_OK


# --- admission: the question asked BEFORE a lease is taken -------------------
# Deterministic, evidence-only. A local model may annotate a leg (priority,
# summary, routing hint) but nothing here consults one: ALLOW is never a model
# opinion. Verdicts: ALLOW (claimable now), DEFER (someone holds it, or a retry
# window is still open), DENY (finished, dead-lettered, superseded, or this
# lane cannot do it).

ADMIT_ALLOW, ADMIT_DEFER, ADMIT_DENY = "ALLOW", "DEFER", "DENY"
_TERMINAL_LEG_STATUS = {"complete", "closed", "published", "superseded"}


def admit(root: Path, leg: dict, lane: str | None = None, *, machine: str | None = None,
          agent: str | None = None, now_dt=None) -> tuple:
    """Return (verdict, reason). Reads the leg record and its lease file only."""
    leg_id = str(leg.get("id") or leg.get("leg_id") or "").strip()
    if not leg_id:
        return ADMIT_DENY, "leg has no id"
    status = str(leg.get("status") or "").lower()
    if status in _TERMINAL_LEG_STATUS:
        return ADMIT_DENY, f"leg status {status}"
    if status == "blocked":
        return ADMIT_DEFER, "leg is blocked; dependency not ready"
    if lane and not gh.is_lane_eligible(lane, leg):
        return ADMIT_DENY, f"lane {lane} lacks a required capability"
    lease_file = gh.leases_dir(root) / f"{leg_id}.lease.json"
    if lease_file.is_file():
        try:
            lease = json.loads(lease_file.read_text(encoding="utf-8"))
        except Exception:
            lease = None
        if lease:
            lstatus = str(lease.get("status") or "")
            if lstatus == "dead_letter":
                return ADMIT_DENY, f"dead_letter after {lease.get('retry_count')} attempts: {str(lease.get('last_error') or '')[:80]}"
            if lstatus in ("complete", "failed", "abandoned"):
                return ADMIT_DENY, f"lease closed as {lstatus}"
            if gh.lease_is_active(lease):
                me = f"{machine or gh.resolve_machine()}/{agent or gh.resolve_agent()}"
                holder = f"{lease.get('machine')}/{lease.get('agent')}"
                if holder == me:
                    return ADMIT_ALLOW, f"re-entry: this lane already holds token {lease.get('fencing_token')}"
                return ADMIT_DEFER, f"leased by {holder} token {lease.get('fencing_token')}, ttl {lease.get('ttl_minutes')} min"
            if lstatus == "retry_pending" and not gh.is_leg_retryable(lease, now_dt):
                return ADMIT_DEFER, f"retry window open until {lease.get('next_retry_utc')}"
    return ADMIT_ALLOW, "claimable"


def cmd_admit(args: argparse.Namespace) -> int:
    root = gh.repo_root() or Path.cwd()
    rec = None
    leg_file = root / ".handoffs" / f"{args.leg_id}.json"
    if leg_file.is_file():
        try:
            rec = json.loads(leg_file.read_text(encoding="utf-8"))
        except Exception:
            rec = None
    if rec is None:
        rec = {"id": args.leg_id, "status": args.status or "open"}
    verdict, reason = admit(root, rec, args.lane)
    print(json.dumps({"leg_id": args.leg_id, "verdict": verdict, "reason": reason}))
    return 0 if verdict == ADMIT_ALLOW else (2 if verdict == ADMIT_DEFER else 1)


def register(sub) -> None:
    a = sub.add_parser("admit", help="admission verdict for a leg BEFORE a lease is taken (ALLOW/DEFER/DENY)")
    a.add_argument("leg_id")
    a.add_argument("--lane", help="lane asking (capability check)")
    a.add_argument("--status", help="leg status when the record is not local")
    a.set_defaults(func=cmd_admit)
    g = sub.add_parser("guard", help="refuse work another machine has already claimed")
    g.add_argument("--staged", action="store_true",
                   help="check files staged for commit (what the hook uses)")
    g.add_argument("--path", action="append", default=[],
                   help="check this path instead of asking git (repeatable)")
    g.add_argument("--require-claim", action="store_true",
                   help="also fail when YOUR claim is missing, not just warn")
    g.add_argument("--strict", action="store_true",
                   help="treat a repo with no registry as a failure")
    g.add_argument("-q", "--quiet", action="store_true", help="print only problems")
    g.set_defaults(func=cmd_guard)
