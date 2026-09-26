"""Claim Engine: Convert relay from passive inbox into an active work scheduler.

Implements the Fleet Execution Law:
- Message types: ACTIONABLE, INFO, BLOCKER, RESULT
- Concrete capability vector: repos, runtime, tools, provider, machine, write_access, test_access, network_access
- Exact claim scoring formula:
  score = 5*unblocks_others + 4*gm_priority + 3*finishable_now + 2*machine_locality + 2*verification_value + 1*token_efficiency - 5*claim_conflict - 3*destructive_risk - 2*staleness_without_relevance
- Token-to-action & efficiency math (TTA, CTA, coordination_tax_ratio, evidence_yield)
- Mandatory work selection and idle invariant enforcement
"""

from __future__ import annotations

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Re-use core primitives from nougen_relay
from . import core

# Message Types
TYPE_ACTIONABLE = "ACTIONABLE"
TYPE_INFO = "INFO"
TYPE_BLOCKER = "BLOCKER"
TYPE_RESULT = "RESULT"

VALID_MESSAGE_TYPES = {TYPE_ACTIONABLE, TYPE_INFO, TYPE_BLOCKER, TYPE_RESULT}


def infer_message_type(record: dict) -> str:
    """Classify a relay leg into ACTIONABLE, INFO, BLOCKER, or RESULT.

    Default is ACTIONABLE for new work handoffs unless explicitly tagged or
    identified as status/info/result.
    """
    raw_type = (record.get("message_type") or record.get("type") or "").strip().upper()
    if raw_type in VALID_MESSAGE_TYPES:
        return raw_type

    status = (record.get("status") or "").strip().lower()
    if status in ("complete", "abandoned"):
        return TYPE_RESULT
    if status in ("blocked", "dead_letter"):
        return TYPE_BLOCKER

    goal = (record.get("goal") or "").lower()
    tags = [str(t).lower() for t in (record.get("tags") or [])]

    if "info" in tags or "informational" in tags or goal.startswith("info:") or goal.startswith("fyi:"):
        return TYPE_INFO
    if "blocker" in tags or goal.startswith("blocker:") or "blocked" in goal:
        return TYPE_BLOCKER
    if "result" in tags or goal.startswith("result:") or goal.startswith("touchdown:"):
        return TYPE_RESULT

    return TYPE_ACTIONABLE


