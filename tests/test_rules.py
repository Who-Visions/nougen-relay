"""Rules: what runs when another machine's leg arrives.

Same shape as the other cross-machine tests — a real bare remote and two
working copies — because whether a rule fires depends on whose leg it is, and
that is only true after a real push and pull.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

SRC = str(Path(__file__).resolve().parents[1] / "src")


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def relay(repo, *args, machine, agent="claude-cli", **env_extra):
    env = {**os.environ, "PYTHONPATH": SRC, "NOUGEN_MACHINE": machine,
           "NOUGEN_AGENT": agent, "PYTHONIOENCODING": "utf-8"}
    env.update({k: str(v) for k, v in env_extra.items()})
    return subprocess.run([sys.executable, "-m", "nougen_relay.cli", *args],
                          cwd=repo, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


@pytest.fixture()
def fleet(tmp_path):
    bare = tmp_path / "origin.git"
    git("init", "-q", "--bare", "-b", "main", str(bare), cwd=tmp_path)

    seed = tmp_path / "seed"
    git("clone", "-q", str(bare), str(seed), cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=seed)
    git("config", "user.name", "t", cwd=seed)
    (seed / "f.txt").write_text("x\n", encoding="utf-8")
    git("add", ".", cwd=seed)
    git("commit", "-qm", "init", cwd=seed)
    git("push", "-q", "origin", "main", cwd=seed)

    copies = {}
    for name in ("node-c", "node-a"):
        path = tmp_path / name
        git("clone", "-q", str(bare), str(path), cwd=tmp_path)
        git("config", "user.email", f"{name}@example.com", cwd=path)
        git("config", "user.name", name, cwd=path)
        copies[name] = path
    copies["_tmp"] = tmp_path
    return copies


def publish(repo, machine, goal, message="left off here"):
    relay(repo, "create", "-g", goal, "-m", message, machine=machine)
    git("add", ".handoffs", cwd=repo)
    git("commit", "-qm", f"handoff({machine})", cwd=repo)
    git("push", "-q", "origin", "main", cwd=repo)


def receive(repo):
    git("pull", "-q", "--no-rebase", "origin", "main", cwd=repo)


def write_env_receipt(receipt, *names):
    """A rule command that records env vars, in whatever shell the box has.

    `$VAR` is a POSIX-ism: through `shell=True` on Windows it reaches cmd.exe
    verbatim and never expands. Rules are local to a machine so operators may
    write either dialect, but a test asserting the rule *environment* must not
    also be asserting the shell.
    """
    read = "+' '+".join(f"os.environ[{n!r}]" for n in names)
    body = f"import os,sys;open(sys.argv[1],'w').write({read})"
    return f'"{sys.executable}" -c "{body}" "{receipt}"'


def test_arriving_leg_fires_a_rule(fleet):
    mac, receipt = fleet["node-a"], fleet["_tmp"] / "reacted.txt"
    relay(mac, "rules", "add", "--id", "react",
          "--run", write_env_receipt(receipt, "RELAY_FROM_MACHINE", "RELAY_GOAL"),
          machine="node-a")
    # Adopt existing history as the baseline before the leg we care about.
    relay(mac, "react", machine="node-a")

    publish(fleet["node-c"], "node-c", "needs a mac build")
    receive(mac)

    out = relay(mac, "react", machine="node-a")
    assert receipt.exists(), out.stdout + out.stderr
    assert receipt.read_text(encoding="utf-8").strip() == "node-c needs a mac build"
    assert out.returncode == 3, "firing should use the diverged/attention exit code"


def test_a_box_does_not_react_to_its_own_leg(fleet):
    mac, receipt = fleet["node-a"], fleet["_tmp"] / "self.txt"
    relay(mac, "rules", "add", "--id", "self", "--run", f'echo x > "{receipt}"',
          machine="node-a")
    relay(mac, "react", machine="node-a")

    publish(mac, "node-a", "my own work")
    relay(mac, "react", machine="node-a")
    assert not receipt.exists(), "reacting to your own leg is how a rule loop starts"


def test_a_leg_fires_once_however_often_react_runs(fleet):
    mac, counter = fleet["node-a"], fleet["_tmp"] / "count.txt"
    relay(mac, "rules", "add", "--id", "count", "--run", f'echo x >> "{counter}"',
          machine="node-a")
    relay(mac, "react", machine="node-a")

    publish(fleet["node-c"], "node-c", "once only")
    receive(mac)
    for _ in range(3):
        relay(mac, "react", machine="node-a")
    assert counter.read_text(encoding="utf-8").split() == ["x"]


def test_first_run_adopts_history_instead_of_firing_on_all_of_it(fleet):
    """A box joining a repo with existing legs must not run months of rules."""
    publish(fleet["node-c"], "node-c", "old leg one")
    # Record ids are second-granular (<UTC>__machine__agent), so two legs from
    # one machine inside the same second are one id. Space them, or this test
    # races the clock rather than testing baseline adoption.
    time.sleep(1.1)
    publish(fleet["node-c"], "node-c", "old leg two")
    mac, receipt = fleet["node-a"], fleet["_tmp"] / "backlog.txt"
    receive(mac)

    relay(mac, "rules", "add", "--id", "backlog", "--run", f'echo x >> "{receipt}"',
          machine="node-a")
    out = relay(mac, "react", machine="node-a")
    assert not receipt.exists(), out.stdout
    assert out.returncode == 0

    time.sleep(1.1)
    publish(fleet["node-c"], "node-c", "a new one")
    receive(mac)
    relay(mac, "react", machine="node-a")
    assert receipt.read_text(encoding="utf-8").split() == ["x"]


def test_match_filters_narrow_by_machine_and_goal(fleet):
    mac, receipt = fleet["node-a"], fleet["_tmp"] / "narrow.txt"
    relay(mac, "rules", "add", "--id", "narrow", "--run", f'echo x > "{receipt}"',
          "--from-machine", "node-b1", "--goal-contains", "deploy",
          machine="node-a")
    relay(mac, "react", machine="node-a")

    publish(fleet["node-c"], "node-c", "run the deploy")
    receive(mac)
    relay(mac, "react", machine="node-a")
    assert not receipt.exists(), "machine filter should have blocked this"


def test_on_machine_scopes_a_shared_rules_file(fleet):
    mac, receipt = fleet["node-a"], fleet["_tmp"] / "scoped.txt"
    relay(mac, "rules", "add", "--id", "scoped", "--run", f'echo x > "{receipt}"',
          "--on-machine", "node-b1", machine="node-a")
    relay(mac, "react", machine="node-a")

    publish(fleet["node-c"], "node-c", "not for this box")
    receive(mac)
    relay(mac, "react", machine="node-a")
    assert not receipt.exists()


def test_kill_switch_and_dry_run(fleet):
    mac, receipt = fleet["node-a"], fleet["_tmp"] / "switch.txt"
    relay(mac, "rules", "add", "--id", "switch", "--run", f'echo x > "{receipt}"',
          machine="node-a")
    relay(mac, "react", machine="node-a")

    publish(fleet["node-c"], "node-c", "silenced")
    receive(mac)

    relay(mac, "react", machine="node-a", NOUGEN_RULES="off")
    assert not receipt.exists()

    out = relay(mac, "react", "--dry", machine="node-a")
    assert not receipt.exists()
    assert "switch" in out.stdout

    # A dry run must not consume the leg — the real one still fires.
    relay(mac, "react", machine="node-a")
    assert receipt.exists()


def test_a_failing_rule_is_recorded_not_swallowed(fleet):
    mac = fleet["node-a"]
    relay(mac, "rules", "add", "--id", "broken", "--run", "exit 3", machine="node-a")
    relay(mac, "react", machine="node-a")

    publish(fleet["node-c"], "node-c", "will fail")
    receive(mac)
    out = relay(mac, "react", machine="node-a")
    assert out.returncode == 1

    runs = relay(mac, "rules", "runs", machine="node-a").stdout
    assert "broken" in runs and "failed" in runs


def test_rules_and_their_state_never_travel(fleet):
    """Executable config arriving from another box would run commands here."""
    mac = fleet["node-a"]
    relay(mac, "rules", "add", "--id", "local-only", "--run", "true", machine="node-a")
    relay(mac, "react", machine="node-a")
    publish(mac, "node-a", "with a rules file present")

    receive(fleet["node-c"])
    tracked = subprocess.run(["git", "ls-files"], cwd=fleet["node-c"],
                             capture_output=True, text=True, check=False).stdout
    assert "rules.json" not in tracked
    assert "state.json" not in tracked
    assert "runs.jsonl" not in tracked
    assert relay(fleet["node-c"], "rules", "list", machine="node-c").stdout.count("local-only") == 0


def test_no_rules_is_a_no_op(fleet):
    mac = fleet["node-a"]
    publish(fleet["node-c"], "node-c", "nobody is listening")
    receive(mac)
    out = relay(mac, "react", machine="node-a")
    assert out.returncode == 0
    assert "nothing to react to" in out.stdout


def test_env_contract_reaches_the_command(fleet):
    mac, dump = fleet["node-a"], fleet["_tmp"] / "env.json"
    # A script file rather than an inline one-liner: the contract under test is
    # the environment, not shell quoting.
    script = fleet["_tmp"] / "dump_env.py"
    script.write_text(
        "import json, os, sys\n"
        "json.dump({k: v for k, v in os.environ.items() if k.startswith('RELAY_')},\n"
        "          open(sys.argv[1], 'w'))\n",
        encoding="utf-8",
    )
    relay(mac, "rules", "add", "--id", "envdump",
          "--run", f'"{sys.executable}" "{script}" "{dump}"', machine="node-a")
    relay(mac, "react", machine="node-a")

    publish(fleet["node-c"], "node-c", "carry the context")
    receive(mac)
    out = relay(mac, "react", machine="node-a")

    assert dump.exists(), out.stdout + out.stderr
    seen = json.loads(dump.read_text(encoding="utf-8"))
    assert seen["RELAY_EVENT"] == "arrival"
    assert seen["RELAY_FROM_MACHINE"] == "node-c"
    assert seen["RELAY_GOAL"] == "carry the context"
    assert seen["RELAY_LOCAL_MACHINE"] == "node-a"
    assert seen["RELAY_RECORD_ID"]
