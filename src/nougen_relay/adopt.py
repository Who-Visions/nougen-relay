"""Give a repository relay coverage, in one command, idempotently.

A claim only protects the repo whose registry it lives in. NouGenRelay had
`.handoffs`; NouGenTracker did not, so a correctly-taken claim for a tracker
file overlapped nothing and reported all-clear while another machine was
already doing the work. The registry has to exist everywhere work happens, and
"remember to create it" is the same failure one level up.

    relay adopt                 # this repo, lane from git config
    relay adopt --agent claude-cli
    relay adopt --dry           # say what would change, change nothing

Everything here is idempotent and additive: an existing hooksPath is respected
rather than seized, an existing hook is only rewritten when its content differs
from the shipped one, and nothing is deleted.

The hooks are string constants rather than files copied out of this repo,
because `relay` is installed with `pip install -e .` from clones that may not
have the repo's own `hooks/` directory beside them. `test_adopt.py` pins the
repo's checked-in hooks to these constants, so the two can never drift.
"""
from __future__ import annotations

import argparse
import os
import stat
from pathlib import Path

from . import core as gh
from . import ui

# --- shipped hooks ----------------------------------------------------------

PREPARE_COMMIT_MSG = r'''#!/bin/sh
# Stamp every commit with the machine and agent that authored it.
#
# With several machines and several agent lanes pushing to one repo, the git
# author field answers "which human account" and nothing else. These trailers
# answer "which computer, which lane" — the questions you actually ask when
# two histories collide.
#
# Enable per clone (hooks are not themselves tracked into .git/hooks):
#     git config core.hooksPath hooks
#
# Identity resolves the same way core.resolve_agent() does, INCLUDING git
# config. It did not, once: `relay init --agent` stored the lane in git config
# and printed "survives new shells", and this hook — reading only the env —
# refused the very next commit as unknown-agent. Two resolvers, one question,
# different answers.
# git interpret-trailers is idempotent, so amends and rebases do not stack
# duplicate lines.
#
# Two rules, and the first one matters more:
#
# 1. AN EXISTING TRAILER IS NEVER OVERWRITTEN. This hook re-runs on every
#    commit a rebase or cherry-pick replays, with the REPLAYING machine's
#    environment. Measured 2026-07-31: `git rebase origin/main` on blade
#    rewrote a commit stamped `phoebus` / `claude-cli` into `blade1tb` /
#    `unknown-agent` — one command silently reattributed another machine's work
#    and lost the lane. The trailer records who WROTE the commit, so the env is
#    only ever used to fill a blank.
#
# 2. A NEW commit is refused if it would enter history misidentified — unset
#    lane, or a machine name this repo has never seen. Never during a replay:
#    aborting a ten-commit rebase halfway is worse than a wrong trailer, and
#    rule 1 has already kept the replayed identity correct.

MSG_FILE="$1"
SOURCE="$2"

# Leave merges, squashes and explicit -m reuse alone: their messages are not
# ours to annotate.
case "$SOURCE" in
    merge|squash) exit 0 ;;
esac

if [ -n "$NOUGEN_MACHINE" ]; then
    # Passed through untouched, exactly as core.resolve_machine() does it: a
    # dotted name someone typed is their word on what this box is called.
    MACHINE="$NOUGEN_MACHINE"
else
    MACHINE=$(git config --get nougen.machine 2>/dev/null)
    if [ -z "$MACHINE" ]; then
        # A PROBED hostname can carry a suffix the network handed out rather
        # than a name anyone chose. Only known local-network ones are stripped.
        # POSIX `case`, not sed: `\|` alternation is a GNU extension, and BSD
        # sed (macOS) matches it literally — green on Windows, red on a Mac,
        # for a fix about names.
        MACHINE=$(hostname 2>/dev/null)
        case "$MACHINE" in
            *.local|*.lan|*.home|*.internal|*.localdomain) MACHINE="${MACHINE%.*}" ;;
        esac
    fi
fi
[ -z "$MACHINE" ] && MACHINE="unknown-machine"

AGENT="$NOUGEN_AGENT"
[ -z "$AGENT" ] && AGENT=$(git config --get nougen.agent 2>/dev/null)
[ -z "$AGENT" ] && AGENT="unknown-agent"

# Lowercase and slugify to match the handoff filenames, so a grep for a machine
# finds both its commits and its handoffs.
MACHINE=$(printf '%s' "$MACHINE" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9\n' '-' | sed 's/-*$//')
AGENT=$(printf '%s' "$AGENT" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9\n' '-' | sed 's/-*$//')

# --- rule 1: keep what is already there ----------------------------------
existing() {
    git interpret-trailers --parse "$MSG_FILE" 2>/dev/null | sed -n "s/^$1: *//p" | tail -1
}
OLD_MACHINE=$(existing Machine)
OLD_AGENT=$(existing Agent)
[ -n "$OLD_MACHINE" ] && [ "$OLD_MACHINE" != "unknown-machine" ] && MACHINE="$OLD_MACHINE"
[ -n "$OLD_AGENT" ] && [ "$OLD_AGENT" != "unknown-agent" ] && AGENT="$OLD_AGENT"

# --- rule 2: refuse a misidentified NEW commit ---------------------------
GIT_DIR_PATH=$(git rev-parse --git-dir 2>/dev/null) || GIT_DIR_PATH=".git"
REPLAYING=""
for marker in rebase-merge rebase-apply CHERRY_PICK_HEAD MERGE_HEAD REVERT_HEAD; do
    [ -e "$GIT_DIR_PATH/$marker" ] && REPLAYING="1"
done

# One deliberate override, because a guard that cannot be passed is a guard
# people uninstall. NOUGEN_IDENTITY_OK=1 is also how a genuinely new box
# introduces itself the first time.
if [ -z "$REPLAYING" ] && [ "$NOUGEN_IDENTITY_OK" != "1" ]; then
    if [ "$AGENT" = "unknown-agent" ]; then
        echo "✋ refusing to commit as 'unknown-agent'." >&2
        echo "   Nothing on this machine knows which lane is driving, so an" >&2
        echo "   unset lane is permanent once the commit lands." >&2
        echo "" >&2
        echo "   relay init --agent <your-lane>        # stored per clone, survives shells" >&2
        echo "   NOUGEN_IDENTITY_OK=1 git commit ...   # or override, deliberately" >&2
        exit 1
    fi

    ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || ROOT="."
    DIR="$ROOT/${NOUGEN_GIT_HANDOFF_DIR:-.handoffs}"
    KNOWN=$(ls "$DIR" 2>/dev/null | sed -n 's/^[^_]*__\([^_]*\)__.*/\1/p' | sort -u)
    if [ -n "$KNOWN" ] && ! printf '%s\n' "$KNOWN" | grep -qx "$MACHINE"; then
        echo "✋ '$MACHINE' has never written a record in this repo." >&2
        echo "   Machines already here: $(printf '%s ' $KNOWN)" >&2
        echo "" >&2
        echo "   If your hostname is not what the fleet calls this box, name it:" >&2
        echo "     relay init --agent <lane> --machine <the-name-the-fleet-uses>" >&2
        echo "   If this box really is new, introduce it once:" >&2
        echo "     NOUGEN_IDENTITY_OK=1 git commit ..." >&2
        exit 1
    fi
fi

git interpret-trailers --in-place \
    --if-exists replace \
    --trailer "Machine: $MACHINE" \
    --trailer "Agent: $AGENT" \
    "$MSG_FILE"

exit 0
'''

