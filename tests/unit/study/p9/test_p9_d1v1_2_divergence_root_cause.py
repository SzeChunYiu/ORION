"""Pin the D1 v1.2 divergence diagnosis to the part of it that is not local weather.

An earlier version of this file asserted that the archived accuracy reproduces.
It does here and does not in CI -- which is the phenomenon being diagnosed, so
asserting it turned the finding into a flake. The claim does not need it.

What the diagnosis actually rests on is arithmetic on the protected split:
OBSTRUCTION is exactly half of it, so the archived 0.5 is the modal class prior
rather than a measurement; the gap to the locked replay's 0.75 is exactly a
quarter of the split; and a quarter of 128 is the 32 cases sitting on the
decision boundary. None of that depends on which solver ran.

Which side a given environment lands on is reported by the diagnostic and
checked here only to be one of the two known values -- a third value would mean
something else is going on and should fail.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
DIAGNOSTIC = ROOT / "papers/orion-19-structured-epistemic-learning/diagnose_d1v1_2_divergence.py"
RECEIPT = ROOT / (
    "papers/orion-19-structured-epistemic-learning/evidence/"
    "P9_D1V1_2_DIVERGENCE_ROOT_CAUSE_2026-08-23.json"
)


@pytest.fixture(scope="module")
def fresh() -> dict:
    result = subprocess.run(
        [sys.executable, str(DIAGNOSTIC)], capture_output=True, text=True, cwd=ROOT
    )
    if result.returncode == 3:
        pytest.skip(f"diagnostic could not run: {result.stdout}")
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_the_archived_value_is_a_class_prior_not_a_measurement(fresh: dict) -> None:
    counts = fresh["label_counts"]
    assert counts["OBSTRUCTION"] * 2 == sum(counts.values())
    assert fresh["checks"]["the_archived_value_equals_the_modal_class_prior"] is True


def test_the_gap_between_the_two_values_is_the_boundary_set(fresh: dict) -> None:
    assert fresh["checks"]["the_gap_between_the_two_reported_values_is_a_quarter_of_the_split"] is True
    assert fresh["checks"]["a_quarter_of_the_split_is_exactly_thirty_two_cases"] is True


def test_this_environment_lands_on_one_of_the_two_known_values(fresh: dict) -> None:
    """A third value would not be this phenomenon and should not pass quietly."""
    observed = fresh["observed_in_this_environment"]
    assert observed["matches"] in ("ARCHIVED", "LOCKED_REPLAY"), observed


def test_the_responsive_arms_are_not_swept_up_by_the_diagnosis(fresh: dict) -> None:
    """The no-alarm case: a diagnosis that calls every arm degenerate diagnoses nothing."""
    for family in ("TYPED_RELATIONAL", "UNTYPED_PAIR"):
        assert fresh["arms"][family]["unresponsive"] is False


def test_the_committed_receipt_states_the_environment_independent_claims() -> None:
    """The receipt's observed side is local weather; its checks are not."""
    committed = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert committed["all_checks_pass"] is True
    assert committed["authority_scope"] == "DIAGNOSIS_ONLY"
    assert committed["observed_in_this_environment"]["matches"] in ("ARCHIVED", "LOCKED_REPLAY")
