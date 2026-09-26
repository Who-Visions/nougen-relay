"""MCP server — lets a non-Claude lane join the relay.

Antigravity CLI (`agy`), Antigravity IDE and the SDK have no hook system, so
they cannot be made to run `relay check` before working the way a Claude
session can. They *can* call MCP tools. This exposes the relay verbs as tools
so those lanes participate in the same registry as everyone else instead of
being coordinated by documentation alone.

Every tool shells out to the CLI rather than importing the command bodies. That
is deliberate and matches the hook's reasoning: one execution path means the
MCP surface and the CLI can never drift, and the tools inherit the exact
behaviour the test-suite covers.

Install:  pip install "nougen_relay[mcp]"
Register: see docs/AGY.md — global ~/.gemini/config/mcp_config.json for
          Antigravity, or .agents/mcp_config.json per workspace.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    try:
        from mcp.server.fastmcp import FastMCP
    except (ImportError, ModuleNotFoundError):
        from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:  # pragma: no cover - exercised by the import-error path
    raise SystemExit(
        "nougen_relay.mcp_server needs the MCP SDK.\n"
        'Install it with:  pip install "nougen_relay[mcp]"'
    )

mcp = FastMCP("NouGenRelay")

SRC_DIR = Path(__file__).resolve().parents[1]
RELAY_ROOT = Path(__file__).resolve().parents[2]

# A relay verb touches git and may push; it should never wedge an agent
# session waiting on a network stall.
TIMEOUT = 30


def _run(args: list[str], repo: Optional[str] = None) -> str:
    """Invoke the relay CLI and return its output verbatim.

    Errors are returned as text, not raised: a coordination tool that throws
    into an agent's transcript teaches the agent to stop calling it.
    """
    if repo and Path(repo).is_dir():
        cwd = Path(repo)
    elif Path(os.getcwd()).joinpath(".git").is_dir():
        cwd = Path(os.getcwd())
    else:
        cwd = RELAY_ROOT

    try:
        env = {
            **os.environ,
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
            "PYTHONPATH": str(SRC_DIR) + os.pathsep + os.environ.get("PYTHONPATH", "")
        }
        out = subprocess.run(
            [sys.executable, "-m", "nougen_relay.cli", *args],
            cwd=str(cwd), capture_output=True, timeout=TIMEOUT,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return f"error: `relay {' '.join(args)}` timed out after {TIMEOUT}s"
    stdout_str = (out.stdout or b"").decode("utf-8", errors="replace")
    stderr_str = (out.stderr or b"").decode("utf-8", errors="replace")
    body = stdout_str + stderr_str
    return body.strip() or f"(no output, exit {out.returncode})"


@mcp.tool()
def relay_whoami() -> str:
    """Which machine and agent lane this box reports as, and where each answer
    came from. Call this first if records are landing under the wrong name."""
    return _run(["whoami"])


@mcp.tool()
def relay_check(repo: Optional[str] = None) -> str:
    """PRE-FLIGHT — run before starting work. Reports whether another machine
    has moved, whether histories diverged, and who else has published here."""
    return _run(["check"], repo)


@mcp.tool()
def relay_open(repo: Optional[str] = None) -> str:
    """Legs another machine left that nobody has acked yet — work handed to you
    and not yet picked up."""
    return _run(["relay", "open"], repo)


@mcp.tool()
def relay_claim_list(repo: Optional[str] = None) -> str:
    """Active claims across the fleet: what each machine says it is working on
    RIGHT NOW. Check before claiming."""
    return _run(["claim", "list"], repo)


@mcp.tool()
def relay_claim_take(scope: str, goal: str, repo: Optional[str] = None) -> str:
    """ANNOUNCE WORK BEFORE STARTING IT. `scope` is the paths or topics you are
    about to touch (space or comma separated); `goal` is why.

    Refuses if another machine holds an overlapping scope — that refusal is the
    point. When refused, read their claim and either stand down or pick
    different work; do not override it without deciding to.
    """
    return _run(["claim", "take", "-s", scope, "-g", goal], repo)


@mcp.tool()
def relay_claim_release(scope: str, repo: Optional[str] = None) -> str:
    """Release a claim when the work is done, so the scope frees up before its
    expiry."""
    return _run(["claim", "release", "-s", scope], repo)


@mcp.tool()
def relay_create(goal: str, message: str, repo: Optional[str] = None,
                 parent_leg_id: Optional[str] = None) -> str:
    """Write a handoff at the END of work: what you did and where you left off.

    Pass `parent_leg_id` (a FULL leg id) when this leg branches off an earlier
    one, so investigations read as a tree instead of a flat list.

    The record is written locally; commit and push `.handoffs` so the other
    machines can read it.
    """
    args = ["create", "-g", goal, "-m", message]
    if parent_leg_id:
        args += ["--parent", parent_leg_id]
    return _run(args, repo)


@mcp.tool()
def relay_summarize(parent_leg_id: str, summary: str, goal: str = "",
                    repo: Optional[str] = None) -> str:
    """Close an ABANDONED branch: writes a `type: summary` leg pointing at the
    parent and marks the parent `abandoned` so it leaves every open queue.

    Use when giving up on a line of work — the summary carries what the branch
    learned, instead of the leg silently going stale.
    """
    args = ["summarize", "--id", parent_leg_id, "-m", summary]
    if goal:
        args += ["-g", goal]
    return _run(args, repo)


@mcp.tool()
def relay_ack(leg_id: str, message: str, repo: Optional[str] = None) -> str:
    """Take the baton on an open leg — claim responsibility for continuing it.
    A leg stays `open` until someone acks, so an unacked leg is visibly
    dropped rather than silently."""
    return _run(["relay", "ack", "--id", leg_id, "-m", message], repo)


@mcp.tool()
def relay_shards(dry: bool = False, repo: Optional[str] = None) -> str:
    """PUBLISH WHAT THIS BOX LEARNED. Reads the local shard vault and writes
    `docs/FLEET-LOG-<date>.md` — the other machines cannot open the vault, so
    without this the knowledge stays on one box.

    Shards tagged brand/personal/finance/family/legal/medical are named but not
    copied, and credential-shaped values block the write. Set `dry` to see the
    log without writing it. Commit and push the file afterwards; a log that is
    not pushed has relayed nothing.
    """
    return _run(["shards", "--dry"] if dry else ["shards"], repo)


@mcp.prompt()
def research(topic: str) -> str:
    """Autonomous deep research across the NouGen fleet substrate."""
    return f"Execute deep autonomous research on '{topic}' across NouGen FTS5 shards, peer memory, and verified local code."


@mcp.prompt()
def lore(entity: str) -> str:
    """Retrieve canon lore, character depth, and narrative architecture for an entity."""
    return f"Excavate all canon lore, character depth, and narrative architecture for '{entity}' across Veilverse canon and memory shards."


@mcp.prompt()
def fleet_sync() -> str:
    """Reciprocal fleet synchronization across WhoArt, Blade, and Phoebus."""
    return "Perform a reciprocal fleet check: query active handoffs, inspect node inboxes, run health probes across WhoArt/Blade/Phoebus, and report the scoreboard."


@mcp.prompt()
def shot_card(scene_action: str) -> str:
    """Generate a 26-field pre-render camera coherence shot card for AI video generation."""
    return f"Generate a 26-field pre-render shot card for: '{scene_action}' adhering to HyperReality Camera Coherence specifications."


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
