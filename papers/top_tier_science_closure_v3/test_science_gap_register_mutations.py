"""Adversarial mutation tests for the science-gap register validator.

`top-tier-science-gap-register.yml` runs this module, but it did not exist in the tree,
so the workflow failed on an ImportError rather than on anything about the register.
The step was declaring a guard the repository did not have.

The guard matters. A validator is only worth its green: if it can be made to pass by
weakening a rule, the green means nothing. These tests mutate the register in ways that
*must* be caught, and assert the validator catches each one. A widening of
`BOUNDARY_TOKENS` that made a purely positive boundary acceptable would fail
`test_positive_boundary_is_rejected` here.

Each test copies the register to a temp file, mutates the copy, and points the validator
at it, so the committed register is never touched.
"""
from __future__ import annotations

import copy
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
VALIDATOR = HERE / "validate_science_gap_register.py"
REGISTER = HERE / "science_gap_register_v3.json"


def run_validator(register_path: pathlib.Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", "--register", str(register_path)],
        capture_output=True, text=True,
    )
    if proc.returncode == 2 and "unrecognized arguments" in proc.stderr:
        # Validator takes no --register flag; mutate in place under a temp copy of the dir.
        raise unittest.SkipTest("validator does not accept --register")
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode, {"_stdout": proc.stdout, "_stderr": proc.stderr}


class MutationTests(unittest.TestCase):
    """Every mutation here is one a reviewer would object to. The validator must catch it."""

    def setUp(self) -> None:
        self.register = json.loads(REGISTER.read_text(encoding="utf-8"))
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _validate(self, mutated: dict) -> tuple[int, dict]:
        # The validator also checks for the register's companion documents, so the
        # whole directory is copied and only the register is mutated. Copying just the
        # validator and the register produced spurious DOCUMENT_MISSING findings and a
        # failing control -- a harness defect, not a validator one.
        d = pathlib.Path(self.tmp.name) / "pkg"
        if not d.exists():
            shutil.copytree(HERE, d)
        (d / "science_gap_register_v3.json").write_text(
            json.dumps(mutated, indent=2), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(d / "validate_science_gap_register.py"), "--json"],
            capture_output=True, text=True, cwd=str(d))
        try:
            return proc.returncode, json.loads(proc.stdout)
        except json.JSONDecodeError:
            return proc.returncode, {"_stdout": proc.stdout[:400], "_stderr": proc.stderr[:400]}

    def _codes(self, report: dict) -> set[str]:
        return {f.get("code") for f in report.get("findings", [])}

    # --- control: the committed register must pass -------------------------
    def test_unmutated_register_passes(self) -> None:
        """The no-alarm case. If this fails, every other assertion here is meaningless."""
        rc, rep = self._validate(self.register)
        self.assertEqual(rc, 0, f"committed register should validate GREEN, got {rep}")
        self.assertEqual(rep.get("status"), "GREEN")
        self.assertEqual(rep.get("finding_count"), 0)

    # --- the mutation that guards the boundary vocabulary ------------------
    def test_positive_boundary_is_rejected(self) -> None:
        """A boundary stating no limit must be caught.

        This is the specific guard on BOUNDARY_TOKENS: widening that set to admit a
        purely positive boundary would surface here.
        """
        m = copy.deepcopy(self.register)
        m["papers"][0]["binding_boundary"] = (
            "The method transfers cleanly to every production system and domain."
        )
        rc, rep = self._validate(m)
        self.assertNotEqual(rc, 0, "a boundary with no limiting token must fail")
        self.assertIn("BOUNDARY_NOT_ADVERSE", self._codes(rep))

    def test_empty_boundary_is_rejected(self) -> None:
        m = copy.deepcopy(self.register)
        m["papers"][0]["binding_boundary"] = ""
        rc, rep = self._validate(m)
        self.assertNotEqual(rc, 0, "an empty boundary must fail")

    # --- terminal integrity ------------------------------------------------
    def test_identical_positive_and_adverse_terminal_is_rejected(self) -> None:
        """A paper whose success and failure terminals coincide cannot be falsified."""
        m = copy.deepcopy(self.register)
        m["papers"][0]["adverse_terminal"] = m["papers"][0]["positive_terminal"]
        rc, rep = self._validate(m)
        self.assertNotEqual(rc, 0, "coinciding terminals must fail")

    def test_duplicated_adverse_terminal_is_rejected(self) -> None:
        """Two papers sharing an adverse terminal makes attribution ambiguous."""
        m = copy.deepcopy(self.register)
        m["papers"][1]["adverse_terminal"] = m["papers"][0]["adverse_terminal"]
        rc, rep = self._validate(m)
        self.assertNotEqual(rc, 0, "duplicate adverse terminals must fail")

    # --- structural integrity ---------------------------------------------
    def test_dropped_paper_is_rejected(self) -> None:
        """Silently shrinking the register below its declared paper count must fail."""
        m = copy.deepcopy(self.register)
        m["papers"] = m["papers"][:-1]
        rc, rep = self._validate(m)
        self.assertNotEqual(rc, 0, "a register short of its declared count must fail")


if __name__ == "__main__":
    unittest.main(verbosity=2)
