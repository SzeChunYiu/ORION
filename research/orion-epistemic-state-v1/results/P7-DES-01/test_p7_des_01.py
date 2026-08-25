from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


RUNNER = Path(__file__).with_name("run_p7_des_01.py")
SPEC = importlib.util.spec_from_file_location("p7_des_runner", RUNNER)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_normalization_retains_all_public_internal_cases() -> None:
    regime = {
        "standard_rows": [{"term": "x", "condition": "c", "gold": "TRANSPORT", "WITNESS_AWARE": "TRANSPORT", "VALUE_ONLY": "TRANSPORT", "ALWAYS_REOPEN": "REOPEN"}],
        "wine_rows": [{"id": "w", "gold": "CANNOT_CHECK", "WITNESS_AWARE": "CANNOT_CHECK", "VALUE_ONLY": "TRANSPORT", "ALWAYS_REOPEN": "REOPEN"}],
    }
    objective = {
        "cells": [{"id": "o", "gold": "REOPEN"}],
        "systems": {name: {"rows": [{"id": "o", "predicted": "REOPEN"}]} for name in ("WITNESS_AWARE", "VALUE_ONLY", "ALWAYS_REOPEN")},
    }
    rows = MODULE.normalize(regime, objective)
    assert len(rows) == 3
    assert {row["domain"] for row in rows} == {"ONTOLOGY_STANDARD", "TABULAR_LABEL_REGIME", "OBJECTIVE_CHANGE"}


def test_exact_containment_is_not_implicitly_witness_aware() -> None:
    assert "EXACT_CONTAINMENT_DONOR" not in {"WITNESS_AWARE", "VALUE_ONLY", "ALWAYS_REOPEN"}
