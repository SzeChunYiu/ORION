"""Make clean-room modules importable under repository-root pytest collection."""

from __future__ import annotations

import sys
from pathlib import Path


CLEANROOM = Path(__file__).resolve().parent
if str(CLEANROOM) not in sys.path:
    sys.path.insert(0, str(CLEANROOM))
