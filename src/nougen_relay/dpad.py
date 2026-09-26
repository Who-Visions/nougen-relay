"""NouGen D-PAD: Composable Directional Routing Semantics.

Primitives:
  * FORWARD (▶️) : Move baton to the next responsible stage/lane in current dependency chain.
  * BACK (◀️)    : Send evidence, failure, correction, or review back to preceding responsible stage.
  * UP (⬆️)      : Escalate compressed decision/evidence packet to higher authority layer.
  * DOWN (⬇️)    : Push clarified intent, policy, contracts, or decomposition down to execution lanes.

Directions describe responsibility topology, not physical computers.
Sequences carry composable semantics, e.g.:
  `RELAY DOWN → RELAY FORWARD → RELAY UP`
  `RELAY FORWARD → RELAY BACK → RELAY FORWARD`
"""

from __future__ import annotations

import enum
import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union


class DpadDirection(str, enum.Enum):
    FORWARD = "forward"
    BACK = "back"
    UP = "up"
    DOWN = "down"


DIRECTION_GLYPHS = {
    DpadDirection.FORWARD: "▶️",
    DpadDirection.BACK: "◀️",
    DpadDirection.UP: "⬆️",
    DpadDirection.DOWN: "⬇️",
}

DIRECTION_ALIASES: Dict[str, DpadDirection] = {
    "forward": DpadDirection.FORWARD,
    "fwd": DpadDirection.FORWARD,
    "right": DpadDirection.FORWARD,
    ">": DpadDirection.FORWARD,
    "->": DpadDirection.FORWARD,
    "next": DpadDirection.FORWARD,
    "back": DpadDirection.BACK,
    "bk": DpadDirection.BACK,
    "left": DpadDirection.BACK,
    "<": DpadDirection.BACK,
    "<-": DpadDirection.BACK,
    "prev": DpadDirection.BACK,
    "previous": DpadDirection.BACK,
    "up": DpadDirection.UP,
    "ascend": DpadDirection.UP,
    "escalate": DpadDirection.UP,
    "^": DpadDirection.UP,
    "down": DpadDirection.DOWN,
    "descend": DpadDirection.DOWN,
    "delegate": DpadDirection.DOWN,
    "v": DpadDirection.DOWN,
}

# Canonical responsibility pipeline stages
DEFAULT_STAGES: List[str] = [
    "intent",
    "architecture",
    "research",
    "implementation",
    "test",
    "verification",
    "deployment",
]

# Canonical authority hierarchy
DEFAULT_AUTHORITY_CHAIN: List[str] = [
    "worker",
    "lead",
    "orchestrator",
    "gm",
]

# Stage to lane capability mapping
STAGE_TO_CAPABILITIES: Dict[str, Set[str]] = {
    "intent": {"gm", "orchestrator", "claude", "reasoning"},
    "architecture": {"claude-cli", "claude", "gemini", "architecture", "planning"},
    "research": {"gemini", "research", "sol-ai", "analysis"},
    "implementation": {"codex", "openai", "claude", "coding", "execution"},
    "test": {"codex", "ollama", "sol-ai", "tests"},
    "verification": {"sol-ai", "claude", "gemini", "diagnostic"},
    "deployment": {"codex", "operator", "gm", "execution"},
}


class DpadRoutingError(Exception):
    """Base error for D-PAD routing failures."""


class TTLExhaustedError(DpadRoutingError):
    """Raised when hop TTL reaches zero (packet storm protection)."""


class RouteLoopDetectedError(DpadRoutingError):
    """Raised when an unprogressed cycle is detected in route history."""


class InvalidDirectionError(DpadRoutingError):
    """Raised when an invalid direction string is supplied."""


class TopologyBoundaryError(DpadRoutingError):
    """Raised when routing attempts to move beyond topology bounds."""


def normalize_direction(raw: Union[str, DpadDirection]) -> DpadDirection:
    """Normalize a raw direction string or alias to a DpadDirection enum."""
    if isinstance(raw, DpadDirection):
        return raw
    clean = str(raw).strip().lower()
    if clean in DIRECTION_ALIASES:
        return DIRECTION_ALIASES[clean]
    raise InvalidDirectionError(
        f"Unknown D-PAD direction: {raw!r}. Expected one of: "
        f"{', '.join(d.value for d in DpadDirection)}"
    )


def parse_sequence(seq: Union[str, Sequence[str]]) -> List[DpadDirection]:
    """Parse a sequence string or list into a list of DpadDirections.

    Accepts formats such as:
      - "DOWN -> FORWARD -> UP"
      - "DOWN, FORWARD, UP"
      - "down forward up"
      - ["down", "forward", "up"]
    """
    if isinstance(seq, str):
        # Replace common delimiters with space
        cleaned = (
            seq.replace("->", " ")
            .replace("→", " ")
            .replace(",", " ")
            .replace(">", " ")
            .replace("|", " ")
        )
        tokens = [t.strip() for t in cleaned.split() if t.strip()]
    elif isinstance(seq, (list, tuple)):
        tokens = [str(item).strip() for item in seq if str(item).strip()]
    else:
        raise ValueError(f"Unsupported sequence type: {type(seq)}")

    return [normalize_direction(t) for t in tokens]


