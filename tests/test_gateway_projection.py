import base64
import json
import subprocess
from types import SimpleNamespace

from nougen_relay import core


def _remote_metadata(record, sha="sha-1"):
    content = base64.b64encode(
        (json.dumps(record, indent=2) + "\n").encode("utf-8")
    ).decode("ascii")
    return {"sha": sha, "content": content}


def test_gateway_write_merges_remote_events_and_targets_canonical_branch(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / ".handoffs").mkdir(parents=True)
    local = {
        "id": "leg-1",
        "status": "acked",
        "goal": "take the baton",
        "relay": [{"event": "ack", "at": "2026-08-28T18:00:00Z", "agent": "codex"}],
    }
    remote = {
        "id": "leg-1",
        "status": "open",
        "goal": "take the baton",
        "relay": [{"event": "create", "at": "2026-08-28T17:59:00Z", "agent": "claude"}],
    }
    calls = []
    monkeypatch.setenv("NOUGEN_RELAY_REPO_SLUG", "Who-Visions/NouGenRelay")
    monkeypatch.setenv("NOUGEN_RELAY_BRANCH", "main")
    monkeypatch.setattr(core.shutil, "which", lambda _: "gh")

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        if "-X" in argv:
            return subprocess.CompletedProcess(argv, 0, "{}", "")
        return subprocess.CompletedProcess(argv, 0, json.dumps(_remote_metadata(remote)), "")

    monkeypatch.setattr(core.subprocess, "run", fake_run)

    assert core._write_registry_record_upstream(
        root, "origin", "leg-1", local, "ack"
    ) is True

    put_argv, put_kwargs = calls[-1]
    assert put_argv[:5] == ["gh", "api", "-X", "PUT", "repos/Who-Visions/NouGenRelay/contents/.handoffs/leg-1.json"]
    body = json.loads(put_kwargs["input"])
    assert body["branch"] == "main"
    merged = json.loads(base64.b64decode(body["content"]).decode("utf-8"))
    assert merged["status"] == "acked"
    assert {event["event"] for event in merged["relay"]} == {"create", "ack"}


def test_gateway_write_retries_a_stale_sha_without_losing_events(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / ".handoffs").mkdir(parents=True)
    local = {
        "id": "leg-2",
        "status": "acked",
        "relay": [{"event": "ack", "at": "2026-08-28T18:00:00Z", "agent": "codex"}],
    }
    remote_one = {
        "id": "leg-2",
        "status": "open",
        "relay": [{"event": "create", "at": "2026-08-28T17:59:00Z", "agent": "claude"}],
    }
    remote_two = {
        **remote_one,
        "relay": remote_one["relay"] + [
            {"event": "triage", "at": "2026-08-28T18:00:10Z", "agent": "relay-watch"}
        ],
    }
    responses = iter([
        json.dumps(_remote_metadata(remote_one, "sha-1")),
        json.dumps(_remote_metadata(remote_two, "sha-2")),
    ])
    puts = []
    monkeypatch.setenv("NOUGEN_RELAY_REPO_SLUG", "Who-Visions/NouGenRelay")
    monkeypatch.setenv("NOUGEN_RELAY_BRANCH", "main")
    monkeypatch.setenv("NOUGEN_RELAY_UPSTREAM_RETRIES", "2")
    monkeypatch.setattr(core.shutil, "which", lambda _: "gh")

    def fake_run(argv, **kwargs):
        if "-X" in argv:
            puts.append(json.loads(kwargs["input"]))
            if len(puts) == 1:
                return subprocess.CompletedProcess(argv, 1, "", "sha conflict")
            return subprocess.CompletedProcess(argv, 0, "{}", "")
        return subprocess.CompletedProcess(argv, 0, next(responses), "")

    monkeypatch.setattr(core.subprocess, "run", fake_run)

    assert core._write_registry_record_upstream(
        root, "origin", "leg-2", local, "ack"
    ) is True
    assert len(puts) == 2
    merged = json.loads(base64.b64decode(puts[-1]["content"]).decode("utf-8"))
    assert {event["event"] for event in merged["relay"]} == {"create", "triage", "ack"}


def test_cmd_relay_uses_gateway_write_before_branch_push(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    for args in (("init", "-q", "-b", "main"),
                 ("config", "user.email", "test@example.com"),
                 ("config", "user.name", "test")):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    handoffs = root / ".handoffs"
    handoffs.mkdir()
    leg_id = "20260828T180000Z__claude__g-whoentertains"
    (handoffs / f"{leg_id}.json").write_text(
        json.dumps({"id": leg_id, "machine": "claude", "agent": "g-whoentertains",
                    "goal": "take the baton", "status": "open", "relay": []}, indent=2) + "\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(root)
    monkeypatch.setenv("NOUGEN_MACHINE", "codex")
    monkeypatch.setenv("NOUGEN_AGENT", "codex")
    core._MACHINE_CACHE = None
    core._AGENT_CACHE = None
    calls = []
    monkeypatch.setattr(core, "_write_registry_record_upstream",
                        lambda *args: calls.append(args) or True)
    monkeypatch.setattr(core, "_publish", lambda *args: (_ for _ in ()).throw(
        AssertionError("branch push should not be used after gateway write")))
    args = SimpleNamespace(action="ack", id=leg_id, message="taking it", no_push=False)

    assert core.cmd_relay(args) == core.EXIT_OK
    assert calls and calls[0][2] == leg_id
