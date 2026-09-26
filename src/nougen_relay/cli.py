"""Console entry point for the ``relay`` command.

The parser and command bodies live in :mod:`nougen_relay.core`, which is the
implementation three machines already run. This module exists so packaging has
a stable target (``relay = "nougen_relay.cli:main"``) that does not move if the
internals are reorganised.
"""

from .core import (
    DEFAULT_DEDUP_EXACT,
    DEFAULT_DEDUP_NEAR,
    DEFAULT_EMBED_URL,
    check_leg_dedup,
    main,
    resolve_dedup_exact,
    resolve_dedup_near,
    resolve_embed_url,
)

__all__ = [
    "main",
    "check_leg_dedup",
    "resolve_dedup_exact",
    "resolve_dedup_near",
    "resolve_embed_url",
    "DEFAULT_DEDUP_EXACT",
    "DEFAULT_DEDUP_NEAR",
    "DEFAULT_EMBED_URL",
]


if __name__ == "__main__":
    raise SystemExit(main())
