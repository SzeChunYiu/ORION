from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


RUNNER = Path(__file__).with_name("run_des_collision_01.py")
SPEC = importlib.util.spec_from_file_location("des_collision_runner", RUNNER)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
ROOT = Path(__file__).resolve().parents[4]
MODEL = MODULE.load_model(ROOT)


def test_frozen_cartesian_denominator_is_complete() -> None:
    rows = MODULE.enumerate_rows(MODEL)
    assert len(rows) == 3 * 2 * 2 * 2 * 3 * 2 == 144
    assert len({row["case_id"] for row in rows}) == 144


def test_one_axis_collision_proves_label_nonreconstruction() -> None:
    rows = MODULE.enumerate_rows(MODEL)
    collisions, _, all_pairs = MODULE.collision_rows(rows)
    assert all_pairs == 10296
    assert collisions
    assert min(row["axis_hamming_distance"] for row in collisions) == 1
    assert any(
        row["legacy_terminal"] == "BLOCKED"
        and row["left_action"] != row["right_action"]
        for row in collisions
    )


def test_admissible_state_stops_and_blockers_are_noncompensatory() -> None:
    rows = MODULE.enumerate_rows(MODEL)
    admissible = [row for row in rows if row["legacy_terminal"] == "ADMISSIBLE"]
    assert admissible
    assert {row["dynamic_next_action"] for row in admissible} == {"STOP"}
    assert any(row["legacy_terminal"] == "CANNOT_CHECK" for row in rows)
    assert any(row["legacy_terminal"] == "BLOCKED" for row in rows)
