"""Probe-grounded verification gate (GM order 2026-08-31).

The daemon may only ack an execution-shaped leg off probe evidence of live
state, never off persuasive prose. These tests pin the whitelist, the
fail-closed paths, and the question-vs-change routing.
"""

import importlib.util
import sys
from pathlib import Path


_DAEMON_PATH = Path(__file__).resolve().parent.parent / "tools" / "relay_daemon.py"
_spec = importlib.util.spec_from_file_location("relay_daemon", _DAEMON_PATH)
relay_daemon = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("relay_daemon", relay_daemon)
_spec.loader.exec_module(relay_daemon)

allowed = relay_daemon.RelayDaemon._probe_allowed


class TestProbeWhitelist:
    def test_rejects_arbitrary_binaries(self):
        assert not allowed(["rm", "-rf", "/"])
        assert not allowed(["powershell", "-Command", "anything"])
        assert not allowed(["python", "-c", "1"])
        assert not allowed(["bash", "-c", "ls"])

    def test_rejects_non_argv_shapes(self):
        assert not allowed("git log")
        assert not allowed([])
        assert not allowed(None)
        assert not allowed(["git", "log\nrm -rf ."])
        assert not allowed([1, 2])

    def test_gh_api_get_only(self):
        assert allowed(["gh", "api", "repos/o/r/contents/x"])
        assert allowed(["gh", "api", "-X", "GET", "repos/o/r"])
        assert not allowed(["gh", "api", "-X", "PUT", "repos/o/r/contents/x"])
        assert not allowed(["gh", "api", "-X", "DELETE", "repos/o/r"])
        assert not allowed(["gh", "api", "repos/o/r", "-f", "key=value"])
        assert not allowed(["gh", "pr", "merge", "1"])

    def test_git_read_subcommands_only(self):
        assert allowed(["git", "log", "-1", "--format=%H"])
        assert allowed(["git", "status", "--porcelain"])
        assert not allowed(["git", "push"])
        assert not allowed(["git", "commit", "-m", "x"])
        assert not allowed(["git", "reset", "--hard"])

    def test_curl_get_only(self):
        assert allowed(["curl", "-s", "https://example.com/health"])
        assert not allowed(["curl", "-X", "POST", "https://example.com"])
        assert not allowed(["curl", "-d", "x=1", "https://example.com"])
        assert not allowed(["curl", "-o", "f.bin", "https://example.com"])
        assert not allowed(["curl", "-s", "file:///etc/passwd"])


class _StubDaemon:
    """Bare instance carrying only what the pure helpers need."""

    _probe_allowed = staticmethod(relay_daemon.RelayDaemon._probe_allowed)
    _leg_body = relay_daemon.RelayDaemon._leg_body
    _leg_done_when = relay_daemon.RelayDaemon._leg_done_when
    _leg_demands_change = relay_daemon.RelayDaemon._leg_demands_change
    dav1d_probe_verify = relay_daemon.RelayDaemon.dav1d_probe_verify

    def __init__(self):
        self.relay_dir = Path(".")
        self.calls = []

    # Overridden collaborators used by dav1d_probe_verify
    def _dav1d_json(self, prompt, timeout=60):
        raise AssertionError("test must override _dav1d_json")

    def _run_probes(self, probes):
        raise AssertionError("test must override _run_probes")

    def verify_execution(self, triage, exec_res):
        return {"verified": True, "evidence": "prose says done"}


def _triage(wake=False):
    return relay_daemon.TriageResult(
        handoff_id="t1", task_type="EXECUTION_RUN", action="fix the cap",
        requires_harness_wake=wake, confidence=0.9, reasoning="r",
        lag_seconds=0.0, is_lagging=False)


class TestDoneWhenExtraction:
    def test_extracts_done_when_section(self):
        leg = {"notes": "## Context\nstuff\n## Done when\n- cap fixed\n- test added\n## Other\nx"}
        d = _StubDaemon()
        got = d._leg_done_when(leg)
        assert "cap fixed" in got and "Other" not in got

    def test_empty_when_absent(self):
        assert _StubDaemon()._leg_done_when({"notes": "no criteria here"}) == ""


class TestChangeDetection:
    def test_fix_goal_demands_change(self):
        assert _StubDaemon()._leg_demands_change({"goal": "Fix the relay read cap"})

    def test_question_goal_does_not(self):
        assert not _StubDaemon()._leg_demands_change(
            {"goal": "What is the current open leg count?"})


