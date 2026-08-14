#!/usr/bin/env python3
"""Cross-machine handoffs that travel through git.

The local `.handoffs/` registry coordinates agents inside one working copy.
This is the same contract for agents on *different machines*, carried by the
remote instead of the filesystem.

The failure it exists to prevent, observed 2026-07-31 on this repo: two
machines built NouGenQ in parallel — one Astro, one Next.js + vinext — against
the same Cloudflare route, and neither knew until a push was rejected. Eleven
commits of work sat on one side of an unrelated history. A handoff read before
work starts makes that collision visible while it is still cheap.

Design constraints that come from git, not from taste:

  * One file per handoff, named with a UTC stamp + machine + agent. Two
    machines writing at once produce two different filenames, so handoffs
    merge without conflicts. There is deliberately no shared index file —
    an index is a guaranteed conflict marker on every concurrent write.
  * Handoffs are tracked, not ignored. They are the payload.
  * `check` is read-only and never mutates a ref. It fetches and reports.

Rule 0.2: machine, agent, branch, sha, remote and the handoff directory all
resolve env -> git/OS probe -> logged fallback. Nothing here is a constant on
the wire.

Usage:
    python tools/git_handoff.py check
    python tools/git_handoff.py create -g "<goal>" -M notes.md
    python tools/git_handoff.py list [-n 10]
    python tools/git_handoff.py latest
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import ui

EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_USAGE = 2
# `check` uses its own code so CI and pre-work hooks can branch on "someone
# else moved" without treating it as a crash.
EXIT_DIVERGED = 3

DEFAULT_DIR = ".handoffs"
DEFAULT_REMOTE = "origin"


# --- probes -----------------------------------------------------------------

def _git(*args: str, cwd: Optional[Path] = None) -> Optional[str]:
    """Run a git command, returning stripped stdout or None if it failed."""
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            # Handoff bodies are UTF-8 and full of status glyphs. Without an
            # explicit encoding Python decodes with the console default
            # (cp1252 on Windows) and `git show` of any emoji-bearing record
            # raises inside a reader thread, taking the command down.
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def repo_root() -> Optional[Path]:
    top = _git("rev-parse", "--show-toplevel")
    return Path(top) if top else None


# Suffixes a machine gets from its network, not from anyone naming it. mDNS
# hands out `.local` and the box is suddenly `kushboygroups-mac-mini-local` in
# every record — a name no operator recognises as theirs. Only these known
# local-network suffixes are stripped: a general FQDN is left alone, because
# `build.corp.example.com` -> `build` would silently collide with a `build` in
# another domain, and a wrong-but-unique name beats a pretty ambiguous one.
_LOCAL_SUFFIXES = (".local", ".lan", ".home", ".internal", ".localdomain")


def _strip_local_suffix(host: str) -> str:
    lowered = host.lower()
    for suffix in _LOCAL_SUFFIXES:
        if lowered.endswith(suffix) and len(host) > len(suffix):
            return host[: -len(suffix)]
    return host


_MACHINE_CACHE: Optional[str] = None


def resolve_machine() -> str:
    """Which physical box this is: env, then git config, then hostname.

    An explicit NOUGEN_MACHINE is passed through untouched — if someone types a
    name with a dot in it, that is their word on what this box is called.

    `git config nougen.machine` is what `relay init --machine` writes, and
    until 2026-08-05 nothing ever read it back: an env-less shell on a freshly
    init'd clone silently stamped the raw hostname, minting a machine name the
    registry had never seen. The shell hook already read the stored value; a
    record and the commit that carries it disagreeing about which box they
    came from is exactly the confident lie this module exists to prevent.
    """
    explicit = os.environ.get("NOUGEN_MACHINE", "").strip()
    if explicit:
        return _slug(explicit)
    global _MACHINE_CACHE
    if _MACHINE_CACHE is None:
        _MACHINE_CACHE = _git("config", "--get", "nougen.machine") or ""
    stored = _MACHINE_CACHE.strip()
    if stored:
        return _slug(stored)
    try:
        return _slug(_strip_local_suffix(socket.gethostname()))
    except Exception:
        return "unknown-machine"


def machine_source() -> str:
    """Where the machine name came from — for `whoami` and for warnings."""
    if os.environ.get("NOUGEN_MACHINE", "").strip():
        return "NOUGEN_MACHINE"
    if (_git("config", "--get", "nougen.machine") or "").strip():
        return "git config nougen.machine"
    return "socket.gethostname()"


UNKNOWN_AGENT = "unknown-agent"


_AGENT_CACHE: Optional[str] = None


def resolve_agent() -> str:
    """Which agent lane is writing: env, then git config, then unknown.

    `git config nougen.agent` exists because the env var was the single
    largest source of friction in real use. It has to be exported in every
    shell that will ever run a relay command *or* a git commit, and the failure
    when it is missing is silent-ish and permanent: a record stamped
    `unknown-agent`, or a commit the hook refuses. Both happened here on
    2026-07-31, to two different machines, on the same day.

    Git config is the right home for it. It is per-clone rather than
    per-shell, it survives new terminals and reboots, it is already how this
    tool learns everything else about a repository, and setting it is a thing
    you do once: `relay init --agent <lane>`.

    Env still wins, so a one-off `NOUGEN_AGENT=other relay ...` overrides the
    stored answer without unsetting anything.
    """
    global _AGENT_CACHE
    env = os.environ.get("NOUGEN_AGENT", "").strip()
    if env:
        return _slug(env)
    if _AGENT_CACHE is None:
        _AGENT_CACHE = _git("config", "--get", "nougen.agent") or ""
    return _slug(_AGENT_CACHE.strip() or UNKNOWN_AGENT)


def agent_source() -> str:
    """Where the agent name came from — for `whoami` and for warnings."""
    if os.environ.get("NOUGEN_AGENT", "").strip():
        return "NOUGEN_AGENT"
    if (_git("config", "--get", "nougen.agent") or "").strip():
        return "git config nougen.agent"
    return "fallback"


def known_machines(root: Path) -> set:
    """Every machine that has already written a record here.

    Read from record filenames — `<UTC>__<machine>__<agent>` — which is the
    same source the commit hook uses, deliberately. Two different notions of
    "known" would be worse than one: a box could pass one check and fail the
    other with no way to tell which was right.
    """
    directory = handoff_dir(root)
    if not directory.is_dir():
        return set()
    seen = set()
    for entry in directory.iterdir():
        parts = entry.name.split("__")
        if len(parts) >= 3:
            seen.add(parts[1])
    return seen


def identity_ok() -> bool:
    """The one deliberate override, matching the hook's."""
    return os.environ.get("NOUGEN_IDENTITY_OK", "").strip() == "1"


