"""Antigravity PreToolUse hook — enforcement, not advice.

The skill *tells* an Antigravity lane to claim scope before editing. Nothing
made it. This does: it runs before every file-edit tool and decides whether the
edit may proceed, using the same claim registry every other machine reads.

Contract (Antigravity hooks): JSON on stdin, JSON on stdout, always exit 0.
  in : {"toolCall": {"name": ..., "args": {...}}, "workspacePaths": [...], ...}
  out: {"decision": "allow"|"deny"|"ask"|"force_ask", "reason": "..."}

The decision ladder, and why it is not simply "deny when unclaimed":

  another machine holds an overlapping claim  -> deny
        This is the actual collision the registry exists to prevent. Blocking
        here is the whole point, and the reason names who holds it.

  nobody has claimed this scope               -> ask
        A nudge, not a wall. The edit may be entirely reasonable; the lane just
        has not announced it. Denying would train the operator to rip the hook
        out, and a hook that gets removed protects nothing.

  this machine already holds the claim        -> allow
  anything at all goes wrong                  -> allow

That last line is deliberate. A guard that fails closed on its own bug is worse
than the problem it prevents — today a well-meant guard proposal would have
aborted a ten-commit rebase partway. If this hook cannot answer, it gets out of
the way and says why.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Tools that write to files. Read-only tools are none of this hook's business.
EDIT_TOOLS = {"write_to_file", "replace_file_content", "multi_replace_file_content"}

TIMEOUT = 20


def _emit(decision: str, reason: str = "") -> None:
    out = {"decision": decision}
    if reason:
        out["reason"] = reason
    print(json.dumps(out))
    sys.exit(0)


def _target_path(args: dict) -> str:
    for key in ("TargetFile", "AbsolutePath", "target_file"):
        val = args.get(key)
        if isinstance(val, str) and val:
            return val
    return ""


def _repo_for(path: str, workspaces: list) -> str | None:
    """The repo ROOT a path belongs to.

    Not the file's parent directory — `src/app/` holds no `.handoffs`, so
    resolving to it silently disables the guard for every file that is not at
    the top level. Walk up until a marker appears, then fall back to a
    workspace that contains the target.
    """
    if path:
        here = Path(path)
        for cand in [here, *here.parents]:
            try:
                if (cand / ".handoffs").is_dir() or (cand / ".git").exists():
                    return str(cand)
            except OSError:
                break
    for ws in workspaces:
        if not isinstance(ws, str) or not Path(ws).is_dir():
            continue
        if not path:
            return ws
        try:
            Path(path).relative_to(ws)
            return ws
        except ValueError:
            continue
    return None


def _active_claims(core, repo: str) -> list:
    """Active claim records, read structurally.

    An earlier version scraped `claim list` stdout. That was wrong on contact
    with reality: the output carries box glyphs, CR line endings and a
    `[mine  ]` padding field, so the parser silently returned nothing and the
    guard allowed everything while looking like it worked. The records are
    already structured — read those instead of re-deriving them from a display
    format that exists for humans.
    """
    return [rec for rec in core._read_claims_from(Path(repo), None)
            if core.claim_is_active(rec)]


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    try:
        payload = json.load(sys.stdin)
    except Exception:
        _emit("allow", "")  # not our payload to judge

    tool = (payload.get("toolCall") or {}).get("name", "")
    if tool not in EDIT_TOOLS:
        _emit("allow")

    args = (payload.get("toolCall") or {}).get("args") or {}
    target = _target_path(args)
    repo = _repo_for(target, payload.get("workspacePaths") or [])
    if not repo:
        _emit("allow")

    try:
        from . import core
    except Exception:
        _emit("allow", "nougen-relay: registry unavailable, not gating this edit")

    try:
        if not (core.handoff_dir(Path(repo)).is_dir()
                or (Path(repo) / ".handoffs").is_dir()):
            _emit("allow")  # not a relay-coordinated repo

        # Resolved, never assumed: env if the operator named this box, else the
        # OS. The guard must agree with whatever the registry will stamp.
        machine = core.resolve_machine()

        # RESOLVE BOTH SIDES BEFORE COMPARING. A twelve-route independent
        # review reached this unanimously, and it is the difference between a
        # guard and a decoration: the comparison is string-based, so any path
        # that names a claimed file differently walks straight past it —
        # `src/../src/lib/x.ts`, a symlink into a claimed directory, or `./x`.
        # resolve() collapses `..`, follows symlinks, and normalises case on
        # Windows, so the string being compared is the real file's identity
        # rather than the spelling the caller chose.
        try:
            real = Path(target).resolve()
            real_repo = Path(repo).resolve()
        except OSError:
            _emit("ask", "nougen-relay: target path could not be resolved; "
                         "refusing to judge a path I cannot pin down")

        rel = str(real)
        try:
            rel = str(real.relative_to(real_repo))
        except ValueError:
            # Outside the repo after resolution — a symlink pointing out, or a
            # path from another tree. No claim here can speak for it, and
            # silently allowing is how the bypass worked.
            _emit("ask", f"nougen-relay: {real} resolves outside {real_repo}; "
                         f"no claim in this repo governs it")

        # Claims are written with forward slashes; Windows hands us backslashes.
        # Without this the tokens never match and every edit falls through to
        # "ask" — the guard looks alive and gates nothing.
        rel = rel.replace("\\", "/")

        for claim in _active_claims(core, repo):
            if not core._scopes_overlap(rel, claim.get("scope", "")):
                continue
            hits = core._scopes_overlap(rel, claim.get("scope", ""))
            if claim.get("machine") == machine:
                _emit("allow")  # our own claim already covers this
            _emit(
                "deny",
                f"nougen-relay: {claim.get('machine')}/{claim.get('agent')} holds an "
                f"active claim overlapping {', '.join(hits)} — goal: "
                f"{claim.get('goal')}. Read their claim and either stand down and "
                f"pick different work, or take it deliberately with "
                f"`claim take --force`. Do not narrow the scope string to slip "
                f"past this.",
            )

        _emit(
            "ask",
            f"nougen-relay: no claim covers {rel}. Other machines work this repo "
            f"and cannot see what you are about to change. Call "
            f"relay_claim_take(scope, goal) first, or approve to proceed unclaimed.",
        )
    except Exception as exc:  # never let this hook be the thing that breaks a session
        _emit("allow", f"nougen-relay: guard errored ({type(exc).__name__}), allowing")


if __name__ == "__main__":
    main()
