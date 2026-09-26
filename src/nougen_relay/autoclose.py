"""Auto-close status-only legs so nobody has to ack them by hand.

GM directive 2026-09-14 (7:55 AM EDT): "legs need to auto close ... I don't
understand why I got to tell you." A leg whose whole content is a report —
FIXED / CLOSED / DONE / PUSHED, a `[auto]` session-ended notice, a ranked
triage digest, an "Ask: None" handoff — is a baton with nobody to pass it to.
Leaving it `open` puts it on every lane's board as if it were work, and the
only thing that ever happens to it is a human asking a lane to ack it.

The watchers (`relay_watch_node.py`, `relay_live.py`) already recognise this
shape but only *suppress the ping* and leave the record open; that is why the
board fills up. This module acks them, with the same record mutation and
publish path the `ack` verb uses, so the audit trail is identical: an `ack`
event whose note says it was an auto-close and why.

What is NEVER auto-closed (conservative on purpose; a wrong ack hides work,
a missed one is only clutter):

* anything already not `open`
* a leg addressed to a lane in its goal (`[-> @blade ...]`, `-> phoebus`)
* a body with a section that carries work: Ask (unless it says "None"),
  Directive, Required fix, TODO, Next, Follow-ups, Still open, Not done,
  Open (...)
* an Ask that names Dave (owner validation is his to close)
* a leg younger than the grace window, so live pingers see it first
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import core

#: Goal prefixes that are reports by construction.
_REPORT_PREFIX = re.compile(
    r"^\s*(\[auto\]|xoah relay triage:|correction to|record\b|done leg\b)", re.IGNORECASE)

#: Report vocabulary in a goal. Word-bounded and upper-case heavy on purpose:
#: "fixed" inside a sentence about something still broken should not match a
#: goal that is otherwise an ask, so this only counts when no work section
#: exists in the body.
_REPORT_WORDS = re.compile(
    r"\b(FIXED|CLOSED|DONE|PUSHED|BUILT|UNIFIED|VERIFIED|LANDED|SHIPPED|RESTORED|"
    r"COMPLETED|RESOLVED|MERGED|DEPLOYED|hardened|sharded|restored|shipped|"
    r"verified|landed|merged|deployed|published)\b")

#: A goal that addresses a lane is someone's inbox, not sweep material.
#: The arrow form (``[-> x]``, ``-> @x``) is an address whoever x is; the
#: bare ``@name`` form counts only when ``name`` is a lane the registry has
#: actually seen (machines and agents from record filenames), so a new box
#: is recognised the day it writes its first leg and ``NouGen@fleet/branch``
#: in an [auto] notice is never mistaken for one. No lane list lives here.
# Only a bracketed or goal-leading arrow addresses someone; "shim 25840 ->
# worker 29256" in prose is a pipeline, not an addressee.
_ARROW = re.compile(r"(^\s*->|\[->)\s*@?\w")
_MENTION = re.compile(r"(?<![\w/])@([\w-]+)")

#: Broadcast handles are not addresses (same ruling as the watchers).
_BROADCAST = {"all", "fleet", "everyone", "here"}


def known_lanes(root: Optional[Path]) -> set:
    """Every machine and agent name that has written a record here."""
    lanes = set()
    if root is None:
        return lanes
    try:
        for entry in core.handoff_dir(root).iterdir():
            parts = entry.name.split("__")
            if len(parts) >= 3:
                lanes.add(parts[1].lower())
                lanes.add(parts[2].split(".")[0].lower())
    except OSError:
        pass
    return lanes


def _is_addressed(goal: str, lanes: set) -> bool:
    if _ARROW.search(goal):
        return True
    return any(m.lower() in lanes and m.lower() not in _BROADCAST
               for m in _MENTION.findall(goal))

#: Headings whose presence means the body carries work for someone.
_WORK_HEADING = re.compile(
    r"^#{1,4}\s*[^\w\s]*\s*(ask|directive|required fix|todo|next\b|follow[- ]?ups?|still open|"
    r"not done|open \(|gap \d|blocking)", re.IGNORECASE | re.MULTILINE)

_ASK_SECTION = re.compile(r"^#{1,4}\s*[^\w\s]*\s*ask\b[^\n]*\n(.*?)(?=^#{1,4}\s|\Z)",
                          re.IGNORECASE | re.MULTILINE | re.DOTALL)

def _grace_default() -> float:
    """Grace window before a leg is eligible: env first, else the watchers'
    poll interval x2 (a leg must survive at least one full watcher pass so
    live pingers see it before it leaves the open board), else 20."""
    import os
    for key in ("NOUGEN_RELAY_AUTOCLOSE_GRACE_MIN",):
        v = os.environ.get(key)
        if v:
            try:
                return float(v)
            except ValueError:
                pass
    v = os.environ.get("NOUGEN_RELAY_WATCH_SECS")
    if v:
        try:
            return max(5.0, float(v) * 2 / 60.0)
        except ValueError:
            pass
    return 20.0


DEFAULT_GRACE_MINUTES = _grace_default()


def _section(body: str, pattern: re.Pattern) -> Optional[str]:
    m = pattern.search(body)
    return m.group(1).strip() if m else None


def classify(record: dict, body: str, *, now: Optional[datetime] = None,
             grace_minutes: float = DEFAULT_GRACE_MINUTES, lanes: Optional[set] = None) -> tuple:
    """Return ``(should_close, reason)`` for one leg.

    ``reason`` is human text either way, so a dry run explains every decision
    and a skip is as auditable as an ack.
    """
    status = str(record.get("status") or "").strip().lower()
    if status != "open":
        return False, f"status is {status or 'missing'}, not open"

    goal = str(record.get("goal") or "")
    # Reports by construction win before anything else is inspected: a
    # session-ended notice or a triage digest has a "Next move" section by
    # template, and that is advice, not a baton.
    by_shape = bool(_REPORT_PREFIX.search(goal))
    if not by_shape and _is_addressed(goal, lanes or set()):
        return False, "addressed to a lane in the goal"

    created = str(record.get("created_utc") or "")
    if created:
        try:
            born = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if born.tzinfo is None:
                born = born.replace(tzinfo=timezone.utc)
            age_min = ((now or datetime.now(timezone.utc)) - born).total_seconds() / 60.0
            if age_min < grace_minutes:
                return False, f"only {age_min:.0f} min old (grace {grace_minutes:.0f})"
        except ValueError:
            pass

    ask = _section(body, _ASK_SECTION)
    if ask is not None:
        # "None." alone closes. "None." followed by anything else stays open:
        # the author wrote more for a reason ("None. <owner> tries X when
        # convenient" is a request to a person), and that holds whoever the
        # person is — no name is special-cased here.
        flat = " ".join(ask.split())
        m = re.match(r"^(none|n/a|no ask|nothing)\b[.!:]?(\s*for information only[.!]?)?\s*(.*)$",
                     flat, re.IGNORECASE)
        if not flat:
            return True, "ask section is empty"
        if m and not m.group(3).strip():
            return True, "ask section says none"
        if m:
            return False, "ask says none but adds a request"
        return False, "ask section carries work"

    if by_shape:
        return True, "report-shaped goal prefix"
    if _WORK_HEADING.search(body):
        return False, "body has a work section"
    if _REPORT_WORDS.search(goal):
        return True, "report vocabulary in goal, no ask in body"
    return False, "no ask, but nothing marks it as a report"


def _body_for(path: Path, record: dict) -> str:
    md = path.with_suffix(".md")
    if md.is_file():
        try:
            # errors="replace": one cp1252 body on blade (0x97 em-dash) must
            # not take the whole sweep down. A replaced glyph never changes a
            # decision — the rules read headings and ASCII keywords.
            return md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            pass
    return str(record.get("body") or "")


def scan(root: Path, *, grace_minutes: float = DEFAULT_GRACE_MINUTES) -> list:
    """Every leg in the local registry with its classification."""
    out = []
    lanes = known_lanes(root)
    for path in sorted(core.handoff_dir(root).glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if str(rec.get("status") or "").strip().lower() != "open":
            continue
        close, why = classify(rec, _body_for(path, rec), grace_minutes=grace_minutes, lanes=lanes)
        out.append({"id": path.stem, "goal": str(rec.get("goal") or "")[:100],
                    "machine": rec.get("machine"), "close": close, "reason": why})
    return out


def _stamp_local() -> str:
    """Eastern clock time for the note (Rule 0.8); UTC stays in the record."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/New_York")).strftime("%-I:%M %p %Z %a %-m/%-d")
    except Exception:  # Windows strftime lacks %-I; fall back to portable form
        try:
            from zoneinfo import ZoneInfo
            return datetime.now(ZoneInfo("America/New_York")).strftime("%I:%M %p %Z %a %m/%d").lstrip("0")
        except Exception:
            return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def sweep(root: Path, *, dry: bool = False, limit: int = 50,
          grace_minutes: float = DEFAULT_GRACE_MINUTES, push: bool = True) -> dict:
    """Ack every status-only open leg. One commit, one push, per-record
    gateway projection exactly like the `ack` verb."""
    machine, agent = core.resolve_machine(), core.resolve_agent()
    remote = core.resolve_remote()
    stamp = core._now().isoformat()
    when = _stamp_local()
    rows = scan(root, grace_minutes=grace_minutes)
    picked = [r for r in rows if r["close"]][:limit]
    acked, failed = [], []
    if dry:
        return {"dry": True, "would_close": picked, "kept": [r for r in rows if not r["close"]]}
    for row in picked:
        note = f"auto-close: {row['reason']} (relay autoclose on {machine}, {when})"

        def take(rec, note=note):
            rec["status"] = "acked"
            rec.setdefault("relay", []).append(
                {"event": "ack", "machine": machine, "agent": agent, "at": stamp,
                 "note": note, "auto": True})
        rec = core._touch_record(root, row["id"], take)
        if rec is None:
            failed.append(row["id"])
            continue
        acked.append((row["id"], rec))
    result = {"dry": False, "acked": [i for i, _ in acked], "failed": failed,
              "kept": [r for r in rows if not r["close"]], "pushed": None}
    if not acked:
        return result
    dirname = core.handoff_dir(root).name
    core._git("add", dirname)
    core.stamped_commit(f"relay({machine}): auto-close {len(acked)} status-only leg(s)", dirname)
    if not push:
        result["pushed"] = False
        return result
    upstream_ok = True
    for leg_id, rec in acked:
        up = core._write_registry_record_upstream(root, remote, leg_id, rec, "ack")
        if up is False:
            upstream_ok = False
    result["upstream"] = upstream_ok
    result["pushed"] = bool(core._publish(remote, core.current_branch()))
    return result


