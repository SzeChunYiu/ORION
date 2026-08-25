from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


RUNNER = Path(__file__).with_name("run_p4_des_01.py")
SPEC = importlib.util.spec_from_file_location("p4_des_runner", RUNNER)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_contradiction_dominates_semantic_composition() -> None:
    evidence = {"1": [{"label": "SUPPORT"}], "2": [{"label": "CONTRADICT"}]}
    assert MODULE.compose_verdict(evidence) == "CONTRADICT"
    assert MODULE.compose_verdict({}) == "NOT_ENOUGH_INFO"


def test_unavailable_donors_are_not_replaced() -> None:
    obligations = {name: True for name in MODULE.OBLIGATIONS}
    assert MODULE.terminal("SUPPORT", obligations, "CONFIDENCE_ONLY") == "CANNOT_CHECK_ARM_UNAVAILABLE"
    assert MODULE.terminal("SUPPORT", obligations, "IDEAL_TYPED_PRODUCT") == "CANNOT_CHECK_ARM_UNAVAILABLE"


def test_noncompensatory_and_evidence_only_diverge() -> None:
    obligations = {name: True for name in MODULE.OBLIGATIONS}
    obligations["evidence_independence"] = False
    assert MODULE.terminal("SUPPORT", obligations, "EVIDENCE_ONLY") == "PROMOTE"
    assert MODULE.terminal("SUPPORT", obligations, "DYNAMIC_NONCOMPENSATORY") == "CANNOT_CHECK"