PRE_COMMIT = r'''#!/bin/sh
# Refuse a commit that touches files another machine has actively claimed.
#
# `relay claim take` announces work before it starts, and it only helps if
# every lane runs it. Four duplications in two days say that asking people to
# remember does not work, so the question gets asked at the one moment every
# lane passes through regardless of harness or editor: the commit.
#
# Blocks only on ANOTHER machine's claim. A missing claim of your own is a
# warning, because blocking there would fire on every unclaimed typo fix and
# teach the fleet to reach for --no-verify, which disarms the real case too.
# Opt in per repo with: git config nougen.requireClaim true
#
# Fails OPEN. If relay is not installed, or the network is down, or anything
# else goes wrong, the commit proceeds — a guard that can wedge a repo gets
# uninstalled, and an uninstalled guard is worse than none because everyone
# believes it is running.

# The `relay` console script is not guaranteed. On whoart, pip could not write
# C:\Python311\Scripts\relay.exe at all, while `python -m nougen_relay.cli`
# worked from every directory — so a hook that only knows the script name is a
# hook that silently does nothing on a box where the protocol is installed and
# working. Try the script, fall back to the module, give up quietly.
if command -v relay >/dev/null 2>&1; then
    RELAY="relay"
elif command -v python >/dev/null 2>&1 && python -c "import nougen_relay" >/dev/null 2>&1; then
    RELAY="python -m nougen_relay.cli"
elif command -v python3 >/dev/null 2>&1 && python3 -c "import nougen_relay" >/dev/null 2>&1; then
    RELAY="python3 -m nougen_relay.cli"
else
    exit 0
fi

$RELAY guard --staged --quiet
STATUS=$?

# 3 is "someone else has claimed this". Anything else — including relay itself
# erroring — is not a reason to stop a commit.
[ "$STATUS" = "3" ] && exit 1
exit 0
'''

