"""Unit tests for Claim Engine work scheduling and token efficiency metrics."""

from datetime import datetime, timezone
# import pytest
from nougen_relay import claim_engine

FROZEN = datetime(2026, 9, 6, 12, 0, 0, tzinfo=timezone.utc)


def test_infer_message_type():
    assert claim_engine.infer_message_type({"type": "ACTIONABLE"}) == "ACTIONABLE"
    assert claim_engine.infer_message_type({"tags": ["info"]}) == "INFO"
    assert claim_engine.infer_message_type({"goal": "FYI: status update"}) == "INFO"
    assert claim_engine.infer_message_type({"goal": "BLOCKER: missing auth"}) == "BLOCKER"
    assert claim_engine.infer_message_type({"status": "complete"}) == "RESULT"
    assert claim_engine.infer_message_type({"goal": "build claim engine"}) == "ACTIONABLE"


def test_claim_score_calculation():
    caps = {
        "machine": "phoebus",
        "agent": "gemini-cli",
        "repos": ["NouGenRelay"],
        "write_access": True,
        "test_access": True,
    }
    leg = {
        "id": "leg_1",
        "goal": "GM DIRECTIVE: critical scheduler fix",
        "machine": "phoebus",
        "created_utc": "2026-09-06T11:00:00+00:00",
    }
    res = claim_engine.compute_claim_score(leg, caps, active_claims=[], now_dt=FROZEN)
    # unblocks=1(5), gm_priority=1(4), finishable=1(3), locality=1(2), verify=0.5(1.0), token_eff=1.0(1.0)
    # total = 5 + 4 + 3 + 2 + 1.0 + 1.0 = 16.0
    assert res["score"] == 16.0
    assert res["compatible"] is True


def test_claim_score_with_conflict():
    caps = {
        "machine": "phoebus",
        "agent": "gemini-cli",
        "write_access": True,
    }
    leg = {
        "id": "leg_2",
        "goal": "refactor database",
        "machine": "whoart",
    }
    foreign_claim = {
        "machine": "whoart",
        "agent": "claude",
        "scope": "leg_2 database",
        "status": "active",
    }
    res = claim_engine.compute_claim_score(leg, caps, active_claims=[foreign_claim], now_dt=FROZEN)
    assert res["claim_conflict"] == 1.0
    assert res["compatible"] is False


def test_token_efficiency_metrics():
    lifecycle = {
        "leg_seen_at": "2026-09-06T12:00:00+00:00",
        "claim_at": "2026-09-06T12:01:00+00:00",
        "first_action_at": "2026-09-06T12:02:00+00:00",
        "first_evidence_at": "2026-09-06T12:04:00+00:00",
        "complete_at": "2026-09-06T12:10:00+00:00",
        "tokens_at_seen": 1000,
        "tokens_at_claim": 1200,
        "tokens_at_first_action": 1500,
        "tokens_at_first_evidence": 2000,
        "tokens_at_complete": 5000,
        "verified_artifact_count": 2,
    }
    m = claim_engine.calculate_token_efficiency_metrics(lifecycle)
    assert m["TTA_tokens"] == 500
    assert m["CTA_tokens"] == 300
    assert m["TTE_tokens"] == 1000
    assert m["execution_tokens"] == 3500
    assert m["coordination_tax_tokens"] == 500
    assert m["coordination_tax_ratio"] == 0.125
    assert m["productive_token_ratio"] == 0.875
    assert m["execution_efficiency"] == 0.875
    assert m["TTA_seconds"] == 120.0
    assert m["CTA_seconds"] == 60.0
    assert m["evidence_yield"] == 0.5
