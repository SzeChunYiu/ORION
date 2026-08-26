from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from copy import deepcopy

import pytest

from orion.study.p11.wide_panel_revalidation import (
    NOT_REPLICATED,
    PRECONDITION_FAILED,
    SUPPORTED,
    adjudicate_scientific_payload,
)


import pytest

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers" / "orion-21-state-as-computation"
RUNNER = PAPER / "run_p11i_wide_high_width_replication_v1.py"
PROTOCOL = PAPER / "P11I_WIDE_HIGH_WIDTH_REPLICATION_PROTOCOL_V1.md"
PREFLIGHT = PAPER / "P11I_PREFLIGHT_ATTAINABILITY_V1.json"
RESULT = PAPER / "P11I_WIDE_HIGH_WIDTH_REPLICATION_RESULT_V1.json"
REVALIDATION = PAPER / "P11I_REVALIDATION_RECEIPT_V1_1.json"


def _runner():
    spec = importlib.util.spec_from_file_location("p11i_test_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_protocol_is_a_complete_wide_factorial_frozen_before_outcome() -> None:
    runner = _runner()
    assert runner.STATE_WIDTHS == (3, 7)
    assert runner.BANK_GEOMETRIES == ((14, 2), (14, 3), (19, 3))
    assert len(runner.LADDER) == 6
    assert set(runner.LADDER) == {
        (d, s, r)
        for r in runner.STATE_WIDTHS
        for d, s in runner.BANK_GEOMETRIES
    }
    assert len(runner.SEEDS) == len(set(runner.SEEDS)) == 3
    assert "before executing any P11I seed" in PROTOCOL.read_text(encoding="utf-8")
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    assert preflight["outcome_accessed"] is False
    assert preflight["assessment"] == "PROSPECTIVE_REPLICATION_FALSIFIABLE_ON_FRESH_SEEDS"


def test_result_if_present_is_worst_cell_noncompensatory_and_replayed() -> None:
    if not RESULT.exists():
        pytest.skip("P11I execution has not been committed")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    payload = result["scientific_payload"]
    assert payload["independent_unit"] == "execution_seed_x_bank_geometry"
    assert payload["n_high_width_units"] == 9
    assert payload["n_matched_low_width_controls"] == 9
    assert len(payload["high_width_units"]) == 9
    assert len(payload["low_width_controls"]) == 9
    assert all(all(unit["gates"].values()) for unit in payload["high_width_units"])
    assert all(row["attack_live_at_low_width"] for row in payload["low_width_controls"])
    assert all(payload["instrument_gates"].values())
    assert payload["scientific_units_pass"] is True
    assert payload["scientific_terminal"] == runner_terminal()
    assert result["terminal"] == runner_terminal()
    assert result["replay"]["fresh_python_subprocesses"] == 2
    assert result["replay"]["subprocesses_successful"] is True
    assert result["replay"]["byte_identical"] is True
    assert result["replay"]["first_sha256"] == result["replay"]["second_sha256"]


def runner_terminal() -> str:
    return "P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL"


def test_historical_adverse_results_remain_immutable() -> None:
    p11d_path = PAPER / "P11D_SPARSE_DECODER_RESULT_RECEIPT_V1.json"
    p11h_path = PAPER / "P11H_POOLED_SPARSITY_LADDER_RESULT_V1.json"
    p11d = json.loads(p11d_path.read_text())
    p11h = json.loads(p11h_path.read_text())
    assert p11d["terminal"] == "P11D_SPARSE_DECODER_GAP_NOT_MET"
    assert p11h["terminal"] == "P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED"
    assert hashlib.sha256(p11d_path.read_bytes()).hexdigest() == (
        "c24a89813342e0bc7ca09b2b5d5a23654f7c59b948f2a37c432d7ced055518b9"
    )
    assert hashlib.sha256(p11h_path.read_bytes()).hexdigest() == (
        "8436ff99ddec0ab11a16e1ac49a924f0d7c9019998cfc42e8275f71a2db39305"
    )


def test_revalidation_counts_three_rng_replicates_not_nine_cells() -> None:
    receipt = json.loads(REVALIDATION.read_text(encoding="utf-8"))
    adjudication = receipt["adjudication"]
    assert adjudication["independent_unit"] == "execution_seed"
    assert adjudication["n_independent_rng_replicates"] == 3
    assert adjudication["fixed_geometry_strata_per_replicate"] == 3
    assert adjudication["n_prespecified_seed_x_geometry_cells"] == 9
    assert adjudication["terminal"] == SUPPORTED


def test_each_terminal_is_responsive_to_a_raw_measurement_or_replay_failure() -> None:
    scientific = json.loads(RESULT.read_text(encoding="utf-8"))["scientific_payload"]
    assert adjudicate_scientific_payload(
        scientific, byte_identical_replay=True
    )["terminal"] == SUPPORTED

    failed_cell = deepcopy(scientific)
    failed_cell["high_width_units"][0]["compiled_at_64"] = 0.0
    assert adjudicate_scientific_payload(
        failed_cell, byte_identical_replay=True
    )["terminal"] == NOT_REPLICATED

    dead_attack = deepcopy(scientific)
    dead_attack["low_width_controls"][0]["pooled_best_below_256"] = 0.0
    assert adjudicate_scientific_payload(
        dead_attack, byte_identical_replay=True
    )["terminal"] == PRECONDITION_FAILED

    assert adjudicate_scientific_payload(
        scientific, byte_identical_replay=False
    )["terminal"] == PRECONDITION_FAILED
