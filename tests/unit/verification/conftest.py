from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERIFICATION = ROOT / "research" / "verification"
sys.path.insert(0, str(VERIFICATION))