class TestFailClosed:
    def test_nonzero_exit_never_verified(self):
        d = _StubDaemon()
        out = d.dav1d_probe_verify(_triage(True), {"goal": "fix x"}, {"exit_code": 1})
        assert out["verified"] is False

    def test_zero_runnable_probes_not_verified(self):
        d = _StubDaemon()
        d._dav1d_json = lambda prompt, timeout=60: {"probes": [{"argv": ["rm", "-rf", "/"]}]}
        d._run_probes = relay_daemon.RelayDaemon._run_probes.__get__(d)
        out = d.dav1d_probe_verify(
            _triage(True), {"goal": "fix x"}, {"exit_code": 0, "stdout": "I did it, trust me"})
        assert out["verified"] is False
        assert "stays open" in out["evidence"]

    def test_planner_error_not_verified(self):
        d = _StubDaemon()

        def boom(prompt, timeout=60):
            raise RuntimeError("ollama down")

        d._dav1d_json = boom
        out = d.dav1d_probe_verify(
            _triage(True), {"goal": "fix x"}, {"exit_code": 0, "stdout": "done"})
        assert out["verified"] is False

    def test_prose_alone_cannot_ack_change_leg(self):
        """The exact 2026-08-30 failure: persuasive prose restating a diagnosis
        must not verify a leg whose goal demands a fix."""
        d = _StubDaemon()
        d._dav1d_json = lambda prompt, timeout=60: {"probes": []}
        d._run_probes = lambda probes: []
        out = d.dav1d_probe_verify(
            _triage(False),
            {"goal": "Fix relay reads frozen by 1000-entry cap"},
            {"exit_code": 0,
             "stdout": "The system successfully processed entries up to #1000."})
        assert out["verified"] is False


class TestQuestionLegsStillAnswerable:
    def test_question_leg_uses_prose_verify_with_label(self):
        d = _StubDaemon()
        out = d.dav1d_probe_verify(
            _triage(False),
            {"goal": "What is the open leg count today?"},
            {"exit_code": 0, "stdout": "There are 25 open legs."})
        assert out["verified"] is True
        assert out["evidence"].startswith("fleet-answer")


class TestVerifiedTrail:
    def test_verified_evidence_carries_probe_trail(self):
        d = _StubDaemon()
        responses = iter([
            {"probes": [{"argv": ["git", "log", "-1"], "why": "see head"}]},
            {"verified": True, "evidence": "HEAD moved to the fix commit"},
        ])
        d._dav1d_json = lambda prompt, timeout=60: next(responses)
        d._run_probes = lambda probes: [
            {"argv": ["git", "log", "-1"], "status": "ran", "exit_code": 0,
             "output": "abc123 fix: raise cap"}]
        out = d.dav1d_probe_verify(
            _triage(True), {"goal": "fix the cap"}, {"exit_code": 0, "stdout": "did it"})
        assert out["verified"] is True
        assert "probe-verified" in out["evidence"]
        assert "git log -1" in out["evidence"]


class TestStaleClaimGuard:
    """2026-08-31 race: daemon claimed a leg 66s after it was acked - the
    local clone was stale and claim_leg_upstream never re-read live status."""

    def _stub(self):
        return object.__new__(relay_daemon.RelayDaemon)

    def test_skips_claim_when_leg_already_acked_upstream(self):
        d = self._stub()
        d._registry_read_json = lambda path: ({"sha": "x"}, {"status": "acked"})
        assert d.claim_leg_upstream({"id": "20260831T011512Z__x__y"}, {"ttl_minutes": 15}) is False

    def test_skips_claim_when_leg_completed_upstream(self):
        d = self._stub()
        d._registry_read_json = lambda path: ({"sha": "x"}, {"status": "complete"})
        assert d.claim_leg_upstream({"id": "legid-123456"}, {"ttl_minutes": 15}) is False

    def test_unreadable_leg_falls_through_to_claim_fence(self):
        d = self._stub()
        calls = []

        def read(path):
            calls.append(path)
            return None, None  # leg unreadable AND claim path unreadable -> fail safe

        d._registry_read_json = read
        assert d.claim_leg_upstream({"id": "legid-123456"}, {"ttl_minutes": 15}) is False
        assert any(p == ".handoffs/legid-123456.json" for p in calls)
        assert any(p.startswith(".handoffs/claims/") for p in calls)


