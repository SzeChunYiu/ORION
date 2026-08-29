#!/usr/bin/env python3
"""Import smoke check kept separate from mutation tests for CI diagnosis."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PATH = HERE / "validate_science_gap_register.py"
SPEC = importlib.util.spec_from_file_location("science_gap_validator_smoke", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load {PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
findings = MODULE.validate(HERE / "science_gap_register_v3.json", HERE)
if findings:
    raise SystemExit("\n".join(f"{f.code}: {f.message}" for f in findings))
print("SCIENCE GAP VALIDATOR IMPORT: GREEN")
