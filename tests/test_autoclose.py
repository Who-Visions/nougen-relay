"""Auto-close must ack reports and never ack work.

The cost is asymmetric: a leg wrongly left open is clutter someone acks by
hand (the exact chore this removes); a leg wrongly acked hides a baton. So
every rule here is checked from the "would this hide work" side first.
"""
from datetime import datetime, timedelta, timezone

from nougen_relay import autoclose

OLD = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat().replace("+00:00", "Z")


def _rec(goal, status="open", created=OLD):
    return {"goal": goal, "status": status, "created_utc": created}


def test_auto_session_notice_closes_despite_fleet_branch_ref():
    ok, why = autoclose.classify(_rec("[auto] NouGen@fleet/x: session ended with 3 uncommitted file(s)"),
                                 "# h\n## Session ended with uncommitted work in\n- a.py\n")
    assert ok, why


def test_triage_digest_closes_despite_next_move_section():
    ok, why = autoclose.classify(_rec("Xoah relay triage: ranked digest 2026-09-14 11:10Z"),
                                 "## Ranked\n1. x\n## Next move\ndo y\n")
    assert ok, why


def test_ask_none_closes():
    ok, why = autoclose.classify(_rec("Archive: things landed"), "## Ask\nNone. For information only.\n## Done when\nAcked.")
    assert ok, why





def test_ask_with_work_stays_open():
    ok, _ = autoclose.classify(_rec("EchoVault: token budget ported; next = eval"), "## Ask\n1. write recall_eval.py\n")
    assert not ok


def test_addressed_leg_stays_open_even_when_fixed():
    ok, why = autoclose.classify(_rec("[-> @blade] ROOT CAUSE FIXED in #352; restart 4444"), "## Ask (blade)\nrestart\n")
    assert not ok and "addressed" in why


def test_report_vocab_without_ask_closes():
    ok, why = autoclose.classify(_rec("phoebus /msg FIXED end-to-end: connector delivers live"), "## Situation\nall good\n")
    assert ok, why


def test_green_status_with_imperative_goal_stays_open():
    ok, _ = autoclose.classify(_rec("NOW truth guard: 3 origins GREEN; isolate the mismatch"), "body\n")
    assert not ok


def test_work_section_blocks_vocab_match():
    ok, why = autoclose.classify(_rec("Shard ingress restored: worker rolled back"), "## Fixed\nyes\n## Still open\n- thing\n")
    assert not ok and "work section" in why


def test_fresh_leg_waits_for_grace():
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    ok, why = autoclose.classify(_rec("[auto] x: session ended", created=now), "")
    assert not ok and "grace" in why


def test_non_open_never_touched():
    ok, _ = autoclose.classify(_rec("[auto] x", status="acked"), "")
    assert not ok


def test_plain_goal_without_signal_stays_open():
    ok, why = autoclose.classify(_rec("Xoah: begin Black Glass build"), "body only\n")
    assert not ok and "nothing marks" in why


def test_ask_none_plus_request_to_anyone_stays_open():
    ok, why = autoclose.classify(_rec("Archive: cull parity"), "## Ask\nNone. Dave picks which albums to showcase.\n")
    assert not ok and "adds a request" in why
    ok, why = autoclose.classify(_rec("Archive: cull parity"), "## Ask\nNone. Whoever is on blade: restart it.\n")
    assert not ok and "adds a request" in why


def test_ask_none_for_information_only_closes():
    ok, why = autoclose.classify(_rec("Archive: things"), "## Ask\nNone. For information only.\n")
    assert ok, why


def test_mention_counts_only_for_lanes_the_registry_has_seen():
    lanes = {"blade", "newbox"}
    ok, _ = autoclose.classify(_rec("thing FIXED, ping @newbox"), "", lanes=lanes)
    assert not ok
    ok, _ = autoclose.classify(_rec("thing FIXED, ping @fleet"), "", lanes=lanes | {"fleet"})
    assert ok
    ok, _ = autoclose.classify(_rec("NouGen@fleet/x FIXED"), "", lanes=lanes | {"fleet"})
    assert ok


def test_known_lanes_reads_machines_and_agents_from_filenames(tmp_path):
    d = tmp_path / ".handoffs"
    d.mkdir()
    (d / "20260914T000000Z__NewBox__some-agent.json").write_text("{}")
    assert {"newbox", "some-agent"} <= autoclose.known_lanes(tmp_path)


def test_heal_rebase_keeps_upstream_for_handoff_conflicts(tmp_path, monkeypatch):
    """A record conflict during the sweep's pull means another lane already
    acked it: upstream wins, the rebase finishes, the clone is never parked."""
    import json
    import subprocess

    def git(*a, cwd):
        subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True)

    upstream = tmp_path / "up"
    upstream.mkdir()
    git("init", "-q", "-b", "main", cwd=upstream)
    git("config", "user.email", "t@t", cwd=upstream)
    git("config", "user.name", "t", cwd=upstream)
    rec = upstream / ".handoffs" / "20260914T000000Z__a__b.json"
    rec.parent.mkdir()
    rec.write_text(json.dumps({"status": "open"}))
    git("add", ".", cwd=upstream)
    git("commit", "-qm", "open", cwd=upstream)

    clone = tmp_path / "clone"
    git("clone", "-q", str(upstream), str(clone), cwd=tmp_path)
    git("config", "user.email", "t@t", cwd=clone)
    git("config", "user.name", "t", cwd=clone)

    rec.write_text(json.dumps({"status": "acked", "by": "other-lane"}))
    git("commit", "-qam", "other lane acks", cwd=upstream)
    mine = clone / ".handoffs" / rec.name
    mine.write_text(json.dumps({"status": "acked", "by": "sweep"}))
    git("commit", "-qam", "sweep acks", cwd=clone)
    subprocess.run(["git", "pull", "--rebase", "-q", "origin", "main"], cwd=clone, capture_output=True)
    assert autoclose._rebase_in_progress(clone)

    monkeypatch.chdir(clone)
    out = autoclose.heal_rebase(clone)
    assert out and out.startswith("healed")
    assert not autoclose._rebase_in_progress(clone)
    assert json.loads(mine.read_text())["by"] == "other-lane"


def test_arrow_inside_prose_is_not_an_address():
    ok, why = autoclose.classify(_rec("A/B relaunched FIXED (shim 25840 -> worker 29256)"), "## Ask\nNone.\n", lanes={"blade"})
    assert ok, why
    ok, why = autoclose.classify(_rec("-> @blade please restart"), "", lanes={"blade"})
    assert not ok and "addressed" in why


def test_body_reader_tolerates_non_utf8(tmp_path):
    rec = tmp_path / "20260914T000000Z__a__b.json"
    rec.write_text("{}")
    rec.with_suffix(".md").write_bytes(b"# leg \x97 body\n## Ask\nNone.\n")
    body = autoclose._body_for(rec, {})
    assert "## Ask" in body
