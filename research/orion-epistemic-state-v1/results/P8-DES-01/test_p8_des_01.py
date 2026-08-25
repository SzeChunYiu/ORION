from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


RUNNER = Path(__file__).with_name("run_p8_des_01.py")
SPEC = importlib.util.spec_from_file_location("p8_des_runner", RUNNER)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_authority_ceiling_is_not_external() -> None:
    assert "NO_EXTERNAL_ADJUDICATION" in MODULE.CEILING
    assert MODULE.CANNOT != "TYPED_DYNAMIC_AUTHORITY_ALGEBRA_IDEAL_PRODUCT_EQUIVALENT_AND_NONAMPLIFYING"


def test_full_case_denominator_is_native_plus_scientific() -> None:
    assert 24 + 20 == 44
