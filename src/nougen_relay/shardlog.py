"""Relay the shards — publish vault knowledge to the machines that cannot read it.

The registry travels; the vault does not. Claims and legs are tracked in git, so
every box sees them. What one box *learned* lives in a local shard vault
(``~/.nougen/shards``) that no other machine can open, which means a day of hard
knowledge is invisible to the rest of the fleet the moment the session ends.

This is the transport. It reads the vault and writes ``docs/FLEET-LOG-<date>.md``
— tracked, reviewable, and readable on any box.

Three constraints shape it, all learned the hard way:

- **Generated, never retyped.** The log is the record, not a summary of a
  summary. Content is copied verbatim out of the vault; the only edit made to a
  shard's body is demoting its headings so they cannot impersonate the log's own
  structure (the first hand-run relay let ``## VERIFIED LIVE`` inside a shard
  read as a top-level entry).
- **Not everything travels.** Brand, family and money are not engineering. They
  are tagged that way in the vault and this refuses to copy them into a code
  repo — it names them and says where to read them instead. ``--include-tagged``
  exists for the operator who genuinely means it.
- **Scan for secret VALUES before writing.** Shards quote commands, and commands
  carry keys. The scan looks for the shape of a credential, not the word
  "secret" — ``wrangler secret put TWITCH_CLIENT_SECRET`` is a variable name and
  must not trip it, while ``sk-...`` must.

No runtime dependencies: sqlite3 and re are stdlib, like the rest of the package.
"""

import argparse
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Optional

from .core import (
    EXIT_FAILURE,
    EXIT_OK,
    repo_root,
    resolve_machine,
)

DEFAULT_VAULT = "~/.nougen/shards"
VAULT_GLOB = "nougen_shards_*.db"
LOG_DIR = "docs"
LOG_PREFIX = "FLEET-LOG-"

#: Tags that mark a shard as belonging to a person rather than to the fleet.
#: A code repo is the wrong home for these even when the repo is private.
WITHHELD_TAGS = frozenset(
    {"brand", "positioning", "personal", "family", "finance", "legal", "medical",
     "insurance"}
)

#: Machine-readable footer so the *next* relay knows where this one stopped —
#: on any box, including one that has never seen this session. The machine
#: field says whose vault was published; older markers never wrote it.
MARKER_RE = re.compile(
    r"<!--\s*relay-shards\s+through=(\S+)(?:\s+machine=(\S+))?", re.IGNORECASE
)

#: What a captured marker value must look like to be believed. The 2026-08-01
#: log documented the marker format in prose — `through=<iso>` — and MARKER_RE
#: happily matched it. `"<iso>"` then won every string max() against real
#: timestamps ('<' sorts above '9'), so every relay on every box reported
#: "the fleet is already current" from 08-05 onward. A marker that does not
#: parse as a timestamp is prose, not provenance.
MARKER_VALUE_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

#: Fallback when a log predates the marker: entry headings are `## HH:MMZ — …`,
#: which content headings never match.
HEADING_RE = re.compile(r"^## (\d{2}):(\d{2})Z\s+[-—]\s+(.*)$", re.MULTILINE)

#: Withheld shards are listed as `- \`HH:MMZ\` title (tags)` and are just as
#: relayed as the copied ones — the fleet has been told they exist.
WITHHELD_RE = re.compile(r"^- `\d{2}:\d{2}Z` (.*?)(?: \([^()]*\))?$", re.MULTILINE)

FENCE_RE = re.compile(r"^\s*(```|~~~)")

#: Shapes of credentials, not names of them. Each is a value that would be live
#: the moment it landed in a tracked file.
SECRET_PATTERNS = (
    ("openai/openrouter key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}")),
    ("aws access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("huggingface token", re.compile(r"\bhf_[A-Za-z0-9]{20,}")),
    ("google api key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    (
        "assigned credential",
        re.compile(
            r"(?i)\b(?:secret|token|password|passwd|api[_\-]?key|client[_\-]?secret)\b"
            r"\s*[:=]\s*[\"']?[A-Za-z0-9/+_\-]{24,}"
        ),
    ),
)


def vault_paths(explicit: Optional[str] = None) -> list:
    """Every shard database, in stable order.

    The vault is sharded across numbered files; a day's knowledge routinely
    lands in several of them, so reading only the newest silently drops entries.

    Resolved on call, never at import: a box with no HOME still has to be able
    to run `relay --help`, and an import-time expanduser() would take the whole
    CLI down with it.
    """
    configured = explicit or os.environ.get("NOUGEN_VAULT")
    if configured is None and not any(
        os.environ.get(name) for name in ("HOME", "USERPROFILE", "HOMEPATH", "HOMEDRIVE")
    ):
        return []
    raw = configured or DEFAULT_VAULT
    try:
        root = Path(raw).expanduser()
    except RuntimeError:
        return []
    if not root.is_dir():
        return []
    return sorted(root.glob(VAULT_GLOB))


def _log_dir(root: Optional[Path], explicit: Optional[str]) -> Path:
    if explicit:
        return Path(explicit)
    return (root or Path.cwd()) / LOG_DIR


