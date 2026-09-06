#!/usr/bin/env python3
"""Claude Code hooks that feed cross-machine handoff state into the session.

Three entry points, selected by argv[1]:

  session-start   inject what the other machines have done since you last
                  looked, plus any fired triggers, as additionalContext.
  pre-tool        block a force-push onto a ref with unrelated histories.
  stop            remind this machine to publish a handoff before it goes quiet.

Contract: every hook prints one JSON object on stdout and exits 0. A hook that
raises, hangs, or writes garbage degrades the session it was meant to help, so
every path here is wrapped — a broken hook reports itself as degraded and gets
out of the way. Failing soft is the contract, not a convenience.

Wire it up with .claude/settings.json in this repo (see settings.json alongside).
"""
from __future__ import annotations

import json
import sys

# Import the registry as a module so hooks and CLI can never drift apart.
try:
    from . import core as gh
except Exception:  # noqa: BLE001 — a missing tool must not break the session
    gh = None

_GLYPH = {"error": "❌", "warn": "⚠️", "info": "ℹ️"}


def _emit(event: str, context: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": context,
        }
    }))


def _identity_line() -> str:
    """Always state which computer this is. Every line a reader sees is
    ambiguous without it once more than one machine is in play."""
    ident = gh.identity()
    return (
        f"MACHINE: {ident['machine']} (hostname {ident['hostname'] or '?'}, "
        f"via {ident['machine_source']}) · AGENT: {ident['agent']} · "
        f"{ident['branch']}@{ident['sha']} → {ident['remote']}"
    )


def session_start() -> str:
    root = gh.repo_root()
    if root is None:
        return "GIT HANDOFF: not inside a git repository — cross-machine sync unavailable."

    lines = [f"🤝 GIT HANDOFF REGISTRY — {_identity_line()}", ""]

    fired = gh.evaluate_triggers(root, fetch=True)
    if fired:
        lines.append("Triggers fired:")
        for t in fired:
            lines.append(f"  {_GLYPH.get(t['level'], 'ℹ️')} {t['name']}: {t['detail']}")
    else:
        lines.append("✅ no triggers fired — in sync with the other machines.")

    # What the peers actually said, so this session can work off their notes
    # instead of rediscovering their state.
    peers = {}
    for target in gh.watch_targets():
        for rec in gh._remote_handoffs(root, target):
            if rec.get("machine") and rec["machine"] != gh.resolve_machine():
                prev = peers.get(rec["machine"])
                if prev is None or (rec.get("created_utc") or "") > (prev.get("created_utc") or ""):
                    peers[rec["machine"]] = rec
    if peers:
        lines.append("")
        lines.append("Latest handoff from each other machine:")
        for name, rec in sorted(peers.items()):
            lines.append(
                f"  • {name}/{rec.get('agent')} — {rec.get('goal') or '(no goal)'}"
                f" [{rec.get('branch')}@{rec.get('sha')}, {rec.get('created_utc')}]"
            )
        lines.append("  Read one in full: python tools/git_handoff.py pull --full")

    # Claims are the part of this report that can still change what you do:
    # a handoff describes finished work, a claim describes work in flight.
    claims = gh.foreign_claims(root)
    if claims:
        lines.append("")
        lines.append("IN FLIGHT ON OTHER MACHINES — do not duplicate:")
        for (other, scope), rec in sorted(claims.items(), key=lambda kv: str(kv[0])):
            age = gh._claim_age_hours(rec)
            lines.append(
                f"  ⚠️ {other}/{rec.get('agent')} claimed [{scope}]"
                + (f" {age:.1f}h ago" if age is not None else "")
            )
            if rec.get("goal"):
                lines.append(f"     goal: {rec['goal']}")
        lines.append("  Before starting work here, run:")
        lines.append("    python tools/git_handoff.py claim check -s \"<what you will touch>\"")

    lines.append("")
    lines.append(
        "Claim your own work BEFORE starting it — that is what stops duplicate builds:\n"
        "  python tools/git_handoff.py claim take -s \"<paths/topics>\" -g \"<intent>\""
    )

    if any(t["level"] == "error" for t in fired):
        lines.append("")
        lines.append("STOP: an error-level trigger is live. Reconcile before pushing or deploying.")

    return "\n".join(lines)


def pre_tool() -> str:
    """Refuse a force-push when histories are unrelated.

    A force-push is the one action in this workflow that destroys another
    machine's work, and unrelated histories are exactly when it looks
    reasonable and is not.
    """
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return ""
    tool = payload.get("tool_name") or payload.get("toolName") or ""
    if tool != "Bash":
        return ""
    command = (payload.get("tool_input") or payload.get("toolInput") or {}).get("command", "")
    if "push" not in command:
        return ""
    forced = any(flag in command for flag in ("--force", "-f ", "+refs/", "--force-with-lease"))
    if not forced:
        return ""

    root = gh.repo_root()
    if root is None:
        return ""
    fired = gh.evaluate_triggers(root, fetch=True)
    blockers = [t for t in fired if t["name"] == "unrelated_histories"]
    if not blockers:
        return ""
    return (
        "❌ FORCE-PUSH GUARD: " + "; ".join(t["detail"] for t in blockers) +
        f" ({_identity_line()}). Another machine's commits are reachable only from that ref. "
        "Do not force-push. Reconcile, or push to a branch of your own."
    )


def stop() -> str:
    root = gh.repo_root()
    if root is None:
        return ""
    machine = gh.resolve_machine()
    records = [r for _p, r in gh._records(root) if r.get("machine") == machine]

    unpushed = gh._git("log", "--oneline", "@{u}..HEAD") if gh._git(
        "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"
    ) else None
    dirty = bool(gh._git("status", "--porcelain"))
    if not records:
        return (
            f"⚠️ {machine} has never published a git handoff in this repo. "
            "Before ending: python tools/git_handoff.py create -g \"<goal>\" -M <notes.md>"
        )
    if unpushed or dirty:
        return (
            f"⚠️ {machine} has unpublished work (" +
            ", ".join(filter(None, [
                f"{len(unpushed.splitlines())} unpushed commit(s)" if unpushed else "",
                "uncommitted changes" if dirty else "",
            ])) +
            "). The other machines cannot see it. Publish a handoff and push before stopping."
        )
    return ""


_MODES = {
    "session-start": ("SessionStart", session_start),
    "pre-tool": ("PreToolUse", pre_tool),
    "stop": ("Stop", stop),
}


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "session-start"
    event, fn = _MODES.get(mode, _MODES["session-start"])
    if gh is None:
        _emit(event, "GIT HANDOFF: tools/git_handoff.py could not be imported — registry offline.")
        return 0
    try:
        context = fn()
    except Exception as exc:  # noqa: BLE001 — fail-soft is the contract
        context = f"GIT HANDOFF degraded ({type(exc).__name__}: {exc})."
    if context:
        _emit(event, context)
    else:
        print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