HOOKS = {
    "prepare-commit-msg": PREPARE_COMMIT_MSG,
    "pre-commit": PRE_COMMIT,
}


# --- adoption ---------------------------------------------------------------

def hooks_dir(root: Path) -> Path:
    """Where this clone's hooks live: the configured path, else `hooks/`.

    An existing core.hooksPath is respected rather than seized. NouGenTracker
    uses `.githooks`; pointing it at `hooks` would silently disable the hook it
    already had.
    """
    configured = (gh._git("config", "--get", "core.hooksPath") or "").strip()
    if configured:
        path = Path(configured)
        return path if path.is_absolute() else root / path
    return root / "hooks"


def registry_is_ignored(root: Path, registry: Path) -> bool:
    """Whether git refuses to track the registry.

    `registry.exists()` is a filesystem question. Whether the other machines
    can READ it is a git question, and nothing was asking it — NouGen carried
    130+ records under a `.handoffs/` line in .gitignore since June, so every
    leg written there stayed on the box that wrote it. The directory existed,
    which made the repo look maximally covered, and adoption cheerfully
    reported "registry already present" and installed hooks with nothing to
    publish into.
    """
    rel = registry.name
    return gh._git("check-ignore", rel) is not None


def registry_is_tracked(root: Path, registry: Path) -> bool:
    """Whether anything in the registry is actually committed.

    The second half of the same question: a registry can be un-ignored and
    still empty of tracked files, in which case it also does not exist for
    anybody else. `.gitkeep` is what adoption commits to settle it.
    """
    listed = gh._git("ls-files", registry.name)
    return bool((listed or "").strip())


def _write_executable(path: Path, content: str) -> None:
    # Newlines are forced to \n: git runs these through sh even on Windows, and
    # CRLF makes `#!/bin/sh` unparseable with an error that names no cause.
    #
    # Written through open() rather than Path.write_text(newline=...), which
    # only exists on 3.10+. This package declares >=3.9 and CI tests it, so the
    # tidier call broke the floor it advertises — on a machine where 3.10 is the
    # local python, that is invisible until CI says so.
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    try:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        # Windows has no executable bit and does not need one.
        pass