def unintroduced_machine_warning(root: Path) -> Optional[str]:
    """Flag a machine name the registry has never seen. None if fine.

    The hook asks this question too, but only where someone ran
    `git config core.hooksPath hooks` — and on most clones here nobody had.
    The tool writes records on every clone, so the tool has to ask it too.

    It *warns* where the hook *refuses*, and the difference is deliberate. A
    box's first write is very often its ack: pull a leg, take the baton, push.
    Refusing that is refusing the workflow relay exists for, and the way out
    would be NOUGEN_IDENTITY_OK=1 in a shell profile — which is the guard
    uninstalling itself, exactly as the hook's own comment warns. The hook can
    refuse because a human is at the keyboard reading the message; the tool
    frequently runs where nobody is.

    Still the check that catches one box under two names, which is how
    `who-mac-mini`, `phoebus` and `kushboygroups-mac-mini-local` all came to
    mean the same Mac.
    """
    if identity_ok():
        return None
    machine = resolve_machine()
    known = known_machines(root)
    # An empty registry means the first record ever — nobody to be unknown to.
    if not known or machine in known:
        return None
    return (
        f"✋ '{machine}' has never written a record in this repo.\n"
        f"   Machines already here: {', '.join(sorted(known))}\n"
        "\n"
        "   If your hostname is not what the fleet calls this box, name it:\n"
        "     export NOUGEN_MACHINE=<the-name-the-fleet-uses>\n"
        "   If this box really is new, this is just a note — the record is\n"
        "   written either way, and the warning stops once it is in the registry."
    )


def warn_if_anonymous() -> None:
    """Say so, loudly, before writing a record with no lane identity.

    The whole registry exists to answer "who did this, on which box". A record
    stamped `unknown-agent` answers half the question and looks authoritative
    doing it. Observed 2026-07-31: NOUGEN_AGENT set on a shell's `git commit`
    line did not reach the python process on the next line, and the ack landed
    anonymous with no indication anything was wrong.

    A warning, not a refusal — an anonymous record still beats a lost one.
    """
    if resolve_agent() == UNKNOWN_AGENT:
        print(
            f"⚠️ no lane configured — this record will be stamped '{UNKNOWN_AGENT}'.\n"
            "   Fix it once, for this clone:  relay init --agent <name>\n"
            "   (or NOUGEN_AGENT=<name> for a one-off)"
        )


def resolve_remote() -> str:
    """Prefer the branch's own upstream remote over a hardcoded 'origin'."""
    branch = current_branch()
    if branch:
        upstream = _git("config", f"branch.{branch}.remote")
        if upstream:
            return upstream
    remotes = _git("remote")
    if remotes:
        names = [r for r in remotes.splitlines() if r.strip()]
        if DEFAULT_REMOTE in names:
            return DEFAULT_REMOTE
        if names:
            return names[0]
    return DEFAULT_REMOTE


def current_branch() -> Optional[str]:
    b = _git("rev-parse", "--abbrev-ref", "HEAD")
    return None if b in (None, "HEAD") else b


def current_sha() -> Optional[str]:
    return _git("rev-parse", "--short", "HEAD")


def handoff_dir(root: Path) -> Path:
    return root / (os.environ.get("NOUGEN_GIT_HANDOFF_DIR", "").strip() or DEFAULT_DIR)


def _slug(text: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in text]
    return "".join(keep).strip("-") or "unknown"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def unique_record_name(directory: Path, stamp: datetime, machine: str, agent: str) -> str:
    """`<utc>__<machine>__<agent>`, disambiguated if that name is taken.

    Two machines writing at the same instant already produce different names —
    the machine segment differs, which is what makes this registry merge without
    conflicts. One machine writing twice inside the same second does not, and
    the id is second-granular. That was harmless while ids were only labels;
    `react` is the first consumer that depends on their uniqueness, and it skips
    any leg whose id it has already seen — so the second leg of a fast pair
    would never fire a rule, silently.

    The counter goes inside the timestamp segment on purpose: machine and agent
    are parsed back out of these filenames (by the commit hook, among others),
    so a suffix anywhere else would corrupt an identity to fix a collision.
    """
    base = stamp.strftime("%Y%m%dT%H%M%SZ")
    suffix = ""
    n = 2
    while any((directory / f"{base}{suffix}__{machine}__{agent}{ext}").exists()
              for ext in (".json", ".md")):
        suffix = f"-{n}"
        n += 1
    return f"{base}{suffix}__{machine}__{agent}"


# --- claims -----------------------------------------------------------------
#
# A handoff says "here is what I did." A claim says "here is what I am ABOUT to
# do." The second is the one that prevents duplicate work, and this tool
# shipped without it: on 2026-07-31 two machines independently built the Astro
# and Next scaffolds, then two handoff tools, then two fixes for the same OAuth
# host bug. Every collision was visible in the registry only after both sides
# had paid for the work.
#
# Claims reuse the handoff storage discipline exactly — one file per claim,
# named with a UTC stamp plus machine and agent, no shared index — so two
# machines claiming at the same moment produce two filenames and merge without
# conflict. A claim is worthless if it is not pushed, so `take` pushes by
# default; a claim sitting unpushed on one box is the failure it exists to stop.

def _publish(remote: str, branch: Optional[str]) -> bool:
    """Push, rebasing once if the remote moved underneath us.

    The common case for a claim is that another machine pushed seconds ago —
    that is the whole reason you are claiming. A bare push would be rejected
    non-fast-forward and leave the claim sitting local, invisible, protecting
    nothing. Records are separate files per machine, so a rebase here is
    mechanical: there is nothing to conflict over.
    """
    if not branch:
        return False
    if _git("push", remote, f"HEAD:{branch}") is not None:
        return True
    if _git("pull", "--rebase", remote, branch) is None:
        return False
    return _git("push", remote, f"HEAD:{branch}") is not None


def stamped_commit(subject: str, *paths: str) -> Optional[str]:
    """Commit a record with its identity already in the message.

    `paths` limits the commit to the registry's own files. Without it this
    commits whatever the operator happened to have staged, under a message that
    describes a claim — measured here on 2026-08-01, where a `claim release`
    swept a source fix, its tests and a new tool into a commit titled
    "claim(whoart): release". Nothing was lost and the code was correct, but
    `git log` then misdescribes the change, which is worse than a failure that
    announces itself: the next person bisecting or auditing reads the subject
    and believes it.

    A tool that commits on your behalf must only ever commit its own paths.

    Every commit this tool writes is one it *knows* the identity of — machine
    and agent were both resolved a few lines earlier to write the record
    itself. Delegating the stamp to prepare-commit-msg made that knowledge
    conditional on a per-clone `git config core.hooksPath hooks` that nobody
    is reminded to run: of the first twenty commits on this repo's main, every
    unstamped one was written by this function's callers, on boxes where that
    step had been missed.

    The hook still matters — it stamps the commits humans and agents write by
    hand. It should not be load-bearing for the commits the tool writes itself.

    `git interpret-trailers` is idempotent and the hook uses the same trailer
    keys, so a clone that *does* have hooks installed sees no duplication.
    """
    message = (
        f"{subject}\n\n"
        f"Machine: {resolve_machine()}\n"
        f"Agent: {resolve_agent()}\n"
    )
    # `--only <paths>` commits exactly these paths and leaves the rest of the
    # index untouched, so an operator's staged work survives intact and stays
    # staged. Without paths this falls back to the old behaviour rather than
    # committing nothing, so an unconverted caller still works.
    args = ["commit", "-m", message]
    if paths:
        args += ["--only", "--", *paths]
    return _git(*args)


def hook_installed(root: Path) -> bool:
    """Whether this clone routes commits through the repo's hooks."""
    configured = _git("config", "core.hooksPath")
    if not configured:
        return False
    path = Path(configured)
    if not path.is_absolute():
        path = root / path
    return (path / "prepare-commit-msg").exists()


def claims_dir(root: Path) -> Path:
    return handoff_dir(root) / "claims"


