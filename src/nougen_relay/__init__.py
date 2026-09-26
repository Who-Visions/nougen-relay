"""NouGenRelay — cross-machine continuity for coding agents.

A relay is the handoff: the baton moves, nobody stops running. One machine
finishes a leg and passes state to the next — across processes, models and
boxes — carried by git rather than a live message bus.

The protocol has two halves, and it needs both:

    claim take / release      before the leg — announce work, refuse overlap
    create read ack           after the leg  — pass the baton
    checkpoint complete       during / at the end of a leg

``ack`` is the verb most systems skip and the one that makes the rest
trustworthy: a leg stays ``open`` until somebody takes it, so a dropped baton
is visible instead of silent.
"""

from .core import (  # noqa: F401
    DEFAULT_DIR,
    DEFAULT_REMOTE,
    EXIT_DIVERGED,
    EXIT_FAILURE,
    EXIT_OK,
    EXIT_USAGE,
    RELAY_STATES,
    claim_is_active,
    evaluate_triggers,
    foreign_claims,
    identity,
    relay_status,
    repo_root,
    resolve_agent,
    resolve_machine,
    serialize_record,
    write_record,
)

def __getattr__(name: str):
    """Dynamic submodule resolution so 'from nougen_relay import <submodule>' always works cleanly."""
    import importlib
    try:
        mod = importlib.import_module(f".{name}", __name__)
        globals()[name] = mod
        return mod
    except ImportError:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'") from None

