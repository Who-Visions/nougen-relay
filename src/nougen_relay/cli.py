"""Console entry point for the ``relay`` command.

The parser and command bodies live in :mod:`nougen_relay.core`, which is the
implementation three machines already run. This module exists so packaging has
a stable target (``relay = "nougen_relay.cli:main"``) that does not move if the
internals are reorganised.
"""

from .core import main

__all__ = ["main"]


if __name__ == "__main__":
    raise SystemExit(main())