def adopt(root: Path, agent: str = "", machine: str = "", dry: bool = False) -> list:
    """Bring `root` up to relay coverage. Returns a list of (status, detail)."""
    changes = []
    hooks = hooks_dir(root)
    registry = gh.handoff_dir(root)

    if registry.exists():
        if registry_is_ignored(root, registry):
            # Loud, and it does not resolve itself: only a human editing
            # .gitignore can decide which records are worth sharing.
            changes.append(("missing", f"{registry.name}/ is GITIGNORED — records "
                                       f"stay on this machine. Un-ignore it."))
        elif not registry_is_tracked(root, registry):
            # Adoption writes files; committing them is the caller's step, so
            # "written but not yet committed" has to be a stable state rather
            # than something re-reported as a fresh change on every run.
            if (registry / ".gitkeep").exists():
                changes.append(("ok", f"{registry.name}/.gitkeep written — commit it "
                                      f"so the registry exists for others"))
            elif dry:
                changes.append(("would", f"would track {registry.name}/.gitkeep"))
            else:
                (registry / ".gitkeep").write_text("", encoding="utf-8")
                changes.append(("added", f"created {registry.name}/.gitkeep — "
                                         f"commit it so the registry exists for others"))
        else:
            changes.append(("ok", f"registry {registry.name}/ present and shared"))
    elif dry:
        changes.append(("would", f"would create {registry.name}/"))
    else:
        (registry / "claims").mkdir(parents=True, exist_ok=True)
        # Git will not track an empty directory, and a registry that vanishes
        # on clone is a registry the next machine does not have.
        (registry / ".gitkeep").write_text("", encoding="utf-8")
        changes.append(("added", f"created {registry.name}/ and {registry.name}/claims/"))

    for name, content in HOOKS.items():
        target = hooks / name
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current == content:
            changes.append(("ok", f"{name} already current"))
            continue
        verb = "would update" if dry else ("updated" if current else "installed")
        if not dry:
            hooks.mkdir(parents=True, exist_ok=True)
            _write_executable(target, content)
        changes.append(("would" if dry else "added", f"{verb} {hooks.name}/{name}"))

    configured = (gh._git("config", "--get", "core.hooksPath") or "").strip()
    want = os.path.relpath(hooks, root).replace("\\", "/")
    if configured:
        changes.append(("ok", f"core.hooksPath = {configured}"))
    elif dry:
        changes.append(("would", f"would set core.hooksPath = {want}"))
    else:
        gh._git("config", "core.hooksPath", want)
        changes.append(("added", f"set core.hooksPath = {want}"))

    stored = (gh._git("config", "--get", "nougen.agent") or "").strip()
    lane = (agent or stored).strip()
    if not lane:
        changes.append(("missing", "no lane: run relay adopt --agent <name>"))
    elif stored == gh._slug(lane):
        # Already correct is "ok" whether or not --agent was passed, so a
        # second run over an adopted repo reports no changes. Re-running this
        # across every repo is the normal way to use it, and a command that
        # always claims to have changed something is a command whose output
        # stops being read.
        changes.append(("ok", f"lane = {stored}"))
    elif dry:
        changes.append(("would", f"would set nougen.agent = {gh._slug(lane)}"))
    else:
        gh._git("config", "nougen.agent", gh._slug(lane))
        changes.append(("added", f"set nougen.agent = {gh._slug(lane)}"))

    if machine and not dry:
        gh._git("config", "nougen.machine", gh._slug(machine))
        changes.append(("added", f"set nougen.machine = {gh._slug(machine)}"))

    return changes


_GLYPH = {"ok": "✅", "added": "✅", "would": "•", "missing": "⚠️"}
_STYLE = {"ok": "green", "added": "green", "would": "", "missing": "yellow"}


def cmd_adopt(args: argparse.Namespace) -> int:
    root = gh.repo_root()
    if root is None:
        print("✋ not inside a git work tree")
        return gh.EXIT_FAILURE

    print(ui.head(f"relay coverage — {root.name}"))
    changes = adopt(root, agent=args.agent or "", machine=args.machine or "", dry=args.dry)
    for status, detail in changes:
        print(f"  {ui.label(_GLYPH.get(status, '•'), detail, _STYLE.get(status, ''))}")

    if args.dry:
        print(ui.dim("   --dry: nothing was written"))
        return gh.EXIT_OK
    if any(s == "missing" for s, _ in changes):
        return gh.EXIT_USAGE
    print(ui.dim("   commit the registry and hooks so the other machines get them"))
    return gh.EXIT_OK


def register(sub) -> None:
    a = sub.add_parser("adopt", help="give this repo a registry, hooks and a lane")
    a.add_argument("--agent", help="lane name to store (e.g. claude-cli)")
    a.add_argument("--machine", help="override what the fleet calls this box")
    a.add_argument("--dry", action="store_true", help="report changes, make none")
    a.set_defaults(func=cmd_adopt)
