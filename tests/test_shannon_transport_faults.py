"""Fault-injection invariants for the Git-backed Shannon relay channel."""

from pathlib import Path
import sys

import pytest

from nougen_relay import core

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
relay_daemon = pytest.importorskip("relay_daemon")


@pytest.mark.parametrize(
    "merge",
    [core._merge_registry_records, relay_daemon._merge_relay_records],
    ids=["checkout-registry", "watcher-projection"],
)
def test_replica_event_union_converges_after_reordered_duplicate_delivery(merge):
    """Event membership converges; published positions follow the remote trail."""
    create = {
        "event": "create",
        "at": "2026-08-28T00:00:00Z",
        "agent": "boxa",
        "goal": "ship relay",
    }
    ack = {"event": "ack", "at": "2026-08-28T00:01:00Z", "agent": "boxb"}
    complete = {
        "event": "complete",
        "at": "2026-08-28T00:02:00Z",
        "agent": "boxb",
        "evidence": "tests passed",
    }
    local = {"id": "leg-1", "status": "complete", "relay": [ack, complete]}
    remote = {
        "id": "leg-1",
        "status": "open",
        "relay": [complete, create, dict(create)],
    }

    forward = merge(local, remote)
    reverse = merge(remote, local)

    assert {core._relay_event_key(e) for e in forward["relay"]} == {
        core._relay_event_key(e) for e in reverse["relay"]
    }
    assert forward["status"] == "complete"
    assert reverse["status"] == "complete"
    assert [event["event"] for event in forward["relay"]] == [
        "complete",
        "create",
        "ack",
    ]


@pytest.fixture(params=[core._merge_registry_records, relay_daemon._merge_relay_records],
                ids=["checkout-registry", "watcher-projection"])
def merge_record(request):
    return request.param


def test_late_event_appends_without_moving_published_positions(merge_record):
    a = {"event": "create", "at": "2026-08-28T00:00:10Z", "agent": "a"}
    b = {"event": "checkpoint", "at": "2026-08-28T00:00:20Z", "agent": "b"}
    c = {"event": "ack", "at": "2026-08-28T00:00:15Z", "agent": "c"}
    remote = {"id": "leg-1", "relay": [a, b]}
    local = {"id": "leg-1", "relay": [a, c]}

    result = merge_record(local, remote)

    assert result["relay"] == [a, b, c]
    assert remote["relay"] == [a, b]
    assert local["relay"] == [a, c]


def test_equal_timestamps_preserve_each_published_replica_order(merge_record):
    a = {"event": "create", "at": "2026-08-28T00:00:10Z", "agent": "a"}
    b = {"event": "ack", "at": "2026-08-28T00:00:10Z", "agent": "b"}
    first = {"id": "leg-1", "relay": [a, b]}
    second = {"id": "leg-1", "relay": [b, a]}

    assert merge_record(first, second)["relay"] == [b, a]
    assert merge_record(second, first)["relay"] == [a, b]


def test_future_clock_does_not_reorder_or_block_later_arrivals(merge_record):
    a = {"event": "create", "at": "2026-08-28T00:00:10Z", "agent": "a"}
    future = {"event": "ack", "at": "2099-01-01T00:00:00Z", "agent": "b"}
    complete = {"event": "complete", "at": "2026-08-28T00:00:20Z", "agent": "c"}
    remote = {"id": "leg-1", "status": "acked", "relay": [a, future]}
    local = {"id": "leg-1", "status": "complete", "relay": [a, complete]}

    result = merge_record(local, remote)

    assert result["relay"] == [a, future, complete]
    assert result["status"] == "complete"


@pytest.mark.parametrize("stamp", [None, "not-a-date"])
def test_legacy_create_timestamp_does_not_move_after_complete(merge_record, stamp):
    create = {"event": "create", "agent": "a"}
    if stamp is not None:
        create["at"] = stamp
    ack = {"event": "ack", "at": "2026-08-28T00:00:10Z", "agent": "b"}
    complete = {"event": "complete", "at": "2026-08-28T00:00:20Z", "agent": "b"}
    remote = {"id": "leg-1", "status": "acked", "relay": [create, ack]}
    local = {"id": "leg-1", "status": "complete", "relay": [create, complete]}

    result = merge_record(local, remote)

    assert result["relay"] == [create, ack, complete]
    assert result["status"] == "complete"
