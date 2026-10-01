"""Self-Healing Relay Daemon Harness for NouGenAi Ecosystem.

Envelops the execution harness:
- Watches NouGenRelay .handoffs/ and grid coordination queues.
- Emits a periodic heartbeat (default: 200s) via local Ollama (dav1d:e2b / sol-ai:e4b) at zero cloud cost.
- Detects relay lag and delivery latency.
- Triages incoming batons using local AI inference.
- Automatically dispatches vetted execution tasks to the Dav1d / AGY CLI harness.
- Maintains self-healing SQLite state ledger and auto-recovers on drift.
"""

from __future__ import annotations

import argparse
import atexit
import base64
import ctypes
import datetime
import json
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Local imports
try:
    from nougen_shards.dav1d_executor import run_dav1d_agy
    from nougen_shards.handoff_dialects import read_all_handoffs
except ImportError:
    # Fallback when running standalone from tools/
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    try:
        from nougen_shards.dav1d_executor import run_dav1d_agy
        from nougen_shards.handoff_dialects import read_all_handoffs
    except ImportError:
        run_dav1d_agy = None
        read_all_handoffs = None

# The daemon is also launched directly from ``tools/`` by the Windows watcher.
# Put this checkout's package ahead of ambient installs so execution leases and
# retries always use the same relay version as the daemon itself.
_RELAY_SRC = Path(__file__).resolve().parent.parent / "src"
if _RELAY_SRC.is_dir() and str(_RELAY_SRC) not in sys.path:
    sys.path.insert(0, str(_RELAY_SRC))

try:
    from nougen_relay.core import (
        acquire_lease,
        claim_is_active,
        is_leg_retryable,
        lease_is_active,
        leases_dir,
        record_leg_failure,
        release_lease,
    )
except ImportError:
    # Fail closed at dispatch time if this copy is somehow separated from its
    # package; a worker without a lease primitive must never execute a leg.
    acquire_lease = None
    claim_is_active = None
    is_leg_retryable = None
    lease_is_active = None
    leases_dir = None
    record_leg_failure = None
    release_lease = None

DEFAULT_HEARTBEAT_SEC = 200
DEFAULT_LAG_THRESHOLD_SEC = 300  # 5 minutes


def _resolve_ollama_url() -> str:
    raw = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").strip()
    if not raw.startswith("http://") and not raw.startswith("https://"):
        raw = f"http://{raw}"
    # Replace bind-all 0.0.0.0 with loopback for client requests
    raw = raw.replace("://0.0.0.0", "://127.0.0.1")
    # Add port if missing
    host_part = raw.split("://", 1)[1]
    if ":" not in host_part:
        raw = f"{raw}:11434"
    return raw.rstrip("/")


def _resolve_watchtower_root() -> Path:
    """Locate the Watchtower root: env -> walk up from this file -> logged fallback."""
    env = os.environ.get("NOUGEN_WATCHTOWER_ROOT", "").strip()
    if env:
        return Path(env)
    for parent in Path(__file__).resolve().parents:
        if parent.name.lower() == "watchtower" or (parent / "NouGen").is_dir():
            return parent
    fallback = Path.home() / "Watchtower"
    print(f"[RelayDaemon] WARN using fallback watchtower root: {fallback}")
    return fallback


def _resolve_relay_dir() -> Path:
    """Locate the relay repo: env -> known layouts -> the repo this file ships in."""
    env = os.environ.get("NOUGEN_RELAY_DIR", "").strip()
    if env:
        return Path(env)
    root = _resolve_watchtower_root()
    for candidate in (root / "NouGen" / "NouGenRelay", root / "NouGenRelay"):
        if candidate.is_dir():
            return candidate
    for parent in Path(__file__).resolve().parents:
        if (parent / ".handoffs").is_dir():
            return parent
    fallback = root / "NouGen" / "NouGenRelay"
    print(f"[RelayDaemon] WARN using fallback relay dir: {fallback}")
    return fallback


def _resolve_shards_src() -> Optional[Path]:
    """Locate the optional NouGenShards Python source without a machine path."""
    env = os.environ.get("NOUGEN_SHARDS_SRC", "").strip()
    if env:
        return Path(env)
    root = _resolve_watchtower_root()
    candidates = (
        root / "NouGen" / "NouGenShards-push-main" / "src",
        root / "NouGenShards-push-main" / "src",
        root / "NouGen" / "NouGenShards" / "src",
    )
    return next((path for path in candidates if path.is_dir()), None)


def _resolve_machine_name() -> str:
    return (
        os.environ.get("NOUGEN_MACHINE")
        or os.environ.get("COMPUTERNAME")
        or platform.node()
        or "unknown"
    ).lower()


def _pid_alive(pid: int) -> bool:
    """True if the PID belongs to a live process. Never signals the target."""
    if pid <= 0:
        return False
    if os.name == "nt":
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return code.value == STILL_ACTIVE
            return True
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


class SingletonLock:
    """One daemon per state DB. Stale locks (dead PID) are reclaimed automatically."""

    # Locks held by this process. A crashed daemon leaves a lock stamped with a
    # PID Windows may hand to someone else, so "is it mine?" cannot be answered
    # by the PID alone -- an in-process claim is tracked here instead.
    _held: set = set()

    def __init__(self, lock_path: Path):
        self.lock_path = Path(lock_path)
        self.acquired = False
        self.holder_pid: Optional[int] = None

    def acquire(self) -> bool:
        """Atomically claim the lock. O_EXCL so two racing starts cannot both win."""
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {
                "pid": os.getpid(),
                "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "argv": sys.argv[1:],
                "machine": _resolve_machine_name(),
            }
        )
        for _ in range(2):
            try:
                fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                # O_EXCL publishes the pathname before this process can finish
                # writing the JSON body. A competing starter that reads in that
                # interval sees an invalid/empty lock; deleting it would let a
                # second process win. Briefly wait for the atomic creator to
                # finish before treating an unreadable record as stale.
                pid = -1
                for _ in range(10):
                    pid = self._holder_pid()
                    if pid != -1:
                        break
                    time.sleep(0.01)
                if str(self.lock_path.resolve()) in SingletonLock._held:
                    self.holder_pid = pid
                    return False
                if pid != os.getpid() and _pid_alive(pid):
                    self.holder_pid = pid
                    return False
                # Stale lock (holder dead or unreadable) -- clear it and retry once.
                print(f"[RelayDaemon] reclaiming stale lock from pid {pid}")
                try:
                    self.lock_path.unlink(missing_ok=True)
                except OSError:
                    return False
                continue
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(payload)
            self.acquired = True
            SingletonLock._held.add(str(self.lock_path.resolve()))
            atexit.register(self.release)
            return True
        return False

    def _holder_pid(self) -> int:
        try:
            holder = json.loads(self.lock_path.read_text(encoding="utf-8"))
            return int(holder.get("pid", -1))
        except Exception:
            return -1

    def release(self) -> None:
        if not self.acquired:
            return
        try:
            holder = json.loads(self.lock_path.read_text(encoding="utf-8"))
            if int(holder.get("pid", -1)) == os.getpid():
                self.lock_path.unlink(missing_ok=True)
        except Exception:
            pass
        SingletonLock._held.discard(str(self.lock_path.resolve()))
        self.acquired = False


DEFAULT_OLLAMA_URL = _resolve_ollama_url()
DEFAULT_MODEL = os.environ.get("NOUGEN_DAEMON_MODEL", "dav1d:e2b")
DEFAULT_RELAY_DIR = _resolve_relay_dir()
DEFAULT_DB_PATH = Path(
    os.environ.get("NOUGEN_DAEMON_DB")
    or (_resolve_watchtower_root() / "Sol-Ai" / "relay_daemon_state.db")
)
DEFAULT_MACHINE = _resolve_machine_name()
DEFAULT_AGY_BIN = os.environ.get("NOUGEN_AGY_BIN", "agy")