class TestAckWritesRelayEvent:
    """2026-08-31: daemon acks set top-level fields only; readers surfacing the
    relay events array saw authorless acks (status flipped, relay:[] empty)."""

    def test_ack_appends_attributed_event(self, monkeypatch):
        import base64 as b64
        import json as js
        d = object.__new__(relay_daemon.RelayDaemon)
        d.machine_name = "testbox"
        written = {}
        rec = {"id": "leg-x", "status": "open", "relay": []}
        meta = {"content": b64.b64encode(js.dumps(rec).encode()).decode(), "sha": "s"}

        def fake_run(argv, **kw):
            class R:
                returncode = 0
                stdout = js.dumps(meta)
                stderr = ""
            if "-X" in argv:  # the PUT
                body_arg = next(a for a in argv if a.startswith("content="))
                written.update(js.loads(b64.b64decode(body_arg[8:]).decode()))
            return R()

        monkeypatch.setattr(relay_daemon.shutil, "which", lambda _: "gh")
        monkeypatch.setattr(relay_daemon.subprocess, "run", fake_run)
        monkeypatch.setattr(d, "_registry_repo_slug", lambda: "o/r")
        monkeypatch.setattr(d, "_registry_branch", lambda: "main")
        assert d.ack_leg_upstream("leg-x", "probe evidence") is True
        assert written["status"] == "acked"
        ev = written["relay"][0]
        assert ev["event"] == "ack"
        assert ev["machine"] == "testbox"
        assert ev["agent"] == relay_daemon.DAEMON_AGENT
        assert "probe evidence" in ev["note"]


class TestDefectReportsAreNotQuestions:
    """2026-08-31: a DEFECT leg with no fix-verb triaged as question-shaped and
    was closed by a generated fleet-answer 15 minutes after filing."""

    def test_defect_marker_blocks_fleet_answer_path(self):
        d = _StubDaemon()
        d._dav1d_json = lambda prompt, timeout=60: {"probes": []}
        d._run_probes = lambda probes: []
        out = d.dav1d_probe_verify(
            _triage(False),
            {"goal": "DEFECT + falsifier result: shards_capture returns captured:true "
                     "for a shard that recall, search, AND window all cannot surface"},
            {"exit_code": 0, "stdout": "The query returned shard IDs confirming things."})
        assert out["verified"] is False, "a defect report must never close on a generated answer"

    def test_incident_and_p1_also_blocked(self):
        d = _StubDaemon()
        for goal in ("P1 ESCALATION: something is down", "INCIDENT: node wedged again"):
            assert d._leg_demands_change({"goal": goal}) is True

    def test_plain_question_still_answerable(self):
        d = _StubDaemon()
        out = d.dav1d_probe_verify(
            _triage(False),
            {"goal": "What is the open leg count today?"},
            {"exit_code": 0, "stdout": "There are 25 open legs."})
        assert out["verified"] is True

    def test_question_path_judges_leg_goal_not_triage_action(self):
        d = _StubDaemon()
        seen = {}

        def spy_verify(triage, exec_res):
            seen["action"] = triage.action
            return {"verified": True, "evidence": "ok"}

        d.verify_execution = spy_verify
        d.dav1d_probe_verify(
            _triage(False),
            {"goal": "How many relay legs mention Kaedra?"},
            {"exit_code": 0, "stdout": "Nine."})
        assert seen["action"] == "How many relay legs mention Kaedra?"


class TestTodoPrefixShapeRule:
    """A goal starting 'TODO:' is a queue item by fleet convention - 90 of 220
    open legs are relay-watch TODOs. Prefix only: completion reports that
    MENTION a TODO must stay answerable (claude-app's false-positive pair)."""

    def test_leading_todo_is_execution_shaped(self):
        d = _StubDaemon()
        assert d._leg_demands_change(
            {"goal": "TODO: decide canonical keymaker secrets store"}) is True
        assert d._leg_demands_change(
            {"goal": "  todo: review the thing"}) is True

    def test_mentioning_a_todo_is_not(self):
        d = _StubDaemon()
        assert d._leg_demands_change(
            {"goal": "Report: the count of open questions was tallied"}) is False
        assert d._leg_demands_change(
            {"goal": "Everything from that queue item was absorbed; summary within"}) is False
