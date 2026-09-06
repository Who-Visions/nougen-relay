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
import base64
import hashlib
import io
import json
import os
import socket
import shutil
import subprocess
import sys
import tarfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlsplit

from . import ui

EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_USAGE = 2
# `check` uses its own code so CI and pre-work hooks can branch on "someone
# else moved" without treating it as a crash.
EXIT_DIVERGED = 3

DEFAULT_DIR = ".handoffs"
DEFAULT_REMOTE = "origin"

# Leased execution, routing, wake signals, and retry defaults
DEFAULT_LEASE_TTL_MINUTES = 15.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE_SEC = 5.0
DEFAULT_BACKOFF_FACTOR = 2.0
DEFAULT_BACKOFF_MAX_SEC = 300.0

# Semantic deduplication defaults (Agent Mesh, arXiv 2608.26225)
DEFAULT_DEDUP_EXACT = 0.96
DEFAULT_DEDUP_NEAR = 0.85
DEFAULT_EMBED_URL = "http://127.0.0.1:11434"

LANE_CAPABILITIES = {
    "sol-ai": {"local", "fleet", "triage", "informational", "status", "diagnostic", "fast"},
    "dav1d": {"local", "fleet", "triage", "informational", "status", "diagnostic", "fast"},
    "ollama": {"local", "fleet", "triage", "informational", "status", "diagnostic", "fast"},
    "codex": {"coding", "tests", "refactor", "patching", "cli", "backend", "execution"},
    "openai": {"coding", "tests", "refactor", "patching", "cli", "backend", "execution"},
    "claude-cli": {"reasoning", "architecture", "complex", "review", "planning", "frontend", "coding", "execution"},
    "claude": {"reasoning", "architecture", "complex", "review", "planning", "frontend", "coding", "execution"},
    "gemini": {"analysis", "multimodal", "search", "docs", "research", "reasoning", "execution"},
}


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