#: The relay dir is a git clone of the live registry; without a pull per cycle
#: the daemon inspects a frozen snapshot forever (observed 2026-08-27: clone
#: four days stale, every phone-posted leg invisible, "Open: 58" never moved).
SYNC_TIMEOUT_SEC = int(os.environ.get("NOUGEN_DAEMON_SYNC_TIMEOUT", "120"))
#: Ceiling for one real dispatched execution.
EXEC_TIMEOUT_SEC = int(os.environ.get("NOUGEN_DAEMON_EXEC_TIMEOUT", "900"))
#: Fresh legs triaged per cycle, and real executions per cycle. Dispatch
#: fallback raised 1 -> 3 by GM order 2026-08-27 to drain the 79-leg backlog;
#: executions within a cycle still run serially, so 3 caps a cycle at ~3x
#: EXEC_TIMEOUT_SEC worst case, it does not run harnesses in parallel.
TRIAGE_PER_CYCLE = int(os.environ.get("NOUGEN_DAEMON_TRIAGE_PER_CYCLE", "3"))
DISPATCH_PER_CYCLE = int(os.environ.get("NOUGEN_DAEMON_DISPATCH_PER_CYCLE", "3"))
#: Informational/diagnostic legs answered by the free local fleet per cycle.
#: These never touch the harness: the local model composes the answer and the
#: answer rides the upstream ack, so the backlog drains at $0.
FLEET_PER_CYCLE = int(os.environ.get("NOUGEN_DAEMON_FLEET_PER_CYCLE", "3"))
#: Multi-lane fleet responder roster (GM order 2026-08-27): walk these free
#: lanes in order until one returns a non-empty answer. Each value is a lane
#: name handled inside fleet_respond; unknown names are skipped with a note.
FLEET_LANES = tuple(
    s.strip()
    for s in os.environ.get(
        "NOUGEN_DAEMON_FLEET_LANES",
        "ollama-local,ollama-cloud,openrouter,kimi-space,hf-kimi",
    ).split(",")
    if s.strip()
)
#: Cloud model reachable through the same local ollama daemon.
FLEET_CLOUD_MODEL = os.environ.get("NOUGEN_DAEMON_CLOUD_MODEL", "gemma4:31b-cloud")
#: OpenRouter free-tier nemotron agents; each model in the list is one agent,
#: tried in order (free models rotate/rate-limit, so a list, not a constant).
OPENROUTER_URL = os.environ.get(
    "NOUGEN_OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions"
)
FLEET_OR_MODELS = tuple(
    s.strip()
    for s in os.environ.get(
        "NOUGEN_DAEMON_OR_MODELS",
        "nvidia/nemotron-3-ultra-550b-a55b:free,"
        "nvidia/nemotron-3-super-120b-a12b:free,"
        "z-ai/glm-5.2:free",
    ).split(",")
    if s.strip()
)
#: HF inference router (same constants rhea_noir.py uses); kimi model comes
#: from NOUGEN_RHEA_MODEL and the lane is skipped silently when unset.
HF_ROUTER_URL = os.environ.get(
    "NOUGEN_ROUTER_URL", "https://router.huggingface.co/v1/chat/completions"
)
#: Per-lane HTTP timeout for one fleet answer attempt.
FLEET_LANE_TIMEOUT_SEC = int(os.environ.get("NOUGEN_DAEMON_LANE_TIMEOUT", "120"))
DAEMON_AGENT = os.environ.get("NOUGEN_DAEMON_AGENT", "relay-daemon").strip() or "relay-daemon"
#: Probe-grounded verification (GM order 2026-08-31): before an ack, dav1d
#: proposes read-only probes of live state, the daemon runs the ones that
#: survive the whitelist, and the verdict must cite probe output. A leg whose
#: body demands a state change can no longer be acked off persuasive prose.
PROBE_MAX = int(os.environ.get("NOUGEN_DAEMON_PROBE_MAX", "4"))
PROBE_TIMEOUT_SEC = int(os.environ.get("NOUGEN_DAEMON_PROBE_TIMEOUT", "45"))
ACK_NOTE_MAX = int(os.environ.get("NOUGEN_DAEMON_ACK_NOTE_MAX", "1000"))
#: Words in a leg's goal/done-when that mark it execution-shaped; a fleet
#: answer alone must never close such a leg.
CHANGE_MARKERS = tuple(
    s.strip()
    for s in os.environ.get(
        "NOUGEN_DAEMON_CHANGE_MARKERS",
        "fix,patch,deploy,rotate,migrate,build,implement,create,delete,"
        "restart,push,merge,rebuild,provision,repair,land,ship,install",
    ).split(",")
    if s.strip()
)
#: A DEFECT REPORT is not a question even when it contains no fix-verb. On
#: 2026-08-31 a capture-integrity defect leg ("DEFECT + falsifier result: ...")
#: carried none of the change markers, triaged INFORMATIONAL, and was closed 15
#: minutes after filing by a generated fleet-answer that was not even responsive
#: to it (leg 20260831T195956Z, caught by its own author). Legs matching these
#: markers must never be closed by a generated answer - probes or a human.
DEFECT_MARKERS = tuple(
    s.strip()
    for s in os.environ.get(
        "NOUGEN_DAEMON_DEFECT_MARKERS",
        "defect,bug,broken,regression,incident,p1,escalation,urgent,outage,"
        "corrupt,failure,falsifier,silently,leak,wedge,exposed,vulnerab",
    ).split(",")
    if s.strip()
)
def _space_pluck(node):
    """Deepest useful text in a gradio Space output blob; raises on errors.

    Space endpoints return anything from a bare string to a full chat history
    (list of role dicts) to nested content blocks, so walk tolerantly instead
    of hardcoding one Space's shape (mirrors rhea_noir._space_pluck)."""
    if isinstance(node, str):
        text = node.strip()
        if text.startswith("Error"):
            raise RuntimeError(text[:200])
        return text or None
    if isinstance(node, dict):
        if node.get("error"):
            raise RuntimeError(str(node["error"])[:200])
        for key in ("text", "content", "value", "answer"):
            if key in node:
                got = _space_pluck(node[key])
                if got:
                    return got
        return None
    if isinstance(node, list):
        for item in reversed(node):
            got = _space_pluck(item)
            if got:
                return got
    return None


#: Keymaker (DPAPI-wrapped secrets) fallback when a key is not in the env.
KEYMAKER_BIN_DIR = Path(
    os.environ.get("NOUGEN_KEYMAKER_BIN", r"C:/Users/super/.nougen/bin")
)
KEYMAKER_DB_PATH = Path(
    os.environ.get(
        "NOUGEN_KEYMAKER_DB", r"C:/Users/super/.nougen/secrets/shards_secrets.db"
    )
)


def _keymaker_load(label: str) -> Optional[str]:
    """Fetch one secret value from the keymaker store; None if unavailable.

    The value is returned to the caller for use as a bearer token only and
    must NEVER be printed, logged, or embedded in any report/handoff."""
    try:
        bin_dir = str(KEYMAKER_BIN_DIR)
        if bin_dir not in sys.path:
            sys.path.insert(0, bin_dir)
        from keymaker_peel import load  # type: ignore
        rows = load(label, db=KEYMAKER_DB_PATH)
        if rows:
            return rows[0][1]
    except Exception:
        pass
    return None

# Which statuses count as "waiting to be picked up". Core's vocabulary says
# only "open" means unacked; "active" and "held" are legacy values found in
# records written before RELAY_STATES existed. Terminal states — complete,
# abandoned (branch summarized away) — must never appear here, or the daemon
# lag-alerts on legs nobody should pick up. Env-resolvable per Rule 0.2.
OPEN_HANDOFF_STATES = tuple(
    s.strip()
    for s in os.environ.get(
        "NOUGEN_RELAY_OPEN_STATES", "open,active,held"
    ).split(",")
    if s.strip()
)


def _relay_status_rank(status: Any) -> int:
    """Return the progress rank used when two registry projections disagree.

    The gateway and Git projections can legitimately observe the same leg at
    different points in its lifecycle.  A stale ``open`` record must never
    erase a local acknowledgement or completion.  The order is configurable
    so deployments with an extended state vocabulary can add states without
    changing the merge algorithm.
    """
    raw = os.environ.get(
        "NOUGEN_RELAY_STATUS_ORDER",
        "open,active,held,acked,in_progress,retry_pending,failed,blocked,released,complete,abandoned,dead_letter",
    )
    order = {name.strip(): index for index, name in enumerate(raw.split(","))
             if name.strip()}
    return order.get(str(status or "open"), 0)


def _relay_event_key(event: Any) -> Tuple[str, str, str]:
    """Stable identity for one append-only relay event.

    The identity deliberately follows the relay contract's
    ``(event, at, agent)`` tuple; machine is evidence on the event, not a
    second identity axis.
    """
    if not isinstance(event, dict):
        return ("", "", "")
    return (
        str(event.get("event") or ""),
        str(event.get("at") or ""),
        str(event.get("agent") or ""),
    )


