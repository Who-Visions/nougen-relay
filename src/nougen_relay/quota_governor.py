"""Quota Governor: Economics layer for autonomous fleet execution.

Implements the three-layer Jarvis Mode architecture:
  Layer 1: Fleet Execution Law (ghost worker detection, orphan work detection)
  Layer 2: Quota Governor (SOFT/HARD/RESERVE thresholds, burn velocity, ledger)
  Layer 3: Jarvis Mode (adaptive routing, preserve autonomy, expose economics)

Ground truth calibration from the 40.5h Phoebus marathon (2026-09-04/06):
  - 3,428,792,775 total context tokens moved
  - 99.96% cache hit ratio
  - 1,352,838 fresh input + 537,826 output = 1,890,664 billable
  - 3,130 tool calls over 40.5 hours
  - Shadow cost: $64.52 (Flash) / $1,075.29 (Pro)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path as _Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Marathon calibration constants (ground truth from 40.5h session)
# ---------------------------------------------------------------------------

MARATHON_CALIBRATION = {
    "session_id": "2a2461da-c74e-43fa-884d-ad5f4da18da7",
    "duration_hours": 40.5,
    "total_steps": 7816,
    "user_turns": 40,
    "model_invocations": 3606,
    "tool_calls": 3130,
    "fresh_input_tokens": 1_352_838,
    "output_tokens": 537_826,
    "cache_read_tokens": 3_426_902_111,
    "total_context_tokens": 3_428_792_775,
    "cache_hit_ratio": 0.9996,
    "billable_tokens": 1_890_664,
    "shadow_cost_flash_usd": 64.52,
    "shadow_cost_pro_usd": 1075.29,
    # Derived rates
    "tokens_per_hour_total": 84_660_315,
    "tokens_per_hour_billable": 46_683,
    "tool_calls_per_hour": 77.3,
    "tokens_per_1k_tool_calls": 604_000,
    "tokens_per_model_invocation": 524,
    "cost_per_hour_flash_usd": 1.59,
    "cost_per_hour_pro_usd": 26.55,
    "artifacts_landed": 5,
    "tokens_per_landing": 378_133,
}


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RoutingDecision(Enum):
    """What the governor recommends for the next claim."""
    CLOUD_FULL = "cloud_full"       # Full cloud reasoning (Pro/Flash)
    CLOUD_LITE = "cloud_lite"       # Downshift to cheaper model tier
    LOCAL_ONLY = "local_only"       # Local/free execution only
    RESERVE_HOLD = "reserve_hold"   # Quota reserved for interactive GM sessions
    BLOCKED = "blocked"             # Cannot proceed at all


class GhostStatus(Enum):
    """Ghost worker classification."""
    CLEAN = "clean"                 # Session has active claim matching its work
    GHOST = "ghost"                 # Active session, zero registered claims
    ORPHAN = "orphan"               # Evidence/commits exist for a leg with no claim


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class QuotaThresholds:
    """User-configurable thresholds as fraction of total budget.

    Semantic: autonomous work is GOOD. Surprise depletion is the bug.
    These thresholds preserve autonomy while adding visibility.
    """
    soft: float = 0.70     # 70% used -> downshift to cheaper models
    hard: float = 0.90     # 90% used -> stop claiming cloud legs
    reserve: float = 0.10  # 10% always held back for interactive GM sessions


@dataclass
class QuotaSnapshot:
    """Point-in-time quota state for a provider."""
    provider: str
    timestamp: str
    tokens_used: int = 0
    tokens_limit: int = 0       # 0 = unlimited (local/free)
    cost_used_usd: float = 0.0
    budget_usd: float = 0.0     # 0 = no budget cap set
    weekly_limit_pct_remaining: Optional[float] = None     # e.g., 10.0% means 90% used (HARD BREACH)
    five_hour_limit_pct_remaining: Optional[float] = None  # e.g., 30.0% means 70% used

    @property
    def utilization(self) -> float:
        if self.tokens_limit <= 0:
            return 0.0
        return min(1.0, self.tokens_used / self.tokens_limit)

    @property
    def cost_utilization(self) -> float:
        if self.budget_usd <= 0:
            return 0.0
        return min(1.0, self.cost_used_usd / self.budget_usd)

    @property
    def effective_utilization(self) -> float:
        """Whichever limit is closer to breach across tokens, cost, and short/weekly windows."""
        util = max(self.utilization, self.cost_utilization)
        if self.weekly_limit_pct_remaining is not None:
            # e.g. 10% remaining means 90% utilized
            weekly_util = max(0.0, min(1.0, (100.0 - self.weekly_limit_pct_remaining) / 100.0))
            util = max(util, weekly_util)
        if self.five_hour_limit_pct_remaining is not None:
            five_hour_util = max(0.0, min(1.0, (100.0 - self.five_hour_limit_pct_remaining) / 100.0))
            util = max(util, five_hour_util)
        return util

    @property
    def is_local(self) -> bool:
        return self.provider in ("local", "ollama", "gemma")


@dataclass
class BurnRecord:
    """One leg\'s token consumption."""
    leg_id: str
    claim_id: str
    provider: str
    tokens_in: int
    tokens_out: int
    cache_reads: int
    cost_usd: float
    artifacts_verified: int
    duration_seconds: float
    timestamp: str


