"""Bind the cross-paper preservation dichotomy to its registered numbers.

The checker discharging its own laws is not enough: a later edit could weaken a
law and still report seven greens. These assertions pin the counts that the V2
theory document quotes, so the document and the artifact cannot drift apart
silently.

They are regression pins, not findings. As V2 section 3.1 records, six of the
seven laws are consequences of the model's own definition of standing and could
not come out otherwise -- 31 is 2**5 - 1, and every required coordinate is
load-bearing by the determination theorem alone. Only
``test_verdict_exposing_donors_are_strictly_weaker`` pins a computed result.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "papers/candidates/cross_paper_preservation_v2/check_preservation_dichotomy_v2.py"


@pytest.fixture(scope="module")
def receipt() -> dict:
    result = subprocess.run(
        [sys.executable, str(CHECKER)], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_every_law_is_discharged(receipt: dict) -> None:
    assert receipt["failures"] == []
    assert receipt["laws_discharged"] == receipt["laws_total"] == 7


def test_determination_holds_over_the_whole_ladder(receipt: dict) -> None:
    law = receipt["laws"]["determination"]
    assert law["pairs_checked"] == 1024
    assert law["states_per_model"] == 32


def test_every_ladder_level_is_load_bearing(receipt: dict) -> None:
    """Forced by the determination theorem; pinned so a broken core is caught, not as evidence."""
    law = receipt["laws"]["ladder_irredundancy"]
    assert law["load_bearing_levels"] == list(receipt["ladder"])
    # The engine must also be able to say "redundant" -- one that never can is
    # not deciding irredundancy, it is asserting it.
    assert law["inert_coordinate_correctly_found_redundant"] is True


def test_partial_repair_never_restores_standing(receipt: dict) -> None:
    """31 = 2**5 - 1 and 211 = sum C(5,k)(2**k - 1): subset combinatorics of the conjunction."""
    law = receipt["laws"]["selective_revalidation"]
    assert law["total_revalidations_restoring_standing"] == 31
    assert law["proper_subset_revalidations_denied"] == 211


def test_ideal_product_ties_the_centralized_system(receipt: dict) -> None:
    """P6.V4.5, P7.V3.6 and P8.V3.10 as one statement, with no exception."""
    assert receipt["laws"]["ideal_product_equivalence"]["centralized_vs_ideal_product_mismatches"] == 0


def test_verdict_exposing_donors_are_strictly_weaker(receipt: dict) -> None:
    """The positive half: the tie is a property of the interface, not of decentralization."""
    law = receipt["laws"]["verdict_composition_insufficiency"]
    assert law["every_stack_observes_all_required_coordinates"] is True
    assert law["ideal_coordinate_exposing_stack_still_decides"] is True
    assert law["informative_stacks_enumerated"] == 196
    assert law["informative_stacks_where_no_join_suffices"] == 96
    assert law["named_witness_blocked"] is True


def test_satisfied_contracts_are_granted(receipt: dict) -> None:
    """The no-alarm case: a rule that refuses everything passes every separation."""
    law = receipt["laws"]["no_alarm_transport_succeeds"]
    assert law["contracts_granted_when_fully_satisfied"] == 243
    assert law["spurious_abstentions"] == 0
