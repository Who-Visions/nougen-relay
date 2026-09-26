"""Deterministic disposition for every leg: ack, resolve, route, or hold.

GM directive 2026-09-14 (1:14 PM EDT): "guardrails that force auto ack, auto
close, auto resolve, auto send to specific lane, dynamically and
deterministically." One pure function decides what happens to a leg from
its content plus a snapshot of the registry, nothing else:

=========  ==================================================================
``ack``    status-only report (autoclose rules): acked, off the open board
``resolve``a report that names earlier legs it finished ("DONE leg 112826Z",
           "FIXED ... supersedes ask #1 of leg 2026...") — those legs are
           completed with a note pointing here, then this one is acked
``route``  addressed to a lane (``[-> @x]`` / ``@x``): ``target_agent`` is
           stamped from the registry's known lanes and a wake signal is
           emitted, so the addressee's watcher picks it up. Stays open —
           the addressee acks
``hold``   carries an ask for nobody in particular: stays open for the
           scheduler / a human
=========  ==================================================================

Dynamic: lanes are whatever the registry has seen (machines and agents in
record filenames); leg references resolve against the registry's own ids.
No lane list, no person, no project name lives in this file.

Deterministic: same record + same registry snapshot = same decision, and
every decision carries the reason it was made so a dry run is a full audit.

Enforced twice: at birth (``create`` stamps ``disposition`` and the route
target into the record before it is written) and by the sweep (``relay
policy`` on a timer, for legs written by lanes without this code).
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from . import autoclose, core

_FULL_ID = re.compile(r"\b(\d{8}T\d{6}Z)(?:__([\w.-]+)__([\w.-]+))?\b")
_SHORT_ID = re.compile(r"(?<![\dT])(\d{6}Z)\b")

#: Verbs that make a leg a resolution of the legs it references.
_RESOLVES = re.compile(
    r"\b(DONE|FIXED|CLOSED|RESOLVED|COMPLETE[DS]?|SHIPPED|LANDED|MERGED|supersedes|closes|resolves)\b")


@dataclass(frozen=True)
class Decision:
    action: str                     # ack | resolve | route | hold | none
    reason: str
    target: Optional[str] = None    # route: lane name from the registry
    resolves: tuple = field(default_factory=tuple)  # resolve: leg ids

    def as_dict(self) -> dict:
        d = {"action": self.action, "reason": self.reason}
        if self.target:
            d["target"] = self.target
        if self.resolves:
            d["resolves"] = list(self.resolves)
        return d


@dataclass
class Registry:
    """The snapshot a decision is made against."""
    lanes: set                      # lower-cased machines + agents seen
    ids: dict                       # leg id -> status (for reference resolution)

    @classmethod
    def load(cls, root: Optional[Path]) -> "Registry":
        ids = {}
        if root is not None:
            try:
                for p in core.handoff_dir(root).glob("*.json"):
                    try:
                        ids[p.stem] = str(json.loads(p.read_text(encoding="utf-8")).get("status") or "")
                    except (OSError, ValueError):
                        ids[p.stem] = ""
            except OSError:
                pass
        return cls(lanes=autoclose.known_lanes(root), ids=ids)


def references(text: str, registry: Registry, *, self_id: str = "") -> tuple:
    """Leg ids this text points at, resolved against the registry.

    Full ids match directly. A short ``HHMMSSZ`` resolves only if exactly
    one registry id ends with it — ambiguity means no reference, never a
    guess.
    """
    found = []
    for m in _FULL_ID.finditer(text):
        stamp = m.group(1)
        hits = [i for i in registry.ids if i.startswith(stamp)]
        if m.group(2) and m.group(3):
            exact = f"{stamp}__{m.group(2)}__{m.group(3)}"
            hits = [i for i in hits if i == exact] or hits
        if len(hits) == 1 and hits[0] != self_id and hits[0] not in found:
            found.append(hits[0])
    for m in _SHORT_ID.finditer(text):
        short = m.group(1)
        hits = [i for i in registry.ids if i.split("__")[0].endswith(short)]
        if len(hits) == 1 and hits[0] != self_id and hits[0] not in found:
            found.append(hits[0])
    return tuple(found)


def route_target(goal: str, registry: Registry) -> Optional[str]:
    """The lane a goal addresses, if it is one the registry knows.

    ``[-> @blade]``, ``-> phoebus``, ``[-> Xoah lane]`` and a bare
    ``@name`` all count; the name must be a known machine or agent, matched
    case-insensitively, longest name first so ``blade1tb`` beats ``blade``.
    """
    candidates = []
    m = re.search(r"(?:^\s*|\[)->\s*@?([\w. -]{1,40}?)\s*[\]:,]", goal)
    if m:
        candidates.append(m.group(1))
    candidates += autoclose._MENTION.findall(goal)
    for cand in candidates:
        words = [w.lower() for w in re.findall(r"[\w.-]+", cand)]
        for lane in sorted(registry.lanes, key=len, reverse=True):
            if lane in words or any(w.startswith(lane) or lane.startswith(w) for w in words if len(w) >= 4):
                if lane not in autoclose._BROADCAST:
                    return lane
    return None


def decide(record: dict, body: str, registry: Registry, *, self_id: str = "",
           grace_minutes: float = autoclose.DEFAULT_GRACE_MINUTES) -> Decision:
    status = str(record.get("status") or "").strip().lower()
    goal = str(record.get("goal") or "")
    if status != "open":
        return Decision("none", f"status is {status or 'missing'}")

    # 1. Route: an addressee beats everything — even a FIXED report that
    #    names a lane is that lane's to read and ack.
    if autoclose._is_addressed(goal, registry.lanes) and not autoclose._REPORT_PREFIX.search(goal):
        target = route_target(goal, registry)
        if target:
            if str(record.get("target_agent") or "").lower() == target and record.get("routed_utc"):
                return Decision("none", f"already routed to {target}", target=target)
            return Decision("route", f"addressed to {target}", target=target)
        return Decision("hold", "addressed, but to no lane the registry knows")

    # 2. Resolve: a report that names earlier legs closes them.
    close, why = autoclose.classify(record, body, grace_minutes=grace_minutes, lanes=registry.lanes)
    refs = tuple(i for i in references(goal + "\n" + body, registry, self_id=self_id)
                 if registry.ids.get(i, "").lower() in ("open", "acked", "in_progress"))
    if close and refs and _RESOLVES.search(goal):
        return Decision("resolve", f"{why}; closes {len(refs)} referenced leg(s)", resolves=refs)

    # 3. Ack: status-only.
    if close:
        return Decision("ack", why)

    # 4. Hold.
    return Decision("hold", why)


def stamp_at_birth(record: dict, body: str, root: Optional[Path]) -> dict:
    """Guardrail on ``create``: every record leaves with its disposition and,
    when addressed, its target lane. Grace is zero here — the decision is
    about shape, and the sweep re-checks age before acting."""
    registry = Registry.load(root)
    d = decide(dict(record, status="open"), body, registry, grace_minutes=0.0)
    record["disposition"] = d.as_dict()
    if d.action == "route" and d.target:
        record.setdefault("target_agent", d.target)
        record.setdefault("target", d.target)
    return record


def scan(root: Path, *, grace_minutes: float = autoclose.DEFAULT_GRACE_MINUTES) -> list:
    registry = Registry.load(root)
    out = []
    for path in sorted(core.handoff_dir(root).glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if str(rec.get("status") or "").lower() != "open":
            continue
        d = decide(rec, autoclose._body_for(path, rec), registry, self_id=path.stem,
                   grace_minutes=grace_minutes)
        out.append({"id": path.stem, "goal": str(rec.get("goal") or "")[:100], **d.as_dict()})
    return out


def apply(root: Path, *, dry: bool = False, push: bool = True,
          grace_minutes: float = autoclose.DEFAULT_GRACE_MINUTES) -> dict:
    machine, agent = core.resolve_machine(), core.resolve_agent()
    remote = core.resolve_remote()
    stamp = core._now().isoformat()
    when = autoclose._stamp_local()
    rows = scan(root, grace_minutes=grace_minutes)
    if dry:
        return {"dry": True, "rows": rows}
    touched, failed = [], []

    def note(text: str) -> str:
        return f"auto-{text} (relay policy on {machine}, {when})"

    for row in rows:
        act = row["action"]
        if act == "ack" or act == "resolve":
            def take(rec, why=row["reason"]):
                rec["status"] = "acked"
                rec.setdefault("relay", []).append(
                    {"event": "ack", "machine": machine, "agent": agent, "at": stamp,
                     "note": note("ack: " + why), "auto": True})
            rec = core._touch_record(root, row["id"], take)
            (touched if rec else failed).append((row["id"], rec, "ack"))
            for ref in row.get("resolves", []):
                def done(r, src=row["id"]):
                    r["status"] = "complete"
                    r.setdefault("relay", []).append(
                        {"event": "complete", "state": "complete", "machine": machine, "agent": agent,
                         "at": stamp, "note": note(f"resolve: closed by {src}"), "auto": True,
                         "resolved_by": src})
                r = core._touch_record(root, ref, done)
                (touched if r else failed).append((ref, r, "complete"))
        elif act == "route":
            def route(rec, target=row["target"], why=row["reason"]):
                rec["target_agent"] = target
                rec["target"] = target
                rec["routed_utc"] = stamp
                rec.setdefault("relay", []).append(
                    {"event": "route", "machine": machine, "agent": agent, "at": stamp,
                     "target": target, "note": note("route: " + why), "auto": True})
            rec = core._touch_record(root, row["id"], route)
            if rec:
                core.emit_wake_signal(root, row["id"], rec)
            (touched if rec else failed).append((row["id"], rec, "route"))
    result = {"dry": False, "rows": rows, "touched": [(i, a) for i, _, a in touched],
              "failed": [i for i, _, _ in failed], "pushed": None}
    if not touched:
        return result
    dirname = core.handoff_dir(root).name
    core._git("add", dirname)
    counts = {}
    for _, _, a in touched:
        counts[a] = counts.get(a, 0) + 1
    summary = ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
    core.stamped_commit(f"relay({machine}): policy sweep — {summary}", dirname)
    if not push:
        result["pushed"] = False
        return result
    ok = True
    for leg_id, rec, act in touched:
        if core._write_registry_record_upstream(root, remote, leg_id, rec, act) is False:
            ok = False
    result["upstream"] = ok
    result["pushed"] = bool(core._publish(remote, core.current_branch()))
    return result


def cmd_policy(args: argparse.Namespace) -> int:
    autoclose._go_windowless()
    root = core.repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return core.EXIT_FAILURE
    healed = autoclose.heal_rebase(root)
    if healed:
        print("ℹ️ stale rebase: " + healed)
    if not args.no_fetch and not args.dry_run:
        core._git("pull", "--rebase", "--autostash", "--quiet", core.resolve_remote())
        healed = autoclose.heal_rebase(root)
        if healed:
            print("ℹ️ pull conflicted: " + healed)
    res = apply(root, dry=args.dry_run, push=not args.no_push, grace_minutes=args.grace)
    if args.json:
        print(json.dumps(res, indent=2, default=str))
        return core.EXIT_OK
    rows = res["rows"]
    by = {}
    for r in rows:
        by.setdefault(r["action"], []).append(r)
    for act in ("route", "resolve", "ack", "hold", "none"):
        for r in by.get(act, []):
            extra = f" -> {r['target']}" if r.get("target") else ""
            extra += f" closes {', '.join(r['resolves'])}" if r.get("resolves") else ""
            print(f"  {act:<7} {r['id']}{extra}\n          {r['reason']} | {r['goal'][:80]}")
    if res.get("dry"):
        print(f"dry run: {len(rows)} open leg(s) — " +
              ", ".join(f"{len(v)} {k}" for k, v in sorted(by.items())))
        return core.EXIT_OK
    print(f"✅ policy applied: {len(res['touched'])} record(s) touched"
          + ("" if res["pushed"] is None else f"; pushed={res['pushed']}"))
    for i in res["failed"]:
        print(f"  ❌ could not touch {i}")
    return core.EXIT_OK if not res["failed"] else core.EXIT_FAILURE


def add_parser(sub) -> None:
    p = sub.add_parser("policy", help="deterministic disposition sweep: ack / resolve / route / hold every open leg")
    p.add_argument("--dry-run", action="store_true", help="show every decision, change nothing")
    p.add_argument("--grace", type=float, default=autoclose.DEFAULT_GRACE_MINUTES)
    p.add_argument("--no-push", action="store_true")
    p.add_argument("--no-fetch", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_policy)