# Read in order. NOUGEN_SESSION first so a lane can always override, then
# session ids harnesses already export — VERIFIED to exist, not guessed at.
# CLAUDE_CODE_SESSION_ID was confirmed on whoart 2026-08-02 as the per-session
# UUID (it matches the session's own scratchpad directory name). Add another
# only after seeing it on a real box: a variable that is usually unset would
# make this look configured while doing nothing, which is the failure this
# whole mechanism exists to stop.
_SESSION_VARS = ("NOUGEN_SESSION", "CLAUDE_CODE_SESSION_ID")


def resolve_session() -> str:
    """Which SESSION on this lane is speaking, or "" when nothing knows.

    Identity is machine+lane, and that was enough while a lane meant one
    session. On 2026-08-02 two agent sessions ran on whoart under the same
    `claude-cli` lane at the same time: they were invisible to each other's
    claims, and a bare `claim release` in one released the other's, mid-work.

    A `relay` invocation is a fresh process each time, so pid and ppid say
    nothing about which session drove it. What DOES exist is the id the harness
    already keeps: CLAUDE_CODE_SESSION_ID is exported into every tool call, so
    reading it makes this work with nothing to configure. That matters more than
    it sounds — the first cut required NOUGEN_SESSION, and the two sessions that
    collided both had it unset. It then collided AGAIN, in the session writing
    the fix. A mitigation nobody enables prevents nothing.

    When no source answers, the record carries NO session field and every
    consumer behaves exactly as before. Half a discriminator that lies would be
    worse than none, since the whole point is knowing who holds a claim.
    """
    for var in _SESSION_VARS:
        value = os.environ.get(var, "").strip()
        if value:
            return _slug(value)
    return ""


def _claim_ttl_hours() -> float:
    """How long a claim stays binding before it is treated as abandoned.

    A claim that never expires becomes a tombstone: a machine that crashes
    mid-task would block that scope forever, and the next agent would either
    wait on nothing or learn to ignore claims entirely. Both are worse than a
    claim that quietly ages out.
    """
    raw = os.environ.get("NOUGEN_CLAIM_TTL_HOURS", "").strip()
    try:
        return float(raw) if raw else 8.0
    except ValueError:
        return 8.0


def _normalize_scope(scope: str) -> list:
    """Split a scope string into comparable tokens (paths or topic words).

    Separators are folded to `/` because the fleet is mixed. A Windows lane
    claims `src\\lib.py` and a mac lane claims `src/lib.py`; without folding,
    the two share no token and the overlap check reports all-clear on the exact
    collision it exists to catch. Logged as a known bug on 2026-07-31 and
    worked around hook-side rather than fixed; the guard reads git's output,
    which is always POSIX, so a claim typed by hand was the remaining hole.
    """
    cleaned = scope.replace(",", " ").replace("\\", "/")
    parts = [p.strip().strip("/").lower() for p in cleaned.split()]
    return [p for p in parts if p]


def _scopes_overlap(a: str, b: str) -> list:
    """Tokens two scopes share.

    Deliberately literal: prefix matching on path-ish tokens, exact match
    otherwise. A cleverer matcher that guesses at synonyms would produce
    confident false overlaps, and a claim system that cries wolf gets ignored —
    which returns us to the duplicate work it was built to prevent.
    """
    hits = []
    for x in _normalize_scope(a):
        for y in _normalize_scope(b):
            if x == y or x.startswith(y + "/") or y.startswith(x + "/"):
                hits.append(x)
                break
    return sorted(set(hits))


def _claim_age_hours(rec: dict) -> Optional[float]:
    stamp = rec.get("created_utc") or ""
    try:
        return (_now() - datetime.fromisoformat(stamp)).total_seconds() / 3600.0
    except Exception:
        return None


def claim_is_active(rec: dict) -> bool:
    if rec.get("status") != "active":
        return False
    age = _claim_age_hours(rec)
    ttl = rec.get("ttl_hours") or _claim_ttl_hours()
    return age is None or age <= float(ttl)


def _read_claims_from(root: Path, target: Optional[str]) -> list:
    """Claims on a ref (or on disk when target is None)."""
    out = []
    if target is None:
        directory = claims_dir(root)
        if not directory.is_dir():
            return out
        for path in sorted(directory.glob("*.json")):
            try:
                rec = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            rec["_file"] = path.name
            out.append(rec)
        return out

    rel = f"{handoff_dir(root).name}/claims"
    listing = _git("ls-tree", "--name-only", f"{target}:{rel}")
    if not listing:
        return out
    for fname in sorted(listing.splitlines()):
        if not fname.endswith(".json"):
            continue
        blob = _git("show", f"{target}:{rel}/{fname}")
        if not blob:
            continue
        try:
            rec = json.loads(blob)
        except Exception:
            continue
        rec["_file"] = fname
        out.append(rec)
    return out


def foreign_claims(root: Path, *, active_only: bool = True) -> dict:
    """Newest claim per (machine, scope) from every watched ref, excluding ours."""
    machine = resolve_machine()
    found = {}
    for target in watch_targets():
        for rec in _read_claims_from(root, target):
            if rec.get("machine") == machine:
                continue
            if active_only and not claim_is_active(rec):
                continue
            key = (rec.get("machine"), rec.get("scope"))
            prev = found.get(key)
            if prev is None or (rec.get("created_utc") or "") > (prev.get("created_utc") or ""):
                found[key] = rec
    return found


# --- the baton (NouGenRelay lifecycle) --------------------------------------
#
# A claim covers work about to start; a handoff records work that ended. Both
# are one-sided. The leg only closes when someone on the other end picks the
# baton up, and until then a handoff is indistinguishable from one nobody read.
#
# So a record carries a status. It is `open` when written and stays open until
# another machine acks it. That makes a DROPPED baton visible — the failure
# mode a write-only registry can never surface, because an ignored handoff and
# a handled one look identical on disk.
#
# Records written before this existed have no status field and read as `open`,
# which is the honest answer for them: nobody ever acked them.

RELAY_STATES = ("open", "acked", "in_progress", "blocked", "complete")


def record_id(rec: dict, path: Optional[Path] = None) -> Optional[str]:
    """A record's id: the embedded field, else the filename stem.

    Records written before ids were embedded have none, so the filename
    remains the fallback — that is what every existing leg in the fleet
    depends on and it must keep working.
    """
    embedded = (rec.get("id") or "").strip()
    if embedded:
        return embedded
    if path is not None:
        return path.stem
    stem = (rec.get("_file") or "").strip()
    return stem[:-5] if stem.endswith(".json") else (stem or None)