@dataclass
class BurnLedger:
    """Rolling ledger of token burn per leg with velocity computation."""
    records: List[BurnRecord] = field(default_factory=list)
    window_hours: int = 24

    def record(self, rec: BurnRecord) -> None:
        self.records.append(rec)

    def _windowed(self) -> List[BurnRecord]:
        if not self.records:
            return []
        cutoff = datetime.now(timezone.utc).timestamp() - (self.window_hours * 3600)
        out = []
        for r in self.records:
            try:
                ts = datetime.fromisoformat(r.timestamp).timestamp()
                if ts >= cutoff:
                    out.append(r)
            except Exception:
                out.append(r)
        return out

    def velocity(self) -> Dict[str, float]:
        """Compute rolling burn velocity over the window."""
        windowed = self._windowed()
        if not windowed:
            return {
                "tokens_per_hour": 0.0,
                "cost_per_hour": 0.0,
                "legs_per_hour": 0.0,
                "artifacts_per_hour": 0.0,
            }

        total_tokens = sum(r.tokens_in + r.tokens_out for r in windowed)
        total_cost = sum(r.cost_usd for r in windowed)
        total_artifacts = sum(r.artifacts_verified for r in windowed)
        total_duration = sum(r.duration_seconds for r in windowed)
        hours = max(0.001, total_duration / 3600.0)

        return {
            "tokens_per_hour": round(total_tokens / hours, 1),
            "cost_per_hour": round(total_cost / hours, 4),
            "legs_per_hour": round(len(windowed) / hours, 2),
            "artifacts_per_hour": round(total_artifacts / hours, 2),
        }

    def cost_per_leg(self) -> float:
        if not self.records:
            return 0.0
        return round(sum(r.cost_usd for r in self.records) / len(self.records), 4)

    def cost_per_artifact(self) -> float:
        total_artifacts = sum(r.artifacts_verified for r in self.records)
        if total_artifacts == 0:
            return 0.0
        return round(sum(r.cost_usd for r in self.records) / total_artifacts, 4)

    def tokens_per_1k_tools(self) -> float:
        """Estimate from marathon calibration or ledger data."""
        windowed = self._windowed()
        if not windowed:
            return float(MARATHON_CALIBRATION["tokens_per_1k_tool_calls"])
        total_tokens = sum(r.tokens_in + r.tokens_out for r in windowed)
        # Approximate tool calls from legs (each leg ~ 77.3 tool calls/hour)
        total_hours = sum(r.duration_seconds for r in windowed) / 3600.0
        est_tools = total_hours * MARATHON_CALIBRATION["tool_calls_per_hour"]
        if est_tools < 1:
            return float(MARATHON_CALIBRATION["tokens_per_1k_tool_calls"])
        return round((total_tokens / est_tools) * 1000, 0)


