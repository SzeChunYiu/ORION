#!/usr/bin/env python3
"""Tests for the post-failure R23 parent-replay diagnostic."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


DIAGNOSTIC = Path(__file__).with_name("diagnose_r23_parent_replay_r24.py")
SLURM = Path(__file__).with_name("ORION02_R24_R23_PARENT_DIAGNOSTIC.slurm")
SYSTEM_PINNED_SLURM = Path(__file__).with_name(
    "ORION02_R24_R23_PARENT_DIAGNOSTIC_SYSTEM_PINNED.slurm"
)


def load_diagnostic():
    spec = importlib.util.spec_from_file_location("orion02_r24_parent_diagnostic", DIAGNOSTIC)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R24 parent diagnostic")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StructuredDiffTests(unittest.TestCase):
    def test_recursive_diff_reports_exact_paths_and_numeric_delta(self) -> None:
        module = load_diagnostic()
        frozen = {"a": [1, {"x": 0.125}], "only_frozen": True}
        replay = {"a": [1, {"x": 0.126}], "only_replay": "new"}
        summary = module.structured_diff(frozen, replay)
        self.assertEqual(summary["difference_count"], 3)
        self.assertEqual(summary["numeric_difference_count"], 1)
        self.assertAlmostEqual(summary["max_abs_numeric_difference"], 0.001)
        self.assertEqual(
            [row["path"] for row in summary["samples"]],
            ["$.a[1].x", "$.only_frozen", "$.only_replay"],
        )

    def test_identical_payloads_have_zero_differences(self) -> None:
        module = load_diagnostic()
        payload = {"z": [1, 2.0, None], "a": {"b": False}}
        summary = module.structured_diff(payload, payload)
        self.assertEqual(summary["difference_count"], 0)
        self.assertEqual(summary["samples"], [])
        self.assertEqual(summary["max_abs_numeric_difference"], 0.0)


class DiagnosticIsolationTests(unittest.TestCase):
    def test_diagnostic_never_executes_the_r24_policy(self) -> None:
        source = DIAGNOSTIC.read_text() if DIAGNOSTIC.exists() else ""
        self.assertNotIn("policy_phase(", source)
        self.assertNotIn("execute(subject_repo", source)
        self.assertIn("r23.execute(", source)

    def test_slurm_uses_allocated_compute_and_binds_source(self) -> None:
        source = SLURM.read_text() if SLURM.exists() else ""
        self.assertIn("#SBATCH --cpus-per-task=2", source)
        self.assertIn("EXPECTED_SOURCE_COMMIT", source)
        self.assertIn("diagnose_r23_parent_replay_r24.py", source)
        self.assertNotIn("fiberguard_pmlb_arm_conditional_r24.py --subject-repo", source)

    def test_system_pinned_profile_changes_only_the_interpreter(self) -> None:
        baseline = SLURM.read_text() if SLURM.exists() else ""
        profile = SYSTEM_PINNED_SLURM.read_text() if SYSTEM_PINNED_SLURM.exists() else ""
        self.assertIn(
            "PYTHON=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3",
            profile,
        )
        for line in (
            "export PYTHONHASHSEED=0",
            "export OPENBLAS_NUM_THREADS=1",
            "export OMP_NUM_THREADS=1",
            "export MKL_NUM_THREADS=1",
            'test "$(git rev-parse HEAD)" = "$EXPECTED_SOURCE_COMMIT"',
        ):
            self.assertIn(line, baseline)
            self.assertIn(line, profile)
        self.assertIn("diagnose_r23_parent_replay_r24.py", profile)


if __name__ == "__main__":
    unittest.main()