def _record_path(root: Path, handoff_id: str) -> Optional[Path]:
    """Resolve an id to a file, exact matches first.

    Order matters. Globbing a substring can match more than one leg, and
    picking the newest of several is a silent wrong-record edit. Exact
    filename, then exact embedded id, then — only if nothing exact matched —
    a substring search that refuses to guess when it is ambiguous.
    """
    directory = handoff_dir(root)
    candidate = directory / f"{handoff_id}.json"
    if candidate.is_file():
        return candidate

    for path in sorted(directory.glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if (rec.get("id") or "").strip() == handoff_id:
            return path

    matches = sorted(directory.glob(f"*{handoff_id}*.json"))
    if len(matches) > 1:
        print(f"❌ ambiguous id {handoff_id!r} matches {len(matches)} records:")
        for m in matches:
            print(f"     {m.stem}")
        print("   Pass a full id — refusing to guess which leg you meant.")
        return None
    return matches[0] if matches else None


def relay_status(rec: dict) -> str:
    return rec.get("status") or "open"


def _open_legs(root: Path) -> list:
    """Handoffs from OTHER machines that nobody has acked."""
    machine = resolve_machine()
    out = []
    for target in watch_targets():
        for rec in _remote_handoffs(root, target):
            if rec.get("machine") == machine:
                continue
            if relay_status(rec) == "open":
                out.append(rec)
    seen, unique = set(), []
    for rec in sorted(out, key=lambda r: r.get("created_utc") or ""):
        key = rec.get("_file")
        if key in seen:
            continue
        seen.add(key)
        unique.append(rec)
    return unique


def _touch_record(root: Path, handoff_id: Optional[str], mutate) -> Optional[dict]:
    """Apply `mutate` to a record on disk, newest open one if no id is given."""
    directory = handoff_dir(root)
    if handoff_id:
        path = _record_path(root, handoff_id)
    else:
        machine = resolve_machine()
        candidates = [
            p for p in sorted(directory.glob("*.json"))
            # Default to a leg from someone else: acking your own note is
            # almost never what you meant.
            if machine not in p.name
        ]
        path = candidates[-1] if candidates else None
    if path is None or not path.is_file():
        return None
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    mutate(rec)
    path.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    rec["_file"] = path.name
    return rec


def cmd_relay(args: argparse.Namespace) -> int:
    warn_if_anonymous()
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE

    # Only writes are flagged: warning on a read would make the guard noise on
    # the very command you run to find out which name the fleet uses.
    if args.action in {"ack", "checkpoint", "complete"}:
        warning = unintroduced_machine_warning(root)
        if warning:
            print(warning)

    machine, agent = resolve_machine(), resolve_agent()
    remote = resolve_remote()
    action = args.action

    if action == "open":
        if not args.no_fetch:
            _git("fetch", remote)
        legs = _open_legs(root)
        if not legs:
            print("✅ no unacked legs — every baton has been picked up")
            return EXIT_OK
        print(ui.label("⚠️", ui.head(f"{len(legs)} leg(s) waiting for an ack:"), "yellow"))
        for rec in legs:
            who = f"{ui.machine(str(rec.get('machine')))}/{ui.lane(str(rec.get('agent')))}"
            print(f"  {ui.warn('•')} {who} — {rec.get('goal') or ui.dim('(no goal)')}")
            print(f"     {ui.dim('id')} {ui.ident((rec.get('_file') or '').replace('.json', ''))}")
            print(ui.dim(f"     {rec.get('created_utc')} · {rec.get('branch')}@{rec.get('sha')}"))
        print(f"  {ui.dim('Take one:')} relay ack --id <id>")
        return EXIT_DIVERGED

    stamp = _now().isoformat()

    if action == "ack":
        def take(rec):
            rec["status"] = "acked"
            rec.setdefault("relay", []).append(
                {"event": "ack", "machine": machine, "agent": agent, "at": stamp,
                 "note": args.message or ""}
            )
        rec = _touch_record(root, args.id, take)
        if rec is None:
            print("❌ no matching handoff record found")
            return EXIT_FAILURE
        print(f"✅ baton taken by {machine}/{agent}: {rec.get('goal') or rec['_file']}")

    elif action in ("checkpoint", "complete"):
        state = "complete" if action == "complete" else (args.state or "in_progress")
        if state not in RELAY_STATES:
            print(f"❌ unknown state {state!r} — one of {', '.join(RELAY_STATES)}")
            return EXIT_USAGE

        def mark(rec):
            rec["status"] = state
            rec.setdefault("relay", []).append(
                {"event": action, "state": state, "machine": machine,
                 "agent": agent, "at": stamp, "note": args.message or ""}
            )
        rec = _touch_record(root, args.id, mark)
        if rec is None:
            print("❌ no matching handoff record found")
            return EXIT_FAILURE
        glyph = "✅" if state == "complete" else ("❌" if state == "blocked" else "ℹ️")
        print(f"{glyph} {rec['_file']} -> {state}")

    else:
        print(f"❌ unknown relay action: {action}")
        return EXIT_USAGE

    if args.no_push:
        print("⚠️ --no-push: the other machines will not see this until you push")
        return EXIT_OK
    _git("add", handoff_dir(root).name)
    stamped_commit(f"relay({machine}): {action} {rec.get('goal') or rec['_file']}",
                   handoff_dir(root).name)
    if not _publish(remote, current_branch()):
        print("⚠️ push failed — this leg is local only. Reconcile and push.")
        return EXIT_FAILURE
    return EXIT_OK


def cmd_claim(args: argparse.Namespace) -> int:
    warn_if_anonymous()
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE

    # Only writes are flagged: warning on a read would make the guard noise on
    # the very command you run to find out which name the fleet uses.
    if args.action in {"take", "release"}:
        warning = unintroduced_machine_warning(root)
        if warning:
            print(warning)

    action = args.action
    machine, agent = resolve_machine(), resolve_agent()
    session = resolve_session()
    remote = resolve_remote()

    if action in ("take", "check"):
        if not args.scope:
            print("❌ --scope is required (paths and/or topic words)")
            return EXIT_USAGE
        if not args.no_fetch:
            _git("fetch", remote)

        conflicts = []
        for (other, scope), rec in foreign_claims(root).items():
            shared = _scopes_overlap(args.scope, scope or "")
            if shared:
                conflicts.append((other, rec, shared))

        if conflicts:
            print(f"⚠️ {len(conflicts)} active claim(s) overlap this scope:")
            for other, rec, shared in conflicts:
                age = _claim_age_hours(rec)
                age_s = f"{age:.1f}h ago" if age is not None else "unknown age"
                print(f"  ⚠️ {other}/{rec.get('agent')} — \"{rec.get('goal') or '(no goal)'}\"")
                print(f"     scope: {rec.get('scope')}")
                print(f"     overlap: {', '.join(shared)} · claimed {age_s}")
        else:
            print("✅ no active claim overlaps this scope")

        if action == "check":
            return EXIT_DIVERGED if conflicts else EXIT_OK
        if conflicts and not args.force:
            print("❌ not claiming. Coordinate first, or re-run with --force to claim anyway.")
            return EXIT_FAILURE

        stamp = _now()
        outdir = claims_dir(root)
        outdir.mkdir(parents=True, exist_ok=True)
        name = unique_record_name(outdir, stamp, machine, agent)
        rec = {
            "machine": machine,
            "agent": agent,
            "goal": args.goal or "",
            "scope": args.scope,
            "status": "active",
            # Omitted entirely when unknown, so a reader can tell "a different
            # session" from "nobody recorded one" — they need different answers.
            **({"session": session} if session else {}),
            "branch": current_branch(),
            "sha": current_sha(),
            "created_utc": stamp.isoformat(),
            "ttl_hours": args.ttl if args.ttl is not None else _claim_ttl_hours(),
        }
        (outdir / f"{name}.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        print(f"✅ claimed: {args.scope}")

        if args.no_push:
            print("⚠️ --no-push: this claim is invisible to the other machines until you push it")
            return EXIT_OK
        rel = f"{handoff_dir(root).name}/claims"
        _git("add", rel)
        stamped_commit(f"claim({machine}): {args.goal or args.scope}",
                       f"{handoff_dir(root).name}/claims")
        if not _publish(remote, current_branch()):
            print("⚠️ push failed — claim is local only, and an unpublished claim")
            print("   protects nothing. Reconcile and push before starting work.")
            return EXIT_FAILURE
        print(f"ℹ️ published to {remote}/{current_branch()}")
        return EXIT_OK

    if action == "list":
        if not args.no_fetch:
            _git("fetch", remote)
        mine = [r for r in _read_claims_from(root, None) if r.get("machine") == machine]
        theirs = foreign_claims(root, active_only=not args.all)
        rows = [("mine", r) for r in mine if args.all or claim_is_active(r)]
        rows += [("theirs", r) for r in theirs.values()]
        if not rows:
            print("ℹ️ no claims recorded")
            return EXIT_OK
        print(f"🔍 Found {len(rows)} claim(s)")
        for whose, rec in rows:
            age = _claim_age_hours(rec)
            state = "active" if claim_is_active(rec) else (rec.get("status") or "expired")
            print(f"  [{whose:<6}] {rec.get('machine')}/{rec.get('agent')} · {state}"
                  f" · {f'{age:.1f}h' if age is not None else '?'}")
            print(f"           scope: {rec.get('scope')}")
            if rec.get("goal"):
                print(f"           goal:  {rec['goal']}")
        return EXIT_OK

    if action == "release":
        directory = claims_dir(root)
        released = 0
        skipped_other_session = 0
        for rec in _read_claims_from(root, None):
            if rec.get("machine") != machine or rec.get("status") != "active":
                continue
            if args.scope and not _scopes_overlap(args.scope, rec.get("scope") or ""):
                continue
            # A claim that names a DIFFERENT session belongs to a sibling still
            # working. Releasing it is what happened on 2026-08-02, mid-task.
            # Claims with no session recorded are released as before, so this
            # changes nothing for a fleet that does not set NOUGEN_SESSION.
            held = rec.get("session")
            if held and session and held != session and not args.all_sessions:
                skipped_other_session += 1
                continue
            rec["status"] = "released"
            rec["released_utc"] = _now().isoformat()
            fname = rec.pop("_file")
            (directory / fname).write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
            released += 1
        if skipped_other_session:
            print(f"ℹ️ left {skipped_other_session} claim(s) held by another session "
                  f"on this lane  ({ui.dim('--all-sessions to take them too')})")
        if not released:
            print("ℹ️ nothing to release")
            return EXIT_OK
        print(f"✅ released {released} claim(s)")
        if args.no_push:
            return EXIT_OK
        _git("add", f"{handoff_dir(root).name}/claims")
        stamped_commit(f"claim({machine}): release",
                       f"{handoff_dir(root).name}/claims")
        if not _publish(remote, current_branch()):
            print("⚠️ release is local only — push it so others see the scope freed")
            return EXIT_FAILURE
        return EXIT_OK

    print(f"❌ unknown claim action: {action}")
    return EXIT_USAGE


# --- stack fingerprint ------------------------------------------------------

def stack_fingerprint(root: Path) -> dict:
    """A cheap read of what this tree actually is.

    Two machines agreeing on a repo name while disagreeing on the framework is
    the exact collision this tool was written for, so the fingerprint travels
    inside every handoff. Detection is by observation — read the manifest — not
    by a remembered list of what this project 'should' be.
    """
    fp: dict = {"manifests": [], "frameworks": []}
    pkg = root / "package.json"
    if pkg.is_file():
        fp["manifests"].append("package.json")
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        deps = {}
        for key in ("dependencies", "devDependencies"):
            value = data.get(key)
            if isinstance(value, dict):
                deps.update(value)
        # Report what is present with the version actually pinned, so a reader
        # sees "astro ^5.0.0" vs "next 16.2.12" instead of a boolean.
        for name in ("next", "astro", "vite", "vinext", "react", "svelte", "nuxt", "remix"):
            if name in deps:
                fp["frameworks"].append(f"{name} {deps[name]}")
        if data.get("name"):
            fp["package_name"] = data["name"]
    for manifest in ("pyproject.toml", "Cargo.toml", "go.mod", "requirements.txt"):
        if (root / manifest).is_file():
            fp["manifests"].append(manifest)
    return fp


# --- write ------------------------------------------------------------------

def cmd_create(args: argparse.Namespace) -> int:
    warn_if_anonymous()
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE

    warning = unintroduced_machine_warning(root)
    if warning:
        print(warning)

    if args.message_file:
        path = Path(args.message_file)
        if not path.is_file():
            print(f"❌ message file not found: {path}")
            return EXIT_USAGE
        body = path.read_text(encoding="utf-8")
    elif args.message:
        # Mirrors the local writer's warning: a shell eats a multi-line -m and
        # silently lands the first line only. Say so rather than truncating.
        if "\n" in args.message:
            print("⚠️ multi-line -m survives poorly through shells — prefer -M/--message-file")
        body = args.message
    else:
        body = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not body.strip():
        print("❌ empty handoff body — pass -M <file>, -m <text>, or pipe stdin")
        return EXIT_USAGE

    machine, agent = resolve_machine(), resolve_agent()
    stamp = _now()
    outdir = handoff_dir(root)
    outdir.mkdir(parents=True, exist_ok=True)
    name = unique_record_name(outdir, stamp, machine, agent)

    record = {
        # The leg's identity, carried IN the record rather than only in the
        # filename. Without this a rename silently destroys identity and `ack
        # --id` has to glob for a substring — which can match the wrong leg.
        # Kept equal to the filename stem so every id already in circulation
        # keeps resolving.
        "id": name,
        "machine": machine,
        "agent": agent,
        "goal": args.goal or "",
        "branch": current_branch(),
        "sha": current_sha(),
        "remote": resolve_remote(),
        "created_utc": stamp.isoformat(),
        "stack": stack_fingerprint(root),
        "dirty": bool(_git("status", "--porcelain")),
        # Open until another machine acks it. An unacked leg is a dropped
        # baton, and that is only visible if the record says so.
        "status": "open",
    }

    (outdir / f"{name}.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )

    header = [
        f"# 🤝 Git Handoff — {machine} / {agent}",
        "",
        f"**Goal**: {record['goal'] or '(none stated)'}",
        f"**Branch**: `{record['branch']}` @ `{record['sha']}`"
        + ("  ⚠️ uncommitted changes present" if record["dirty"] else ""),
        f"**Stack**: {', '.join(record['stack'].get('frameworks') or ['(undetected)'])}",
        f"**When**: {record['created_utc']}",
        "",
        "---",
        "",
    ]
    (outdir / f"{name}.md").write_text(
        "\n".join(header) + body.rstrip() + "\n", encoding="utf-8"
    )

    print(f"✅ git handoff written: {outdir.name}/{name}.md")
    print("ℹ️ commit and push it so the other machines can read it")
    return EXIT_OK


# --- read -------------------------------------------------------------------

def _records(root: Path) -> list:
    outdir = handoff_dir(root)
    if not outdir.is_dir():
        return []
    found = []
    for path in sorted(outdir.glob("*.json")):
        try:
            found.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except Exception:
            continue  # a malformed handoff must not blind the rest
    return found


def cmd_list(args: argparse.Namespace) -> int:
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE
    found = _records(root)
    if not found:
        print("ℹ️ no git handoffs recorded yet")
        return EXIT_OK
    print(f"🔍 Found {len(found)} git handoff(s)")
    for path, rec in found[-args.number:]:
        flag = " ⚠️dirty" if rec.get("dirty") else ""
        flag += f" [{relay_status(rec)}]"
        print(
            f"  {rec.get('created_utc', '?')} | {rec.get('machine', '?')}"
            f"/{rec.get('agent', '?')} | {rec.get('branch', '?')}@{rec.get('sha', '?')}"
            f"{flag} | {rec.get('goal', '')}"
        )
    return EXIT_OK


def cmd_latest(args: argparse.Namespace) -> int:
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE
    found = _records(root)
    if not found:
        print("ℹ️ no git handoffs recorded yet")
        return EXIT_OK
    path, _ = found[-1]
    md = path.with_suffix(".md")
    print(md.read_text(encoding="utf-8") if md.is_file() else json.dumps(_records(root)[-1][1], indent=2))
    return EXIT_OK


def cmd_check(args: argparse.Namespace) -> int:
    """Read-only pre-flight. Run this BEFORE starting work, not after."""
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE

    machine, agent = resolve_machine(), resolve_agent()
    branch, remote = current_branch(), resolve_remote()
    print(f"ℹ️ {machine}/{agent} on `{branch}` → remote `{remote}`")

    if not args.no_fetch:
        if _git("fetch", remote) is None:
            print(f"⚠️ could not fetch `{remote}` — reporting on stale refs")

    diverged = False

    # Compare against the branch's upstream when it has one; fall back to the
    # remote's HEAD, which is what a fresh clone would land on.
    upstream = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    target = upstream or _git("rev-parse", "--abbrev-ref", f"{remote}/HEAD")
    if not target:
        print(f"⚠️ `{branch}` has no upstream and `{remote}` has no HEAD — nothing to compare")
        return EXIT_OK

    counts = _git("rev-list", "--left-right", "--count", f"{target}...HEAD")
    if counts:
        behind, ahead = (counts.split() + ["0", "0"])[:2]
        if behind != "0" or ahead != "0":
            diverged = True
            print(f"⚠️ {target} is {behind} ahead of you, you are {ahead} ahead of it")
        else:
            print(f"✅ in sync with {target}")

        base = _git("merge-base", target, "HEAD")
        if base is None and behind != "0":
            print(f"❌ UNRELATED HISTORIES with {target} — do not force-push, reconcile first")

    # Stack drift: what the remote thinks this project is vs what is on disk.
    mine = stack_fingerprint(root)
    theirs_raw = _git("show", f"{target}:package.json")
    if theirs_raw:
        try:
            theirs_data = json.loads(theirs_raw)
        except Exception:
            theirs_data = {}
        deps = {}
        for key in ("dependencies", "devDependencies"):
            value = theirs_data.get(key)
            if isinstance(value, dict):
                deps.update(value)
        theirs = sorted(
            f"{n} {deps[n]}"
            for n in ("next", "astro", "vite", "vinext", "react", "svelte", "nuxt", "remix")
            if n in deps
        )
        if theirs and sorted(mine.get("frameworks", [])) != theirs:
            diverged = True
            print(f"⚠️ STACK DRIFT — yours: {', '.join(mine.get('frameworks') or ['(none)'])}")
            print(f"              {target}: {', '.join(theirs)}")

    # Whose handoffs exist on the remote that are not yours.
    listing = _git("ls-tree", "--name-only", f"{target}:{handoff_dir(root).name}")
    if listing:
        others = sorted(
            {
                f.split("__")[1]
                for f in listing.splitlines()
                if f.endswith(".md") and f.count("__") >= 2
            }
            - {machine}
        )
        if others:
            print(f"ℹ️ other machines with handoffs on {target}: {', '.join(others)}")
            print(f"ℹ️ read them: git show {target}:{handoff_dir(root).name}/<file>")
    else:
        print(f"⚠️ no handoff registry on {target} yet — you are the first to publish one")

    return EXIT_DIVERGED if diverged else EXIT_OK


# --- identity ---------------------------------------------------------------

def identity() -> dict:
    """Who and where, with the provenance of each answer.

    Provenance matters: a handoff that says `blade1tb` is only trustworthy if
    the reader can tell whether that came from an env var someone set or from
    the OS itself. Both are legitimate; conflating them is not.
    """
    try:
        host = socket.gethostname()
    except Exception:
        host = ""
    return {
        "machine": resolve_machine(),
        "machine_source": machine_source(),
        "hostname": host,
        "agent": resolve_agent(),
        "agent_source": agent_source(),
        "branch": current_branch(),
        "sha": current_sha(),
        "remote": resolve_remote(),
    }


def cmd_whoami(args: argparse.Namespace) -> int:
    ident = identity()
    if args.json:
        print(json.dumps(ident, indent=2))
        return EXIT_OK
    host = ident["hostname"] or "?"
    machine_via = ui.dim(f"(via {ident['machine_source']}; hostname={host})")
    agent_via = ui.dim(f"(via {ident['agent_source']})")
    remote_via = ui.dim(f"→ {ident['remote']}")
    print(ui.label("🧠", ui.kv("machine", f"{ui.machine(ident['machine'])}  {machine_via}")))
    print(ui.label("🤝", ui.kv("agent", f"{ui.lane(ident['agent'])}  {agent_via}")))
    print(ui.label("ℹ️", ui.kv("branch",
                               f"{ident['branch']}@{ui.ident(str(ident['sha']))} {remote_via}")))
    # A missing hook is invisible until someone reads the history back and finds
    # a month of unattributed commits. Say it where identity is the question.
    root = repo_root()
    if root is not None and not hook_installed(root):
        print("⚠️ hook      not installed in this clone — commits you write by hand")
        print("             carry no identity. Records this tool writes are stamped")
        print("             either way. Fix: git config core.hooksPath hooks")
    return EXIT_OK


# --- triggers ---------------------------------------------------------------

def _stale_hours() -> float:
    """Freshness budget. Matches the local lane_freshness default of 48h."""
    raw = os.environ.get("NOUGEN_HANDOFF_STALE_HOURS", "").strip()
    try:
        return float(raw) if raw else 48.0
    except ValueError:
        return 48.0


def _remote_handoffs(root: Path, target: str) -> list:
    """Handoff records that exist on `target`, newest last."""
    dirname = handoff_dir(root).name
    listing = _git("ls-tree", "--name-only", f"{target}:{dirname}")
    if not listing:
        return []
    out = []
    for fname in sorted(listing.splitlines()):
        if not fname.endswith(".json"):
            continue
        blob = _git("show", f"{target}:{dirname}/{fname}")
        if not blob:
            continue
        try:
            rec = json.loads(blob)
        except Exception:
            continue
        rec["_file"] = fname
        out.append(rec)
    return out


def watch_targets(remote: Optional[str] = None) -> list:
    """Refs worth comparing against, most relevant first.

    Your own upstream is not enough. Once this branch has its own upstream,
    comparing only against it hides the very thing the tool exists to catch —
    another machine landing work on the default branch. So the default branch
    is always watched too, and any extra refs named in NOUGEN_HANDOFF_WATCH
    (comma-separated) are appended.
    """
    remote = remote or resolve_remote()
    ordered = []
    upstream = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if upstream:
        ordered.append(upstream)
    default = _git("rev-parse", "--abbrev-ref", f"{remote}/HEAD")
    if default:
        ordered.append(default)
    for extra in os.environ.get("NOUGEN_HANDOFF_WATCH", "").split(","):
        extra = extra.strip()
        if extra:
            ordered.append(extra)
    # Dedupe, preserve order, and drop refs git cannot resolve.
    seen, out = set(), []
    for ref in ordered:
        if ref in seen:
            continue
        seen.add(ref)
        if _git("rev-parse", "--verify", "--quiet", ref) is not None:
            out.append(ref)
    return out


def evaluate_triggers(root: Path, *, fetch: bool = True) -> list:
    """Return the list of fired triggers, each a dict with level/name/detail.

    Every trigger is a comparison against *observed* remote state, never
    against a remembered assumption about what the other machine is doing.
    """
    fired = []
    machine = resolve_machine()
    remote = resolve_remote()

    if fetch:
        _git("fetch", remote)

    targets = watch_targets(remote)
    if not targets:
        return fired

    ahead = "0"
    mine = sorted(stack_fingerprint(root).get("frameworks", []))
    seen_foreign = {}

    for target in targets:
        counts = _git("rev-list", "--left-right", "--count", f"{target}...HEAD")
        behind = "0"
        if counts:
            behind, ahead_here = (counts.split() + ["0", "0"])[:2]
            # `ahead` is only meaningful against our own upstream.
            if target == targets[0]:
                ahead = ahead_here
            if behind != "0":
                fired.append({
                    "level": "warn",
                    "name": "remote_moved",
                    "detail": f"{target} has {behind} commit(s) you do not have",
                })

        if behind != "0" and _git("merge-base", target, "HEAD") is None:
            fired.append({
                "level": "error",
                "name": "unrelated_histories",
                "detail": f"no merge-base with {target} — reconcile, never force-push",
            })

        theirs_raw = _git("show", f"{target}:package.json")
        if theirs_raw:
            try:
                data = json.loads(theirs_raw)
            except Exception:
                data = {}
            deps = {}
            for key in ("dependencies", "devDependencies"):
                value = data.get(key)
                if isinstance(value, dict):
                    deps.update(value)
            theirs = sorted(
                f"{n} {deps[n]}"
                for n in ("next", "astro", "vite", "vinext", "react", "svelte", "nuxt", "remix")
                if n in deps
            )
            if theirs and mine != theirs:
                fired.append({
                    "level": "warn",
                    "name": "stack_drift",
                    "detail": f"yours [{', '.join(mine) or 'none'}] vs {target} [{', '.join(theirs)}]",
                })

        for rec in _remote_handoffs(root, target):
            if rec.get("machine") and rec["machine"] != machine:
                # Keep the newest per machine, whichever branch carries it.
                prev = seen_foreign.get(rec["machine"])
                if prev is None or (rec.get("created_utc") or "") > (prev.get("created_utc") or ""):
                    seen_foreign[rec["machine"]] = rec

    for other, rec in sorted(seen_foreign.items()):
        fired.append({
            "level": "info",
            "name": "foreign_handoff",
            "detail": f"{other}/{rec.get('agent')} published "
                      f"\"{rec.get('goal') or '(no goal)'}\" at {rec.get('created_utc')}",
        })

    # Active claims outrank finished handoffs: they describe work in flight,
    # which is the only kind you can still avoid duplicating.
    for (other, scope), rec in sorted(foreign_claims(root).items(), key=lambda kv: str(kv[0])):
        age = _claim_age_hours(rec)
        fired.append({
            "level": "warn",
            "name": "foreign_claim",
            "detail": f"{other}/{rec.get('agent')} is working on [{scope}]"
                      f" — \"{rec.get('goal') or '(no goal)'}\""
                      + (f" ({age:.1f}h ago)" if age is not None else ""),
        })

    unacked = _open_legs(root)
    if unacked:
        oldest = unacked[0]
        fired.append({
            "level": "warn",
            "name": "unacked_leg",
            "detail": f"{len(unacked)} leg(s) nobody has acked; oldest is "
                      f"{oldest.get('machine')}/{oldest.get('agent')} "
                      f"\"{oldest.get('goal') or '(no goal)'}\"",
        })

    mine_local = [r for _p, r in _records(root) if r.get("machine") == machine]
    budget = _stale_hours()
    if not mine_local:
        fired.append({
            "level": "info",
            "name": "no_handoff_from_this_machine",
            "detail": f"{machine} has never published a handoff here",
        })
    else:
        last = mine_local[-1].get("created_utc") or ""
        try:
            age_h = (_now() - datetime.fromisoformat(last)).total_seconds() / 3600.0
            if age_h > budget:
                fired.append({
                    "level": "warn",
                    "name": "stale_handoff",
                    "detail": f"last {machine} handoff is {age_h:.1f}h old (budget {budget:.0f}h)",
                })
        except Exception:
            pass

    if ahead != "0" and _git("status", "--porcelain"):
        fired.append({
            "level": "info",
            "name": "unpushed_and_dirty",
            "detail": f"{ahead} unpushed commit(s) plus uncommitted changes on this machine",
        })

    return fired


_LEVEL_GLYPH = {"error": "❌", "warn": "⚠️", "info": "ℹ️"}


def cmd_triggers(args: argparse.Namespace) -> int:
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE
    fired = evaluate_triggers(root, fetch=not args.no_fetch)
    if args.json:
        print(json.dumps(fired, indent=2))
    elif not fired:
        print("✅ no triggers fired")
    else:
        for t in fired:
            print(f"{_LEVEL_GLYPH.get(t['level'], 'ℹ️')} {t['name']}: {t['detail']}")
    if any(t["level"] == "error" for t in fired):
        return EXIT_FAILURE
    return EXIT_DIVERGED if fired else EXIT_OK


def cmd_pull(args: argparse.Namespace) -> int:
    """Render what the OTHER machines have published, newest first."""
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE
    remote = resolve_remote()
    if not args.no_fetch:
        _git("fetch", remote)
    target = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}") \
        or _git("rev-parse", "--abbrev-ref", f"{remote}/HEAD")
    if not target:
        print("⚠️ no upstream to pull handoffs from")
        return EXIT_OK

    machine = resolve_machine()
    records = _remote_handoffs(root, target)
    foreign = [r for r in records if r.get("machine") != machine]
    if not foreign:
        print(f"ℹ️ no handoffs from other machines on {target}")
        return EXIT_OK

    dirname = handoff_dir(root).name
    for rec in list(reversed(foreign))[: args.number]:
        print(f"🤝 {rec.get('machine')}/{rec.get('agent')} — {rec.get('goal') or '(no goal)'}")
        print(f"   {rec.get('created_utc')} · {rec.get('branch')}@{rec.get('sha')}"
              f" · stack: {', '.join(rec.get('stack', {}).get('frameworks') or ['(undetected)'])}")
        if args.full:
            body = _git("show", f"{target}:{dirname}/{rec['_file'].replace('.json', '.md')}")
            if body:
                print(body)
        print()
    return EXIT_OK


def cmd_init(args: argparse.Namespace) -> int:
    """Store this clone's lane once, so nothing has to be exported again."""
    root = repo_root()
    if root is None:
        print("✋ not inside a git work tree")
        return EXIT_FAILURE
    agent = (args.agent or "").strip()
    if not agent:
        print("✋ name the lane: relay init --agent <name>   (e.g. claude-cli)")
        return EXIT_USAGE
    if _git("config", "nougen.agent", _slug(agent)) is None:
        print("✋ could not write git config nougen.agent")
        return EXIT_FAILURE
    global _AGENT_CACHE, _MACHINE_CACHE
    _AGENT_CACHE = None
    if args.machine:
        _git("config", "nougen.machine", _slug(args.machine))
        _MACHINE_CACHE = None
    if not hook_installed(root):
        _git("config", "core.hooksPath", "hooks")
    print(f"✅ this clone is {resolve_machine()}/{resolve_agent()}")
    print("   stored in git config — no exports, survives new shells")
    return EXIT_OK


def cmd_status(args: argparse.Namespace) -> int:
    """`relay` with no arguments: everything you need before starting work.

    Three questions were being asked as three commands — has anything moved,
    is a leg waiting, is anyone in my way — and in practice the first two got
    skipped. One command with no flags is the only version people actually run.
    """
    root = repo_root()
    if root is None:
        print("✋ not inside a git work tree")
        return EXIT_FAILURE
    print(f"🧠 {resolve_machine()}/{resolve_agent()}  ({agent_source()})")
    worst = EXIT_OK
    for fn in (cmd_check, lambda a: cmd_relay(_ns(action="open")), cmd_claim):
        try:
            rc = fn(args if fn is cmd_check else _ns(action="list"))
        except Exception as exc:  # a status view must never be the thing that fails
            print(f"   (skipped: {type(exc).__name__})")
            continue
        worst = rc if rc and not worst else worst
    return worst


def _ns(**kw) -> argparse.Namespace:
    base = dict(id=None, state=None, message="", no_push=True, no_fetch=True,
                scope=None, goal=None, ttl=None, force=False, action=None, all=False)
    base.update(kw)
    return argparse.Namespace(**base)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="git_handoff",
        description="Cross-machine agent handoffs carried by git.",
    )
    sub = p.add_subparsers(dest="command")

    c = sub.add_parser("create", help="write a handoff for the other machines")
    c.add_argument("-g", "--goal", default="", help="one-line goal")
    c.add_argument("-m", "--message", help="body text (single line; prefer -M)")
    c.add_argument("-M", "--message-file", help="path to a UTF-8 markdown body")
    c.set_defaults(func=cmd_create)

    listing = sub.add_parser("list", help="list recorded handoffs")
    listing.add_argument("-n", "--number", type=int, default=10)
    listing.set_defaults(func=cmd_list)

    sub.add_parser("latest", help="print the most recent handoff").set_defaults(func=cmd_latest)

    k = sub.add_parser("check", help="pre-flight: has another machine moved?")
    k.add_argument("--no-fetch", action="store_true", help="report on refs already local")
    k.set_defaults(func=cmd_check)

    w = sub.add_parser("whoami", help="resolved machine/agent identity and its provenance")
    w.add_argument("--json", action="store_true")
    w.set_defaults(func=cmd_whoami)

    t = sub.add_parser("triggers", help="evaluate cross-machine trigger conditions")
    t.add_argument("--json", action="store_true")
    t.add_argument("--no-fetch", action="store_true")
    t.set_defaults(func=cmd_triggers)

    c2 = sub.add_parser("claim", help="announce work BEFORE starting it")
    c2.add_argument("--all-sessions", action="store_true",
                    help="(release) also release claims held by another session on this lane")
    c2.add_argument("action", choices=["take", "check", "list", "release"])
    c2.add_argument("-s", "--scope", help="paths and/or topic words this work touches")
    c2.add_argument("-g", "--goal", default="", help="one-line intent")
    c2.add_argument("--ttl", type=float, help="hours before the claim ages out")
    c2.add_argument("--force", action="store_true", help="claim despite an overlap")
    c2.add_argument("--all", action="store_true", help="list expired/released too")
    c2.add_argument("--no-push", action="store_true", help="keep the claim local (it will be invisible)")
    c2.add_argument("--no-fetch", action="store_true")
    c2.set_defaults(func=cmd_claim)

    r = sub.add_parser("relay", help="the baton: ack / checkpoint / complete a leg")
    r.add_argument("action", choices=["open", "ack", "checkpoint", "complete"])
    r.add_argument("--id", help="record id (defaults to the newest foreign leg)")
    r.add_argument("--state", choices=list(RELAY_STATES), help="checkpoint state")
    r.add_argument("-m", "--message", default="", help="note recorded with the event")
    r.add_argument("--no-push", action="store_true")
    r.add_argument("--no-fetch", action="store_true")
    r.set_defaults(func=cmd_relay)

    # `relay relay ack` reads like a stutter and got typed wrong constantly.
    # The baton verbs are the ones used most, so they are also top level.
    # `relay relay <action>` still works — muscle memory and scripts both.
    for verb, blurb in (
        ("open", "legs nobody has taken (exit 3 if any)"),
        ("ack", "take the baton"),
        ("checkpoint", "record progress on a leg you hold"),
        ("complete", "close a leg"),
    ):
        f = sub.add_parser(verb, help=blurb)
        f.add_argument("--id", help="record id (defaults to the newest foreign leg)")
        f.add_argument("--state", choices=list(RELAY_STATES), help="checkpoint state")
        f.add_argument("-m", "--message", default="", help="note recorded with the event")
        f.add_argument("--no-push", action="store_true")
        f.add_argument("--no-fetch", action="store_true")
        f.set_defaults(func=cmd_relay, action=verb)

    i = sub.add_parser("init", help="name this clone's lane once, in git config")
    i.add_argument("--agent", help="lane name, e.g. claude-cli")
    i.add_argument("--machine", help="override the hostname for this box")
    i.set_defaults(func=cmd_init)

    u = sub.add_parser("pull", help="read handoffs published by the other machines")
    u.add_argument("-n", "--number", type=int, default=3)
    u.add_argument("--full", action="store_true", help="include full markdown bodies")
    u.add_argument("--no-fetch", action="store_true")
    u.set_defaults(func=cmd_pull)

    # Imported here rather than at module scope: both import helpers from this
    # module, and the package must stay importable in either order.
    from . import rules as _rules
    from . import shardlog as _shardlog
    from . import guard as _guard
    from . import adopt as _adopt

    _rules.register(sub)
    _shardlog.register(sub)
    _guard.register(sub)
    _adopt.register(sub)
    return p


def _force_utf8_stdio() -> None:
    """Windows consoles default to cp1252, which cannot encode this tool's glyphs.

    Probe and reconfigure rather than stripping the glyphs: they carry the
    severity of every line here. `errors="replace"` keeps a legacy console
    readable instead of raising mid-report.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        if (getattr(stream, "encoding", "") or "").lower().replace("-", "") == "utf8":
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main() -> int:
    _force_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args()
    if not getattr(args, "func", None):
        # Bare `relay` answers the three questions you should ask before
        # working, instead of printing help nobody reads twice. `--help` is
        # still there for the person who actually wants the list.
        return cmd_status(_ns(no_fetch=False))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