def machine_capabilities(root: Optional[Path] = None) -> Dict[str, Any]:
    """Extract a concrete machine capability vector from environment and local probes."""
    root = root or core.repo_root()
    machine = core.resolve_machine()
    agent = core.resolve_agent()

    repos: List[str] = []
    if root is not None:
        parent = root.parent
        if parent.is_dir():
            for p in parent.iterdir():
                if p.is_dir() and (p / ".git").exists():
                    repos.append(p.name)
        if root.name not in repos:
            repos.append(root.name)

    runtime = f"python{sys.version_info.major}.{sys.version_info.minor}"
    provider = os.environ.get("NOUGEN_PROVIDER") or ("google" if "gemini" in agent else ("anthropic" if "claude" in agent else "local"))

    tools: Set[str] = set()
    for tool_name in ("git", "gh", "python3", "bun", "ollama", "docker", "curl"):
        if shutil.which(tool_name):
            tools.add(tool_name)

    write_access = True
    if root is not None and not os.access(str(root), os.W_OK):
        write_access = False

    test_access = False
    if root is not None and ((root / "tests").is_dir() or (root / "test").is_dir()):
        test_access = True

    network_access = bool(os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY") or True)

    return {
        "machine": machine,
        "agent": agent,
        "repos": sorted(repos),
        "runtime": runtime,
        "provider": provider,
        "tools": sorted(list(tools)),
        "write_access": write_access,
        "test_access": test_access,
        "network_access": network_access,
    }


def compute_claim_score(
    leg: dict,
    capabilities: Dict[str, Any],
    active_claims: Optional[List[dict]] = None,
    now_dt: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Compute exact claim score per Fleet Execution Law:

    score = 5*unblocks_others + 4*gm_priority + 3*finishable_now + 2*machine_locality
            + 2*verification_value + 1*token_efficiency - 5*claim_conflict
            - 3*destructive_risk - 2*staleness_without_relevance
    """
    now = now_dt or core._now()
    leg_id = core.record_id(leg) or leg.get("_file", "")
    goal = (leg.get("goal") or "").lower()
    leg_machine = (leg.get("machine") or "").lower()

    unblocks_others = 1.0 if any(k in goal for k in ("unblock", "deadlock", "ceiling", "scheduler", "core", "critical")) else 0.0
    gm_priority = 1.0 if any(k in goal for k in ("gm", "directive", "hadouken", "rule 0.", "prime directive", "priority")) else 0.0

    finishable_now = 1.0
    if not capabilities.get("write_access", False):
        finishable_now = 0.0

    target = (leg.get("target_agent") or leg.get("target_lane") or "").strip().lower()
    if target and target not in capabilities.get("agent", "").lower() and capabilities.get("agent", "").lower() not in target:
        finishable_now = 0.0

    my_machine = capabilities.get("machine", "").lower()
    machine_locality = 1.0 if (leg_machine == my_machine or not leg_machine) else 0.0

    verification_value = 1.0 if any(k in goal for k in ("test", "verify", "benchmark", "prove", "check")) else 0.5
    token_efficiency = float(leg.get("execution_efficiency", 1.0))

    claim_conflict = 0.0
    if active_claims:
        for c in active_claims:
            c_scope = str(c.get("scope", "")).lower()
            c_mach = str(c.get("machine", "")).lower()
            c_agent = str(c.get("agent", "")).lower()
            if (c_mach != my_machine or c_agent != capabilities.get("agent", "").lower()) and core.claim_is_active(c):
                if leg_id in c_scope or (goal and c_scope and core._scopes_overlap(goal, c_scope)):
                    claim_conflict = 1.0
                    break

    destructive_risk = 1.0 if any(k in goal for k in ("drop", "delete", "purge", "rm -rf", "force-push", "reset --hard")) else 0.0

    created_str = leg.get("created_utc") or ""
    staleness = 0.0
    if created_str:
        try:
            created_dt = datetime.fromisoformat(created_str)
            age_hours = (now - created_dt).total_seconds() / 3600.0
            if age_hours > 72.0 and not gm_priority:
                staleness = 1.0
        except Exception:
            pass

    score = (
        5.0 * unblocks_others
        + 4.0 * gm_priority
        + 3.0 * finishable_now
        + 2.0 * machine_locality
        + 2.0 * verification_value
        + 1.0 * token_efficiency
        - 5.0 * claim_conflict
        - 3.0 * destructive_risk
        - 2.0 * staleness
    )

    return {
        "leg_id": leg_id,
        "score": round(score, 3),
        "unblocks_others": unblocks_others,
        "gm_priority": gm_priority,
        "finishable_now": finishable_now,
        "machine_locality": machine_locality,
        "verification_value": verification_value,
        "token_efficiency": token_efficiency,
        "claim_conflict": claim_conflict,
        "destructive_risk": destructive_risk,
        "staleness": staleness,
        "compatible": (finishable_now > 0 and claim_conflict == 0 and score > 0),
    }


def actionable_unclaimed_compatible(
    legs: List[dict],
    claims: List[dict],
    capabilities: Dict[str, Any],
) -> List[Tuple[dict, Dict[str, Any]]]:
    """Filter open legs to those that are ACTIONABLE, unclaimed, and compatible."""
    candidates = []
    for leg in legs:
        if infer_message_type(leg) != TYPE_ACTIONABLE:
            continue
        sc = compute_claim_score(leg, capabilities, active_claims=claims)
        if sc["compatible"]:
            candidates.append((leg, sc))
    return candidates


def schedule_best_leg(
    root: Optional[Path] = None,
    capabilities: Optional[Dict[str, Any]] = None,
    quota_snapshot: Optional[Any] = None,
) -> Optional[Tuple[dict, Dict[str, Any]]]:
    """Mandatory work selection: find highest scoring compatible open leg.

    When quota_snapshot is provided, candidates are filtered through the
    Quota Governor gate — legs that would breach HARD/RESERVE thresholds
    are excluded, and SOFT threshold legs get a routing downshift annotation.

    Fleet Execution Law invariant: scheduling considers claims and concrete
    scope overlap, NOT inferred busyness. A marathon runner with no claim
    cannot suppress the queue.
    """
    root = root or core.repo_root()
    if root is None:
        return None

    caps = capabilities or machine_capabilities(root)
    open_legs = core._open_legs(root)
    active_claims = [r for r in core._read_claims_from(root, None) if core.claim_is_active(r)]
    active_claims += list(core.foreign_claims(root, active_only=True).values())

    candidates = actionable_unclaimed_compatible(open_legs, active_claims, caps)
    if not candidates:
        return None

    # Quota gate: filter through governor if snapshot available
    if quota_snapshot is not None:
        try:
            from . import quota_governor as qg
            governor = qg.QuotaGovernor(qg.load_thresholds_from_env())
            gated = []
            for leg, score_info in candidates:
                allowed, reason, decision = governor.gate_claim(leg, quota_snapshot)
                score_info["quota_decision"] = decision.value
                score_info["quota_reason"] = reason
                if allowed:
                    gated.append((leg, score_info))
            candidates = gated
        except Exception:
            pass  # Degrade gracefully if governor unavailable

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[1]["score"], reverse=True)
    return candidates[0]


def ghost_worker_check(root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Run ghost worker detection against current session/claim state.

    Returns list of ghost worker reports. A ghost is an active session
    with zero registered claims — it's doing work but hasn't announced
    what scope it owns, which can suppress queue scheduling.
    """
    root = root or core.repo_root()
    if root is None:
        return []

    try:
        from . import quota_governor as qg

        # Gather active claims
        active_claims = [r for r in core._read_claims_from(root, None) if core.claim_is_active(r)]
        active_claims += list(core.foreign_claims(root, active_only=True).values())

        # Build active sessions from claims + current session
        machine = core.resolve_machine()
        agent = core.resolve_agent()
        session = core.resolve_session()

        # Current session is always "active"
        active_sessions = [{"machine": machine, "agent": agent, "session_id": session}]

        # Also infer sessions from recent handoffs (last 24h activity)
        handoffs_dir = root / core.DEFAULT_DIR
        if handoffs_dir.is_dir():
            seen_lanes = set()
            for f in sorted(handoffs_dir.glob("*.json"), reverse=True)[:50]:
                try:
                    rec = __import__("json").loads(f.read_text(encoding="utf-8"))
                    lane_key = f"{rec.get('machine', '')}|{rec.get('agent', '')}"
                    if lane_key not in seen_lanes and rec.get("machine"):
                        seen_lanes.add(lane_key)
                        active_sessions.append({
                            "machine": rec["machine"],
                            "agent": rec.get("agent", ""),
                            "session_id": rec.get("session", ""),
                        })
                except Exception:
                    pass

        reports = qg.detect_ghost_workers(active_sessions, active_claims)
        return [
            {
                "machine": r.machine,
                "agent": r.agent,
                "session": r.session,
                "status": r.status.value,
                "active_claims": r.active_claims,
                "detail": r.detail,
            }
            for r in reports
        ]
    except Exception:
        return []


def calculate_token_efficiency_metrics(lifecycle: dict) -> Dict[str, Any]:
    """Calculate token-to-action economics from a claim/leg lifecycle record."""
    t_seen = lifecycle.get("tokens_at_seen", 0)
    t_claim = lifecycle.get("tokens_at_claim", t_seen)
    t_action = lifecycle.get("tokens_at_first_action", t_claim)
    t_evidence = lifecycle.get("tokens_at_first_evidence", t_action)
    t_complete = lifecycle.get("tokens_at_complete", t_evidence)

    tta_tokens = max(0, t_action - t_seen)
    cta_tokens = max(0, t_action - t_claim)
    tte_tokens = max(0, t_evidence - t_seen)
    execution_tokens = max(0, t_complete - t_action)
    coordination_tax_tokens = max(0, t_action - t_seen)

    total_tokens = max(1, t_complete - t_seen)
    coordination_tax_ratio = round(coordination_tax_tokens / total_tokens, 4)
    productive_token_ratio = round(execution_tokens / total_tokens, 4)

    artifact_count = lifecycle.get("verified_artifact_count", 0)
    evidence_yield = round(artifact_count / max(1.0, total_tokens / 1000.0), 4)

    def parse_dt(stamp_str: str) -> Optional[datetime]:
        if not stamp_str:
            return None
        try:
            return datetime.fromisoformat(stamp_str)
        except Exception:
            return None

    dt_seen = parse_dt(lifecycle.get("leg_seen_at", ""))
    dt_claim = parse_dt(lifecycle.get("claim_at", ""))
    dt_action = parse_dt(lifecycle.get("first_action_at", ""))

    tta_seconds = (dt_action - dt_seen).total_seconds() if (dt_action and dt_seen) else None
    cta_seconds = (dt_action - dt_claim).total_seconds() if (dt_action and dt_claim) else None
    execution_efficiency = max(0.0, min(1.0, round(1.0 - coordination_tax_ratio, 4)))

    return {
        "TTA_tokens": tta_tokens,
        "CTA_tokens": cta_tokens,
        "TTE_tokens": tte_tokens,
        "execution_tokens": execution_tokens,
        "coordination_tax_tokens": coordination_tax_tokens,
        "coordination_tax_ratio": coordination_tax_ratio,
        "productive_token_ratio": productive_token_ratio,
        "evidence_yield": evidence_yield,
        "TTA_seconds": tta_seconds,
        "CTA_seconds": cta_seconds,
        "execution_efficiency": execution_efficiency,
    }