def format_sequence(seq: Sequence[DpadDirection]) -> str:
    """Format a sequence of directions into a human-readable glyph string."""
    parts = []
    for d in seq:
        glyph = DIRECTION_GLYPHS.get(d, "")
        parts.append(f"{d.value.upper()} {glyph}".strip())
    return " → ".join(parts)


@dataclass
class RouteHop:
    """A recorded single hop in a directional relay route."""
    hop: int
    direction: str
    from_stage: str
    to_stage: str
    from_authority: str
    to_authority: str
    machine: str
    agent: str
    timestamp_utc: str
    receipts_count: int = 0
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DirectionalBaton:
    """A composable directional baton carrying D-PAD routing semantics."""
    direction: str
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    field_position: str = "intent"
    authority_level: str = "orchestrator"
    proven_receipts: List[Any] = field(default_factory=list)
    unresolved_uncertainty: List[str] = field(default_factory=list)
    requested_next_action: str = ""
    expected_return_path: List[str] = field(default_factory=list)
    return_required: bool = False
    ttl: int = 10
    route_history: List[Dict[str, Any]] = field(default_factory=list)
    sequence: List[str] = field(default_factory=list)
    sequence_index: int = 0
    origin_machine: str = ""
    origin_agent: str = ""
    origin_stage: str = "intent"
    origin_authority: str = "orchestrator"
    created_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DirectionalBaton:
        """Construct from raw dictionary safely."""
        valid_fields = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


def calculate_next_stage(
    current_stage: str,
    direction: DpadDirection,
    stages: Optional[List[str]] = None,
) -> str:
    """Calculate the next responsibility stage given current stage and direction."""
    pipeline = stages or DEFAULT_STAGES
    current_norm = current_stage.lower().strip()
    
    if current_norm not in pipeline:
        current_idx = 0
    else:
        current_idx = pipeline.index(current_norm)

    if direction == DpadDirection.FORWARD:
        next_idx = min(current_idx + 1, len(pipeline) - 1)
        return pipeline[next_idx]
    elif direction == DpadDirection.BACK:
        next_idx = max(current_idx - 1, 0)
        return pipeline[next_idx]
    elif direction in (DpadDirection.UP, DpadDirection.DOWN):
        # UP / DOWN shifts authority, preserves current functional stage
        return current_norm if current_norm in pipeline else pipeline[0]
    return pipeline[current_idx]


def calculate_next_authority(
    current_authority: str,
    direction: DpadDirection,
    authority_chain: Optional[List[str]] = None,
) -> str:
    """Calculate the next authority level given current level and direction."""
    chain = authority_chain or DEFAULT_AUTHORITY_CHAIN
    norm = current_authority.lower().strip()
    
    if norm not in chain:
        current_idx = 0
    else:
        current_idx = chain.index(norm)

    if direction == DpadDirection.UP:
        next_idx = min(current_idx + 1, len(chain) - 1)
        return chain[next_idx]
    elif direction == DpadDirection.DOWN:
        next_idx = max(current_idx - 1, 0)
        return chain[next_idx]
    elif direction in (DpadDirection.FORWARD, DpadDirection.BACK):
        # FORWARD / BACK moves within the same authority band
        return norm if norm in chain else chain[0]
    return chain[current_idx]


def detect_route_loop(
    route_history: Sequence[Dict[str, Any]],
    next_stage: str,
    next_authority: str,
    direction: DpadDirection,
    max_cycle_repeats: int = 2,
) -> bool:
    """Detect if the route is stuck in an unprogressed cycle."""
    signature = (next_stage, next_authority, direction.value)
    seen_count = 0
    for hop in route_history:
        h_sig = (
            hop.get("to_stage", ""),
            hop.get("to_authority", ""),
            hop.get("direction", ""),
        )
        if h_sig == signature:
            seen_count += 1
            if seen_count >= max_cycle_repeats:
                return True
    return False


