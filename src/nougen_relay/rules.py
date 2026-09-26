"""React to a leg you did not write.

`relay triggers` answers "has something moved" with a fixed set of diagnostics.
This answers the next question — "and then what" — with operator-defined rules
that run a command when a leg arrives from another machine.

The distinction that matters: a leg is written when work *ends*, and the box
that should react to it is usually asleep when that happens. Without this, the
baton is only picked up when a human remembers to look. `relay react` is what
lets the Mac start a build because the PC finished one.

Three constraints shape the whole module:

- **Rules do not travel.** Everything else in this registry is tracked on
  purpose — records are the payload. A rule is not a record, it is executable
  configuration, and a rule arriving from another machine would run commands
  here. Rules, their fire state and their audit log live in a subdirectory
  that ignores itself, so they stay local in any consumer repo.
- **Nothing runs unless someone wrote a rule.** An empty registry is a no-op,
  and `NOUGEN_RULES=off` is a per-machine kill switch for a box that should
  stay passive.
- **Firing is once per leg, tracked by record id.** A leg that re-fired on
  every `react` would make the whole thing unusable inside a shell hook.

No runtime dependencies, in keeping with the rest of the package.
"""

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .core import (
    EXIT_DIVERGED,
    EXIT_FAILURE,
    EXIT_OK,
    EXIT_USAGE,
    _records,
    handoff_dir,
    record_id,
    repo_root,
    resolve_agent,
    resolve_machine,
    write_record,
)

# A subdirectory, not loose files in the registry: core._records() globs
# `<handoff dir>/*.json` and would read a rules file as if it were a leg,
# corrupting `list`, `latest` and `pull` as well as this module.
RULES_SUBDIR = "rules"
RULES_FILE = "rules.json"
STATE_FILE = "state.json"
RUNS_FILE = "runs.jsonl"

EVENTS = ("arrival",)
FALLBACK_TIMEOUT = 60
_OUTPUT_TAIL = 2000


def default_timeout() -> int:
    """How long a foreground rule may run before it is killed.

    Machine-shaped, not universal: the box that reacts by running a build
    needs minutes, the one that pings a webhook needs seconds. Resolved per
    machine from the environment so a rules file can be copied between boxes
    without carrying the slowest box's patience with it.
    """
    raw = os.environ.get("NOUGEN_RULES_TIMEOUT", "").strip()
    try:
        value = int(float(raw)) if raw else FALLBACK_TIMEOUT
    except ValueError:
        return FALLBACK_TIMEOUT
    return value if value > 0 else FALLBACK_TIMEOUT


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rules_dir(root: Path) -> Path:
    """The rules directory, which ignores itself.

    Dropping a `.gitignore` of `*` inside means the rules, their fire state and
    their audit log stay untracked in *any* consumer repo, without that repo
    having to know this feature exists. Everything else in the registry is
    tracked on purpose; executable configuration must not be.
    """
    directory = handoff_dir(root) / RULES_SUBDIR
    directory.mkdir(parents=True, exist_ok=True)
    marker = directory / ".gitignore"
    if not marker.exists():
        marker.write_text(
            "# Rules are executable configuration, not records. They do not\n"
            "# travel: a rule arriving from another machine would run commands\n"
            "# here. Copy them deliberately if you want them shared.\n*\n",
            encoding="utf-8",
        )
    return directory


def rules_path(root: Path) -> Path:
    return rules_dir(root) / RULES_FILE


def state_path(root: Path) -> Path:
    return rules_dir(root) / STATE_FILE


def runs_path(root: Path) -> Path:
    return rules_dir(root) / RUNS_FILE


def mode() -> str:
    """'on' | 'dry' | 'off' — the machine-level switch for rule execution."""
    raw = os.environ.get("NOUGEN_RULES", "").strip().lower()
    if raw in {"off", "0", "false", "no", "disabled"}:
        return "off"
    if raw in {"dry", "dry-run", "dryrun", "test"}:
        return "dry"
    return "on"


def _read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fallback


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    write_record(tmp, data)
    tmp.replace(path)