def last_relayed(log_dir: Path, machine: Optional[str] = None) -> Optional[str]:
    """The timestamp the previous relay stopped at, read off the logs themselves.

    Deliberately not stored in a state file: the cutoff has to survive a fresh
    clone, because the next relay may run on a different machine.

    Vaults are per-box, so when ``machine`` is given, only markers written by
    that machine (or by nobody — attribution postdates the first logs) can
    advance its cutoff. Observed 2026-08-08: whoart's 08-05 relay had pushed
    the fleet-wide cutoff past shards blade1tb had never published at all —
    not republished, never published, and nothing would ever offer them again.
    A box relaying for the first time therefore sees its whole vault as
    unpublished, which is the truth; curate with --since / --exclude.
    """
    best: Optional[str] = None
    for path in sorted(log_dir.glob(f"{LOG_PREFIX}*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        # All matches, not the first: a log can quote the marker format in
        # prose above its real footer. Only values shaped like timestamps
        # count, and the newest one in the file is the one that stands.
        found = [(m.group(1), m.group(2)) for m in MARKER_RE.finditer(text)
                 if MARKER_VALUE_RE.match(m.group(1))]
        if found:
            binding = [ts for ts, who in found
                       if machine is None or who is None
                       or who.lower() == machine.lower()]
            if not binding:
                # A real marker, another box's relay: it says nothing about
                # our vault, and its headings must not become a cutoff either.
                continue
            candidate = max(binding)
        else:
            # Pre-marker log: recover the cutoff from its newest entry heading.
            date = path.stem[len(LOG_PREFIX):]
            times = HEADING_RE.findall(text)
            if not times:
                continue
            hh, mm, _ = max(times)
            # Headings carry minutes, so the true cutoff is somewhere inside
            # that minute. Round DOWN: re-offering a shard is caught by title,
            # skipping one is silent and permanent.
            candidate = f"{date}T{hh}:{mm}:00.000000Z"
        if best is None or candidate > best:
            best = candidate
    return best


def relayed_titles(log_dir: Path) -> set:
    """Titles the fleet has already been shown, copied or merely named.

    The cutoff alone is not enough: a marker can be missing, a clock can be
    coarse, and a hand-run relay leaves neither. Nothing here is authoritative
    about *content* — it exists so the same knowledge is never published twice.
    """
    seen = set()
    for path in sorted(log_dir.glob(f"{LOG_PREFIX}*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        seen.update(t.strip() for _, _, t in HEADING_RE.findall(text))
        seen.update(t.strip() for t in WITHHELD_RE.findall(text))
    return seen


def read_shards(paths: list, since: Optional[str]) -> list:
    """Shards captured after ``since``, oldest first, de-duplicated across files.

    Read-only URIs throughout: a relay must never be the reason the vault is
    locked or altered.
    """
    seen = set()
    rows = []
    for db in paths:
        try:
            conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        except sqlite3.Error:
            continue
        try:
            sql = (
                "SELECT timestamp, event_type, title, content, tags, file_hash "
                "FROM shards"
            )
            params: tuple = ()
            if since:
                sql += " WHERE timestamp > ?"
                params = (since,)
            for ts, event, title, content, tags, digest in conn.execute(sql, params):
                if digest in seen:
                    continue
                seen.add(digest)
                try:
                    parsed = json.loads(tags) if tags else []
                except (TypeError, ValueError):
                    parsed = []
                rows.append(
                    {
                        "timestamp": ts,
                        "event_type": event,
                        "title": title,
                        "content": content or "",
                        "tags": [str(t).lower() for t in parsed],
                        "hash": digest,
                        "source": db.name,
                    }
                )
        except sqlite3.Error:
            continue
        finally:
            conn.close()
    rows.sort(key=lambda r: r["timestamp"])
    return rows


def demote_headings(text: str) -> str:
    """Push a shard's own headings one level down, leaving code fences alone.

    Without this a shard body claims the log's structure: its `## LESSON` reads
    as a sibling of the entries and the table of contents becomes nonsense.
    """
    out = []
    fenced = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            fenced = not fenced
            out.append(line)
            continue
        if not fenced and line.startswith("#"):
            hashes = len(line) - len(line.lstrip("#"))
            if 1 <= hashes <= 5 and line[hashes:hashes + 1] in (" ", ""):
                line = "#" + line
        out.append(line)
    return "\n".join(out)


def scan_secrets(entries: list) -> list:
    """Credential-shaped strings in what is about to be committed."""
    hits = []
    for entry in entries:
        blob = f"{entry['title']}\n{entry['content']}"
        for label, pattern in SECRET_PATTERNS:
            match = pattern.search(blob)
            if match:
                found = match.group(0)
                redacted = found[:6] + "…" + found[-4:] if len(found) > 14 else found
                hits.append((entry, label, redacted))
    return hits


def _heading_time(ts: str) -> str:
    return f"{ts[11:13]}:{ts[14:16]}Z" if len(ts) >= 16 else ts


def render(entries: list, withheld: list, *, date: str, machine: str,
           cutoff: Optional[str], through: str) -> str:
    """The log itself. Verbatim bodies, generated frame."""
    count = len(entries)
    noun = "entry" if count == 1 else "entries"
    lines = [
        f"# Fleet log — {date}",
        "",
        f"Everything {machine} learned since the last relay, published because",
        "**shards do not travel**. The vault lives at `~/.nougen/shards` on",
        f"{machine}; the other machines cannot read it. This file is the transport,",
        "and it is the record you should trust over any summary in a chat window.",
        "",
        f"{count} {noun}, oldest first. Verbatim from the vault — not re-summarised."
        if count
        else "Nothing engineering-side crossed since the last relay. What was"
             " captured is named below and stays in the vault.",
    ]
    if cutoff:
        lines += ["", f"Covers shards captured after `{cutoff}`."]
    lines += ["", "---", ""]

    for entry in entries:
        lines.append(f"## {_heading_time(entry['timestamp'])} — {entry['title']}")
        lines.append("")
        lines.append(demote_headings(entry["content"]).strip())
        lines.append("")
        lines.append("---")
        lines.append("")

    if withheld:
        lines += [
            "## Not included here",
            "",
            "These were captured in the same window but are not engineering, and a",
            "code repo is the wrong home for them. They stay in the vault — read",
            "them with `recall_memory` on a box that has it:",
            "",
        ]
        for entry in withheld:
            tags = ", ".join(t for t in entry["tags"] if t in WITHHELD_TAGS)
            lines.append(f"- `{_heading_time(entry['timestamp'])}` {entry['title']} ({tags})")
        lines += ["", "---", ""]

    lines.append(
        f"<!-- relay-shards through={through} machine={machine} "
        f"generated-by=relay-shards -->"
    )
    return "\n".join(lines) + "\n"


def cmd_shards(args: argparse.Namespace) -> int:
    root = repo_root()
    log_dir = _log_dir(root, args.out)
    paths = vault_paths(args.vault)
    if not paths:
        print("❌ no shard vault found — set NOUGEN_VAULT or pass --vault")
        return EXIT_FAILURE

    cutoff = args.since or last_relayed(log_dir, resolve_machine())
    rows = read_shards(paths, cutoff)
    if not rows:
        where = f" since {cutoff}" if cutoff else ""
        print(f"✅ nothing new in the vault{where} — the fleet is already current")
        return EXIT_OK

    excluded = set(args.exclude or [])
    rows = [r for r in rows if r["hash"] not in excluded and r["title"] not in excluded]

    published = relayed_titles(log_dir)
    repeats = [r for r in rows if r["title"] in published]
    rows = [r for r in rows if r["title"] not in published]
    if repeats:
        print(f"ℹ️ {len(repeats)} already published by an earlier relay — skipped")
    if not rows:
        print("✅ nothing new to publish — the fleet is already current")
        return EXIT_OK

    if args.include_tagged:
        entries, withheld = rows, []
    else:
        entries = [r for r in rows if not (WITHHELD_TAGS & set(r["tags"]))]
        withheld = [r for r in rows if WITHHELD_TAGS & set(r["tags"])]

    hits = scan_secrets(entries)
    if hits:
        print("🛑 refusing to write — credential-shaped values in the payload:")
        for entry, label, redacted in hits:
            print(f"   {entry['timestamp']} {entry['title'][:60]}")
            print(f"      {label}: {redacted}")
        print("   Fix the shard, or drop it with --exclude <title|hash>.")
        return EXIT_FAILURE

    through = rows[-1]["timestamp"]
    date = args.date or through[:10]
    machine = resolve_machine()
    body = render(entries, withheld, date=date, machine=machine,
                  cutoff=cutoff, through=through)

    target = log_dir / f"{LOG_PREFIX}{date}.md"
    if args.dry:
        print(f"— would write {target} ({len(entries)} relayed, "
              f"{len(withheld)} withheld) —\n")
        print(body)
        return EXIT_OK

    log_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    print(f"✅ wrote {target}")
    print(f"   {len(entries)} relayed · {len(withheld)} withheld · through {through}")
    if withheld:
        print("   withheld stay in the vault; the log says where to read them")
    print("   commit and push it, then pass the baton: relay create -g '…'")
    return EXIT_OK


def register(sub) -> None:
    """Wire `relay shards` into the parser."""
    s = sub.add_parser(
        "shards", help="publish vault knowledge the other machines cannot read"
    )
    s.add_argument("--since", help="ISO cutoff (default: where the last relay stopped)")
    s.add_argument("--vault", help=f"shard directory (default: $NOUGEN_VAULT, else {DEFAULT_VAULT})")
    s.add_argument("--out", help=f"log directory (default: <repo>/{LOG_DIR})")
    s.add_argument("--date", help="log date (default: the newest shard's UTC date)")
    s.add_argument("--exclude", action="append", metavar="TITLE|HASH",
                   help="drop one shard from this relay; repeatable")
    s.add_argument("--include-tagged", action="store_true",
                   help=f"also copy shards tagged {sorted(WITHHELD_TAGS)} into the repo")
    s.add_argument("-n", "--dry", action="store_true", help="print the log, write nothing")
    s.set_defaults(func=cmd_shards)
