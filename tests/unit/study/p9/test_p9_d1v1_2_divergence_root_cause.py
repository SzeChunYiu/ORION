"""Pin the D1 v1.2 divergence diagnosis to the arithmetic that makes it a diagnosis.

The claim is not "the numbers differ across environments" -- that was already
known. It is that TYPED_SERIALIZED_BAG is a constant predictor whose accuracy is
a class prior, that exactly a quarter of the protected split sits on the decision
boundary, and that the runner-up is correct on all of it, so 0.5 + 32/128 = 0.75
reaches the locked replay's value exactly. Each of those is asserted separately,
because the conclusion only follows if all of them hold.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
DIAGNOSTIC = ROOT / "papers/paper-09-structured-epistemic-learning/diagnose_d1v1_2_divergence.py"
RECEIPT = ROOT / (
    "papers/paper-09-structured-epistemic-learning/evidence/"
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


def test_the_arm_is_unresponsive_not_merely_wrong(fresh: dict) -> None:
    arm = fresh["arms"]["TYPED_SERIALIZED_BAG"]
    assert arm["distinct_predictions"] == 1
    assert arm["unresponsive"] is True
    assert arm["accuracy"] == 0.5


def test_a_quarter_of_the_split_is_on_the_boundary(fresh: dict) -> None:
    arm = fresh["arms"]["TYPED_SERIALIZED_BAG"]
    assert arm["protected_cases"] == 128
    assert arm["boundary_cases"] == 32
    assert arm["boundary_fraction"] == 0.25


def test_flipping_the_boundary_set_lands_exactly_on_the_replayed_value(fresh: dict) -> None:
    arm = fresh["arms"]["TYPED_SERIALIZED_BAG"]
    assert arm["boundary_cases_whose_runner_up_is_correct"] == arm["boundary_cases"]
    assert arm["accuracy_if_boundary_set_flips"] == 0.75 == fresh["locked_replay_accuracy"]


def test_transcript_bag_is_degenerate_the_same_way(fresh: dict) -> None:
    """Naming one degenerate arm and not the other would understate the problem."""
    assert fresh["arms"]["TRANSCRIPT_BAG"]["unresponsive"] is True


def test_the_responsive_arms_are_not_swept_up_by_the_diagnosis(fresh: dict) -> None:
    """The no-alarm case: a diagnosis that calls every arm degenerate diagnoses nothing."""
    for family in ("TYPED_RELATIONAL", "UNTYPED_PAIR"):
        assert fresh["arms"][family]["unresponsive"] is False


def test_the_committed_receipt_still_states_the_diagnosis(fresh: dict) -> None:
    """Environment-dependent numbers may move; the structural claims may not."""
    committed = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert committed["all_checks_pass"] is True
    assert committed["authority_scope"] == "DIAGNOSIS_ONLY"
    arm = committed["arms"]["TYPED_SERIALIZED_BAG"]
    assert arm["distinct_predictions"] == 1
    assert arm["boundary_cases"] == 32
    assert arm["accuracy_if_boundary_set_flips"] == 0.75