def load_rules(root: Path) -> list:
    data = _read_json(rules_path(root), {})
    rules = data.get("rules") if isinstance(data, dict) else data
    return [r for r in (rules or []) if isinstance(r, dict)]


def save_rules(root: Path, rules: list) -> Path:
    path = rules_path(root)
    _write_json(path, {"version": 1, "rules": rules})
    return path


def add_rule(
    root: Path,
    rule_id: str,
    run: str,
    machine: Optional[str] = None,
    agent: Optional[str] = None,
    branch: Optional[str] = None,
    goal_contains: Optional[str] = None,
    on_machine: Optional[str] = None,
    background: bool = False,
    timeout: Optional[int] = None,
) -> dict:
    if not run.strip():
        raise ValueError("a rule needs a command to run")
    rule = {
        "id": rule_id,
        "enabled": True,
        "on": ["arrival"],
        "match": {
            "machine": machine or None,
            "agent": agent or None,
            "branch": branch or None,
            "goal_contains": goal_contains or None,
        },
        # One rules file can be copied to every box while each rule still only
        # fires on the one that owns it.
        "on_machine": on_machine or None,
        "run": run,
        "background": bool(background),
        # Left unset unless the operator pinned one, so a rules file copied to
        # another box resolves that box's timeout instead of this one's.
        "timeout": int(timeout) if timeout else None,
    }
    rules = [r for r in load_rules(root) if r.get("id") != rule_id]
    rules.append(rule)
    save_rules(root, rules)
    return rule


def remove_rule(root: Path, rule_id: str) -> bool:
    rules = load_rules(root)
    remaining = [r for r in rules if r.get("id") != rule_id]
    if len(remaining) == len(rules):
        return False
    save_rules(root, remaining)
    return True


def set_enabled(root: Path, rule_id: str, enabled: bool) -> bool:
    rules = load_rules(root)
    found = False
    for rule in rules:
        if rule.get("id") == rule_id:
            rule["enabled"] = enabled
            found = True
    if found:
        save_rules(root, rules)
    return found


def matches(rule: dict, rec: dict) -> bool:
    """Whether one rule applies to one arrived leg. Literal comparisons only.

    A cleverer matcher that guessed would fire the wrong build on the wrong
    machine, which is the one failure this is not allowed to have.
    """
    if not rule.get("enabled", True):
        return False

    on_machine = rule.get("on_machine")
    if on_machine and on_machine != resolve_machine():
        return False

    match = rule.get("match") or {}
    wanted = match.get("machine")
    if wanted and rec.get("machine") != wanted:
        return False
    wanted = match.get("agent")
    if wanted and rec.get("agent") != wanted:
        return False
    wanted = match.get("branch")
    if wanted and rec.get("branch") != wanted:
        return False
    needle = match.get("goal_contains")
    if needle and needle.lower() not in (rec.get("goal") or "").lower():
        return False
    return True


def build_env(rec: dict, path: Path, rec_id: str) -> dict:
    """What a rule's command sees. Everything a reacting script needs."""
    env = dict(os.environ)
    env.update({
        "RELAY_EVENT": "arrival",
        "RELAY_RECORD_ID": rec_id,
        "RELAY_RECORD_PATH": str(path),
        "RELAY_FROM_MACHINE": str(rec.get("machine") or "unknown"),
        "RELAY_FROM_AGENT": str(rec.get("agent") or "unknown-agent"),
        "RELAY_BRANCH": str(rec.get("branch") or "unknown"),
        "RELAY_SHA": str(rec.get("sha") or ""),
        "RELAY_GOAL": str(rec.get("goal") or ""),
        "RELAY_LOCAL_MACHINE": resolve_machine(),
        "RELAY_LOCAL_AGENT": resolve_agent(),
    })
    return env


def _log_run(root: Path, entry: dict) -> None:
    try:
        path = runs_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        # An unwritable audit log must not stop the reaction it is recording.
        pass