# ---------------------------------------------------------------------------
# Ghost Worker Detector (Fleet Execution Law)
# ---------------------------------------------------------------------------

@dataclass
class GhostWorkerReport:
    """Result of ghost worker analysis."""
    machine: str
    agent: str
    session: str
    status: GhostStatus
    active_claims: int
    detail: str


def detect_ghost_workers(
    active_sessions: List[Dict[str, Any]],
    active_claims: List[Dict[str, Any]],
    threshold_minutes: float = 30.0,
) -> List[GhostWorkerReport]:
    """Detect active sessions with no registered claims.

    Fleet Execution Law invariants:
      1. Session/process/provider activity != ownership
      2. ONLY an explicit live claim reserves a leg/scope
      3. Scheduler should continue assigning work while one provider marathons
    """
    reports = []
    for session in active_sessions:
        s_machine = (session.get("machine") or "").lower()
        s_agent = (session.get("agent") or "").lower()
        s_id = session.get("session_id") or session.get("id") or ""

        matching_claims = [
            c for c in active_claims
            if (c.get("machine") or "").lower() == s_machine
            and (c.get("agent") or "").lower() == s_agent
        ]

        if not matching_claims:
            reports.append(GhostWorkerReport(
                machine=s_machine,
                agent=s_agent,
                session=s_id,
                status=GhostStatus.GHOST,
                active_claims=0,
                detail=f"Active session on {s_machine}/{s_agent} with ZERO registered claims. ",
            ))
        else:
            reports.append(GhostWorkerReport(
                machine=s_machine,
                agent=s_agent,
                session=s_id,
                status=GhostStatus.CLEAN,
                active_claims=len(matching_claims),
                detail=f"{len(matching_claims)} active claim(s) registered.",
            ))

    return reports


# ---------------------------------------------------------------------------
# Orphan Work Detector
# ---------------------------------------------------------------------------

