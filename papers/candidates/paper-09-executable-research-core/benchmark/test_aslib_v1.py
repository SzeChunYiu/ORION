from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p9_aslib_v1", HERE / "run_aslib_v1.py")
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def test_frozen_inputs_match_and_align() -> None:
    protocol = json.loads((HERE / "ASLIB_SAT11_PROTOCOL_V1.json").read_text())
    data = RUNNER.load_scenario(protocol)

    assert len(data["keys"]) == 296
    assert data["x"].shape == (296, 115)
    assert data["runtime"].shape == (296, 15)
    assert data["solved"].shape == (296, 15)
    assert sorted(np.unique(data["folds"]).tolist()) == list(range(1, 11))


def test_input_digest_mismatch_stops_reproduction(monkeypatch: pytest.MonkeyPatch) -> None:
    protocol = json.loads((HERE / "ASLIB_SAT11_PROTOCOL_V1.json").read_text())
    protocol["source"]["files"]["cv.arff"] = "0" * 64
    with pytest.raises(ValueError, match="input digest mismatch for cv.arff"):
        RUNNER.load_scenario(protocol)


def test_committed_result_satisfies_only_the_numerical_gate() -> None:
    result_path = HERE.parent / "results" / "ASLIB_SAT11_HAND_ALGO_V1.json"
    result = json.loads(result_path.read_text())

    assert result["numerical_standalone_gate"]["passes"] is True
    assert result["primary_comparison"]["estimate"] >= 0.20
    assert result["primary_comparison"]["paired_bootstrap_95_percent_interval"][0] > 0.0
    assert result["primary_comparison"]["rf_solved_retention"] >= 0.95
    assert result["disposition"] == "PENDING_NEAREST_WORK_AND_OWNERSHIP_REVIEW"