def _go_windowless() -> None:
    """Under pythonw every git child allocates its own console and flashes a
    window at the operator (Dave saw it 8:36 AM EDT 2026-09-14, first
    scheduled run). Same fix relay_daemon.py carries: default every
    subprocess to CREATE_NO_WINDOW with stdin closed so git can never prompt."""
    import os
    import subprocess
    if os.name != "nt" or getattr(subprocess, "_nougen_windowless", False):
        return
    flag = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    orig_run, orig_popen = subprocess.run, subprocess.Popen

    def run(*a, **kw):
        kw.setdefault("creationflags", flag)
        if "input" not in kw:
            kw.setdefault("stdin", subprocess.DEVNULL)
        return orig_run(*a, **kw)

    class Popen(orig_popen):
        def __init__(self, *a, **kw):
            kw.setdefault("creationflags", flag)
            kw.setdefault("stdin", subprocess.DEVNULL)
            super().__init__(*a, **kw)

    subprocess.run, subprocess.Popen = run, Popen
    subprocess._nougen_windowless = True


def _rebase_in_progress(root: Path) -> bool:
    return (root / ".git" / "rebase-merge").exists() or (root / ".git" / "rebase-apply").exists()


def heal_rebase(root: Path) -> Optional[str]:
    """Resolve a rebase the sweep's own pull left behind.

    Unattended, a conflict must never park the clone: the 9:35 AM EDT
    2026-09-14 run conflicted on one record another lane had acked in the
    same minute and left ``.git/rebase-merge`` sitting for four hours, which
    silently stopped every later sweep and broke the next human commit.

    A conflict inside ``.handoffs`` always means the same thing — someone
    else already wrote that record — so upstream wins (``--ours`` during a
    rebase). Any conflict outside ``.handoffs`` is not the sweep's to judge:
    abort and leave the tree as it was.
    """
    if not _rebase_in_progress(root):
        return None
    dirname = core.handoff_dir(root).name
    unmerged = (core._git("diff", "--name-only", "--diff-filter=U") or "").split()
    if any(not p.startswith(dirname + "/") for p in unmerged):
        core._git("rebase", "--abort")
        return "aborted: conflict outside {}".format(dirname)
    for path in unmerged:
        core._git("checkout", "--ours", "--", path)
        core._git("add", "--", path)
    for _ in range(20):  # one pass per queued commit; bounded, never spins
        import os
        os.environ.setdefault("GIT_EDITOR", "true")
        core._git("rebase", "--continue")
        if not _rebase_in_progress(root):
            return "healed: upstream kept for {} record(s)".format(len(unmerged))
        more = (core._git("diff", "--name-only", "--diff-filter=U") or "").split()
        if any(not p.startswith(dirname + "/") for p in more):
            break
        for path in more:
            core._git("checkout", "--ours", "--", path)
            core._git("add", "--", path)
    core._git("rebase", "--abort")
    return "aborted: could not finish rebase"