def detect_orphan_work(
    recent_evidence: List[Dict[str, Any]],
    active_claims: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Detect commits/evidence for relay legs without corresponding claims.

    An orphan is evidence (commit, file, artifact) that references a leg ID
    but no active claim covers that leg.
    """
    claimed_scopes = set()
    for c in active_claims:
        scope = (c.get("scope") or "").lower()
        claimed_scopes.add(scope)
        # Also extract leg IDs from scope
        for token in scope.split():
            if token.startswith("relay:"):
                claimed_scopes.add(token.replace("relay:", ""))

    orphans = []
    for ev in recent_evidence:
        leg_ref = (ev.get("leg_id") or ev.get("ref") or "").lower()
        if leg_ref and leg_ref not in claimed_scopes:
            # Check if any claim scope contains this leg reference
            covered = any(leg_ref in s for s in claimed_scopes)
            if not covered:
                orphans.append({
                    "leg_id": leg_ref,
                    "evidence_type": ev.get("type", "unknown"),
                    "detail": ev.get("detail", ""),
                    "machine": ev.get("machine", ""),
                    "timestamp": ev.get("timestamp", ""),
                })

    return orphans


# ---------------------------------------------------------------------------
# Quota Governor
# ---------------------------------------------------------------------------

class QuotaGovernor:
    """Governs quota burn across the fleet.

    Core semantic: autonomous work is GOOD. Surprise depletion is the bug.
    The governor preserves autonomy and adds economics.

    Integration points:
      - Gates claim_engine.schedule_best_leg() with quota checks
      - Exposes burn velocity to Claim Engine scoring
      - Projects threshold breach timing from marathon calibration
      - Never kills productive local/Ollama work for cloud quota exhaustion
    """

    def __init__(
        self,
        thresholds: Optional[QuotaThresholds] = None,
        ledger: Optional[BurnLedger] = None,
    ):
        self.thresholds = thresholds or QuotaThresholds()
        self.ledger = ledger or BurnLedger()

    def evaluate(self, snapshot: QuotaSnapshot) -> RoutingDecision:
        """Returns routing decision based on current quota state.

        Never kills productive local work. Only governs cloud routing.
        """
        if snapshot.is_local:
            return RoutingDecision.CLOUD_FULL  # Local is always green

        util = snapshot.effective_utilization

        if util < self.thresholds.soft:
            return RoutingDecision.CLOUD_FULL
        elif util < self.thresholds.hard:
            return RoutingDecision.CLOUD_LITE
        elif util <= (1.0 - self.thresholds.reserve):
            return RoutingDecision.LOCAL_ONLY
        else:
            return RoutingDecision.RESERVE_HOLD

    def gate_claim(
        self,
        leg: Dict[str, Any],
        snapshot: QuotaSnapshot,
    ) -> Tuple[bool, str, RoutingDecision]:
        """Should this leg be claimed given current quota?

        Returns (allowed, reason, decision).
        """
        decision = self.evaluate(snapshot)

        if decision == RoutingDecision.RESERVE_HOLD:
            return False, "RESERVE: quota reserved for interactive GM sessions", decision

        if decision == RoutingDecision.LOCAL_ONLY:
            requires_cloud = leg.get("requires_cloud", False)
            provider = (leg.get("provider") or "").lower()
            if requires_cloud or provider in ("google", "anthropic", "openai"):
                return False, "HARD: cloud quota exhausted, leg requires cloud provider", decision
            return True, "LOCAL_ONLY: proceeding with local/free execution", decision

        if decision == RoutingDecision.CLOUD_LITE:
            return True, "SOFT: downshifted to cheaper model tier", decision

        return True, "OK: full cloud reasoning available", decision

    def project_breach(self, snapshot: QuotaSnapshot) -> Dict[str, Any]:
        """Project when thresholds will be breached at current velocity.

        Uses marathon calibration as fallback when ledger has insufficient data.
        """
        vel = self.ledger.velocity()
        cost_per_hour = vel["cost_per_hour"] or MARATHON_CALIBRATION["cost_per_hour_flash_usd"]

        if snapshot.budget_usd <= 0 or cost_per_hour <= 0:
            return {
                "soft_breach_hours": None,
                "hard_breach_hours": None,
                "reserve_breach_hours": None,
                "exhaustion_hours": None,
                "burn_rate_usd_per_hour": cost_per_hour,
            }

        remaining = snapshot.budget_usd - snapshot.cost_used_usd
        util = snapshot.cost_utilization

        def hours_to(threshold: float) -> Optional[float]:
            target_cost = threshold * snapshot.budget_usd
            delta = target_cost - snapshot.cost_used_usd
            if delta <= 0:
                return 0.0
            return round(delta / cost_per_hour, 2)

        return {
            "soft_breach_hours": hours_to(self.thresholds.soft),
            "hard_breach_hours": hours_to(self.thresholds.hard),
            "reserve_breach_hours": hours_to(1.0 - self.thresholds.reserve),
            "exhaustion_hours": round(remaining / cost_per_hour, 2) if remaining > 0 else 0.0,
            "burn_rate_usd_per_hour": cost_per_hour,
            "remaining_usd": round(remaining, 2),
            "current_utilization": round(util, 4),
        }

    def status_report(self, snapshot: QuotaSnapshot) -> Dict[str, Any]:
        """Full status for CLI display."""
        decision = self.evaluate(snapshot)
        breach = self.project_breach(snapshot)
        vel = self.ledger.velocity()

        return {
            "provider": snapshot.provider,
            "routing_decision": decision.value,
            "utilization": round(snapshot.effective_utilization, 4),
            "thresholds": {
                "soft": self.thresholds.soft,
                "hard": self.thresholds.hard,
                "reserve": self.thresholds.reserve,
            },
            "velocity": vel,
            "breach_projection": breach,
            "is_local": snapshot.is_local,
            "ledger_records": len(self.ledger.records),
        }


# ---------------------------------------------------------------------------
# CLI formatting helpers
# ---------------------------------------------------------------------------

def format_quota_status(report: Dict[str, Any]) -> str:
    """Human-readable quota status card."""
    lines = []
    decision = report["routing_decision"]
    util = report["utilization"]
    provider = report["provider"]

    # Status icon
    icon = {
        "cloud_full": "🟢",
        "cloud_lite": "🟡",
        "local_only": "🟠",
        "reserve_hold": "🔴",
        "blocked": "⛔",
    }.get(decision, "⚪")

    lines.append(f"{icon} QUOTA GOVERNOR — {provider.upper()}")
    lines.append(f"   Routing: {decision} | Utilization: {util:.1%}")

    th = report["thresholds"]
    lines.append(f"   Thresholds: SOFT={th['soft']:.0%} | HARD={th['hard']:.0%} | RESERVE={th['reserve']:.0%}")

    vel = report["velocity"]
    if vel["tokens_per_hour"] > 0:
        lines.append(f"   Burn rate: {vel['tokens_per_hour']:,.0f} tok/hr | ${vel['cost_per_hour']:.2f}/hr | {vel['legs_per_hour']:.1f} legs/hr")

    bp = report["breach_projection"]
    if bp.get("exhaustion_hours") is not None:
        lines.append(f"   Breach ETA: SOFT={bp.get('soft_breach_hours', '—')}h | HARD={bp.get('hard_breach_hours', '—')}h | Empty={bp['exhaustion_hours']}h")
        lines.append(f"   Remaining: ${bp.get('remaining_usd', 0):.2f} at ${bp['burn_rate_usd_per_hour']:.2f}/hr")

    if report["is_local"]:
        lines.append("   ⚡ Local provider — unlimited, zero cloud cost")

    lines.append(f"   Ledger: {report['ledger_records']} records in window")
    return "\n".join(lines)


def format_ghost_report(reports: List[GhostWorkerReport]) -> str:
    """Human-readable ghost worker report."""
    if not reports:
        return "✅ No active sessions detected."

    lines = []
    ghosts = [r for r in reports if r.status == GhostStatus.GHOST]
    clean = [r for r in reports if r.status == GhostStatus.CLEAN]

    if ghosts:
        lines.append(f"👻 GHOST WORKERS DETECTED: {len(ghosts)}")
        for g in ghosts:
            lines.append(f"   ⚠️ {g.machine}/{g.agent} — {g.detail}")
    else:
        lines.append("✅ No ghost workers.")

    if clean:
        lines.append(f"   ✅ {len(clean)} session(s) with valid claims.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def load_thresholds_from_env() -> QuotaThresholds:
    """Load thresholds from environment or use defaults."""
    return QuotaThresholds(
        soft=float(os.environ.get("NOUGEN_QUOTA_SOFT", "0.70")),
        hard=float(os.environ.get("NOUGEN_QUOTA_HARD", "0.90")),
        reserve=float(os.environ.get("NOUGEN_QUOTA_RESERVE", "0.10")),
    )


def load_snapshot_from_env() -> QuotaSnapshot:
    """Build a snapshot from environment variables or tracker data."""
    provider = os.environ.get("NOUGEN_PROVIDER", "local")
    return QuotaSnapshot(
        provider=provider,
        timestamp=datetime.now(timezone.utc).isoformat(),
        tokens_used=int(os.environ.get("NOUGEN_TOKENS_USED", "0")),
        tokens_limit=int(os.environ.get("NOUGEN_TOKENS_LIMIT", "0")),
        cost_used_usd=float(os.environ.get("NOUGEN_COST_USED", "0.0")),
        budget_usd=float(os.environ.get("NOUGEN_BUDGET_USD", "0.0")),
    )


def load_ledger_from_file(path: _Path) -> BurnLedger:
    """Load a burn ledger from a JSON file."""
    ledger = BurnLedger()
    if not path.is_file():
        return ledger
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for rec in data.get("records", []):
            ledger.record(BurnRecord(**rec))
    except Exception:
        pass
    return ledger


def save_ledger_to_file(ledger: BurnLedger, path: _Path) -> None:
    """Persist a burn ledger to JSON."""
    from .core import write_record
    data = {"records": [asdict(r) for r in ledger.records]}
    write_record(path, data)
