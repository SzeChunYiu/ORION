from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

RUNNER = Path(__file__).with_name("run_p14_des_01.py")
SPEC = importlib.util.spec_from_file_location("p14_des_runner", RUNNER)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_terminal_preserves_frozen_p14d_blocker() -> None:
    assert MODULE.TERMINAL == "P14D_EXTERNAL_ACQUISITION_BLOCKED"


def test_claim_ceiling_forbids_causal_authority() -> None:
    assert "ZERO_UNSEEN_INCIDENTS_EXECUTED" in MODULE.CEILING
    assert "NO_CAUSAL_GOVERNANCE" in MODULE.CEILING
