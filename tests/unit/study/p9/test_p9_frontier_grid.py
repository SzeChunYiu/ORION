"""The P9-U-T3 prospective frontier grid, and the three values it can return.

The grid has no outcomes today and the honest verdict over it is ``CANNOT_CHECK``
with the denominator printed. A detector that has only ever returned one value
is not known to be able to return the others, so every test below drives the
assessment to a different verdict on a synthetic outcome file. The synthetic
files are fixtures for the *detector*; none of them is evidence about P9.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from orion.programme.records import Outcome
from orion.study.p9 import frontier_grid as grid

REPO_ROOT = Path(__file__).resolve().parents[4]


def _quality(representation: str, scale_index: int) -> tuple[int, int]:
    """A synthetic surface where one representation reaches the target sooner."""

    if representation == "TYPED_TUPLE_SET":
        correct = 100 if scale_index >= 1 else 40
    elif representation == "FLAT_TEXT_SERIALIZATION":
        correct = 100 if scale_index >= 3 else 40
    else:
        correct = 40
    return 128, correct


def _full_grid(**overrides: dict[str, object]) -> dict[str, grid.CellOutcome]:
    cells: dict[str, grid.CellOutcome] = {}
    for key in grid.declared_cells():
        k_part, representation, family, scale, _budget, block = key.split("|")
        assert k_part and block
        scale_index = grid.SCALE_LADDERS[family].index(scale)
        n_items, correct = _quality(representation, scale_index)
        cells[key] = grid.CellOutcome(
            key=key, status="EXECUTED", n_items=n_items, n_verified_correct=correct
        )
    for key, value in overrides.items():
        cells[key] = value  # type: ignore[assignment]
    return cells


def _flat_grid(correct: int) -> dict[str, grid.CellOutcome]:
    return {
        key: grid.CellOutcome(
            key=key, status="EXECUTED", n_items=128, n_verified_correct=correct
        )
        for key in grid.declared_cells()
    }


def test_the_declared_grid_is_deterministic_complete_and_collision_free():
    first = grid.declared_cells()
    assert first == grid.declared_cells()
    assert len(first) == grid.DECLARED_CELL_COUNT == 1344
    assert len(set(first)) == len(first)
    for key in first:
        assert key.count("|") == 5


def test_the_runner_digest_matches_the_frozen_twin():
    twin = json.loads((REPO_ROOT / grid.FREEZE_TWIN).read_text(encoding="utf-8"))
    assert twin["parameters_sha256"] == grid.frozen_digest()
    assert twin["parameters"] == grid.FROZEN_PARAMETERS
    assert twin["outcome_accessed"] is False
    assert twin["cells_executed_at_freeze_time"] == 0
    grid.verify_against_twin(REPO_ROOT)


def test_the_runner_refuses_to_execute_when_its_constants_have_drifted(tmp_path):
    twin_path = tmp_path / grid.FREEZE_TWIN
    twin_path.parent.mkdir(parents=True, exist_ok=True)
    twin_path.write_text(json.dumps({"parameters_sha256": "sha256:" + "0" * 64}), encoding="utf-8")
    with pytest.raises(grid.FreezeViolation):
        grid.verify_against_twin(tmp_path)


def test_todays_state_is_cannot_check_with_the_denominator_printed():
    payload = grid.assess_grid({})
    assert payload["outcome"] == Outcome.CANNOT_CHECK.value
    assert payload["verdict"] == grid.VERDICT_NO_CELL_EXECUTED
    assert payload["census"]["declared_cells"] == 1344
    assert payload["census"]["cells_executed"] == 0
    assert payload["claimed_crossing_audit"]["exercised"] is False


def test_a_cell_missing_from_the_outcome_file_blocks_rather_than_being_dropped():
    cells = _full_grid()
    dropped = grid.declared_cells()[7]
    del cells[dropped]
    payload = grid.assess_grid(cells)
    assert payload["verdict"] == grid.VERDICT_GRID_INCOMPLETE
    assert payload["outcome"] == Outcome.CANNOT_CHECK.value
    assert payload["census"]["cells_missing_from_outcome_file"] == 1
    assert dropped in payload["missing_cells"]


def test_a_fully_executed_grid_with_no_uncensored_frontier_is_cannot_check_not_pass():
    payload = grid.assess_grid(_flat_grid(correct=40))
    assert payload["verdict"] == grid.VERDICT_NO_EVALUABLE_TEST
    assert payload["outcome"] == Outcome.CANNOT_CHECK.value
    assert payload["crossing_census"]["tests_evaluable"] == 0
    assert payload["crossing_census"]["tests_declared"] > 0


def test_a_grid_whose_every_cell_saturates_has_evaluable_tests_and_zero_crossings():
    payload = grid.assess_grid(_flat_grid(correct=128))
    assert payload["verdict"] == grid.VERDICT_ON_GRID
    assert payload["outcome"] == Outcome.PASS.value
    assert payload["crossing_census"]["tests_evaluable"] > 0
    assert payload["crossing_census"]["crossings_found"] == 0


def test_a_real_crossing_is_detected_and_read_at_declared_ladder_points():
    payload = grid.assess_grid(_full_grid())
    assert payload["verdict"] == grid.VERDICT_ON_GRID
    assert payload["outcome"] == Outcome.PASS.value
    assert payload["crossing_census"]["crossings_found"] > 0
    crossing = next(
        item
        for item in payload["crossings_found"]
        if item["faster"] == "TYPED_TUPLE_SET" and item["slower"] == "FLAT_TEXT_SERIALIZATION"
    )
    assert crossing["faster_frontier"]["value"] in grid.SCALE_LADDERS["QWEN2_5"]
    assert crossing["slower_frontier"]["value"] in grid.SCALE_LADDERS["QWEN2_5"]
    assert crossing["faster_frontier"]["on_grid"] is True
    assert crossing["p_value"] is not None


def test_a_claimed_crossing_over_a_censored_frontier_fails():
    claim = grid.ClaimedCrossing(
        axis="S",
        target=0.95,
        k=1,
        family="QWEN2_5",
        budget=1,
        block="FORMAL_RELATIONAL",
        faster="TYPED_GRAPH_STATE",
        slower="QUERY_MATCHED_INTERFACE",
    )
    payload = grid.assess_grid(_full_grid(), [claim])
    assert payload["verdict"] == grid.VERDICT_OFF_GRID
    assert payload["outcome"] == Outcome.FAIL.value
    assert payload["claimed_crossing_audit"]["claims_checked"] == 1
    assert payload["claimed_crossing_audit"]["claims_off_grid"] == 1


def test_a_claimed_crossing_the_ladder_carries_is_accepted():
    claim = grid.ClaimedCrossing(
        axis="S",
        target=0.7,
        k=1,
        family="QWEN2_5",
        budget=1,
        block="FORMAL_RELATIONAL",
        faster="TYPED_TUPLE_SET",
        slower="FLAT_TEXT_SERIALIZATION",
    )
    payload = grid.assess_grid(_full_grid(), [claim])
    assert payload["claimed_crossing_audit"]["claims_checked"] == 1
    assert payload["claimed_crossing_audit"]["claims_off_grid"] == 0
    assert payload["verdict"] == grid.VERDICT_ON_GRID


def test_a_frontier_is_right_censored_rather_than_extrapolated():
    frontier = grid.scale_frontier(
        _flat_grid(correct=40),
        k=1,
        representation="TYPED_GRAPH_STATE",
        family="QWEN2_5",
        budget=1,
        block="FORMAL_RELATIONAL",
        target=0.95,
    )
    assert frontier.value == grid.RIGHT_CENSORED
    assert frontier.on_grid is False


def test_non_monotone_series_are_flagged_and_not_smoothed():
    cells = _flat_grid(correct=40)
    keys = [
        grid.cell_key(
            k=1,
            representation="TYPED_TUPLE_SET",
            family="QWEN2_5",
            scale=scale,
            budget=1,
            block="FORMAL_RELATIONAL",
        )
        for scale in grid.SCALE_LADDERS["QWEN2_5"]
    ]
    cells[keys[1]] = grid.CellOutcome(
        key=keys[1], status="EXECUTED", n_items=128, n_verified_correct=128
    )
    frontier = grid.scale_frontier(
        cells,
        k=1,
        representation="TYPED_TUPLE_SET",
        family="QWEN2_5",
        budget=1,
        block="FORMAL_RELATIONAL",
        target=0.95,
    )
    assert frontier.value == "1.5B"
    assert frontier.non_monotone is True


def test_a_cell_that_did_not_run_may_not_carry_a_quality():
    with pytest.raises(ValueError):
        grid.CellOutcome(key="x", status="NOT_RUN", n_items=128, n_verified_correct=100)
    with pytest.raises(ValueError):
        grid.CellOutcome(key="x", status="EXECUTED", n_items=None, n_verified_correct=None)
    censored = grid.CellOutcome(key="x", status="INFEASIBLE_RESOURCE", n_items=None, n_verified_correct=None)
    assert censored.quality is None


def test_an_outcome_file_from_a_different_grid_is_refused(tmp_path):
    path = tmp_path / "cells.json"
    path.write_text(
        json.dumps(
            {
                "schema": "P9.UT3FrontierGridOutcomes.v1",
                "parameters_sha256": "sha256:" + "0" * 64,
                "cells": {},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(grid.OutcomeFileError):
        grid.load_outcomes(path)


def test_the_shipped_status_artifact_reports_zero_of_1344():
    payload = json.loads(
        (
            REPO_ROOT
            / "papers/paper-09-structured-epistemic-learning/evidence/"
            "P9_U_T3_FRONTIER_GRID_STATUS_2026-08-21.json"
        ).read_text(encoding="utf-8")
    )
    assert payload["parameters_sha256"] == grid.frozen_digest()
    assert payload["verdict"] == grid.VERDICT_NO_CELL_EXECUTED
    assert payload["outcome"] == Outcome.CANNOT_CHECK.value
    assert payload["census"]["cells_executed"] == 0
    assert payload["census"]["declared_cells"] == 1344
    assert payload["environment_boundary"]["grid_executable_here"] is False


def test_the_module_runs_as_a_subprocess_and_exits_four_for_cannot_check(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "orion.study.p9.frontier_grid",
            "--repo-root",
            str(REPO_ROOT),
            "--output",
            str(tmp_path / "status.json"),
        ],
        cwd=str(REPO_ROOT),
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin:/usr/local/bin"},
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 4, completed.stderr
    written = json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))
    assert written["verdict"] == grid.VERDICT_NO_CELL_EXECUTED


def test_main_requires_its_argv_and_can_print_its_digest(capsys):
    with pytest.raises(TypeError):
        grid.main()  # type: ignore[call-arg]
    assert grid.main(["--print-digest"]) == 0
    assert capsys.readouterr().out.strip() == grid.frozen_digest()
