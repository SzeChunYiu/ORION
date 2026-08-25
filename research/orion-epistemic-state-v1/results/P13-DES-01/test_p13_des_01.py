#!/usr/bin/env python3
"""Focused tests for the frozen P13-DES-01 internal replay."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
RUNNER = HERE / "run_p13_des_01.py"
FREEZE_HEAD = "FREEZE_HEAD_FOR_FOCUSED_TEST"
CORE = (
    "CASE_OUTCOMES_V1.json",
    "PRIMARY_RESULT_V1.json",
    "IDEAL_DONOR_RESULT_V1.json",
    "NEGATIVE_CONTROLS_V1.json",
    "TRANSFER_RESULT_V1.json",
)


def load_runner():
    spec = importlib.util.spec_from_file_location("p13_des_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class P13DES01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()

    def execute(self, out: Path) -> None:
        subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--input-dir",
                str(HERE),
                "--out",
                str(out),
                "--execution-head",
                FREEZE_HEAD,
                "--executed-at",
                "2026-08-25T19:00:00Z",
                "--slurm-job-id",
                "TEST",
                "--platform-label",
                "TEST",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_axis_policy_boundaries(self) -> None:
        base = {
            "identifiability": "KNOWN_TRUE",
            "obligations": "SATISFIED",
            "support": "COMPLETE",
            "defeaters": "ABSENT",
            "custody": "EXTERNAL",
            "authority": "PRESENT",
        }
        expected = {
            ("identifiability", "KNOWN_FALSE"): "DISCRIMINATE",
            ("identifiability", "CANNOT_CHECK"): "DISCRIMINATE",
            ("obligations", "UNRESOLVED"): "ACQUIRE_EVIDENCE",
            ("support", "ABSENT"): "ACQUIRE_EVIDENCE",
            ("defeaters", "PRESENT"): "REVALIDATE",
            ("custody", "NOT_EXTERNAL"): "OBTAIN_EXTERNAL_CUSTODY",
            ("custody", "CANNOT_CHECK"): "OBTAIN_EXTERNAL_CUSTODY",
            ("authority", "ABSENT"): "REVALIDATE",
        }
        self.assertEqual(self.runner.dynamic_action(base), "STOP")
        for (axis, value), action in expected.items():
            mutated = {**base, axis: value}
            self.assertEqual(self.runner.dynamic_action(mutated), action)

    def test_complete_control_and_retained_cannot_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.execute(out)
            primary = json.loads((out / "PRIMARY_RESULT_V1.json").read_text())
            cases = json.loads((out / "CASE_OUTCOMES_V1.json").read_text())
            controls = json.loads((out / "NEGATIVE_CONTROLS_V1.json").read_text())
            self.assertEqual(primary["metrics"]["dynamic_state_correct"], 144)
            self.assertEqual(primary["metrics"]["terminal_only_correct"], 97)
            self.assertEqual(primary["metrics"]["terminal_only_planning_regret"], 47)
            self.assertEqual(cases["cannot_check_planner_cells"], 432)
            self.assertEqual(cases["executed_planner_cells"], 288)
            self.assertTrue(controls["all_pass"])
            self.assertEqual(
                primary["exact_terminal"],
                "BOUNDED_DYNAMIC_STATE_BEATS_TERMINAL_ONLY__FULL_P13_CONTROL_CANNOT_CHECK",
            )
            self.assertFalse(primary["intended_full_positive_terminal_attained"])

    def test_core_replay_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            left, right = Path(first), Path(second)
            self.execute(left)
            self.execute(right)
            for name in CORE:
                self.assertEqual((left / name).read_bytes(), (right / name).read_bytes(), name)


if __name__ == "__main__":
    unittest.main()
