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
def test_replica_merge_converges_after_reordered_duplicate_delivery(merge):
    """Reordered replicas must converge while duplicate events remain one event."""
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

    assert forward == reverse
    assert forward["status"] == "complete"
    assert [event["event"] for event in forward["relay"]] == [
        "create",
        "ack",
        "complete",
    ]


@pytest.mark.parametrize(
    "merge",
    [core._merge_registry_records, relay_daemon._merge_relay_records],
    ids=["checkout-registry", "watcher-projection"],
)
def test_replica_merge_orders_undated_legacy_events_first(merge):
    """Legacy/undated events without 'at' must sort before subsequent state events."""
    create_undated = {
        "event": "create",
        "agent": "boxa",
        "goal": "legacy handoff",
    }
    ack = {"event": "ack", "at": "2026-08-28T00:01:00Z", "agent": "boxb"}
    complete = {
        "event": "complete",
        "at": "2026-08-28T00:02:00Z",
        "agent": "boxb",
        "evidence": "tests passed",
    }
    local = {"id": "leg-legacy", "status": "complete", "relay": [ack, complete]}
    remote = {
        "id": "leg-legacy",
        "status": "open",
        "relay": [complete, create_undated],
    }

    forward = merge(local, remote)
    reverse = merge(remote, local)

    assert forward == reverse
    assert forward["status"] == "complete"
    assert [event["event"] for event in forward["relay"]] == [
        "create",
        "ack",
        "complete",
    ]
