"""Make the standalone visualization package importable in its documented test lane."""

from __future__ import annotations

import sys
from pathlib import Path


VISUALIZATION_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(VISUALIZATION_SRC))
