#!/usr/bin/env python3
"""P4 V2 independent headline reproduction wrapper.

The V1 reproducer is intentionally independent of the protected evaluator. V2
keeps that implementation but derives the panel IDs from the exact repaired
subject rather than carrying the earlier six-ID tuple in the harness source.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

from orion.benchmarks.authority_external import FROZEN_AUTHORITY_BASELINE_IDS

_HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("p4_independent_reproduce_v1", _HERE / "independent_reproduce.py")
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load frozen P4 V1 independent reproducer")
_v1 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_v1)
_v1.PANEL_IDS = tuple(FROZEN_AUTHORITY_BASELINE_IDS)

if __name__ == "__main__":
    raise SystemExit(_v1.main())
