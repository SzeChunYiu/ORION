from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from orion.study.p12.equal_action_successor_v1_1 import (
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
from orion.study.p12.successor_authority import (
    build_active_claim_authority,
    build_active_claim_authority_v3,
)

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers/orion-22-adaptive-state-reasoning"
HISTORICAL_RESULT = PAPER / "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_RESULT_V1.json"
RESULT = PAPER / "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_RESULT_V1_1.json"
AUTHORITY = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V3.json"
AUTHORITY_V4 = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V4.json"


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


def test_locked_environment_identity_is_a_noncompensatory_gate() -> None:
    core = build_core()
    for field, replacement in (
        ("python_version", "3.12.12"),
        ("numpy_version", "2.5.1"),
        ("uv_lock_sha256", "0" * 64),
    ):
        drifted = deepcopy(core)
        drifted["environment"][field] = replacement
        result = adjudicate(drifted, byte_identical_replay=True)
        assert result["gates"]["locked_environment_identity_matches_v1_1"] is False
        assert result["terminal"] == NOT_SUPPORTED


def test_v1_receipt_is_preserved_append_only() -> None:
    assert sha256(HISTORICAL_RESULT.read_bytes()).hexdigest() == (
        "a373fcbc63114eac5d42cafa96cce1898a9e6392e480c5d4d0e177cafd7a0523"
    )


def test_v3_authority_rebuilds_and_keeps_p12a_historical() -> None:
    authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    assert authority == build_active_claim_authority_v3()
    assert authority["active_claim_leaf"]["terminal"] == SUPPORTED
    assert authority["historical_boundary_leaf"]["terminal"] == (
        "P12A_SUPERIORITY_AUTHORITY_WITHHELD"
    )
    assert authority["active_claim_leaf"]["scope"]["independent_family_rng_blocks"] == 32
    environment = json.loads(RESULT.read_text(encoding="utf-8"))["core"]["environment"]
    assert authority["active_claim_leaf"]["scope"]["locked_environment"] == {
        "python_version": environment["python_version"],
        "numpy_version": environment["numpy_version"],
        "uv_lock_sha256": environment["uv_lock_sha256"],
    }


def test_v4_authority_preserves_v3_and_binds_landed_lifecycle() -> None:
    authority = json.loads(AUTHORITY_V4.read_text(encoding="utf-8"))
    assert authority == build_active_claim_authority()
    v3 = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    assert authority["active_claim_leaf"] == v3["active_claim_leaf"]
    assert authority["historical_boundary_leaf"] == v3["historical_boundary_leaf"]
    assert authority["robustness_boundary_leaf"]["price_axis"] == "BROKEN"
    assert authority["robustness_boundary_leaf"]["distribution_shift_axis"] == "BROKEN"
    assert authority["price_aware_successor_leaf"]["forward_time_deployability"] == "CANNOT_CHECK"
    assert authority["top_tier_submission_allowed"] is False