def cmd_autoclose(args: argparse.Namespace) -> int:
    _go_windowless()
    root = core.repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return core.EXIT_FAILURE
    healed = heal_rebase(root)
    if healed:
        print("ℹ️ stale rebase: " + healed)
    if not args.no_fetch and not args.dry_run:
        # --autostash: the unattended task must not be refused by a dirty
        # working tree (a developer's edits in the clone), and the sweep only
        # ever commits .handoffs. Verified 2026-09-14: without it the first
        # live run rebased nothing and pushed onto a base 6 commits stale.
        core._git("pull", "--rebase", "--autostash", "--quiet", core.resolve_remote())
        healed = heal_rebase(root)
        if healed:
            print("ℹ️ pull conflicted: " + healed)
    res = sweep(root, dry=args.dry_run, limit=args.limit, grace_minutes=args.grace,
                push=not args.no_push)
    if args.json:
        print(json.dumps(res, indent=2, default=str))
        return core.EXIT_OK
    if res.get("dry"):
        print(f"would auto-close {len(res['would_close'])} leg(s):")
        for r in res["would_close"]:
            print(f"  ✓ {r['id']}  — {r['reason']}\n      {r['goal']}")
        print(f"kept open {len(res['kept'])}:")
        for r in res["kept"]:
            print(f"  · {r['id']}  — {r['reason']}")
        return core.EXIT_OK
    print(f"✅ auto-closed {len(res['acked'])} leg(s); {len(res['kept'])} still open"
          + ("" if res["pushed"] is None else f"; pushed={res['pushed']}"))
    for i in res["failed"]:
        print(f"  ❌ could not touch {i}")
    return core.EXIT_OK if not res["failed"] else core.EXIT_FAILURE


def add_parser(sub) -> None:
    p = sub.add_parser("autoclose", help="ack status-only open legs (reports, [auto] notices, Ask: None)")
    p.add_argument("--dry-run", action="store_true", help="show decisions, change nothing")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--grace", type=float, default=DEFAULT_GRACE_MINUTES,
                   help="minutes a leg must age before it is eligible")
    p.add_argument("--no-push", action="store_true")
    p.add_argument("--no-fetch", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_autoclose)
