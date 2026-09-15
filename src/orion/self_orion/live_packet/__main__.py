"""Entry point for `python -m orion.self_orion.live_packet`.

The published packet names that exact command in the `execution` block its
fingerprint is taken over, so the command has to keep working -- splitting the
module into a package without this file would break a string the freeze binds.
"""

from __future__ import annotations

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
