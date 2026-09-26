import unittest
from nougen_relay import quota_governor as qg

class TestQuotaGovernor(unittest.TestCase):
    def setUp(self):
        self.thresholds = qg.QuotaThresholds(soft=0.70, hard=0.85, reserve=0.10)
        self.gov = qg.QuotaGovernor(thresholds=self.thresholds)

    def test_local_provider_always_full(self):
        snap = qg.QuotaSnapshot(provider="local", timestamp="2026-09-06T19:00:00Z")
        self.assertEqual(self.gov.evaluate(snap), qg.RoutingDecision.CLOUD_FULL)

    def test_soft_threshold_downshift(self):
        snap = qg.QuotaSnapshot(
            provider="google",
            timestamp="2026-09-06T19:00:00Z",
            tokens_used=750,
            tokens_limit=1000,
        )
        self.assertEqual(self.gov.evaluate(snap), qg.RoutingDecision.CLOUD_LITE)

    def test_hard_threshold_local_only(self):
        # With soft=0.70, hard=0.85, 1-reserve=0.90
        # 88% is between hard (0.85) and 1 - reserve (0.90) -> LOCAL_ONLY
        snap = qg.QuotaSnapshot(
            provider="google",
            timestamp="2026-09-06T19:00:00Z",
            tokens_used=880,
            tokens_limit=1000,
        )
        self.assertEqual(self.gov.evaluate(snap), qg.RoutingDecision.LOCAL_ONLY)

    def test_reserve_hold_breach(self):
        # 95% is > 1 - reserve (0.90) -> RESERVE_HOLD
        snap = qg.QuotaSnapshot(
            provider="google",
            timestamp="2026-09-06T19:00:00Z",
            tokens_used=950,
            tokens_limit=1000,
        )
        self.assertEqual(self.gov.evaluate(snap), qg.RoutingDecision.RESERVE_HOLD)

    def test_dual_window_weekly_reserve_breach(self):
        # 10% weekly reserve remaining = 90% utilized
        snap = qg.QuotaSnapshot(
            provider="google",
            timestamp="2026-09-06T19:00:00Z",
            tokens_used=100,
            tokens_limit=1000,
            weekly_limit_pct_remaining=10.0,
            five_hour_limit_pct_remaining=50.0,
        )
        # 90% is <= 1-0.10 (0.90) -> LOCAL_ONLY
        self.assertEqual(self.gov.evaluate(snap), qg.RoutingDecision.LOCAL_ONLY)

    def test_gate_claim(self):
        snap = qg.QuotaSnapshot(provider="google", timestamp="2026-09-06T19:00:00Z", tokens_used=100, tokens_limit=1000)
        allowed, reason, dec = self.gov.gate_claim({"tags": ["cloud"]}, snap)
        self.assertTrue(allowed)
        self.assertEqual(dec, qg.RoutingDecision.CLOUD_FULL)

        snap_depleted = qg.QuotaSnapshot(provider="google", timestamp="2026-09-06T19:00:00Z", weekly_limit_pct_remaining=5.0)
        # 5% remaining = 95% used -> RESERVE_HOLD
        allowed, reason, dec = self.gov.gate_claim({"tags": ["cloud_required"]}, snap_depleted)
        self.assertFalse(allowed)
        self.assertEqual(dec, qg.RoutingDecision.RESERVE_HOLD)

    def test_ghost_worker_detection(self):
        sessions = [
            {"machine": "phoebus", "agent": "worker-1", "session_id": "s1"},
            {"machine": "phoebus", "agent": "worker-2", "session_id": "s2"},
        ]
        claims = [
            {"machine": "phoebus", "agent": "worker-1", "scope": "relay:123"},
        ]
        reports = qg.detect_ghost_workers(sessions, claims)
        self.assertEqual(len(reports), 2)
        r1 = next(r for r in reports if r.agent == "worker-1")
        r2 = next(r for r in reports if r.agent == "worker-2")
        self.assertEqual(r1.status, qg.GhostStatus.CLEAN)
        self.assertEqual(r2.status, qg.GhostStatus.GHOST)

if __name__ == "__main__":
    unittest.main()