def _relay_event_order(event: dict) -> tuple:
    """Canonical ordering for events merged from independently updated replicas."""
    stamp = str(event.get("at") or "")
    try:
        parsed = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=datetime.timezone.utc)
        instant = parsed.astimezone(datetime.timezone.utc).isoformat()
        stamp_key = (0, instant)
    except (TypeError, ValueError):
        stamp_key = (1, stamp)
    payload = json.dumps(event, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return (*stamp_key, *_relay_event_key(event), payload)


def _merge_relay_events(remote_events: Any, local_events: Any) -> List[dict]:
    """Union relay event arrays without allowing either projection to win.

    Remote events are retained in their existing order, then local-only events
    are appended.  For a duplicate key, non-empty fields from both records are
    combined; this preserves a richer note or evidence field without creating
    a second audit event.
    """
    merged: List[dict] = []
    positions: Dict[Tuple[str, str, str], int] = {}
    for candidate in list(remote_events or []) + list(local_events or []):
        if not isinstance(candidate, dict):
            continue
        key = _relay_event_key(candidate)
        # Events without identity are retained rather than silently collapsed.
        if not any(key):
            merged.append(dict(candidate))
            continue
        position = positions.get(key)
        if position is None:
            positions[key] = len(merged)
            merged.append(dict(candidate))
            continue
        combined = dict(merged[position])
        for field, value in candidate.items():
            if value not in (None, "", [], {}):
                combined[field] = value
        merged[position] = combined
    return sorted(merged, key=_relay_event_order)


def _merge_relay_records(local: Optional[dict], remote: Optional[dict]) -> dict:
    """Merge one local checkout record with its fetched registry projection.

    The old sync path checked out ``origin/<branch> -- .handoffs`` and could
    replace a newer local ack/checkpoint with the gateway's stale ``open``
    snapshot.  This function treats both inputs as projections: scalar fields
    are retained when present, status advances monotonically, and the relay
    event array is append-only.
    """
    if not local:
        return dict(remote or {})
    if not remote:
        return dict(local)

    merged = dict(remote)
    for field, value in local.items():
        if field == "relay":
            continue
        if value not in (None, "", [], {}):
            merged[field] = value

    local_status = local.get("status", "open")
    remote_status = remote.get("status", "open")
    if _relay_status_rank(local_status) >= _relay_status_rank(remote_status):
        merged["status"] = local_status
    else:
        merged["status"] = remote_status

    events = _merge_relay_events(remote.get("relay"), local.get("relay"))
    if events:
        merged["relay"] = events
    elif "relay" in local or "relay" in remote:
        merged["relay"] = []
    return merged


@dataclass
class HeartbeatPulse:
    pulse_id: int
    timestamp_utc: str
    ollama_status: str
    ollama_latency_ms: float
    loaded_models: List[str]
    open_handoffs_count: int
    lag_alerts_count: int
    status: str


@dataclass
class TriageResult:
    handoff_id: str
    task_type: str  # EXECUTION_RUN | CODE_MUTATION | STATUS_CHECK | INFORMATIONAL | DIAGNOSTIC
    action: str
    requires_harness_wake: bool
    confidence: float
    reasoning: str
    lag_seconds: float
    is_lagging: bool


class RelayRaceHUD:
    """Animated Olympic Relay Race Terminal Dashboard for NouGenAi Relay Daemon."""
    C_RESET = "\033[0m"
    C_BOLD = "\033[1m"
    C_DIM = "\033[2m"
    C_CYAN = "\033[36m"
    C_MAGENTA = "\033[35m"
    C_GREEN = "\033[32m"
    C_YELLOW = "\033[33m"
    C_BLUE = "\033[34m"
    C_RED = "\033[31m"
    C_WHITE = "\033[37m"

    TRACK_FRAMES = [
        "|🏃 Claude ======== ⚡ Codex ======== 🛡️ Apollo ======== 🏁|",
        "|=== 🏃 Claude ====== ⚡ Codex ====== 🛡️ Apollo ====== 🏁|",
        "|===== 🏃 Claude ==== ⚡ Codex ==== 🛡️ Apollo ==== 🏁|",
        "|======= 🏃 Claude == ⚡ Codex == 🛡️ Apollo == 🏁|",
        "|========= 🏃 Claude= ⚡ Codex= 🛡️ Apollo= 🏁|",
        "|=========== 🤝 BATON PASS (Claude ➔ Codex) ======= 🏁|",
        "|=== ⚡ Codex ======== 🛡️ Apollo ======== 🏃 Claude ==== 🏁|",
        "|===== ⚡ Codex ====== 🛡️ Apollo ====== 🏃 Claude ====== 🏁|",
        "|======= ⚡ Codex ==== 🛡️ Apollo ==== 🏃 Claude ======== 🏁|",
        "|=========== 🤝 BATON PASS (Codex ➔ Apollo) ======= 🏁|",
        "|=== 🛡️ Apollo ======== 🏃 Claude ======== ⚡ Codex ==== 🏁|",
        "|===== 🛡️ Apollo ====== 🏃 Claude ====== ⚡ Codex ====== 🏁|",
        "|=========== 🤝 BATON PASS (Apollo ➔ Claude) ====== 🏁|",
    ]

    @classmethod
    def render_race_card(cls, daemon_inst, pulse: HeartbeatPulse, cycle_summary: Dict[str, Any]):
        frame_idx = pulse.pulse_id % len(cls.TRACK_FRAMES)
        track_line = cls.TRACK_FRAMES[frame_idx]

        print("\n" + "=" * 76)
        print(f"🏟️  {cls.C_BOLD}{cls.C_YELLOW}NOUGEN RELAY GRAND PRIX{cls.C_RESET} — {cls.C_CYAN}{daemon_inst.machine_name.upper()}{cls.C_RESET} | {cls.C_GREEN}Pulse #{pulse.pulse_id}{cls.C_RESET}")
        print("=" * 76)
        print(f"🏁 {cls.C_BOLD}{cls.C_YELLOW}{track_line}{cls.C_RESET}")
        print("-" * 76)
        print(f"🟣 {cls.C_MAGENTA}LANE 1 (Claude Code):{cls.C_RESET}  Live Pulse & SSE Broadcast Room (Sub-ms)")
        print(f"🟢 {cls.C_GREEN}LANE 2 (Codex):{cls.C_RESET}        Autonomous Lease & Dispatch Loop")
        print(f"🔵 {cls.C_CYAN}LANE 3 (Apollo / AGY):{cls.C_RESET} Keymaker Vault & Cel Art Engines")
        print("-" * 76)
        print(f"💓 {cls.C_BOLD}Telemetry:{cls.C_RESET} Ollama: {cls.C_GREEN}{pulse.ollama_status}{cls.C_RESET} ({pulse.ollama_latency_ms:.1f}ms) | Open: {pulse.open_handoffs_count} | Lag: {pulse.lag_alerts_count} | Model: {daemon_inst.model_name}")

        triages = cycle_summary.get("triages", [])
        if triages:
            print(f"🏃 {cls.C_BOLD}Active Baton Action:{cls.C_RESET}")
            for t in triages[:3]:
                tr = t.get("triage", {})
                print(f"   💨 [{tr.get('task_type', 'TASK')}] {tr.get('handoff_id', '')[:35]}... ➔ {tr.get('action', '')[:40]}")
        print("=" * 76 + "\n", flush=True)


class RelayDaemon:
    """Self-healing background daemon enveloping the NouGen execution harness."""

    def __init__(
        self,
        relay_dir: Optional[Path] = None,
        db_path: Optional[Path] = None,
        heartbeat_sec: int = DEFAULT_HEARTBEAT_SEC,
        lag_threshold_sec: int = DEFAULT_LAG_THRESHOLD_SEC,
        ollama_url: Optional[str] = None,
        model_name: str = DEFAULT_MODEL,
        machine_name: Optional[str] = None,
    ):
        self.relay_dir = Path(relay_dir) if relay_dir else DEFAULT_RELAY_DIR
        self.handoffs_dir = self.relay_dir / ".handoffs"
        self.claims_dir = self.handoffs_dir / "claims"
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.heartbeat_sec = heartbeat_sec
        self.lag_threshold_sec = lag_threshold_sec
        self.ollama_url = ollama_url.rstrip("/") if ollama_url else DEFAULT_OLLAMA_URL
        self.model_name = model_name
        self.machine_name = machine_name or DEFAULT_MACHINE
        self.is_running = False
        self.pulse_counter = 0

        self._ensure_directories()
        self._init_db()

    def _ensure_directories(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.handoffs_dir.mkdir(parents=True, exist_ok=True)
        self.claims_dir.mkdir(parents=True, exist_ok=True)

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daemon_pulses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pulse_number INTEGER,
                    timestamp_utc TEXT,
                    ollama_status TEXT,
                    ollama_latency_ms REAL,
                    loaded_models TEXT,
                    open_handoffs_count INTEGER,
                    lag_alerts_count INTEGER,
                    status TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS triage_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    handoff_id TEXT UNIQUE,
                    source_machine TEXT,
                    goal TEXT,
                    task_type TEXT,
                    action TEXT,
                    requires_harness_wake INTEGER,
                    confidence REAL,
                    lag_seconds REAL,
                    status TEXT,
                    execution_result TEXT,
                    created_utc TEXT,
                    updated_utc TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lag_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    handoff_id TEXT,
                    lag_seconds REAL,
                    threshold_seconds REAL,
                    detected_utc TEXT,
                    reported INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def check_ollama_health(self) -> Tuple[bool, float, List[str]]:
        """Probes local Ollama at zero cloud cost. Returns (is_alive, latency_ms, loaded_models).

        One immediate retry: the first probe after a cold start routinely fails
        while the daemon's socket stack warms, which used to print a false
        "unreachable (-1.0ms)" on pulse #1. Latency is never negative — a
        failed probe reports 0.0 (no sample), not a sentinel.
        """
        for attempt in (1, 2):
            t0 = time.monotonic()
            try:
                req = urllib.request.Request(f"{self.ollama_url}/api/tags", headers={"User-Agent": "NouGen-RelayDaemon/1.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name", "") for m in data.get("models", [])]
                    latency_ms = (time.monotonic() - t0) * 1000.0
                    return True, latency_ms, models
            except Exception:
                if attempt == 1:
                    time.sleep(0.5)
        return False, 0.0, []

    def _registry_branch(self) -> str:
        """The branch the live registry lives on: env -> origin/HEAD -> main."""
        branch = os.environ.get("NOUGEN_RELAY_BRANCH", "").strip()
        if branch:
            return branch
        try:
            head = subprocess.run(
                ["git", "-C", str(self.handoffs_dir.parent), "symbolic-ref",
                 "--short", "refs/remotes/origin/HEAD"],
                capture_output=True, text=True, timeout=SYNC_TIMEOUT_SEC)
            if head.returncode == 0 and "/" in head.stdout:
                return head.stdout.strip().split("/", 1)[1]
        except Exception:
            pass
        return "main"

    def _registry_repo_slug(self) -> str:
        """owner/repo of the registry remote, for contents-API writes."""
        env = os.environ.get("NOUGEN_RELAY_REPO_SLUG", "").strip()
        if env:
            return env
        try:
            url = subprocess.run(
                ["git", "-C", str(self.handoffs_dir.parent), "remote",
                 "get-url", "origin"],
                capture_output=True, text=True, timeout=SYNC_TIMEOUT_SEC)
            tail = url.stdout.strip().rstrip("/").removesuffix(".git")
            parts = tail.replace(":", "/").split("/")
            if len(parts) >= 2:
                return f"{parts[-2]}/{parts[-1]}"
        except Exception:
            pass
        return ""

    def _registry_read_json(self, path: str) -> Tuple[Optional[dict], Optional[dict]]:
        """Read one JSON record from the canonical registry branch.

        ``({}, {})`` means the path does not exist and is safe to create.
        ``(None, None)`` means registry state could not be established, so a
        caller must fail closed instead of executing without fleet ownership.
        """
        slug = self._registry_repo_slug()
        gh = shutil.which("gh")
        if not slug or not gh:
            return None, None
        api = f"repos/{slug}/contents/{path}"
        branch = self._registry_branch()
        try:
            result = subprocess.run(
                [gh, "api", f"{api}?ref={branch}"],
                capture_output=True,
                text=True,
                timeout=SYNC_TIMEOUT_SEC,
            )
            if result.returncode != 0:
                detail = f"{result.stdout}\n{result.stderr}".lower()
                if "404" in detail or "not found" in detail:
                    return {}, {}
                print(f"[RelayDaemon] WARN registry read failed for {path}: "
                      f"{result.stderr.strip()[:160]}")
                return None, None
            meta = json.loads(result.stdout)
            record = json.loads(base64.b64decode(meta["content"]).decode("utf-8"))
            if not isinstance(record, dict):
                return None, None
            return meta, record
        except Exception as exc:
            print(f"[RelayDaemon] WARN registry read raised for {path}: {exc}")
            return None, None

    def _registry_write_json(
        self,
        path: str,
        record: dict,
        message: str,
        sha: Optional[str] = None,
    ) -> bool:
        """Atomically create/update one canonical registry JSON record."""
        slug = self._registry_repo_slug()
        gh = shutil.which("gh")
        if not slug or not gh:
            return False
        api = f"repos/{slug}/contents/{path}"
        body = base64.b64encode(
            (json.dumps(record, indent=2) + "\n").encode("utf-8")
        ).decode("ascii")
        argv = [
            gh,
            "api",
            "-X",
            "PUT",
            api,
            "-f",
            f"message={message}",
            "-f",
            f"content={body}",
            "-f",
            f"branch={self._registry_branch()}",
        ]
        if sha:
            argv.extend(["-f", f"sha={sha}"])
        try:
            result = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=SYNC_TIMEOUT_SEC,
            )
            if result.returncode == 0:
                return True
            print(f"[RelayDaemon] WARN registry write failed for {path}: "
                  f"{result.stderr.strip()[:160]}")
        except Exception as exc:
            print(f"[RelayDaemon] WARN registry write raised for {path}: {exc}")
        return False

    def _upstream_claim_path(self, handoff_id: str) -> str:
        safe_id = re.sub(r"[^A-Za-z0-9._-]+", "-", handoff_id).strip("-_")
        return f".handoffs/claims/{safe_id}__autonomous.json"

    def claim_leg_upstream(self, handoff_data: Dict[str, Any], lease: dict) -> bool:
        """Publish one fleet-visible, per-leg claim before any dispatch.

        Every machine contends on the same path for a leg. GitHub's contents
        API SHA precondition is the cross-machine fence; an active foreign
        holder wins, while an expired claim can be reclaimed after a crash.
        """
        handoff_id = str(handoff_data.get("id") or "").strip()
        if not handoff_id or claim_is_active is None:
            return False
        # Re-validate the LEG's live status before claiming. The local clone is
        # only as fresh as this cycle's sync, so a leg acked upstream in the gap
        # was still claimed off the stale read (observed 2026-08-31: claim
        # created 66s AFTER the leg was acked). A readable non-open leg is
        # never claimed; an unreadable one falls through to the claim-file SHA
        # fence, which still serializes writers.
        leg_meta, leg_record = self._registry_read_json(f".handoffs/{handoff_id}.json")
        if leg_record is not None and leg_record.get("status") not in OPEN_HANDOFF_STATES:
            print(f"[RelayDaemon] skip claim for {handoff_id}: live status is "
                  f"'{leg_record.get('status')}' (local clone was stale)")
            return False
        path = self._upstream_claim_path(handoff_id)
        meta, existing = self._registry_read_json(path)
        if meta is None or existing is None:
            return False

        same_holder = (
            existing.get("machine") == self.machine_name
            and existing.get("agent") == DAEMON_AGENT
        )
        if existing and claim_is_active(existing) and not same_holder:
            print(f"[RelayDaemon] claim held elsewhere for {handoff_id}: "
                  f"{existing.get('machine')}/{existing.get('agent')}")
            return False

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        ttl_minutes = float(lease.get("ttl_minutes") or 0)
        if ttl_minutes <= 0:
            # Derive a safe fallback from the configured execution ceiling and
            # heartbeat rather than baking another machine-specific duration.
            ttl_minutes = (EXEC_TIMEOUT_SEC + self.heartbeat_sec) / 60.0
            print(f"[RelayDaemon] WARN lease omitted TTL; derived {ttl_minutes:.1f}m")
        record = {
            "machine": self.machine_name,
            "agent": DAEMON_AGENT,
            "goal": str(handoff_data.get("goal") or ""),
            "scope": f"relay:{handoff_id}",
            "status": "active",
            "branch": self._registry_branch(),
            "created_utc": now,
            "ttl_hours": ttl_minutes / 60.0,
            "leg_id": handoff_id,
            "idempotency_key": lease.get("idempotency_key"),
        }
        sha = str(meta.get("sha") or "") or None
        claimed = self._registry_write_json(
            path,
            record,
            f"claim({self.machine_name}): autonomous pickup {handoff_id}",
            sha=sha,
        )
        if claimed:
            print(f"[RelayDaemon] ✅ claimed {handoff_id} upstream")
        return claimed

    def release_upstream_claim(
        self,
        handoff_id: str,
        outcome: str,
        evidence: str = "",
    ) -> bool:
        """Release this daemon's canonical claim with durable outcome evidence."""
        path = self._upstream_claim_path(handoff_id)
        meta, record = self._registry_read_json(path)
        if meta is None or record is None:
            return False
        if not record:
            return True
        if (record.get("machine"), record.get("agent")) != (
            self.machine_name,
            DAEMON_AGENT,
        ):
            return False
        record["status"] = "released"
        record["released_utc"] = datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat()
        record["outcome"] = outcome
        if evidence:
            record["evidence"] = evidence[:400]
        return self._registry_write_json(
            path,
            record,
            f"claim({self.machine_name}): release {handoff_id} ({outcome})",
            sha=str(meta.get("sha") or "") or None,
        )

    def verify_execution(self, triage: TriageResult, exec_res: Dict[str, Any]) -> Dict[str, Any]:
        """Self-verify a dispatch: hard gate on exit code, then the local
        model judges whether the output is evidence of the goal being done.
        Returns {verified, evidence}. Never trusts a zero exit code alone."""
        if not exec_res or exec_res.get("exit_code") != 0:
            return {"verified": False,
                    "evidence": f"non-zero exit ({(exec_res or {}).get('exit_code')})"}
        out = (exec_res.get("stdout") or "")[-1500:]
        prompt = (
            "You are verifying whether an autonomous dispatch actually did its job.\n"
            f"GOAL: {triage.action}\n\nEXECUTION OUTPUT (tail):\n{out}\n\n"
            "The output must DIRECTLY ADDRESS this exact goal - a confident "
            "answer about an adjacent or related topic is NOT verification.\n"
            'Answer as JSON: {"verified": true|false, "evidence": "<one line citing the output>"}. '
            "verified=true ONLY if the output contains concrete evidence the goal "
            "was accomplished; progress reports and plans are not evidence.")
        try:
            req = urllib.request.Request(
                f"{self.ollama_url}/api/generate",
                data=json.dumps({"model": self.model_name, "prompt": prompt,
                                 "stream": False, "format": "json"}).encode("utf-8"),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                parsed = json.loads(json.loads(resp.read().decode("utf-8")).get("response", "{}"))
            return {"verified": bool(parsed.get("verified", False)),
                    "evidence": str(parsed.get("evidence", ""))[:300]}
        except Exception as exc:
            # An unverifiable dispatch is NOT a verified one.
            return {"verified": False, "evidence": f"verifier unavailable: {exc}"}

    def _dav1d_json(self, prompt: str, timeout: int = 60) -> Dict[str, Any]:
        """One JSON-mode round trip to the local dav1d model; raises on failure."""
        req = urllib.request.Request(
            f"{self.ollama_url}/api/generate",
            data=json.dumps({"model": self.model_name, "prompt": prompt,
                             "stream": False, "format": "json"}).encode("utf-8"),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            parsed = json.loads(json.loads(resp.read().decode("utf-8")).get("response", "{}"))
        if not isinstance(parsed, dict):
            raise ValueError("dav1d returned non-object JSON")
        return parsed

    def _leg_body(self, handoff_data: Dict[str, Any]) -> str:
        return str(handoff_data.get("notes") or handoff_data.get("message")
                   or handoff_data.get("body") or "")

    def _leg_done_when(self, handoff_data: Dict[str, Any]) -> str:
        """The leg's own acceptance criteria; empty string when it has none."""
        m = re.search(r"(?ims)^#+\s*done[ -]?when\b.*?(?=^#|\Z)",
                      self._leg_body(handoff_data))
        return m.group(0).strip()[:800] if m else ""

    def _leg_demands_change(self, handoff_data: Dict[str, Any]) -> bool:
        """True when a leg needs execution or human resolution - never a
        generated answer. Three tests, any of which suffices:
        1. SHAPE: a goal starting "TODO:" is a queue item by fleet convention
           (relay-watch files its whole queue that way - 90 of 220 open legs),
           whatever verbs follow. A bare substring match would over-fire on
           completion reports that MENTION a TODO, so prefix only.
        2. Change verbs (CHANGE_MARKERS).
        3. Defect-report markers (DEFECT_MARKERS) - a defect report without a
           fix-verb is still not a question."""
        goal = str(handoff_data.get("goal") or "")
        if goal.strip().lower().startswith("todo:"):
            return True
        text = (goal + " " + self._leg_done_when(handoff_data)).lower()
        return any(w in text for w in CHANGE_MARKERS) or any(
            w in text for w in DEFECT_MARKERS)

    @staticmethod
    def _probe_allowed(argv: Any) -> bool:
        """Hard whitelist for model-proposed probes: read-only, argv-list only.

        The probe list comes from a model fed untrusted leg text, so nothing
        here trusts intent - only shape. No shell ever; unknown binary = no."""
        if not isinstance(argv, list) or not argv:
            return False
        if not all(isinstance(a, str) and "\n" not in a and len(a) < 500 for a in argv):
            return False
        exe = Path(argv[0]).name.lower()
        if exe in ("gh", "gh.exe"):
            if len(argv) < 3 or argv[1] != "api":
                return False
            banned = {"-X", "--method", "-f", "--field", "-F", "--raw-field", "--input"}
            # -X GET is redundant but harmless; anything else that mutates is out.
            for i, a in enumerate(argv):
                if a in ("-X", "--method"):
                    if i + 1 >= len(argv) or argv[i + 1].upper() != "GET":
                        return False
                elif a in banned - {"-X", "--method"}:
                    return False
            return True
        if exe in ("git", "git.exe"):
            return len(argv) >= 2 and argv[1] in (
                "log", "show", "status", "diff", "ls-files", "rev-parse", "ls-remote")
        if exe in ("curl", "curl.exe"):
            banned = {"-X", "--request", "-d", "--data", "--data-raw", "--data-binary",
                      "-F", "--form", "-T", "--upload-file", "-o", "--output"}
            if any(a in banned for a in argv[1:]):
                return False
            return any(a.startswith(("http://", "https://")) for a in argv[1:])
        return False

    def _run_probes(self, probes: Any) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        if not isinstance(probes, list):
            return results
        for p in probes[:PROBE_MAX]:
            argv = p.get("argv") if isinstance(p, dict) else None
            if not self._probe_allowed(argv):
                results.append({"argv": argv, "status": "rejected"})
                continue
            try:
                proc = subprocess.run(
                    argv, capture_output=True, text=True,
                    timeout=PROBE_TIMEOUT_SEC, cwd=str(self.relay_dir))
                results.append({
                    "argv": argv, "status": "ran", "exit_code": proc.returncode,
                    "output": (proc.stdout or proc.stderr or "").strip()[-800:]})
            except Exception as exc:
                results.append({"argv": argv, "status": "error",
                                "error": str(exc)[:200]})
        return results

    def dav1d_probe_verify(self, triage: TriageResult,
                           handoff_data: Dict[str, Any],
                           exec_res: Dict[str, Any]) -> Dict[str, Any]:
        """Grounded verification: dav1d proposes read-only probes of live
        state, the daemon runs the whitelisted ones, and the verdict must cite
        probe output. Prose-only verification remains legal ONLY for legs that
        are pure questions (no change demanded, no harness wake). Every error
        path fails closed - an unprobeable claim of completion stays open."""
        if not exec_res or exec_res.get("exit_code") != 0:
            return {"verified": False,
                    "evidence": f"non-zero exit ({(exec_res or {}).get('exit_code')})"}
        if not self._leg_demands_change(handoff_data) and not triage.requires_harness_wake:
            # Judge the answer against the LEG'S OWN GOAL, not the triage
            # one-liner: a confident answer about an adjacent topic passed the
            # old check (observed: an ack note answering 170210Z's row counts
            # on a leg that asked about capture integrity).
            leg_goal = str(handoff_data.get("goal") or triage.action)
            judged = replace(triage, action=leg_goal)
            verdict = self.verify_execution(judged, exec_res)
            verdict["evidence"] = (
                "fleet-answer (question-shaped leg): " + verdict["evidence"])[:400]
            return verdict
        goal = str(handoff_data.get("goal") or triage.action)
        done_when = self._leg_done_when(handoff_data)
        out = (exec_res.get("stdout") or "")[-1200:]
        try:
            plan = self._dav1d_json(
                "You are Dav1d, verification planner on the Blade node. An autonomous "
                "dispatch claims it completed a relay leg. Propose up to "
                f"{PROBE_MAX} READ-ONLY probe commands that would prove or refute it "
                "against live state. Allowed binaries: gh (api GET only), git "
                "(log/show/status/diff/ls-files/rev-parse/ls-remote), curl (GET only). "
                "Each probe is an argv array, no shell syntax.\n"
                f"LEG GOAL: {goal}\n"
                + (f"LEG DONE-WHEN:\n{done_when}\n" if done_when else "")
                + f"CLAIMED EXECUTION OUTPUT (tail):\n{out}\n\n"
                'Respond ONLY as JSON: {"probes": [{"argv": ["git", "log", "-1"], '
                '"why": "<what this proves>"}]}')
            probe_results = self._run_probes(plan.get("probes"))
        except Exception as exc:
            return {"verified": False,
                    "evidence": f"probe planning failed ({exc}); execution-shaped leg stays open"}
        ran = [r for r in probe_results if r.get("status") == "ran"]
        if not ran:
            return {"verified": False, "probes": probe_results,
                    "evidence": "no runnable read-only probes; execution-shaped leg stays open"}
        evidence_blob = "\n".join(
            f"$ {' '.join(r['argv'])}\n(exit {r['exit_code']}) {r['output'][:400]}"
            for r in ran)
        try:
            verdict = self._dav1d_json(
                "You are Dav1d, verification judge on the Blade node. Decide whether "
                "the PROBE OUTPUTS below prove the leg's goal was accomplished in live "
                "state. The dispatch's own prose is NOT evidence; only probe output "
                "counts. Unclear or partial = not verified.\n"
                f"LEG GOAL: {goal}\n"
                + (f"LEG DONE-WHEN:\n{done_when}\n" if done_when else "")
                + f"PROBE OUTPUTS:\n{evidence_blob}\n\n"
                'Respond ONLY as JSON: {"verified": true|false, '
                '"evidence": "<one line citing a probe output>"}')
        except Exception as exc:
            return {"verified": False, "probes": probe_results,
                    "evidence": f"probe verdict failed ({exc}); leg stays open"}
        trail = "; ".join(
            f"{' '.join(r['argv'])} -> exit {r['exit_code']}" for r in ran)[:400]
        return {
            "verified": bool(verdict.get("verified", False)),
            "probes": probe_results,
            "evidence": (f"probe-verified: {str(verdict.get('evidence', ''))[:300]}"
                         f" | probes: {trail}")[:ACK_NOTE_MAX - 30],
        }

    def ack_leg_upstream(self, handoff_id: str, evidence: str) -> bool:
        """Write the ack to the LIVE registry via the GitHub contents API.

        Never `git push` from this clone: its checked-out branch carries code
        history that must not ride along with a registry ack. The contents API
        touches exactly one file on the registry branch - the same lane the
        fleet worker itself writes through."""
        slug = self._registry_repo_slug()
        gh = shutil.which("gh")
        if not slug or not gh:
            print("[RelayDaemon] WARN ack skipped: no repo slug or gh CLI")
            return False
        branch = self._registry_branch()
        path = f".handoffs/{handoff_id}.json"
        api = f"repos/{slug}/contents/{path}"
        try:
            cur = subprocess.run(
                [gh, "api", f"{api}?ref={branch}"],
                capture_output=True, text=True, timeout=SYNC_TIMEOUT_SEC)
            if cur.returncode != 0:
                err = (cur.stderr or cur.stdout or "").strip()[:120]
                if "404" in err or "Not Found" in err:
                    # Leg exists in another registry (gateway/connector lane) but was
                    # never pushed to the git registry — split-brain artifact, not an
                    # ack failure this daemon can heal.
                    print(f"[RelayDaemon] INFO ack skipped for {handoff_id}: not in git registry (gateway-only leg)")
                else:
                    print(f"[RelayDaemon] WARN ack read failed for {handoff_id}: {err or 'gh api error'}")
                return False
            meta = json.loads(cur.stdout)
            record = json.loads(base64.b64decode(meta["content"]).decode("utf-8"))
            if record.get("status") not in OPEN_HANDOFF_STATES:
                return True  # someone else closed it first; healed either way
            record["status"] = "acked"
            record["acked_by"] = f"relay-daemon@{self.machine_name}"
            record["acked_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            record["ack_note"] = f"daemon dispatch verified: {evidence}"[:ACK_NOTE_MAX]
            # Also record the ack as a relay EVENT. Readers that surface only the
            # events array (the connector's relay_read serializer among them) saw
            # daemon acks as authorless - status flipped with relay:[] empty -
            # which even blocked a leg's own author from correcting it
            # (2026-08-31 finding, leg 20260831T221346Z).
            events = record.get("relay")
            if not isinstance(events, list):
                events = []
            events.insert(0, {
                "event": "ack",
                "machine": self.machine_name,
                "agent": DAEMON_AGENT,
                "at": record["acked_utc"],
                "note": record["ack_note"][:200],
            })
            record["relay"] = events
            body = base64.b64encode(
                (json.dumps(record, indent=2) + "\n").encode("utf-8")).decode("ascii")
            put = subprocess.run(
                [gh, "api", "-X", "PUT", api,
                 "-f", f"message=relay: daemon ack {handoff_id}",
                 "-f", f"content={body}", "-f", f"sha={meta['sha']}",
                 "-f", f"branch={branch}"],
                capture_output=True, text=True, timeout=SYNC_TIMEOUT_SEC)
            if put.returncode != 0:
                print(f"[RelayDaemon] WARN ack push failed for {handoff_id}: "
                      f"{put.stderr.strip()[:120]}")
                return False
            print(f"[RelayDaemon] ✅ acked {handoff_id} upstream ({evidence[:80]})")
            return True
        except Exception as exc:
            print(f"[RelayDaemon] WARN ack raised for {handoff_id}: {exc}")
            return False

    def fleet_respond(self, handoff_data: Dict[str, Any], triage: TriageResult) -> Dict[str, Any]:
        """Answer an informational/diagnostic leg on the free local fleet.

        The harness is for execution; a leg that only needs an answer,
        summary, or status readout is fleet work (local-first doctrine).
        Multiple free lanes are walked in FLEET_LANES order (GM order
        2026-08-27): ollama-local (dav1d), ollama-cloud (gemma cloud),
        openrouter (several free nemotron agents, one per model),
        kimi-space (FREE Kimi via a public HF Space gradio tunnel), and
        hf-kimi (HF inference router, rhea_noir's billed kimi lane). The first
        lane returning a non-empty answer wins; its answer becomes the
        dispatch output and flows through the same verify -> ack-upstream
        path as a harness run. Total failure returns exit_code 1 with the
        last lane error in stderr."""
        goal = handoff_data.get("goal", "")
        notes = str(handoff_data.get("notes") or handoff_data.get("message") or "")[:2000]
        prompt = (
            "You are the on-machine fleet responder for the NouGen relay. "
            "Answer this leg concisely and concretely; if it asks for status "
            "or a summary, give your best evidence-based answer; if it cannot "
            "be answered without running commands, say exactly what is "
            f"missing.\n\nLEG GOAL: {goal}\n\nLEG NOTES:\n{notes}")
        timeout = FLEET_LANE_TIMEOUT_SEC
        last_err = "no fleet lane configured"

        def _ollama_gen(model: str) -> str:
            req = urllib.request.Request(
                f"{self.ollama_url}/api/generate",
                data=json.dumps({"model": model, "prompt": prompt,
                                 "stream": False}).encode("utf-8"),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8")).get("response", "").strip()

        def _openai_chat(url: str, token: str, model: str) -> str:
            req = urllib.request.Request(
                url,
                data=json.dumps({"model": model,
                                 "messages": [{"role": "user", "content": prompt}]
                                 }).encode("utf-8"),
                method="POST")
            req.add_header("Authorization", f"Bearer {token}")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            return (body["choices"][0]["message"]["content"] or "").strip()

        def _win(lane: str, model: str, answer: str) -> Dict[str, Any]:
            return {"status": "success", "command": f"fleet:{lane}:{model}",
                    "stdout": answer[-2000:], "stderr": "", "exit_code": 0}

        for lane in FLEET_LANES:
            try:
                if lane == "ollama-local":
                    answer = _ollama_gen(self.model_name)
                    if answer:
                        return _win(lane, self.model_name, answer)
                    last_err = f"{lane}: empty answer from {self.model_name}"
                elif lane == "ollama-cloud":
                    answer = _ollama_gen(FLEET_CLOUD_MODEL)
                    if answer:
                        return _win(lane, FLEET_CLOUD_MODEL, answer)
                    last_err = f"{lane}: empty answer from {FLEET_CLOUD_MODEL}"
                elif lane == "openrouter":
                    or_key = (os.environ.get("OPENROUTER_API_KEY") or "").strip() \
                        or _keymaker_load("OPENROUTER_KEY_NOUGENAI")
                    if not or_key:
                        last_err = f"{lane}: no API key (env or keymaker)"
                        continue
                    for or_model in FLEET_OR_MODELS:
                        try:
                            answer = _openai_chat(OPENROUTER_URL, or_key, or_model)
                            if answer:
                                return _win(lane, or_model, answer)
                            last_err = f"{lane}: empty answer from {or_model}"
                        except Exception as exc:
                            last_err = f"{lane}:{or_model}: {str(exc)[:120]}"
                elif lane == "kimi-space":
                    # FREE Kimi through a public HF Space's gradio tunnel
                    # (GM order 2026-08-27): the Space's own credit pays, so
                    # this outranks the billed hf-kimi router lane. Endpoint
                    # discovered live from /gradio_api/info (probe, don't
                    # assume); any failure falls through to the next lane.
                    space = (os.environ.get("NOUGEN_KIMI_SPACE") or "").strip() \
                        or "akhaliq/Kimi-K3"
                    try:
                        sp_timeout = int(os.environ.get(
                            "NOUGEN_KIMI_SPACE_TIMEOUT", "90"))
                    except ValueError:
                        sp_timeout = 90
                    host = space.replace("/", "-").replace("_", "-") \
                        .replace(".", "-").lower()
                    base = f"https://{host}.hf.space/gradio_api"
                    with urllib.request.urlopen(
                            f"{base}/info", timeout=min(sp_timeout, 30)) as resp:
                        sp_info = json.loads(resp.read().decode("utf-8"))
                    ep_name, wants_dict, extras = None, False, []
                    for ep_key, ep in (sp_info.get("named_endpoints") or {}).items():
                        params = ep.get("parameters") or []
                        if params and params[0].get("parameter_name") == "message":
                            ep_name = ep_key.lstrip("/")
                            wants_dict = (params[0].get("type") or {}).get(
                                "type") == "object"
                            # Required no-default params (history) must be
                            # sent concretely; None breaks the Space app.
                            extras = [p.get("parameter_default")
                                      if p.get("parameter_default") is not None
                                      else []
                                      for p in params[1:]]
                            break
                    if not ep_name:
                        last_err = f"{lane}:{space}: no message-led endpoint"
                        continue
                    sp_msg = {"text": prompt, "files": []} if wants_dict else prompt
                    call_url = f"{base}/call/{ep_name}"
                    req = urllib.request.Request(
                        call_url,
                        data=json.dumps({"data": [sp_msg] + extras}).encode("utf-8"),
                        headers={"Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(
                            req, timeout=min(sp_timeout, 30)) as resp:
                        event_id = json.loads(resp.read().decode("utf-8"))["event_id"]
                    sp_payload = None
                    with urllib.request.urlopen(
                            f"{call_url}/{event_id}", timeout=sp_timeout) as resp:
                        for raw_line in resp:
                            line = raw_line.decode("utf-8", "replace").strip()
                            if line.startswith("data:"):
                                sp_payload = line[5:].strip()
                    answer = _space_pluck(
                        json.loads(sp_payload)) if sp_payload else None
                    if answer:
                        return _win(lane, space, answer)
                    last_err = f"{lane}:{space}: empty answer"
                elif lane == "hf-kimi":
                    hf_model = (os.environ.get("NOUGEN_RHEA_MODEL") or "").strip()
                    hf_token = ""
                    raw = os.environ.get("NGS_INFERENCE_TOKENS", "")
                    for cand in [k.strip() for k in raw.split(",")] + [
                            (os.environ.get("NGS_INFERENCE_TOKEN") or "").strip(),
                            (os.environ.get("HF_TOKEN") or "").strip()]:
                        if cand:
                            hf_token = cand
                            break
                    if not hf_token:
                        hf_token = _keymaker_load("HUGGINGFACE_API_KEY") or ""
                    if not hf_token or not hf_model:
                        continue  # skip silently: lane not configured
                    answer = _openai_chat(HF_ROUTER_URL, hf_token, hf_model)
                    if answer:
                        return _win(lane, hf_model, answer)
                    last_err = f"{lane}: empty answer from {hf_model}"
                else:
                    last_err = f"unknown fleet lane '{lane}'"
            except Exception as exc:
                last_err = f"{lane}: {str(exc)[:200]}"
        return {"status": "exception", "command": "fleet:exhausted",
                "stdout": "", "stderr": last_err[:300], "exit_code": 1}

    def sync_relay_repo(self) -> None:
        """Merge the fetched registry projection into the local checkout.

        The clone may sit on any local branch (pi-remix, detached, mid-work),
        so a plain ``git pull`` is wrong twice: it needs an upstream, and it
        would drag code changes along just to read legs.  The previous overlay
        used ``git checkout origin/<branch> -- .handoffs``; that was unsafe
        because a gateway snapshot with an older ``open`` status could erase a
        newer local ack/checkpoint.  Fetch the registry branch and merge each
        relay record instead.  Git and gateway are still projections for now,
        but neither projection can destroy append-only evidence from the other.
        """
        repo = self.handoffs_dir.parent
        if not (repo / ".git").exists():
            return

        def _git(*args: str):
            return subprocess.run(
                ["git", "-C", str(repo), *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=SYNC_TIMEOUT_SEC,
            )

        branch = self._registry_branch()
        try:
            fetched = _git("fetch", "--quiet", "origin", branch)
            if fetched.returncode != 0:
                print(f"[RelayDaemon] WARN relay fetch failed: {fetched.stderr.strip()[:160]}")
                return

            remote_ref = f"origin/{branch}"
            listing = _git("ls-tree", "-r", "--name-only", remote_ref, ".handoffs")
            if listing.returncode != 0:
                print(f"[RelayDaemon] WARN relay tree read failed: {listing.stderr.strip()[:160]}")
                return

            remote_paths = {
                line.strip() for line in listing.stdout.splitlines()
                if line.strip().startswith(".handoffs/")
            }

            # Materialise files that are missing locally, and merge only JSON
            # relay records that exist on both sides. Existing markdown bodies
            # are intentionally preserved: structured JSON is the mergeable
            # audit surface, while the body is an immutable brief.
            for rel_path in sorted(remote_paths):
                remote_file = _git("show", f"{remote_ref}:{rel_path}")
                if remote_file.returncode != 0:
                    print(f"[RelayDaemon] WARN relay file read failed: {rel_path}")
                    continue
                target = repo / Path(rel_path.replace("/", os.sep))
                target.parent.mkdir(parents=True, exist_ok=True)
                remote_text = remote_file.stdout

                if not target.exists():
                    target.write_text(remote_text, encoding="utf-8")
                    continue
                if target.suffix.lower() != ".json":
                    continue

                try:
                    local_data = json.loads(target.read_text(encoding="utf-8"))
                    remote_data = json.loads(remote_text)
                except (OSError, json.JSONDecodeError) as exc:
                    print(f"[RelayDaemon] WARN relay merge skipped {rel_path}: {exc}")
                    continue
                if not isinstance(local_data, dict) or not isinstance(remote_data, dict):
                    continue

                merged = _merge_relay_records(local_data, remote_data)
                merged_text = json.dumps(merged, indent=2) + "\n"
                if merged_text != target.read_text(encoding="utf-8"):
                    target.write_text(merged_text, encoding="utf-8")

            # Local-only legs may have been created by a worker or connector
            # that has not reached the remote projection yet. Leave them
            # untouched; deleting them would recreate the same data-loss window.
        except Exception as exc:
            print(f"[RelayDaemon] WARN relay sync raised: {exc}")

    def already_triaged_ids(self) -> set:
        """Handoff ids this daemon has already triaged (persisted across runs)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("SELECT handoff_id FROM triage_events").fetchall()
            return {r[0] for r in rows}
        except Exception:
            return set()

    # --- lease control plane glue -------------------------------------------
    # tokens issued by acquire_lease, keyed by leg; every write that ends a
    # lease presents its token so a reclaimed lease cannot be closed by the
    # worker that lost it.
    _lease_tokens: Dict[str, Any] = {}

    def _admit(self, handoff: dict):
        try:
            from nougen_relay.guard import admit
        except Exception:
            return "ALLOW", "admission controller unavailable; legacy path"
        try:
            return admit(self.relay_dir, handoff, machine=self.machine_name, agent=DAEMON_AGENT)
        except Exception as exc:  # pylint: disable=broad-except
            return "DEFER", f"admit error {type(exc).__name__}"

    def _release(self, handoff_id: str, status: str, evidence: str = "") -> bool:
        if release_lease is None:
            return False
        token = self._lease_tokens.pop(handoff_id, None)
        try:
            ok = release_lease(self.relay_dir, handoff_id, status=status, fencing_token=token, evidence=evidence)
        except TypeError:  # older core without fencing
            ok = release_lease(self.relay_dir, handoff_id, status=status)
        if not ok:
            print(f"[RelayDaemon] FENCED release({status}) for {handoff_id}: token {token} is stale")
        return ok

    def _start_heartbeat(self, handoff_id: str):
        """Heartbeat every TTL/3 while execution runs; returns the stop event."""
        import threading
        stop = threading.Event()
        token = self._lease_tokens.get(handoff_id)
        try:
            from nougen_relay.core import heartbeat_interval_seconds, heartbeat_lease
        except Exception:
            return stop
        lease = self._lease_record(handoff_id) or {}
        interval = heartbeat_interval_seconds(lease.get("ttl_minutes"))

        def beat():
            while not stop.wait(interval):
                if not heartbeat_lease(self.relay_dir, handoff_id, token):
                    print(f"[RelayDaemon] heartbeat rejected for {handoff_id} (token {token}); lease lost")
                    return
        threading.Thread(target=beat, name=f"lease-heartbeat-{handoff_id[:16]}", daemon=True).start()
        return stop

    def _sweep_leases(self) -> Dict[str, Any]:
        try:
            from nougen_relay.core import lease_metrics, sweep_expired_leases
        except Exception:
            return {}
        swept = sweep_expired_leases(self.relay_dir)
        for leg_id in swept:
            self._lease_tokens.pop(leg_id, None)
        metrics = lease_metrics(self.relay_dir)
        if swept:
            print(f"[RelayDaemon] swept {len(swept)} expired lease(s): {', '.join(x[:20] for x in swept[:5])}")
        return {"swept": swept, **metrics}

    def _lease_record(self, handoff_id: str) -> Optional[dict]:
        if leases_dir is None:
            return None
        path = leases_dir(self.relay_dir) / f"{handoff_id}.lease.json"
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            return record if isinstance(record, dict) else None
        except (OSError, json.JSONDecodeError):
            return None

    def _ready_handoffs(self, open_handoffs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Newest unseen legs plus failed legs whose durable backoff elapsed.

        The former loop permanently excluded every id found in triage_events.
        One crash, verifier outage, or harness error therefore burned the leg
        forever. Retry state now lives in the lease record and survives daemon
        restarts; active leases fence duplicate workers and expired leases are
        reclaimed by ``acquire_lease``.
        """
        seen = self.already_triaged_ids()
        ready = []
        for handoff in reversed(open_handoffs):
            handoff_id = str(handoff.get("id") or "").strip()
            if not handoff_id:
                continue
            if handoff_id not in seen:
                ready.append(handoff)
                continue
            lease = self._lease_record(handoff_id)
            if not lease or lease_is_active is None or is_leg_retryable is None:
                continue
            if lease_is_active(lease):
                continue
            if is_leg_retryable(lease):
                ready.append(handoff)
        return ready[:TRIAGE_PER_CYCLE]

    def reconcile_verified_acks(self) -> int:
        """Retry registry acks for verified work without executing it twice."""
        reconciled = 0
        try:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute(
                    "SELECT handoff_id, execution_result FROM triage_events "
                    "WHERE execution_result IS NOT NULL"
                ).fetchall()
                for handoff_id, raw_result in rows:
                    try:
                        result = json.loads(raw_result)
                    except (TypeError, json.JSONDecodeError):
                        continue
                    if not result.get("verified") or result.get("acked_upstream"):
                        continue
                    evidence = str(result.get("verify_evidence") or "verified execution")
                    if not self.ack_leg_upstream(handoff_id, evidence):
                        continue
                    result["acked_upstream"] = True
                    result["reconciled_utc"] = datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat()
                    conn.execute(
                        "UPDATE triage_events SET execution_result=?, updated_utc=? "
                        "WHERE handoff_id=?",
                        (json.dumps(result), result["reconciled_utc"], handoff_id),
                    )
                    if release_lease is not None:
                        self._release(handoff_id, "complete", "reconciled: verified ack retried upstream")
                    self.release_upstream_claim(handoff_id, "complete", evidence)
                    reconciled += 1
                conn.commit()
        except Exception as exc:
            print(f"[RelayDaemon] WARN ack reconcile raised: {exc}")
        return reconciled

    def get_open_handoffs(self) -> List[Dict[str, Any]]:
        """Scans .handoffs/ for open/unresolved baton records."""
        results = []
        if not self.handoffs_dir.exists():
            return results

        json_files = list(self.handoffs_dir.glob("*.json"))
        for jf in sorted(json_files):
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
                status = data.get("status", "open")
                if status in OPEN_HANDOFF_STATES:
                    data["_file_path"] = str(jf)
                    results.append(data)
            except Exception:
                continue
        return results

    def calculate_lag(self, handoff_data: Dict[str, Any]) -> Tuple[float, bool]:
        """Calculates lag in seconds between creation and current time."""
        created_str = (
            handoff_data.get("created_utc")
            or handoff_data.get("created_at")
            or handoff_data.get("timestamp")
            or handoff_data.get("when")
        )
        if not created_str:
            return 0.0, False

        try:
            # Parse ISO 8601 string
            clean_str = created_str.replace("Z", "+00:00")
            dt = datetime.datetime.fromisoformat(clean_str)
            now = datetime.datetime.now(datetime.timezone.utc)
            lag_sec = max(0.0, (now - dt).total_seconds())
            is_lagging = lag_sec >= self.lag_threshold_sec
            return lag_sec, is_lagging
        except Exception:
            return 0.0, False

    def triage_with_ollama(self, handoff_data: Dict[str, Any]) -> TriageResult:
        """Invokes local Ollama (dav1d:e2b) to classify the baton and formulate action."""
        handoff_id = handoff_data.get("id", Path(handoff_data.get("_file_path", "unknown")).stem)
        goal = handoff_data.get("goal", "")
        lag_sec, is_lagging = self.calculate_lag(handoff_data)

        # Build local prompt
        prompt = (
            f"You are Dav1d, the local execution triager on the Blade node.\n"
            f"Classify this incoming relay goal into JSON:\n"
            f"Goal: {goal}\n\n"
            f"Allowed task_type values: EXECUTION_RUN, CODE_MUTATION, STATUS_CHECK, INFORMATIONAL, DIAGNOSTIC.\n"
            f"Respond ONLY with valid JSON in this exact structure:\n"
            f'{{"task_type": "EXECUTION_RUN", "action": "subcommand or task name", "requires_harness_wake": true, "confidence": 0.95, "reasoning": "brief explanation"}}'
        )

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        try:
            req = urllib.request.Request(
                f"{self.ollama_url}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                response_text = res.get("response", "{}")
                parsed = json.loads(response_text)
                return TriageResult(
                    handoff_id=handoff_id,
                    task_type=parsed.get("task_type", "INFORMATIONAL"),
                    action=parsed.get("action", goal),
                    requires_harness_wake=bool(parsed.get("requires_harness_wake", False)),
                    confidence=float(parsed.get("confidence", 0.8)),
                    reasoning=parsed.get("reasoning", "Triaged via local Ollama"),
                    lag_seconds=lag_sec,
                    is_lagging=is_lagging,
                )
        except Exception as e:
            # Fallback rule-based triage when Ollama is unreachable
            requires_wake = any(w in goal.lower() for w in ["exec", "run", "agy", "antigravity", "dispatch", "build", "test", "patch"])
            task_type = "EXECUTION_RUN" if requires_wake else "INFORMATIONAL"
            return TriageResult(
                handoff_id=handoff_id,
                task_type=task_type,
                action=goal,
                requires_harness_wake=requires_wake,
                confidence=0.5,
                reasoning=f"Fallback rule-based triage (Ollama error: {e})",
                lag_seconds=lag_sec,
                is_lagging=is_lagging,
            )

    def dispatch_execution(self, triage: TriageResult, dry_run: bool = False) -> Dict[str, Any]:
        """Dispatches work to the AGY CLI / Dav1d execution harness."""
        if dry_run:
            return {
                "status": "dry_run",
                "message": f"Dry-run dispatch: would execute '{triage.action}' for {triage.handoff_id}",
                "exit_code": 0,
            }

        # Real dispatch: the leg's own brief goes to the AGY harness as a
        # prompt. The previous version ran only canned diagnostics (mcp list /
        # status / --version) whatever the leg asked -- a daemon that could
        # prove agy's version number but never do the work (found 2026-08-27
        # when 58 open legs sat untouched pulse after pulse).
        # Binary resolved on PATH (or NOUGEN_AGY_BIN); argv list, never
        # shell=True, so leg text can never become a shell command.
        agy_bin = shutil.which(DEFAULT_AGY_BIN) or shutil.which(f"{DEFAULT_AGY_BIN}.cmd")
        if not agy_bin:
            return {
                "status": "error",
                "message": f"AGY binary '{DEFAULT_AGY_BIN}' not found on PATH",
                "exit_code": 127,
            }

        brief = (
            f"Relay leg {triage.handoff_id} (machine dispatch, act autonomously, "
            f"report evidence):\n\nGOAL: {triage.action}\n\n"
            f"Triage reasoning: {triage.reasoning}"
        )
        argv = [agy_bin, "-p", brief]

        stop_beat = self._start_heartbeat(triage.handoff_id)
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=int(os.environ.get("NOUGEN_AGY_TIMEOUT_SEC", str(EXEC_TIMEOUT_SEC))),
            )
            stop_beat.set()
            return {
                "status": "success" if proc.returncode == 0 else "error",
                "command": f"{argv[0]} -p <brief for {triage.handoff_id}>",
                "stdout": (proc.stdout.strip() if proc.stdout else "")[-2000:],
                "stderr": (proc.stderr.strip() if proc.stderr else "")[-500:],
                "exit_code": proc.returncode,
            }
        except Exception as e:
            return {
                "status": "exception",
                "message": str(e),
                "exit_code": 1,
            }

    def record_pulse(self, pulse: HeartbeatPulse) -> None:
        """Persists a pulse event to SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO daemon_pulses (
                    pulse_number, timestamp_utc, ollama_status, ollama_latency_ms,
                    loaded_models, open_handoffs_count, lag_alerts_count, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    pulse.pulse_id,
                    pulse.timestamp_utc,
                    pulse.ollama_status,
                    pulse.ollama_latency_ms,
                    json.dumps(pulse.loaded_models),
                    pulse.open_handoffs_count,
                    pulse.lag_alerts_count,
                    pulse.status,
                ),
            )
            conn.commit()

    def record_triage(self, handoff_data: Dict[str, Any], triage: TriageResult, exec_res: Optional[Dict[str, Any]] = None) -> None:
        """Persists a triage and execution event to SQLite."""
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO triage_events (
                    handoff_id, source_machine, goal, task_type, action,
                    requires_harness_wake, confidence, lag_seconds, status,
                    execution_result, created_utc, updated_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(handoff_id) DO UPDATE SET
                    task_type=excluded.task_type,
                    action=excluded.action,
                    requires_harness_wake=excluded.requires_harness_wake,
                    confidence=excluded.confidence,
                    lag_seconds=excluded.lag_seconds,
                    status=excluded.status,
                    execution_result=excluded.execution_result,
                    updated_utc=excluded.updated_utc
            """,
                (
                    triage.handoff_id,
                    handoff_data.get("machine", "unknown"),
                    handoff_data.get("goal", ""),
                    triage.task_type,
                    triage.action,
                    1 if triage.requires_harness_wake else 0,
                    triage.confidence,
                    triage.lag_seconds,
                    exec_res.get("status", "triaged") if exec_res else "triaged",
                    json.dumps(exec_res) if exec_res else None,
                    handoff_data.get("created_utc", now_str),
                    now_str,
                ),
            )
            if triage.is_lagging:
                conn.execute(
                    """
                    INSERT INTO lag_alerts (handoff_id, lag_seconds, threshold_seconds, detected_utc)
                    VALUES (?, ?, ?, ?)
                """,
                    (triage.handoff_id, triage.lag_seconds, self.lag_threshold_sec, now_str),
                )
            conn.commit()

    def _superseding_relay_ids(
        self, handoff_id: str, created_utc: Optional[str]
    ) -> List[str]:
        """Return later correction legs that explicitly name ``handoff_id``.

        A relay can arrive late or be auto-captured long after its author has
        retracted it.  Do not infer supersession from timestamps alone: require
        both a correction marker and an exact source-leg reference.  Unknown or
        malformed records are ignored rather than blocking a capture.
        """
        if not handoff_id:
            return []
        corrections = re.compile(
            r"\b(?:correct(?:ion|ed|ing)?|retract(?:ion|ed|ing)?|"
            r"withdraw(?:al|n|ing)?|supersed(?:e|ed|ing)|amend(?:ed|ment|ing)?)\b",
            re.IGNORECASE,
        )
        matches: List[str] = []
        handoffs_dir = self.relay_dir / ".handoffs"
        for path in handoffs_dir.glob("*.json"):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            candidate_id = str(record.get("id") or path.stem)
            if candidate_id == handoff_id:
                continue
            candidate_created = str(record.get("created_utc") or "")
            if created_utc and candidate_created and candidate_created <= created_utc:
                continue
            text = "\n".join(
                str(record.get(field) or "") for field in ("goal", "body", "message")
            )
            if handoff_id in text and corrections.search(text):
                matches.append(candidate_id)
        return sorted(matches)

    def auto_capture_shard(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        *,
        handoff_id: Optional[str] = None,
        created_utc: Optional[str] = None,
    ) -> bool:
        """Autonomously captures a durable milestone memory shard into the NouGen vault."""
        superseded_by = self._superseding_relay_ids(handoff_id or "", created_utc)
        if superseded_by:
            print(
                "[RelayDaemon] refusing stale auto-shard "
                f"{handoff_id}; corrected by {', '.join(superseded_by)}"
            )
            return False
        try:
            shards_src = _resolve_shards_src()
            if shards_src and str(shards_src) not in sys.path:
                sys.path.insert(0, str(shards_src))
            from nougen_shards.core import capture
            tag_list = list(tags or [])
            if "daemon" not in tag_list:
                tag_list.append("daemon")
            if "relay" not in tag_list:
                tag_list.append("relay")
            # The shards capture() signature drifts under other lanes (e.g. the
            # 2026-08-28 vector-graph rework crashed a stale daemon with an
            # unexpected-kwarg TypeError). Pass only kwargs the live signature
            # accepts and log what gets dropped, so this daemon survives drift
            # in either direction.
            import inspect as _inspect
            wanted = {
                "event_type": "DAEMON_AUTO_SHARD",
                "title": title,
                "content": content,
                "source_uri": f"relay_daemon://{self.machine_name}",
                "tags": tag_list,
                "utility": 0.9,
            }
            params = _inspect.signature(capture).parameters
            accepts_var_kw = any(p.kind is _inspect.Parameter.VAR_KEYWORD for p in params.values())
            kwargs = wanted if accepts_var_kw else {k: v for k, v in wanted.items() if k in params}
            dropped = set(wanted) - set(kwargs)
            if dropped:
                print(f"[RelayDaemon] note: capture() no longer accepts {sorted(dropped)}; dropped")
            return capture(**kwargs)
        except Exception as e:
            print(f"[RelayDaemon] ⚠️ Auto-shard capture error: {e}")
            return False

    def run_cycle(self, dry_run: bool = False) -> Dict[str, Any]:
        """Executes a single heartbeat and inspection cycle."""
        self.pulse_counter += 1
        now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 1. Probe local Ollama
        is_alive, latency_ms, models = self.check_ollama_health()
        ollama_status = "healthy" if is_alive else "unreachable"

        # 2. Sync the clone, then scan open handoffs -- without the pull this
        # daemon watched a four-day-old snapshot and never saw a new leg.
        self.sync_relay_repo()
        reconciled = 0 if dry_run else self.reconcile_verified_acks()
        if not dry_run:
            self._sweep_leases()
        open_handoffs = self.get_open_handoffs()
        lag_alerts = []
        triage_reports = []

        # 3. Triage FRESH legs only (newest first): re-triaging the same three
        # forever was the second reason nothing ever happened. Dispatch is
        # capped per cycle so a burst of legs cannot fan out in parallel.
        fresh = self._ready_handoffs(open_handoffs)
        dispatched = 0
        fleet_answered = 0
        for h in fresh:
            handoff_id = str(h.get("id") or "").strip()
            lease = None
            if not dry_run:
                if acquire_lease is None or release_lease is None:
                    print("[RelayDaemon] WARN lease primitives unavailable; dispatch skipped")
                    break
                # admission BEFORE acquisition: deterministic, evidence-only
                verdict, why = self._admit(h)
                if verdict != "ALLOW":
                    print(f"[RelayDaemon] admit {verdict} {handoff_id}: {why}")
                    continue
                lease = acquire_lease(
                    self.relay_dir,
                    handoff_id,
                    machine=self.machine_name,
                    agent=DAEMON_AGENT,
                    goal=str(h.get("goal") or ""),
                )
                if lease is None:
                    continue
                self._lease_tokens[handoff_id] = lease.get("fencing_token")
                if not self.claim_leg_upstream(h, lease):
                    self._release(handoff_id, "released", "upstream claim refused")
                    continue

            triage = self.triage_with_ollama(h)
            if triage.is_lagging:
                lag_alerts.append({
                    "handoff_id": triage.handoff_id,
                    "lag_seconds": triage.lag_seconds,
                })

            # Two lanes (local-first doctrine): execution goes to the harness,
            # everything answerable goes to the free local fleet. Both feed the
            # same self-verify -> ack-upstream path so the open count falls.
            exec_res = None
            if triage.requires_harness_wake and dispatched < DISPATCH_PER_CYCLE:
                exec_res = self.dispatch_execution(triage, dry_run=dry_run)
                dispatched += 1
            elif (not triage.requires_harness_wake
                  and fleet_answered < FLEET_PER_CYCLE and not dry_run):
                exec_res = self.fleet_respond(h, triage)
                fleet_answered += 1
            if exec_res is None and not dry_run:
                # Capacity was exhausted after triage. Do not burn the id into
                # the seen ledger; release it for the next cycle.
                self._release(handoff_id, "released", "deferred: capacity exhausted after triage")
                self.release_upstream_claim(handoff_id, "deferred")
                continue
            if exec_res is not None and not dry_run:
                verdict = self.dav1d_probe_verify(triage, h, exec_res)
                exec_res["verified"] = verdict["verified"]
                exec_res["verify_evidence"] = verdict["evidence"]
                if verdict["verified"]:
                    exec_res["acked_upstream"] = self.ack_leg_upstream(
                        triage.handoff_id, verdict["evidence"])
                    self._release(handoff_id, "complete", str(verdict["evidence"])[:200])
                    if exec_res["acked_upstream"]:
                        self.release_upstream_claim(
                            handoff_id, "complete", verdict["evidence"]
                        )
                    self.auto_capture_shard(
                        title=f"Autonomous Verified Relay: {triage.handoff_id}",
                        content=f"Handoff {triage.handoff_id} verified ({verdict['evidence']}). Goal: {h.get('goal', '')}",
                        tags=["verified_execution", "fleet", triage.task_type],
                        handoff_id=triage.handoff_id,
                        created_utc=str(h.get("created_utc") or ""),
                    )
                else:
                    failure = verdict["evidence"] or str(
                        exec_res.get("stderr")
                        or exec_res.get("message")
                        or "execution was not verified"
                    )
                    if record_leg_failure is not None:
                        try:
                            retry = record_leg_failure(
                                self.relay_dir, handoff_id, failure,
                                fencing_token=self._lease_tokens.get(handoff_id),
                            )
                        except TypeError:  # older core / test double without fencing
                            retry = record_leg_failure(self.relay_dir, handoff_id, failure)
                        if retry.get("rejected"):
                            print(f"[RelayDaemon] FENCED failure write for {handoff_id}: {retry.get('reason')}")
                        exec_res["retry_status"] = retry.get("status")
                        exec_res["retry_count"] = retry.get("retry_count")
                        self.release_upstream_claim(
                            handoff_id,
                            str(retry.get("status") or "failed"),
                            failure,
                        )
                    else:
                        self._release(handoff_id, "failed", failure[:200])
                        self.release_upstream_claim(handoff_id, "failed", failure)

            if not dry_run:
                self.record_triage(h, triage, exec_res)
            triage_reports.append({
                "triage": asdict(triage),
                "execution": exec_res,
            })

        # 4. Record pulse
        pulse = HeartbeatPulse(
            pulse_id=self.pulse_counter,
            timestamp_utc=now_utc,
            ollama_status=ollama_status,
            ollama_latency_ms=latency_ms,
            loaded_models=models,
            open_handoffs_count=len(open_handoffs),
            lag_alerts_count=len(lag_alerts),
            status="ok" if is_alive else "degraded",
        )
        self.record_pulse(pulse)

        return {
            "pulse": asdict(pulse),
            "open_handoffs_count": len(open_handoffs),
            "lag_alerts": lag_alerts,
            "reconciled_count": reconciled,
            "triaged_count": len(triage_reports),
            "triages": triage_reports,
        }

    def start_loop(self, dry_run: bool = False) -> None:
        """Starts the infinite daemon loop with heartbeat_sec intervals."""
        self.is_running = True
        print(f"[RelayDaemon] 🛡️ Starting Self-Healing Daemon Loop on {self.machine_name}")
        print(f"[RelayDaemon] ⏱️ Cadence: {self.heartbeat_sec}s | Model: {self.model_name} | Lag Threshold: {self.lag_threshold_sec}s")
        print(f"[RelayDaemon] 📂 Watching: {self.handoffs_dir}")

        while self.is_running:
            try:
                cycle_summary = self.run_cycle(dry_run=dry_run)
                pulse_dict = cycle_summary["pulse"]
                pulse_obj = HeartbeatPulse(**pulse_dict)
                RelayRaceHUD.render_race_card(self, pulse_obj, cycle_summary)
            except KeyboardInterrupt:
                print("\n[RelayDaemon] 🛑 Shutting down gracefully...")
                self.is_running = False
                break
            except Exception as e:
                print(f"[RelayDaemon] ⚠️ Cycle error (self-healing): {e}")

            time.sleep(self.heartbeat_sec)

    def get_status_report(self) -> Dict[str, Any]:
        """Queries recent pulses, lag alerts, and triage events for high-fidelity reporting."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            recent_pulses = [
                dict(r) for r in conn.execute("SELECT * FROM daemon_pulses ORDER BY id DESC LIMIT 5").fetchall()
            ]
            recent_triages = [
                dict(r) for r in conn.execute("SELECT * FROM triage_events ORDER BY id DESC LIMIT 5").fetchall()
            ]
            recent_lags = [
                dict(r) for r in conn.execute("SELECT * FROM lag_alerts ORDER BY id DESC LIMIT 5").fetchall()
            ]

        is_alive, latency_ms, models = self.check_ollama_health()
        return {
            "daemon_live_check": {
                "ollama_alive": is_alive,
                "latency_ms": latency_ms,
                "models": models,
            },
            "recent_pulses": recent_pulses,
            "recent_triages": recent_triages,
            "recent_lag_alerts": recent_lags,
            "db_path": str(self.db_path),
        }


def main():
    parser = argparse.ArgumentParser(description="NouGenAi Self-Healing Relay Daemon")
    parser.add_argument("--once", action="store_true", help="Run a single heartbeat/triage cycle and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuous loop")
    parser.add_argument("--dry-run", action="store_true", help="Triage without executing live mutations")
    parser.add_argument("--status", action="store_true", help="Print live daemon telemetry and recent pulses")
    parser.add_argument("--heartbeat-sec", type=int, default=DEFAULT_HEARTBEAT_SEC, help=f"Heartbeat interval (default: {DEFAULT_HEARTBEAT_SEC}s)")
    parser.add_argument("--lag-threshold-sec", type=int, default=DEFAULT_LAG_THRESHOLD_SEC, help=f"Lag alert threshold (default: {DEFAULT_LAG_THRESHOLD_SEC}s)")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"Ollama model (default: {DEFAULT_MODEL})")
    parser.add_argument("--lock-file", type=str, default=None, help="Singleton lock path (default: alongside the state DB)")
    parser.add_argument("--force", action="store_true", help="Start even if another daemon holds the lock (NOT recommended)")
    args = parser.parse_args()

    daemon = RelayDaemon(
        heartbeat_sec=args.heartbeat_sec,
        lag_threshold_sec=args.lag_threshold_sec,
        model_name=args.model,
    )

    if args.status:
        report = daemon.get_status_report()
        print(json.dumps(report, indent=2))
        return

    if args.once:
        res = daemon.run_cycle(dry_run=args.dry_run)
        print(json.dumps(res, indent=2))
        return

    # Default to daemon loop -- one live daemon per state DB.
    lock_path = Path(args.lock_file) if args.lock_file else daemon.db_path.with_suffix(".lock")
    lock = SingletonLock(lock_path)
    if not lock.acquire() and not args.force:
        print(
            f"[RelayDaemon] another daemon is already running (pid {lock.holder_pid}, lock {lock_path}). "
            "Use --status to inspect it, or --force to override."
        )
        sys.exit(3)

    daemon.start_loop(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