def _execute(root: Path, rule: dict, rec: dict, path: Path, rec_id: str, run_mode: str) -> dict:
    entry = {
        "timestamp": _now(),
        "rule": rule.get("id"),
        "record": rec_id,
        "from": rec.get("machine"),
        "command": rule.get("run"),
        "machine": resolve_machine(),
        "status": "matched",
        "exit_code": None,
        "stderr": "",
    }
    if run_mode == "dry":
        entry["status"] = "dry-run"
        _log_run(root, entry)
        return entry
    try:
        if rule.get("background"):
            subprocess.Popen(
                rule["run"], shell=True, cwd=str(root),
                env=build_env(rec, path, rec_id),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            entry["status"] = "background"
        else:
            done = subprocess.run(
                rule["run"], shell=True, cwd=str(root),
                env=build_env(rec, path, rec_id),
                capture_output=True, text=True, check=False,
                timeout=int(rule.get("timeout") or default_timeout()),
            )
            entry["exit_code"] = done.returncode
            entry["stderr"] = (done.stderr or "")[-_OUTPUT_TAIL:]
            entry["status"] = "ok" if done.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        entry["status"] = "timeout"
    except Exception as exc:  # noqa: BLE001 - a rule may fail any way; the leg must survive it
        entry["status"] = "error"
        entry["stderr"] = str(exc)[-_OUTPUT_TAIL:]
    _log_run(root, entry)
    return entry


def react(root: Path, *, dry: bool = False, replay_all: bool = False) -> list:
    """Fire rules for legs written elsewhere that this box has not reacted to.

    'Elsewhere' is decided by the record's own machine stamp rather than by
    what git considers new, so a leg is reacted to once per box no matter how
    many times it is fetched, rebased or re-cloned.
    """
    run_mode = "dry" if dry else mode()
    if run_mode == "off":
        return []

    rules = load_rules(root)
    if not rules:
        return []

    state = _read_json(state_path(root), {})
    seen = set(state.get("reacted") or [])
    me = resolve_machine()
    fired = []
    newly_seen = []

    for path, rec in _records(root):
        rec_id = record_id(rec, path)
        if not rec_id or rec_id in seen:
            continue
        if rec.get("machine") == me:
            # Our own leg. Reacting to it would be this machine talking to
            # itself, which is how a rule loop starts.
            newly_seen.append(rec_id)
            continue
        if not replay_all and not state.get("reacted") and not state.get("initialised"):
            # First run on a box with existing history: adopt it as the
            # baseline instead of firing every rule against months of legs.
            newly_seen.append(rec_id)
            continue
        for rule in rules:
            try:
                if not matches(rule, rec):
                    continue
            except Exception:  # noqa: BLE001, S112 - one bad rule must not stop the others
                continue
            fired.append(_execute(root, rule, rec, path, rec_id, run_mode))
        newly_seen.append(rec_id)

    if run_mode != "dry":
        state["reacted"] = sorted(seen | set(newly_seen))
        state["initialised"] = True
        _write_json(state_path(root), state)
    return fired


def recent_runs(root: Path, limit: int = 20) -> list:
    try:
        lines = runs_path(root).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out = []
    for line in lines[-limit:]:
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return list(reversed(out))


# --- CLI --------------------------------------------------------------------

def cmd_rules(args) -> int:
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE

    if args.action == "list":
        rules = load_rules(root)
        print(f"🧠 machine  {resolve_machine()}")
        print(f"⚙️  mode     {mode()}  (NOUGEN_RULES=off|dry to change)")
        print(f"📄 rules    {rules_path(root)}")
        if not rules:
            print("ℹ️ no rules registered — nothing will run")
            return EXIT_OK
        for rule in rules:
            match = rule.get("match") or {}
            filters = ", ".join(f"{k}={v}" for k, v in match.items() if v) or "any leg"
            state = "enabled" if rule.get("enabled", True) else "disabled"
            scope = rule.get("on_machine") or "any machine"
            print(f"\n• {rule.get('id')} [{state}] on {scope}")
            print(f"  when : arrival, {filters}")
            print(f"  run  : {rule.get('run')}" + ("  (background)" if rule.get("background") else ""))
        return EXIT_OK

    if args.action == "add":
        if not args.id or not args.run:
            print("❌ rules add needs --id and --run")
            return EXIT_USAGE
        try:
            rule = add_rule(
                root, args.id, args.run,
                machine=args.from_machine, agent=args.from_agent,
                branch=args.branch, goal_contains=args.goal_contains,
                on_machine=args.on_machine, background=args.background,
                timeout=args.timeout,
            )
        except ValueError as exc:
            print(f"❌ {exc}")
            return EXIT_USAGE
        print(f"✅ rule '{rule['id']}' → {rules_path(root)}")
        return EXIT_OK

    if args.action == "rm":
        if not args.id:
            print("❌ rules rm needs --id")
            return EXIT_USAGE
        ok = remove_rule(root, args.id)
        print("✅ removed" if ok else f"ℹ️ no rule '{args.id}'")
        return EXIT_OK if ok else EXIT_FAILURE

    if args.action in {"enable", "disable"}:
        if not args.id:
            print(f"❌ rules {args.action} needs --id")
            return EXIT_USAGE
        ok = set_enabled(root, args.id, args.action == "enable")
        print(f"✅ {args.action}d" if ok else f"ℹ️ no rule '{args.id}'")
        return EXIT_OK if ok else EXIT_FAILURE

    if args.action == "runs":
        runs = recent_runs(root, args.number)
        if not runs:
            print("ℹ️ no rule runs recorded")
            return EXIT_OK
        for run in runs:
            print(
                f"{run.get('timestamp', '?')}  {run.get('rule')}  "
                f"{run.get('status')}  exit={run.get('exit_code')}  "
                f"from={run.get('from')}  leg={run.get('record')}"
            )
        return EXIT_OK

    return EXIT_USAGE


def cmd_react(args) -> int:
    root = repo_root()
    if root is None:
        print("❌ not inside a git repository")
        return EXIT_FAILURE
    fired = react(root, dry=args.dry, replay_all=args.all)
    if not fired:
        print("✅ nothing to react to")
        return EXIT_OK
    for entry in fired:
        glyph = {"ok": "✅", "background": "🚀", "dry-run": "🧪"}.get(entry["status"], "❌")
        detail = "" if entry.get("exit_code") in (None, 0) else f" (exit {entry['exit_code']})"
        print(f"{glyph} {entry['rule']} ← {entry['from']}: {entry['status']}{detail}")
    if any(e["status"] in {"failed", "error", "timeout"} for e in fired):
        return EXIT_FAILURE
    return EXIT_DIVERGED


def register(sub) -> None:
    """Wire both subcommands into relay's parser."""
    r = sub.add_parser("rules", help="what to run when another machine's leg arrives")
    r.add_argument("action", choices=["list", "add", "rm", "enable", "disable", "runs"])
    r.add_argument("--id")
    r.add_argument("--run", help="shell command to execute")
    r.add_argument("--from-machine", dest="from_machine", help="only legs from this box")
    r.add_argument("--from-agent", dest="from_agent", help="only legs from this lane")
    r.add_argument("--branch", help="only legs on this branch")
    r.add_argument("--goal-contains", dest="goal_contains", help="substring of the leg's goal")
    r.add_argument("--on-machine", dest="on_machine", help="only run the rule on this box")
    r.add_argument("--background", action="store_true", help="detach instead of waiting")
    r.add_argument("--timeout", type=int, default=None,
                   help=f"seconds before a foreground rule is killed "
                        f"(default: NOUGEN_RULES_TIMEOUT, else {FALLBACK_TIMEOUT})")
    r.add_argument("-n", "--number", type=int, default=20, help="(runs) how many to show")
    r.set_defaults(func=cmd_rules)

    a = sub.add_parser("react", help="run rules for legs this box has not reacted to")
    a.add_argument("--dry", action="store_true", help="show what would run, run nothing")
    a.add_argument("--all", action="store_true",
                   help="include pre-existing legs instead of adopting them as baseline")
    a.set_defaults(func=cmd_react)