def advance_directional_baton(
    baton: Union[DirectionalBaton, Dict[str, Any]],
    direction: Optional[Union[str, DpadDirection]] = None,
    receipts: Optional[Sequence[Any]] = None,
    uncertainty: Optional[Union[str, Sequence[str]]] = None,
    next_action: Optional[str] = None,
    machine: str = "",
    agent: str = "",
    note: str = "",
    stages: Optional[List[str]] = None,
    authority_chain: Optional[List[str]] = None,
) -> DirectionalBaton:
    """Advance a directional baton by one step in the responsibility topology."""
    if isinstance(baton, dict):
        baton_obj = DirectionalBaton.from_dict(baton)
    else:
        baton_obj = baton

    # Check TTL
    if baton_obj.ttl <= 0:
        raise TTLExhaustedError(
            f"Baton {baton_obj.correlation_id} exhausted TTL ({baton_obj.ttl}). "
            "Halting to prevent route cycle/packet storm."
        )

    # Determine step direction
    if direction is not None:
        step_dir = normalize_direction(direction)
    elif baton_obj.sequence and baton_obj.sequence_index < len(baton_obj.sequence):
        step_dir = normalize_direction(baton_obj.sequence[baton_obj.sequence_index])
    else:
        step_dir = normalize_direction(baton_obj.direction)

    # Save origin info if first hop
    if not baton_obj.route_history:
        baton_obj.origin_stage = baton_obj.field_position
        baton_obj.origin_authority = baton_obj.authority_level
        if machine and not baton_obj.origin_machine:
            baton_obj.origin_machine = machine
        if agent and not baton_obj.origin_agent:
            baton_obj.origin_agent = agent

    from_stage = baton_obj.field_position
    from_auth = baton_obj.authority_level

    to_stage = calculate_next_stage(from_stage, step_dir, stages)
    to_auth = calculate_next_authority(from_auth, step_dir, authority_chain)

    # Loop detection
    if detect_route_loop(baton_obj.route_history, to_stage, to_auth, step_dir):
        raise RouteLoopDetectedError(
            f"Loop detected in route {baton_obj.correlation_id}: "
            f"state ({to_stage}, {to_auth}, {step_dir.value}) repeated {2} times without exit."
        )

    # Update receipts
    if receipts:
        baton_obj.proven_receipts.extend(list(receipts))

    # Update uncertainty
    if uncertainty:
        if isinstance(uncertainty, str):
            baton_obj.unresolved_uncertainty.append(uncertainty)
        elif isinstance(uncertainty, (list, tuple)):
            baton_obj.unresolved_uncertainty.extend(list(uncertainty))

    if next_action is not None:
        baton_obj.requested_next_action = next_action

    stamp = datetime.now(timezone.utc).isoformat()
    hop_num = len(baton_obj.route_history) + 1

    hop = RouteHop(
        hop=hop_num,
        direction=step_dir.value,
        from_stage=from_stage,
        to_stage=to_stage,
        from_authority=from_auth,
        to_authority=to_auth,
        machine=machine or baton_obj.origin_machine or "unknown",
        agent=agent or baton_obj.origin_agent or "unknown",
        timestamp_utc=stamp,
        receipts_count=len(baton_obj.proven_receipts),
        note=note,
    )

    baton_obj.route_history.append(hop.to_dict())
    baton_obj.direction = step_dir.value
    baton_obj.field_position = to_stage
    baton_obj.authority_level = to_auth
    baton_obj.ttl -= 1

    if baton_obj.sequence:
        baton_obj.sequence_index += 1

    return baton_obj


def prove_round_trip(baton: Union[DirectionalBaton, Dict[str, Any]]) -> Tuple[bool, str]:
    """Prove if a directional baton completed its intended round trip back to origin."""
    if isinstance(baton, dict):
        baton_obj = DirectionalBaton.from_dict(baton)
    else:
        baton_obj = baton

    if not baton_obj.route_history:
        return False, "No hops recorded in route history."

    origin_stage = baton_obj.origin_stage
    origin_auth = baton_obj.origin_authority
    curr_stage = baton_obj.field_position
    curr_auth = baton_obj.authority_level

    # Check if return path was specified
    if baton_obj.expected_return_path:
        expected_dest = baton_obj.expected_return_path[-1]
        if curr_stage == expected_dest:
            return (
                True,
                f"Round trip verified: reached expected destination stage {expected_dest!r} "
                f"across {len(baton_obj.route_history)} hops.",
            )

    # Check if back to origin stage & authority
    if curr_stage == origin_stage and curr_auth == origin_auth:
        return (
            True,
            f"Round trip verified: returned to origin ({origin_stage}, {origin_auth}) "
            f"across {len(baton_obj.route_history)} hops.",
        )

    # Check if sequence completed
    if baton_obj.sequence and baton_obj.sequence_index >= len(baton_obj.sequence):
        return (
            True,
            f"Sequence execution verified: completed all {len(baton_obj.sequence)} steps "
            f"({format_sequence([normalize_direction(s) for s in baton_obj.sequence])}).",
        )

    return (
        False,
        f"Round trip incomplete: currently at ({curr_stage}, {curr_auth}), "
        f"origin was ({origin_stage}, {origin_auth}). Hops completed: {len(baton_obj.route_history)}.",
    )


def simulate_sequence_execution(
    sequence: Union[str, Sequence[str]],
    origin_stage: str = "intent",
    origin_authority: str = "orchestrator",
    stages: Optional[List[str]] = None,
    authority_chain: Optional[List[str]] = None,
    machine: str = "box-a",
    agent: str = "coach",
) -> DirectionalBaton:
    """Simulate execution of a full directional sequence to prove deterministic behavior."""
    dirs = parse_sequence(sequence)
    baton = DirectionalBaton(
        direction=dirs[0].value if dirs else DpadDirection.FORWARD.value,
        field_position=origin_stage,
        authority_level=origin_authority,
        sequence=[d.value for d in dirs],
        sequence_index=0,
        origin_stage=origin_stage,
        origin_authority=origin_authority,
        origin_machine=machine,
        origin_agent=agent,
    )

    for _ in range(len(dirs)):
        advance_directional_baton(
            baton,
            machine=machine,
            agent=agent,
            stages=stages,
            authority_chain=authority_chain,
        )

    return baton