def _git_archive(ref: str, directory: str, *, cwd: Path) -> Optional[bytes]:
    """Read one committed directory from a ref with a single git process."""
    try:
        out = subprocess.run(
            ["git", "archive", "--format=tar", ref, "--", directory],
            cwd=str(cwd),
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout


def _read_json_dir_from_ref(root: Path, target: str, directory: str) -> list:
    """Read direct JSON children from a committed directory in one batch."""
    archive = _git_archive(target, directory, cwd=root)
    if archive is None:
        return []

    prefix = directory.rstrip("/") + "/"
    records = []
    try:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
            members = sorted(bundle.getmembers(), key=lambda member: member.name)
            for member in members:
                if not member.isfile() or not member.name.startswith(prefix):
                    continue
                filename = member.name[len(prefix):]
                if "/" in filename or not filename.endswith(".json"):
                    continue
                stream = bundle.extractfile(member)
                if stream is None:
                    continue
                try:
                    rec = json.loads(stream.read().decode("utf-8", errors="replace"))
                except (UnicodeError, json.JSONDecodeError):
                    continue
                if not isinstance(rec, dict):
                    continue
                rec["_file"] = filename
                records.append(rec)
    except tarfile.TarError:
        return []
    return records


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


def _git_timeout_seconds() -> float:
    """Resolve the bounded GitHub CLI timeout from the environment."""
    raw = os.environ.get("NOUGEN_RELAY_GIT_TIMEOUT", "120").strip()
    try:
        return max(1.0, float(raw))
    except ValueError:
        print("⚠️ invalid NOUGEN_RELAY_GIT_TIMEOUT; using 120 seconds")
        return 120.0


def _registry_branch(root: Path, remote: str) -> str:
    """Resolve the canonical registry branch without trusting this checkout.

    A working clone may be on a feature branch while the gateway reads the
    remote's default branch.  The branch is therefore env -> remote HEAD -> a
    logged fallback, rather than the current checkout branch.
    """
    configured = os.environ.get("NOUGEN_RELAY_BRANCH", "").strip()
    if configured:
        return configured
    head = _git("symbolic-ref", "--short", f"refs/remotes/{remote}/HEAD", cwd=root)
    if head and "/" in head:
        return head.split("/", 1)[1]
    fallback = os.environ.get("NOUGEN_RELAY_FALLBACK_BRANCH", "main").strip() or "main"
    print(f"⚠️ unable to resolve {remote} default branch; using {fallback!r}")
    return fallback


def _registry_repo_slug(root: Path, remote: str) -> Optional[str]:
    """Return a GitHub ``owner/repo`` only when the remote is GitHub-backed."""
    configured = os.environ.get("NOUGEN_RELAY_REPO_SLUG", "").strip()
    if configured:
        return configured
    raw = (_git("remote", "get-url", remote, cwd=root) or "").strip()
    if not raw:
        return None
    normalized = raw.rstrip("/").removesuffix(".git")
    if "://" in normalized:
        parsed = urlsplit(normalized)
        if (parsed.hostname or "").lower() not in {"github.com", "www.github.com"}:
            return None
        parts = [part for part in parsed.path.strip("/").split("/") if part]
    else:
        # SSH remotes are commonly ``git@github.com:owner/repo.git``.
        if "@github.com:" not in normalized.lower():
            return None
        parts = [part for part in normalized.rsplit(":", 1)[1].split("/") if part]
    if len(parts) < 2:
        return None
    return f"{parts[-2]}/{parts[-1]}"


def _relay_event_key(event: Any) -> tuple:
    """Stable append-only identity shared by gateway and checkout records."""
    if not isinstance(event, dict):
        return ("", "", "")
    return (
        str(event.get("event") or ""),
        str(event.get("at") or ""),
        str(event.get("agent") or ""),
    )


def _merge_registry_records(local: Optional[dict], remote: Optional[dict]) -> dict:
    """Union two registry projections without regressing lifecycle state."""
    if not local:
        return dict(remote or {})
    if not remote:
        return dict(local)
    merged = dict(remote)
    for field, value in local.items():
        if field != "relay" and value not in (None, "", [], {}):
            merged[field] = value

    raw_order = os.environ.get(
        "NOUGEN_RELAY_STATUS_ORDER",
        "open,active,held,acked,in_progress,retry_pending,failed,blocked,complete,abandoned,dead_letter",
    )
    order = {name.strip(): index for index, name in enumerate(raw_order.split(","))
             if name.strip()}
    local_status = local.get("status", "open")
    remote_status = remote.get("status", "open")
    if order.get(str(local_status), 0) >= order.get(str(remote_status), 0):
        merged["status"] = local_status
    else:
        merged["status"] = remote_status

    events = []
    positions: Dict[tuple, int] = {}
    for candidate in list(remote.get("relay") or []) + list(local.get("relay") or []):
        if not isinstance(candidate, dict):
            continue
        key = _relay_event_key(candidate)
        if not any(key):
            events.append(dict(candidate))
            continue
        position = positions.get(key)
        if position is None:
            positions[key] = len(events)
            events.append(dict(candidate))
            continue
        combined = dict(events[position])
        for field, value in candidate.items():
            if value not in (None, "", [], {}):
                combined[field] = value
        events[position] = combined
    if events or "relay" in local or "relay" in remote:
        merged["relay"] = events
    return merged


def _write_registry_record_upstream(
    root: Path,
    remote: str,
    handoff_id: str,
    local_record: dict,
    action: str,
) -> Optional[bool]:
    """CAS-write one relay record to the canonical GitHub registry branch.

    Returns ``None`` when this clone is not GitHub-backed (so callers can use
    the legacy git-push path), ``True`` on a successful/idempotent write, and
    ``False`` after an attempted write fails.  A stale SHA is retried by
    refetching and merging again, so concurrent acknowledgements do not lose
    events.
    """
    if Path(handoff_id).name != handoff_id or not handoff_id:
        return False
    gh_name = os.environ.get("NOUGEN_GH_BIN", "gh").strip() or "gh"
    gh = shutil.which(gh_name)
    slug = _registry_repo_slug(root, remote)
    if not gh or not slug:
        return None
    branch = _registry_branch(root, remote)
    retries_raw = os.environ.get("NOUGEN_RELAY_UPSTREAM_RETRIES", "2").strip()
    try:
        retries = max(1, int(retries_raw))
    except ValueError:
        retries = 2
    api = f"repos/{slug}/contents/{handoff_dir(root).name}/{handoff_id}.json"
    payload_local = {key: value for key, value in local_record.items()
                     if not key.startswith("_")}
    for attempt in range(retries):
        try:
            current = subprocess.run(
                [gh, "api", f"{api}?ref={branch}"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=_git_timeout_seconds(),
            )
            if current.returncode != 0:
                print(f"⚠️ canonical registry read failed for {handoff_id}: "
                      f"{current.stderr.strip()[:160]}")
                return False
            metadata = json.loads(current.stdout)
            remote_record = json.loads(
                base64.b64decode(metadata["content"]).decode("utf-8")
            )
            merged = _merge_registry_records(payload_local, remote_record)
            if merged == remote_record:
                return True
            content = base64.b64encode(
                (json.dumps(merged, indent=2) + "\n").encode("utf-8")
            ).decode("ascii")
            body = json.dumps({
                "message": f"relay: {action} {handoff_id}",
                "content": content,
                "sha": metadata["sha"],
                "branch": branch,
            })
            updated = subprocess.run(
                [gh, "api", "-X", "PUT", api, "--input", "-"],
                input=body, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=_git_timeout_seconds(),
            )
            if updated.returncode == 0:
                return True
            if attempt + 1 < retries:
                continue
            print(f"⚠️ canonical registry write failed for {handoff_id}: "
                  f"{updated.stderr.strip()[:160]}")
            return False
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            print(f"⚠️ canonical registry write raised for {handoff_id}: {exc}")
            return False
    return False


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


def _normalize_scope_field(rec: dict) -> dict:
    """Some writers stored `scope` as a list instead of a string. Collapse it
    so every downstream consumer (hashing as a dict key, `.replace()`/`.split()`
    in `_normalize_scope`) can keep treating scope as a plain string."""
    scope = rec.get("scope")
    if isinstance(scope, list):
        rec["scope"] = " ".join(str(s) for s in scope)
    return rec


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
            out.append(_normalize_scope_field(rec))
        return out

    rel = f"{handoff_dir(root).name}/claims"
    for fname, blob in _read_json_blobs_batch(f"{target}:{rel}"):
        try:
            rec = json.loads(blob)
        except Exception:
            continue
        rec["_file"] = fname
        out.append(_normalize_scope_field(rec))
    return out


def _read_json_blobs_batch(tree_spec: str) -> list:
    """Every *.json blob under <ref>:<dir> as (name, text), read with ONE
    `git cat-file --batch` instead of one `git show` per file. The claims dir
    held 384 records on 2026-09-03 and the per-file version took the
    pre-commit guard past two minutes per watched ref. Bytes on purpose: the
    batch header's size is a byte count, each body is decoded on its own."""
    listing = _git("ls-tree", "-z", tree_spec)
    if not listing:
        return []
    entries = []
    for rec in listing.split("\0"):
        if "\t" not in rec:
            continue
        meta, name = rec.split("\t", 1)
        parts = meta.split()
        if len(parts) >= 3 and parts[1] == "blob" and name.endswith(".json"):
            entries.append((parts[2], name))
    if not entries:
        return []
    try:
        cat = subprocess.run(
            ["git", "cat-file", "--batch"], capture_output=True,
            input=("\n".join(sha for sha, _ in entries) + "\n").encode("ascii"),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception:
        return []
    out, pos, data = [], 0, cat.stdout or b""
    for _sha, name in entries:
        nl = data.find(b"\n", pos)
        if nl < 0:
            break
        header = data[pos:nl].split()
        if len(header) < 3 or header[1] == b"missing":
            pos = nl + 1
            continue
        size = int(header[2])
        out.append((name, data[nl + 1: nl + 1 + size].decode("utf-8", errors="replace")))
        pos = nl + 1 + size + 1
    return sorted(out)


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

# `abandoned` is terminal like `complete`, but means the branch was given up
# and distilled into a summary leg rather than finished — see cmd_summarize.
RELAY_STATES = (
    "open",
    "acked",
    "in_progress",
    "blocked",
    "complete",
    "abandoned",
    "dead_letter",
    "failed",
    "retry_pending",
)


# --- wake signals & autonomous triggers -------------------------------------

def wake_dir(root: Path) -> Path:
    env = os.environ.get("NOUGEN_WAKE_DIR", "").strip()
    if env:
        return Path(env) if Path(env).is_absolute() else root / env
    return root / ".relay" / "wake"


def emit_wake_signal(root: Path, leg_id: str, record: Optional[dict] = None) -> Path:
    """Emit an autonomous wake signal/marker when a new relay leg is created."""
    wdir = wake_dir(root)
    wdir.mkdir(parents=True, exist_ok=True)
    stamp = _now()
    rec = record or {}
    marker = {
        "event": "wake",
        "leg_id": leg_id,
        "machine": rec.get("machine") or resolve_machine(),
        "agent": rec.get("agent") or resolve_agent(),
        "goal": rec.get("goal") or "",
        "created_utc": rec.get("created_utc") or stamp.isoformat(),
        "emitted_utc": stamp.isoformat(),
        "status": "pending",
        "idempotency_key": compute_idempotency_key(leg_id, rec.get("goal", "")),
    }
    marker_path = wdir / f"{leg_id}.wake.json"
    marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")

    # Touch trigger marker for file watchers
    try:
        sig_file = wdir.parent / "wake.signal"
        sig_file.write_text(
            json.dumps({"latest_leg_id": leg_id, "emitted_utc": stamp.isoformat()}),
            encoding="utf-8",
        )
    except Exception:
        pass
    return marker_path


def pending_wake_signals(root: Path) -> list:
    """List pending wake signals that have not been consumed."""
    wdir = wake_dir(root)
    if not wdir.is_dir():
        return []
    signals = []
    for p in sorted(wdir.glob("*.wake.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            data["_file"] = p.name
            signals.append(data)
        except Exception:
            continue
    return signals


def consume_wake_signal(root: Path, leg_id: str) -> bool:
    """Consume/clear a wake signal marker once acknowledged or claimed."""
    wdir = wake_dir(root)
    if not wdir.is_dir():
        return False
    target = wdir / f"{leg_id}.wake.json"
    if target.is_file():
        try:
            target.unlink()
            return True
        except OSError:
            pass
    for p in wdir.glob(f"*{leg_id}*.wake.json"):
        try:
            p.unlink()
            return True
        except OSError:
            pass
    return False


# --- idempotency (SHA-256 fingerprinting) -----------------------------------

def compute_idempotency_key(leg_id: str, goal: str = "") -> str:
    """Compute SHA-256 fingerprint for a leg ID and goal combination."""
    payload = f"{leg_id.strip()}:{goal.strip()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def idempotency_fingerprint(record: dict) -> str:
    """Compute idempotency key directly from a record dict."""
    lid = record_id(record) or ""
    goal = record.get("goal") or ""
    return compute_idempotency_key(lid, goal)


def idempotency_dir(root: Path) -> Path:
    env = os.environ.get("NOUGEN_IDEMPOTENCY_DIR", "").strip()
    if env:
        return Path(env) if Path(env).is_absolute() else root / env
    return root / ".relay" / "idempotency"


def is_duplicate_execution(root: Path, leg_id: str, goal: str = "") -> bool:
    """Check if an execution with this idempotency fingerprint has already completed."""
    key = compute_idempotency_key(leg_id, goal)
    idir = idempotency_dir(root)
    key_file = idir / f"{key}.json"
    if key_file.is_file():
        return True
    rpath = _record_path(root, leg_id)
    if rpath and rpath.is_file():
        try:
            rec = json.loads(rpath.read_text(encoding="utf-8"))
            if rec.get("status") in ("complete", "abandoned"):
                return True
        except Exception:
            pass
    return False


def record_idempotency(
    root: Path, leg_id: str, goal: str = "", metadata: Optional[dict] = None
) -> Path:
    """Record an idempotency fingerprint after successful execution."""
    idir = idempotency_dir(root)
    idir.mkdir(parents=True, exist_ok=True)
    key = compute_idempotency_key(leg_id, goal)
    key_file = idir / f"{key}.json"
    data = {
        "idempotency_key": key,
        "leg_id": leg_id,
        "goal": goal,
        "completed_utc": _now().isoformat(),
        "machine": resolve_machine(),
        "agent": resolve_agent(),
        "metadata": metadata or {},
    }
    key_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return key_file


# --- leased execution & atomic claims ----------------------------------------

def _lease_ttl_minutes() -> float:
    raw = os.environ.get("NOUGEN_LEASE_TTL_MINUTES", "").strip()
    try:
        return float(raw) if raw else DEFAULT_LEASE_TTL_MINUTES
    except ValueError:
        return DEFAULT_LEASE_TTL_MINUTES


def leases_dir(root: Path) -> Path:
    env = os.environ.get("NOUGEN_LEASE_DIR", "").strip()
    if env:
        return Path(env) if Path(env).is_absolute() else root / env
    return root / ".relay" / "leases"


def _lease_age_minutes(lease_rec: dict) -> Optional[float]:
    """Minutes since the holder last proved it was alive: the newest heartbeat
    wins, then the acquire stamp, then the leg's creation stamp."""
    stamp = lease_rec.get("heartbeat_utc") or lease_rec.get("leased_utc") or lease_rec.get("created_utc") or ""
    try:
        return (_now() - datetime.fromisoformat(stamp)).total_seconds() / 60.0
    except Exception:
        return None


# --- lease control plane: fencing, heartbeat, history ----------------------
# Git stays the append-only ledger; the lease file is the hot state. Every
# transition below is recorded in history[] with actor and evidence so the
# reconciler can replay it, and every write that ends a lease must present the
# fencing token it was issued, so a worker whose lease was reclaimed cannot
# finish a leg someone else now holds.

LEASE_STATES = ("DISCOVERED", "TRIAGED", "CLAIMABLE", "LEASED", "RUNNING", "COMPLETE", "BLOCKED",
                "RELEASED", "RETRY_WAIT", "DEAD_LETTER", "ARCHIVAL_DEBT", "SUPERSEDED")
_STATUS_TO_STATE = {"active": "LEASED", "released": "RELEASED", "complete": "COMPLETE", "failed": "RETRY_WAIT",
                    "retry_pending": "RETRY_WAIT", "dead_letter": "DEAD_LETTER", "expired": "CLAIMABLE",
                    "blocked": "BLOCKED", "abandoned": "RELEASED", "superseded": "SUPERSEDED"}


def _lease_history_max() -> int:
    raw = os.environ.get("NOUGEN_LEASE_HISTORY_MAX", "").strip()
    try:
        return int(raw) if raw else 50
    except ValueError:
        return 50


def heartbeat_interval_seconds(ttl_minutes: Optional[float] = None) -> float:
    """Heartbeat cadence: TTL / NOUGEN_LEASE_HEARTBEAT_DIVISOR (default 3)."""
    ttl = float(ttl_minutes if ttl_minutes is not None else _lease_ttl_minutes())
    raw = os.environ.get("NOUGEN_LEASE_HEARTBEAT_DIVISOR", "").strip()
    try:
        divisor = float(raw) if raw else 3.0
    except ValueError:
        divisor = 3.0
    return max(1.0, ttl * 60.0 / max(1.0, divisor))


def new_lease_id() -> str:
    import uuid
    return uuid.uuid4().hex[:12]


def _actor(rec: dict) -> str:
    return f"{rec.get('machine') or resolve_machine()}/{rec.get('agent') or resolve_agent()}"


def _append_history(rec: dict, actor: str, frm: Optional[str], to: str, evidence: str = "") -> None:
    hist = list(rec.get("history") or [])
    hist.append({"utc": _now().isoformat(), "actor": actor, "from": frm, "to": to, "evidence": evidence[:300]})
    rec["history"] = hist[-_lease_history_max():]
    rec["state"] = to
    rec["updated_utc"] = _now().isoformat()


def fencing_ok(rec: dict, fencing_token: Optional[int]) -> bool:
    """None = legacy caller (no token issued); otherwise the token must equal
    the one on the record. A stale token is a zombie worker."""
    if fencing_token is None:
        return True
    try:
        return int(rec.get("fencing_token", 0) or 0) == int(fencing_token)
    except (TypeError, ValueError):
        return False


def _read_lease(root: Path, leg_id: str) -> Tuple[Path, Optional[dict]]:
    lease_file = leases_dir(root) / f"{leg_id}.lease.json"
    if not lease_file.is_file():
        return lease_file, None
    try:
        return lease_file, json.loads(lease_file.read_text(encoding="utf-8"))
    except Exception:
        return lease_file, None


def _write_lease(lease_file: Path, rec: dict) -> None:
    lease_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = lease_file.parent / f"{lease_file.stem}.tmp.{os.getpid()}"
    tmp_file.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    try:
        tmp_file.replace(lease_file)
    except OSError:
        lease_file.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        tmp_file.unlink(missing_ok=True)


def heartbeat_lease(root: Path, leg_id: str, fencing_token: Optional[int], state: str = "RUNNING") -> bool:
    """Prove the holder is alive: refresh heartbeat_utc (which is what
    lease_is_active ages against). Rejected when the token is stale or the
    lease is no longer active, so a reclaimed lease cannot be revived."""
    lease_file, rec = _read_lease(root, leg_id)
    if not rec or not lease_is_active(rec):
        return False
    if not fencing_ok(rec, fencing_token):
        rec.setdefault("rejected", []).append({"utc": _now().isoformat(), "op": "heartbeat", "token": fencing_token})
        _write_lease(lease_file, rec)
        return False
    rec["heartbeat_utc"] = _now().isoformat()
    rec["heartbeat_count"] = int(rec.get("heartbeat_count", 0) or 0) + 1
    if rec.get("state") != state:
        _append_history(rec, _actor(rec), rec.get("state"), state, "heartbeat")
    _write_lease(lease_file, rec)
    return True


def sweep_expired_leases(root: Path) -> List[str]:
    """Reclaim step of the control plane: every active lease past its TTL is
    marked expired (state CLAIMABLE) with the evidence in history, so the next
    acquire is a visible reclaim and the metrics count it."""
    ldir = leases_dir(root)
    if not ldir.is_dir():
        return []
    swept: List[str] = []
    for p in sorted(ldir.glob("*.lease.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if rec.get("status") != "active" or lease_is_active(rec):
            continue
        age = _lease_age_minutes(rec)
        rec["status"] = "expired"
        rec["expired_utc"] = _now().isoformat()
        _append_history(rec, "sweeper", rec.get("state") or "LEASED", "CLAIMABLE",
                        f"sweeper: expired after {age:.1f} min (ttl {rec.get('ttl_minutes')})" if age is not None else "sweeper: expired")
        _write_lease(p, rec)
        swept.append(str(rec.get("leg_id") or p.name.split(".lease.json")[0]))
    return swept


def lease_metrics(root: Path) -> Dict[str, Any]:
    """Live claim index in numbers: leases by state and status, expired and
    reclaimed counts, dead letters, fencing rejections, oldest active age."""
    ldir = leases_dir(root)
    out: Dict[str, Any] = {"leases": 0, "by_state": {}, "by_status": {}, "active": 0, "expired_swept": 0,
                           "reclaimed": 0, "dead_letter": 0, "fencing_rejections": 0, "oldest_active_min": None}
    if not ldir.is_dir():
        return out
    for p in ldir.glob("*.lease.json"):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        out["leases"] += 1
        st = str(rec.get("state") or _STATUS_TO_STATE.get(str(rec.get("status")), "?"))
        out["by_state"][st] = out["by_state"].get(st, 0) + 1
        s = str(rec.get("status") or "?")
        out["by_status"][s] = out["by_status"].get(s, 0) + 1
        if lease_is_active(rec):
            out["active"] += 1
            age = _lease_age_minutes(rec)
            if age is not None and (out["oldest_active_min"] is None or age > out["oldest_active_min"]):
                out["oldest_active_min"] = round(age, 1)
        if s == "dead_letter":
            out["dead_letter"] += 1
        out["fencing_rejections"] += len(rec.get("rejected") or [])
        for h in rec.get("history") or []:
            ev = str(h.get("evidence") or "")
            if ev.startswith("sweeper"):
                out["expired_swept"] += 1
            elif ev.startswith("reclaim"):
                out["reclaimed"] += 1
    return out


def lease_is_active(lease_rec: dict) -> bool:
    """Check if an execution lease is currently valid and unexpired."""
    if lease_rec.get("status") != "active":
        return False
    age = _lease_age_minutes(lease_rec)
    ttl = lease_rec.get("ttl_minutes") or _lease_ttl_minutes()
    return age is None or age <= float(ttl)


def acquire_lease(
    root: Path,
    leg_id: str,
    machine: Optional[str] = None,
    agent: Optional[str] = None,
    ttl_minutes: Optional[float] = None,
    goal: str = "",
    force: bool = False,
) -> Optional[dict]:
    """Atomically acquire an exclusive execution lease on a relay leg.

    If the leg is already leased by an active worker, returns None unless force=True.
    If the existing lease has expired (age > TTL), it is automatically reclaimed from dead workers.
    """
    ldir = leases_dir(root)
    ldir.mkdir(parents=True, exist_ok=True)
    lease_file = ldir / f"{leg_id}.lease.json"

    machine = machine or resolve_machine()
    agent = agent or resolve_agent()
    session = resolve_session()
    ttl = ttl_minutes if ttl_minutes is not None else _lease_ttl_minutes()
    stamp = _now()

    prior_retry_count = 0
    prior_max_retries = None
    prior_token = 0
    prior_history: list = []
    acquire_evidence = "acquire"
    existing: Optional[dict] = None
    if lease_file.is_file():
        try:
            existing = json.loads(lease_file.read_text(encoding="utf-8"))
        except Exception:
            existing = None  # Stale or corrupt lease file can be reclaimed
    if existing is not None:
        # the fencing token is monotonic per leg across every holder, forced or not
        try:
            prior_token = int(existing.get("fencing_token", 0) or 0)
        except (TypeError, ValueError):
            prior_token = 0
        prior_history = list(existing.get("history") or [])
    if existing is not None and not force:
        if lease_is_active(existing):
            # If held by the same machine, agent, and session, allow re-entry/renewal
            same_holder = (
                existing.get("machine") == machine
                and existing.get("agent") == agent
                and (not session or existing.get("session") == session)
            )
            if same_holder:
                existing["leased_utc"] = stamp.isoformat()
                existing["heartbeat_utc"] = stamp.isoformat()
                existing["ttl_minutes"] = ttl
                _append_history(existing, f"{machine}/{agent}", existing.get("state") or "LEASED",
                                existing.get("state") or "LEASED", "renew")
                _write_lease(lease_file, existing)
                return existing
            return None  # Active lease held by another worker
        # Inactive lease: this is a reclaim, not a first acquisition. The
        # fresh record used to reset retry_count to 0 here, which made
        # dead_letter unreachable and let one leg be claimed 45 times
        # (148 retry_pending vs 17 complete since 08-30, each claim commit
        # firing CI). Retry history must survive the reclaim, and an
        # exhausted or dead-lettered leg is not claimable without force.
        if not is_leg_retryable(existing):
            return None
        prior_retry_count = int(existing.get("retry_count", 0) or 0)
        prior_max_retries = existing.get("max_retries")
        acquire_evidence = (f"reclaim: {existing.get('status')} lease from "
                            f"{existing.get('machine')}/{existing.get('agent')} token {prior_token}")
    elif existing is not None and force:
        prior_retry_count = int(existing.get("retry_count", 0) or 0)
        prior_max_retries = existing.get("max_retries")
        acquire_evidence = f"force: took over {existing.get('status')} lease token {prior_token}"

    lease_rec = {
        "leg_id": leg_id,
        "lease_id": new_lease_id(),
        "fencing_token": prior_token + 1,
        "machine": machine,
        "agent": agent,
        **({"session": session} if session else {}),
        "status": "active",
        "goal": goal,
        "idempotency_key": compute_idempotency_key(leg_id, goal),
        "leased_utc": stamp.isoformat(),
        "heartbeat_utc": stamp.isoformat(),
        "heartbeat_count": 0,
        "ttl_minutes": ttl,
        "retry_count": prior_retry_count,
        "attempt_count": prior_retry_count + 1,
        **({"max_retries": prior_max_retries} if prior_max_retries is not None else {}),
        "history": prior_history,
    }
    _append_history(lease_rec, f"{machine}/{agent}", "CLAIMABLE", "LEASED", acquire_evidence)
    _write_lease(lease_file, lease_rec)

    consume_wake_signal(root, leg_id)
    return lease_rec


def release_lease(root: Path, leg_id: str, status: str = "released", fencing_token: Optional[int] = None,
                  evidence: str = "") -> bool:
    """End a lease. With a fencing token, a stale token is rejected and recorded,
    so a zombie worker cannot close a leg another holder now owns."""
    lease_file, rec = _read_lease(root, leg_id)
    if rec is None:
        return False
    try:
        if not fencing_ok(rec, fencing_token):
            rec.setdefault("rejected", []).append({"utc": _now().isoformat(), "op": f"release:{status}", "token": fencing_token})
            _write_lease(lease_file, rec)
            return False
        rec["status"] = status
        rec["released_utc"] = _now().isoformat()
        _append_history(rec, _actor(rec), rec.get("state"), _STATUS_TO_STATE.get(status, status.upper()), evidence or f"release:{status}")
        _write_lease(lease_file, rec)
        return True
    except Exception:
        return False


def active_leases(root: Path, active_only: bool = True) -> list:
    """List leases across all legs in this repo."""
    ldir = leases_dir(root)
    if not ldir.is_dir():
        return []
    out = []
    for p in sorted(ldir.glob("*.lease.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
            rec["_file"] = p.name
            if active_only and not lease_is_active(rec):
                continue
            out.append(rec)
        except Exception:
            continue
    return out


# --- capability / tag routing heuristic -------------------------------------

def lane_capabilities(lane: str) -> set:
    """Get the set of capabilities for a given lane name."""
    clean = _slug(lane)
    for known_lane, caps in LANE_CAPABILITIES.items():
        if known_lane in clean or clean in known_lane:
            return set(caps)
    return {"general", "execution"}


def is_lane_eligible(lane: str, leg: dict) -> bool:
    """Determine if a worker lane is eligible to execute an open leg."""
    clean_lane = _slug(lane)

    # 1. Explicit target lane / agent check
    target = (
        leg.get("target_agent")
        or leg.get("target_lane")
        or leg.get("agent_target")
        or ""
    ).strip()
    if target:
        clean_target = _slug(target)
        return clean_target in clean_lane or clean_lane in clean_target

    # 2. Explicit tags / required capabilities
    required_tags = set()
    raw_tags = (
        leg.get("tags") or leg.get("capabilities") or leg.get("required_capabilities")
    )
    if isinstance(raw_tags, (list, tuple, set)):
        required_tags = {str(t).lower().strip() for t in raw_tags if str(t).strip()}
    elif isinstance(raw_tags, str) and raw_tags.strip():
        required_tags = {
            t.lower().strip()
            for t in raw_tags.replace(",", " ").split()
            if t.strip()
        }

    lane_caps = lane_capabilities(lane)
    if required_tags:
        return bool(required_tags & lane_caps)

    # 3. Goal & task type heuristic inference
    goal = (leg.get("goal") or "").lower()
    task_type = (leg.get("type") or leg.get("task_type") or "").lower()

    coding_keywords = (
        "test",
        "fix",
        "patch",
        "bug",
        "refactor",
        "build",
        "compile",
        "implement",
    )
    if any(kw in goal or kw in task_type for kw in coding_keywords):
        return bool({"coding", "tests", "patching", "execution"} & lane_caps)

    triage_keywords = (
        "status",
        "triage",
        "summary",
        "info",
        "check",
        "diagnos",
        "heartbeat",
    )
    if any(kw in goal or kw in task_type for kw in triage_keywords):
        return bool(
            {"triage", "informational", "status", "diagnostic", "fleet"} & lane_caps
        )

    return True


def match_lane_for_leg(
    leg: dict, available_lanes: Optional[list] = None
) -> Optional[str]:
    """Find the best eligible lane for an open leg from candidate lanes."""
    candidates = available_lanes or list(LANE_CAPABILITIES.keys())
    for lane in candidates:
        if is_lane_eligible(lane, leg):
            return lane
    return candidates[0] if candidates else None


def filter_eligible_legs(legs: list, lane: str) -> list:
    """Filter open legs to those eligible for execution by the specified lane."""
    return [leg for leg in legs if is_lane_eligible(lane, leg)]


# --- retry backoff & dead-letter logic --------------------------------------

def _max_retries() -> int:
    raw = os.environ.get("NOUGEN_RELAY_MAX_RETRIES", "").strip()
    try:
        return int(raw) if raw else DEFAULT_MAX_RETRIES
    except ValueError:
        return DEFAULT_MAX_RETRIES


def calculate_backoff_seconds(
    attempt: int,
    base_seconds: float = DEFAULT_BACKOFF_BASE_SEC,
    factor: float = DEFAULT_BACKOFF_FACTOR,
    max_seconds: float = DEFAULT_BACKOFF_MAX_SEC,
) -> float:
    """Calculate exponential backoff duration in seconds."""
    if attempt <= 0:
        return 0.0
    delay = base_seconds * (factor ** (attempt - 1))
    return min(max_seconds, delay)


def record_leg_failure(
    root: Path,
    leg_id: str,
    error_message: str,
    max_retries: Optional[int] = None,
    fencing_token: Optional[int] = None,
) -> dict:
    """Record a failure for a leg, applying exponential retry backoff or marking dead_letter.
    A stale fencing token is rejected without touching the record."""
    limit = max_retries if max_retries is not None else _max_retries()
    stamp = _now()
    ldir = leases_dir(root)
    ldir.mkdir(parents=True, exist_ok=True)
    lease_file = ldir / f"{leg_id}.lease.json"

    lease_rec = {}
    if lease_file.is_file():
        try:
            lease_rec = json.loads(lease_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    if lease_rec and not fencing_ok(lease_rec, fencing_token):
        lease_rec.setdefault("rejected", []).append({"utc": stamp.isoformat(), "op": "failure", "token": fencing_token})
        _write_lease(lease_file, lease_rec)
        return {"leg_id": leg_id, "rejected": True, "reason": "stale fencing token", "status": lease_rec.get("status")}

    retry_count = int(lease_rec.get("retry_count", 0)) + 1
    failures = lease_rec.get("failures", [])
    failures.append({
        "attempt": retry_count,
        "error": error_message,
        "failed_utc": stamp.isoformat(),
    })

    if retry_count >= limit:
        status = "dead_letter"
        next_retry_utc = None
    else:
        status = "retry_pending"
        backoff_sec = calculate_backoff_seconds(retry_count)
        next_retry_dt = stamp + timedelta(seconds=backoff_sec)
        next_retry_utc = next_retry_dt.isoformat()

    lease_rec.update({
        "leg_id": leg_id,
        "status": status,
        "retry_count": retry_count,
        "attempt_count": retry_count,
        "max_retries": limit,
        "failures": failures,
        "last_error": error_message,
        "last_failed_utc": stamp.isoformat(),
        "next_retry_utc": next_retry_utc,
    })
    _append_history(lease_rec, _actor(lease_rec), lease_rec.get("state"), _STATUS_TO_STATE[status],
                    f"attempt {retry_count}/{limit}: {error_message}")

    _write_lease(lease_file, lease_rec)

    def update_rec(rec):
        rec["retry_count"] = retry_count
        rec["failures"] = failures
        if status == "dead_letter":
            rec["status"] = "dead_letter"
            rec.setdefault("relay", []).append({
                "event": "dead_letter",
                "machine": resolve_machine(),
                "agent": resolve_agent(),
                "at": stamp.isoformat(),
                "note": f"Exceeded max retries ({limit}): {error_message[:200]}",
            })

    _touch_record(root, leg_id, update_rec)
    return lease_rec


def is_leg_retryable(lease_rec: dict, now_dt: Optional[datetime] = None) -> bool:
    """Check if a failed/pending leg is eligible for retry after backoff."""
    status = lease_rec.get("status")
    if status in ("dead_letter", "failed", "complete", "abandoned"):
        return False
    if status != "retry_pending":
        return True
    retries = int(lease_rec.get("retry_count", 0))
    max_r = int(lease_rec.get("max_retries", _max_retries()))
    if retries >= max_r:
        return False
    next_retry_str = lease_rec.get("next_retry_utc")
    if not next_retry_str:
        return True
    try:
        next_retry = datetime.fromisoformat(next_retry_str)
        now = now_dt or _now()
        return now >= next_retry
    except Exception:
        return True


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

    # A feature-branch checkout is not necessarily the gateway's canonical
    # registry branch.  Prefer a compare-and-swap contents write when this is
    # a GitHub-backed relay; fall back to the historical branch push for local
    # remotes and installations without `gh`.
    upstream = _write_registry_record_upstream(
        root, remote, Path(str(rec.get("_file", ""))).stem, rec, action
    )
    if upstream is True:
        print(f"ℹ️ published registry projection to {_registry_branch(root, remote)}")
        return EXIT_OK
    if upstream is False:
        print("⚠️ canonical registry write failed — local record is committed but "
              "the gateway may still be stale")
        return EXIT_FAILURE
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


def resolve_dedup_exact() -> float:
    raw = os.environ.get("NOUGEN_DEDUP_EXACT")
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    return DEFAULT_DEDUP_EXACT


def resolve_dedup_near() -> float:
    raw = os.environ.get("NOUGEN_DEDUP_NEAR")
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    return DEFAULT_DEDUP_NEAR


def resolve_embed_url() -> str:
    url = (
        os.environ.get("NOUGEN_EMBED_URL")
        or os.environ.get("OLLAMA_HOST_URL")
        or os.environ.get("NOUGEN_OLLAMA_URL")
        or DEFAULT_EMBED_URL
    )
    return url.rstrip("/")


def _get_dedup_module(root: Optional[Path] = None):
    try:
        import relay_dedup
        return relay_dedup
    except ImportError:
        pass

    candidates = []
    if root:
        candidates.append(root / "tools")
    repo_toplevel = repo_root()
    if repo_toplevel:
        candidates.append(repo_toplevel / "tools")
    candidates.append(Path(__file__).resolve().parents[2] / "tools")
    for c in candidates:
        if c.is_dir() and (c / "relay_dedup.py").is_file():
            if str(c) not in sys.path:
                sys.path.insert(0, str(c))
            try:
                import relay_dedup
                return relay_dedup
            except ImportError:
                pass
    return None


def check_leg_dedup(
    root: Optional[Path],
    outdir: Path,
    goal: str,
) -> Tuple[str, Any, float]:
    """Check candidate goal for duplicate open legs via relay_dedup.

    Returns:
        ("exact", leg_id, score): similarity >= NOUGEN_DEDUP_EXACT
        ("near", [similar_ids], score): similarity >= NOUGEN_DEDUP_NEAR
        ("ok", None, 0.0): no duplicate found
        ("skipped", reason, 0.0): embed lane unreachable or advisory skip
    """
    rd = _get_dedup_module(root)
    if rd is None:
        print("ℹ️ dedup check skipped: relay_dedup module unavailable")
        return ("skipped", "module unavailable", 0.0)

    try:
        report: dict = {}
        status, payload, score = rd.check_dedup(
            goal=goal,
            directory=outdir,
            exact_threshold=resolve_dedup_exact(),
            near_threshold=resolve_dedup_near(),
            report=report,
        )
        if status == "skipped":
            print(f"ℹ️ dedup check skipped: {payload}")
        elif report.get("degraded"):
            # Say which method produced the verdict. A check that silently
            # changes method is how a weaker guarantee gets mistaken for the
            # one that was advertised.
            print(f"⚠️ dedup ran in token-overlap mode ({report.get('reason')}); "
                  "wording-similar legs are caught, semantically-similar ones may not be")
        return status, payload, score
    except Exception as exc:
        print(f"ℹ️ dedup check skipped: {exc}")
        return ("skipped", str(exc), 0.0)


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

    # Semantic deduplication check (Agent Mesh, arXiv 2608.26225)
    goal = (args.goal or "").strip()
    similar_to: List[str] = []
    if goal:
        status, payload, score = check_leg_dedup(root, outdir, goal)
        if status == "exact":
            existing_id = str(payload)
            print(
                f"ℹ️ duplicate leg already exists: {existing_id} "
                f"(similarity {score:.3f} >= {resolve_dedup_exact():.2f})"
            )
            print(existing_id)
            return EXIT_OK
        elif status == "near":
            similar_to = payload if isinstance(payload, list) else [str(payload)]
            print(f"⚠️ near duplicate open leg(s) detected: {', '.join(similar_to)}")

    name = unique_record_name(outdir, stamp, machine, agent)

    # Parentage lives in the JSON, never the filename — filename segments are
    # parsed back out for identity by the commit hook and adopt.py, so nothing
    # may be appended there. Resolve to the FULL id when the parent is local
    # (substring ids inherit _record_path's ambiguity refusal); a parent on an
    # unfetched ref is legitimate, so an unresolved id is stored as given
    # rather than refused.
    parent_id = None
    parent_arg = (getattr(args, "parent", None) or "").strip()
    if parent_arg:
        ppath = _record_path(root, parent_arg)
        if ppath is not None:
            try:
                parent_id = record_id(
                    json.loads(ppath.read_text(encoding="utf-8")), ppath
                )
            except Exception:
                parent_id = ppath.stem
        else:
            parent_id = parent_arg
            print(
                f"⚠️ parent {parent_arg!r} not found locally — stored as given "
                "(it may live on a ref this machine has not fetched)"
            )

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
    if parent_id:
        record["parent_leg_id"] = parent_id
    leg_type = (getattr(args, "leg_type", None) or "").strip()
    if leg_type:
        record["type"] = leg_type
    target_agent = (getattr(args, "target_agent", None) or "").strip()
    if target_agent:
        record["target_agent"] = target_agent
    tags = getattr(args, "tags", None)
    if tags:
        if isinstance(tags, str):
            record["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
        elif isinstance(tags, (list, tuple)):
            record["tags"] = list(tags)
    if similar_to:
        record["similar_to"] = similar_to

    (outdir / f"{name}.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    emit_wake_signal(root, name, record)

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


def cmd_summarize(args: argparse.Namespace) -> int:
    """Close an abandoned branch with a distilled summary leg.

    Two moves in one motion: a new `type: summary` leg is created pointing at
    the parent through `parent_leg_id`, and the parent is checkpointed to
    `abandoned` so it leaves every open queue. The summary carries what the
    branch learned; the abandoned leg stops asking to be picked up. Without
    this, giving up on a leg looks identical to never having seen it.
    """
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE

    parent_arg = (args.id or "").strip()
    if not parent_arg:
        print("❌ summarize needs --id <parent-leg>")
        return EXIT_USAGE

    args.parent = parent_arg
    args.leg_type = "summary"
    if not (getattr(args, "goal", "") or "").strip():
        args.goal = f"Summary of abandoned branch {parent_arg}"

    rc = cmd_create(args)
    if rc != EXIT_OK:
        return rc

    machine, agent = resolve_machine(), resolve_agent()
    stamp = _now().isoformat()

    def mark(rec):
        rec["status"] = "abandoned"
        rec.setdefault("relay", []).append(
            {"event": "checkpoint", "state": "abandoned", "machine": machine,
             "agent": agent, "at": stamp,
             "note": "branch summarized into a summary leg"}
        )

    rec = _touch_record(root, parent_arg, mark)
    if rec is None:
        # The summary still stands on its own; the parent may live on an
        # unfetched ref, in which case whoever holds it marks it themselves.
        print(f"⚠️ summary written, but parent {parent_arg!r} was not found "
              "locally to mark abandoned")
        return EXIT_OK
    print(f"ℹ️ {rec['_file']} -> abandoned (summarized)")
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
    return _read_json_dir_from_ref(root, target, dirname)


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


def cmd_lease(args: argparse.Namespace) -> int:
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE
    action = args.action
    if action == "acquire":
        if not args.id:
            print("❌ --id is required for lease acquire")
            return EXIT_USAGE
        lease = acquire_lease(
            root,
            args.id,
            ttl_minutes=args.ttl,
            goal=args.goal or "",
            force=args.force,
        )
        if lease is None:
            print(f"❌ could not acquire lease for {args.id} (already actively leased)")
            return EXIT_FAILURE
        print(f"✅ leased {args.id} to {lease['machine']}/{lease['agent']} (TTL: {lease['ttl_minutes']:.1f}m)")
        return EXIT_OK
    elif action == "release":
        if not args.id:
            print("❌ --id is required for lease release")
            return EXIT_USAGE
        ok = release_lease(root, args.id)
        if ok:
            print(f"✅ released lease for {args.id}")
            return EXIT_OK
        print(f"⚠️ no active lease found for {args.id}")
        return EXIT_FAILURE
    elif action == "list":
        leases = active_leases(root, active_only=not args.all)
        if not leases:
            print("ℹ️ no leases recorded")
            return EXIT_OK
        print(f"🔍 Found {len(leases)} lease(s)")
        for lease in leases:
            age = _lease_age_minutes(lease)
            state = "active" if lease_is_active(lease) else (lease.get("status") or "expired")
            age_s = f"{age:.1f}m" if age is not None else "?"
            print(f"  [{state:<7}] {lease.get('leg_id')} -> {lease.get('machine')}/{lease.get('agent')} · {age_s} ago (TTL: {lease.get('ttl_minutes', DEFAULT_LEASE_TTL_MINUTES)}m)")
        return EXIT_OK
    print(f"❌ unknown lease action: {action}")
    return EXIT_USAGE


def cmd_wake(args: argparse.Namespace) -> int:
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE
    action = args.action
    if action == "list":
        sigs = pending_wake_signals(root)
        if not sigs:
            print("✅ no pending wake signals")
            return EXIT_OK
        print(f"⚡ {len(sigs)} pending wake signal(s):")
        for s in sigs:
            print(f"  • {s.get('leg_id')} ({s.get('machine')}/{s.get('agent')}) — {s.get('goal')}")
        return EXIT_OK
    elif action == "emit":
        if not args.id:
            print("❌ --id is required to emit wake signal")
            return EXIT_USAGE
        p = emit_wake_signal(root, args.id, {"goal": args.goal or ""})
        print(f"✅ wake signal emitted: {p.name}")
        return EXIT_OK
    elif action == "consume":
        if not args.id:
            print("❌ --id is required to consume wake signal")
            return EXIT_USAGE
        ok = consume_wake_signal(root, args.id)
        if ok:
            print(f"✅ consumed wake signal for {args.id}")
            return EXIT_OK
        print(f"⚠️ no wake signal found for {args.id}")
        return EXIT_FAILURE
    print(f"❌ unknown wake action: {action}")
    return EXIT_USAGE


def cmd_schedule(args: argparse.Namespace) -> int:
    """Evaluate open actionable legs, compute claim scores, and schedule work.

    Integrates the Quota Governor: legs that would breach HARD/RESERVE
    thresholds are filtered out. SOFT threshold triggers a model downshift.
    Ghost worker status is reported alongside the scheduling decision.
    """
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE
    from . import claim_engine
    from . import quota_governor as qg

    caps = claim_engine.machine_capabilities(root)

    # Load quota snapshot (from env vars or defaults)
    snapshot = qg.load_snapshot_from_env()
    governor = qg.QuotaGovernor(qg.load_thresholds_from_env())

    # Show quota status
    status = governor.status_report(snapshot)
    print(qg.format_quota_status(status))
    print()

    # Ghost worker check
    ghosts = claim_engine.ghost_worker_check(root)
    ghost_reports = [qg.GhostWorkerReport(**{
        "machine": g["machine"], "agent": g["agent"], "session": g["session"],
        "status": qg.GhostStatus(g["status"]), "active_claims": g["active_claims"],
        "detail": g["detail"],
    }) for g in ghosts]
    ghost_ghosts = [r for r in ghost_reports if r.status == qg.GhostStatus.GHOST]
    if ghost_ghosts:
        print(qg.format_ghost_report(ghost_reports))
        print()

    # Schedule best leg (quota-gated)
    best = claim_engine.schedule_best_leg(root, caps, quota_snapshot=snapshot)
    if not best:
        print("ℹ️ no compatible unclaimed actionable work available")
        return EXIT_OK
    leg, score_info = best
    lid = record_id(leg) or leg.get("_file", "")
    print(f"🎯 Scheduled best leg: {lid}")
    print(f"   Score: {score_info['score']} (unblocks={score_info['unblocks_others']}, priority={score_info['gm_priority']}, finishable={score_info['finishable_now']})")
    print(f"   Goal:  {leg.get('goal') or '(no goal)'}")
    if score_info.get("quota_decision"):
        print(f"   Quota: {score_info['quota_decision']} — {score_info.get('quota_reason', '')}")
    if args.take:
        print(f"⚡ Auto-claiming leg {lid}...")
        return cmd_claim(_ns(action="take", scope=f"relay:{lid}", goal=f"CLAIMED_FOR_EXECUTION: {leg.get('goal') or lid}", ttl=args.ttl, force=args.force, no_push=args.no_push))
    return EXIT_OK


def cmd_quota(args: argparse.Namespace) -> int:
    """Display quota governor status, burn velocity, and breach projections."""
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE

    from . import quota_governor as qg

    snapshot = qg.load_snapshot_from_env()
    thresholds = qg.load_thresholds_from_env()

    # Try to load burn ledger from disk
    ledger_path = root / ".handoffs" / "burn_ledger.json"
    ledger = qg.load_ledger_from_file(ledger_path)

    governor = qg.QuotaGovernor(thresholds, ledger)
    status = governor.status_report(snapshot)
    print(qg.format_quota_status(status))

    # Marathon calibration reference
    if getattr(args, "calibration", False):
        print()
        print("📊 MARATHON CALIBRATION (40.5h Phoebus session):")
        cal = qg.MARATHON_CALIBRATION
        print(f"   Duration: {cal['duration_hours']}h | Steps: {cal['total_steps']:,}")
        print(f"   Billable: {cal['billable_tokens']:,} tokens ({cal['fresh_input_tokens']:,} in + {cal['output_tokens']:,} out)")
        print(f"   Cache: {cal['cache_read_tokens']:,} reads ({cal['cache_hit_ratio']:.2%} hit)")
        print(f"   Shadow: ${cal['shadow_cost_flash_usd']:.2f} (Flash) / ${cal['shadow_cost_pro_usd']:.2f} (Pro)")
        print(f"   Rate: ${cal['cost_per_hour_flash_usd']:.2f}/hr (Flash) | {cal['tokens_per_hour_billable']:,} billable tok/hr")
        print(f"   Efficiency: {cal['tokens_per_1k_tool_calls']:,} tok/1k tools | {cal['tokens_per_landing']:,} tok/landing")

    return EXIT_OK


def cmd_ghost(args: argparse.Namespace) -> int:
    """Detect ghost workers and orphan work across the fleet."""
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE

    from . import claim_engine
    from . import quota_governor as qg

    ghosts = claim_engine.ghost_worker_check(root)

    if not ghosts:
        print("✅ No active sessions detected.")
        return EXIT_OK

    ghost_reports = [qg.GhostWorkerReport(**{
        "machine": g["machine"], "agent": g["agent"], "session": g["session"],
        "status": qg.GhostStatus(g["status"]), "active_claims": g["active_claims"],
        "detail": g["detail"],
    }) for g in ghosts]

    print(qg.format_ghost_report(ghost_reports))

    # Fleet Execution Law reminder
    ghost_count = sum(1 for r in ghost_reports if r.status == qg.GhostStatus.GHOST)
    if ghost_count:
        print()
        print("📜 FLEET EXECUTION LAW:")
        print("   1. Session/process activity ≠ ownership")
        print("   2. ONLY an explicit live claim reserves a leg/scope")
        print("   3. Scheduler continues assigning unrelated work across all lanes")
        print(f"   ⚠️ {ghost_count} session(s) should register claims or be isolated")

    return EXIT_OK


def cmd_route(args: argparse.Namespace) -> int:
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE
    if not args.id:
        print("❌ --id is required for routing check")
        return EXIT_USAGE
    path = _record_path(root, args.id)
    if not path or not path.is_file():
        print(f"❌ record {args.id} not found")
        return EXIT_FAILURE
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        print("❌ record corrupt")
        return EXIT_FAILURE
    matched = match_lane_for_leg(rec)
    print(f"🎯 Best matched lane for {args.id}: {matched}")
    eligible = [lane for lane in LANE_CAPABILITIES if is_lane_eligible(lane, rec)]
    print(f"   Eligible lanes: {', '.join(eligible)}")
    return EXIT_OK


def cmd_fail(args: argparse.Namespace) -> int:
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE
    if not args.id:
        print("❌ --id is required for fail/retry record")
        return EXIT_USAGE
    err = args.message or "execution error"
    res = record_leg_failure(root, args.id, err, max_retries=args.max_retries)
    status = res.get("status")
    retries = res.get("retry_count")
    if status == "dead_letter":
        print(f"❌ {args.id} marked as dead_letter (exceeded max retries: {retries})")
    else:
        print(f"⚠️ {args.id} failed (attempt {retries}) -> next retry: {res.get('next_retry_utc')}")
    return EXIT_OK


def _ns(**kw) -> argparse.Namespace:
    base = dict(id=None, state=None, message="", no_push=True, no_fetch=True,
                scope=None, goal=None, ttl=None, force=False, action=None, all=False,
                target_agent=None, tags=None, max_retries=None)
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
    c.add_argument("--parent", help="full id of the leg this one branches from")
    c.add_argument("--target-agent", help="designated target lane for capability routing")
    c.add_argument("--tags", help="comma-separated tags / capability requirements")
    c.set_defaults(func=cmd_create)

    s2 = sub.add_parser(
        "summarize",
        help="close an abandoned branch: summary leg + parent -> abandoned",
    )
    s2.add_argument("--id", required=True,
                    help="parent leg to summarize and mark abandoned")
    s2.add_argument("-g", "--goal", default="",
                    help="one-line goal (defaults to naming the parent)")
    s2.add_argument("-m", "--message", help="summary text (single line; prefer -M)")
    s2.add_argument("-M", "--message-file", help="path to a UTF-8 markdown summary")
    s2.set_defaults(func=cmd_summarize)

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

    # Leased execution subcommand
    l_parser = sub.add_parser("lease", help="atomic execution leases for open legs")
    l_parser.add_argument("action", choices=["acquire", "release", "list"])
    l_parser.add_argument("--id", help="leg id to lease/release")
    l_parser.add_argument("-g", "--goal", default="", help="one-line intent")
    l_parser.add_argument("--ttl", type=float, help="minutes before lease expires (default: 15m)")
    l_parser.add_argument("--force", action="store_true", help="force acquire lease")
    l_parser.add_argument("--all", action="store_true", help="list expired leases too")
    l_parser.set_defaults(func=cmd_lease)

    # Wake signal subcommand
    w_parser = sub.add_parser("wake", help="autonomous wake signal queue")
    w_parser.add_argument("action", choices=["list", "emit", "consume"])
    w_parser.add_argument("--id", help="leg id for wake signal")
    w_parser.add_argument("-g", "--goal", default="", help="goal description")
    w_parser.set_defaults(func=cmd_wake)

    # Schedule subcommand (Claim Engine)
    sch_parser = sub.add_parser("schedule", help="auto-score and select the best compatible open leg")
    sch_parser.add_argument("--take", action="store_true", help="automatically take an active claim on the best leg")
    sch_parser.add_argument("--ttl", type=float, help="claim TTL in hours")
    sch_parser.add_argument("--force", action="store_true", help="force claim regardless of overlap")
    sch_parser.add_argument("--no-push", action="store_true", help="keep claim local")
    sch_parser.set_defaults(func=cmd_schedule)

    # Route subcommand
    rt_parser = sub.add_parser("route", help="check capability/tag routing for a leg")
    rt_parser.add_argument("--id", required=True, help="leg id to evaluate")
    rt_parser.set_defaults(func=cmd_route)

    # Fail / Retry subcommand
    f_parser = sub.add_parser("fail", help="record failure with exponential backoff or dead_letter")
    f_parser.add_argument("--id", required=True, help="leg id")
    f_parser.add_argument("-m", "--message", default="", help="error message")
    f_parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES, help="max retries before dead_letter")
    # Quota subcommand (Quota Governor)
    q_parser = sub.add_parser("quota", help="view quota governor status and burn velocity")
    q_parser.add_argument("--calibration", action="store_true", help="show 40.5h marathon calibration metrics")
    q_parser.set_defaults(func=cmd_quota)

    # Ghost subcommand (Ghost Worker Detector)
    g_parser = sub.add_parser("ghost", help="detect ghost workers and unowned background processes")
    g_parser.set_defaults(func=cmd_ghost)

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
