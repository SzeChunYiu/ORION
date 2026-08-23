from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from orion.study.p12.equal_action_successor import (
    ACTIONS,
    EPISODES_PER_FAMILY,
    N_FAMILIES,
    NOT_SUPPORTED,
    OneSignalObservation,
    SIGMAS,
    SUPPORTED,
    TwoSignalObservation,
    adjudicate,
    build_core,
)
from orion.study.p12.successor_authority import build_active_claim_authority

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers/paper-12-adaptive-state-reasoning"
RESULT = PAPER / "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_RESULT_V1.json"
AUTHORITY = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V2.json"


def test_typed_views_do_not_carry_a_withheld_signal() -> None:
    assert tuple(TwoSignalObservation.__dataclass_fields__) == ("state_signal", "reason_signal")
    assert tuple(OneSignalObservation.__dataclass_fields__) == ("signal",)


def test_core_has_32_family_units_and_identical_actions() -> None:
    core = build_core()
    assert core["independent_unit"] == "family_rng_block"
    assert core["n_independent_units"] == N_FAMILIES == 32
    assert set(family["sigma"] for family in core["families"]) == set(SIGMAS)
    expected = [list(action) for action in ACTIONS]
    observed_actions = {
        tuple(map(tuple, arm["action_set"]))
        for arm in core["subject_identity"]["arms"].values()
    }
    assert observed_actions == {tuple(ACTIONS)}
    expected_counts = {
        regime: EPISODES_PER_FAMILY // 4
        for regime in ("EASY", "ACCESS", "REASON", "BOTH")
    }
    assert all(family["regime_counts"] == expected_counts for family in core["families"])


def test_protected_result_recomputes_and_uses_family_block_uncertainty() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    rebuilt = adjudicate(result["core"], byte_identical_replay=True)
    assert rebuilt["summary"] == result["summary"]
    assert rebuilt["gates"] == result["gates"]
    assert result["terminal"] == SUPPORTED
    assert result["summary"]["n_independent_family_rng_blocks"] == 32
    assert result["replay"]["byte_identical"] is True


def test_mutating_the_effect_or_action_equivalence_forces_negative_terminal() -> None:
    core = build_core()
    no_effect = deepcopy(core)
    for family in no_effect["families"]:
        counts = family["correct_counts"]
        counts["TWO_SIGNAL"] = max(counts["STATE_SIGNAL"], counts["REASON_SIGNAL"])
    assert adjudicate(no_effect, byte_identical_replay=True)["terminal"] == NOT_SUPPORTED

    unequal = deepcopy(core)
    unequal["subject_identity"]["arms"]["STATE_SIGNAL"]["action_set"].pop()
    adjudicated = adjudicate(unequal, byte_identical_replay=True)
    assert adjudicated["gates"]["identical_four_action_sets"] is False
    assert adjudicated["terminal"] == NOT_SUPPORTED


def test_replay_is_a_noncompensatory_gate() -> None:
    assert adjudicate(build_core(), byte_identical_replay=False)["terminal"] == NOT_SUPPORTED


def test_v2_authority_rebuilds_and_keeps_p12a_historical() -> None:
    authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    assert authority == build_active_claim_authority()
    assert authority["active_claim_leaf"]["terminal"] == SUPPORTED
    assert authority["historical_boundary_leaf"]["terminal"] == (
        "P12A_SUPERIORITY_AUTHORITY_WITHHELD"
    )
    assert authority["active_claim_leaf"]["scope"]["independent_family_rng_blocks"] == 32
