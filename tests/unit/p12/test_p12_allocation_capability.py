"""P12A's superiority, measured against the capability its baselines were denied.

Every number asserted here is executed, not transcribed: the world is replayed
from the protected seed and must land on the committed receipt to the bit before
any perturbation is read from it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.programme.attainable_margin import (
    AttainableMargin,
    HandicappedContrast,
    MarginVerdictReason,
    assess_attainable_margin,
    require_attainable,
)
from orion.programme.records import Outcome
from orion.study.p12.allocation_arms import (
    ALL_ARMS,
    BUDGET,
    MATCHED_ARMS,
    NEGATIVE_TERMINAL,
    N_FAMILIES,
    SHIPPED_ARMS,
    SHIPPED_REPLAY_SHA256,
    SHIPPED_SUMMARY,
    SHIPPED_TERMINAL,
    arm_capability,
    gate_battery,
    run_families,
    summary,
)
from orion.study.p12.gate_theories import (
    FALSE_THEORIES,
    GATE_IDS,
    STRUCTURALLY_UNFALSIFIABLE,
    baseline_signal_axis,
    measure_gate_capacities,
    reachable_allocations,
)

RECEIPT = (
    Path(__file__).resolve().parents[3]
    / "papers"
    / "paper-12-adaptive-state-reasoning"
    / "P12A_MATCHED_BUDGET_RESULT_RECEIPT_V1.json"
)

MATCHED_PAIR = ("STATE_SIGNAL_ONLY_MATCHED", "REASON_SIGNAL_ONLY_MATCHED")
ONE_AXIS_ARMS = ("ADAPTIVE_STATE_ONLY", "ADAPTIVE_REASON_ONLY")


@pytest.fixture(scope="module")
def families():
    return run_families(ALL_ARMS)


def test_pinned_summary_still_matches_the_committed_receipt() -> None:
    """The instrument is pointed at the artifact, not at its own fixture."""

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["terminal"] == SHIPPED_TERMINAL
    assert receipt["replay_sha256"] == SHIPPED_REPLAY_SHA256
    assert receipt["summary"] == dict(SHIPPED_SUMMARY)
    assert set(receipt["gates"]) - {"byte_identical_replay"} == set(GATE_IDS)


def test_replay_reproduces_every_published_number(families) -> None:
    assert summary(families) == dict(SHIPPED_SUMMARY)
    assert gate_battery(families)["terminal"] == SHIPPED_TERMINAL
    assert all(gate_battery(families)["gates"].values())


def test_the_matched_budget_is_real_and_is_not_what_separates_the_arms(families) -> None:
    """Budget parity holds exactly, so it cannot be the source of the margin."""

    assert sum(family.budget_violations for family in families) == 0
    assert all(c + r <= BUDGET for c, r in reachable_allocations())
    assert {len(set(arm.allocations)) for arm in SHIPPED_ARMS} == {1, 2, 4}


def test_each_one_axis_baseline_tops_out_below_the_winner_in_every_family(families) -> None:
    winner = arm_capability(families, SHIPPED_ARMS[3])
    assert winner.arm_id == "JOINT_FROZEN"
    assert winner.achieved == pytest.approx(0.858154296875)

    for arm in SHIPPED_ARMS:
        if arm.arm_id not in ONE_AXIS_ARMS:
            continue
        baseline = arm_capability(families, arm)
        assert baseline.ceiling < winner.achieved
        below = sum(
            1
            for family in families
            if family.ceiling(arm.arm_id) < family.rate("JOINT_FROZEN")
        )
        assert below == N_FAMILIES

    state_only = arm_capability(families, SHIPPED_ARMS[1])
    assert state_only.ceiling == pytest.approx(0.475464, abs=1e-6)
    assert state_only.headroom == pytest.approx(0.012329, abs=1e-6)


def test_each_baseline_cannot_serve_half_the_benchmark_at_any_signal(families) -> None:
    """The tie-break-free statement of the confound, in item counts."""

    total = sum(len(family.attainable["JOINT_FROZEN"]) for family in families)
    assert total == N_FAMILIES * 512

    def unservable(arm_id: str) -> int:
        return sum(
            len(family.attainable[arm_id]) - sum(family.attainable[arm_id])
            for family in families
        )

    assert unservable("JOINT_FROZEN") == 0
    assert unservable("ADAPTIVE_STATE_ONLY") == 4297
    assert unservable("ADAPTIVE_REASON_ONLY") == 4394
    assert unservable("FIXED_11") == 3969


def test_most_of_the_gain_survives_giving_both_baselines_a_perfect_signal(families) -> None:
    """A margin that a perfect baseline signal barely dents is not about adaptation."""

    joint = [family.rate("JOINT_FROZEN") for family in families]
    achieved = [
        max(family.rate("ADAPTIVE_STATE_ONLY"), family.rate("ADAPTIVE_REASON_ONLY"))
        for family in families
    ]
    ceilings = [
        max(family.ceiling("ADAPTIVE_STATE_ONLY"), family.ceiling("ADAPTIVE_REASON_ONLY"))
        for family in families
    ]
    published = sum(a - b for a, b in zip(joint, achieved)) / N_FAMILIES
    against_ceiling = sum(a - b for a, b in zip(joint, ceilings)) / N_FAMILIES
    assert published == pytest.approx(0.334716796875)
    assert against_ceiling == pytest.approx(0.3193359375)
    assert against_ceiling / published > 0.95
    assert sum(1 for a, b in zip(joint, ceilings) if b < a) == N_FAMILIES


def test_the_reported_margin_is_mostly_unreachable(families) -> None:
    winner = arm_capability(families, SHIPPED_ARMS[3])
    baseline = arm_capability(families, SHIPPED_ARMS[1])
    verdict = assess_attainable_margin(
        "P12A_JOINT_VS_STATE_ONLY", winner=winner, baseline=baseline, min_attainable_margin=0.15
    )
    assert verdict.outcome is Outcome.CANNOT_CHECK
    assert verdict.reason is MarginVerdictReason.BASELINE_CEILING_BELOW_WINNER
    assert verdict.blocks is True
    assert verdict.margin.reported_margin == pytest.approx(0.395020, abs=1e-6)
    assert verdict.margin.handicap == pytest.approx(0.382690, abs=1e-6)
    assert verdict.margin.attainable_margin == pytest.approx(0.012329, abs=1e-6)
    assert verdict.margin.handicap_share > 0.96


def test_require_attainable_names_both_one_axis_arms(families) -> None:
    winner = arm_capability(families, SHIPPED_ARMS[3])
    margins = [
        AttainableMargin(winner=winner, baseline=arm_capability(families, arm))
        for arm in SHIPPED_ARMS
        if arm.arm_id in ONE_AXIS_ARMS
    ]
    with pytest.raises(HandicappedContrast) as caught:
        require_attainable(margins, label="P12A")
    message = str(caught.value)
    assert "2 of 2 baselines" in message
    assert "ADAPTIVE_STATE_ONLY" in message
    assert "ADAPTIVE_REASON_ONLY" in message


def test_capability_matched_baselines_could_have_won(families) -> None:
    winner = arm_capability(families, SHIPPED_ARMS[3])
    for arm in MATCHED_ARMS:
        matched = arm_capability(families, arm)
        assert matched.ceiling == pytest.approx(1.0)
        verdict = assess_attainable_margin(
            f"P12A_JOINT_VS_{arm.arm_id}", winner=winner, baseline=matched
        )
        assert verdict.outcome is Outcome.PASS
        assert verdict.margin.handicap == 0.0
    require_attainable(
        [
            AttainableMargin(winner=winner, baseline=arm_capability(families, arm))
            for arm in MATCHED_ARMS
        ],
        label="P12A capability matched",
    )


def test_the_shipped_gate_battery_flips_when_only_the_action_set_is_matched(families) -> None:
    """The one perturbation the protocol's own words permit and its code does not."""

    matched = gate_battery(families, one_axis_arms=MATCHED_PAIR)
    assert matched["terminal"] == NEGATIVE_TERMINAL
    assert matched["mean_joint_gain"] == pytest.approx(0.040771484375)
    assert matched["worst_family_joint_gain"] == pytest.approx(0.001953125)
    failed = {name for name, value in matched["gates"].items() if not value}
    assert failed == {"mean_joint_gain_ge_0_15", "worst_family_joint_gain_ge_0_05"}
    # The FIXED_11 comparator is untouched by the substitution, so its gate holds
    # and the flip cannot be read as the whole battery collapsing.
    assert matched["gates"]["mean_joint_minus_fixed_ge_0_10"] is True


def test_a_perfect_signal_widens_the_published_gap_and_closes_the_matched_one() -> None:
    """A gap that grows as the signal sharpens is structural, not informational."""

    sharp = run_families(ALL_ARMS, sigma=0.0)
    published = gate_battery(sharp)["mean_joint_gain"]
    matched = gate_battery(sharp, one_axis_arms=MATCHED_PAIR)["mean_joint_gain"]
    assert published == pytest.approx(0.461181640625)
    assert matched == pytest.approx(0.0, abs=1e-12)
    assert published > gate_battery(run_families(ALL_ARMS))["mean_joint_gain"]


def test_the_second_signal_cannot_reach_the_baseline_action_set() -> None:
    axis = baseline_signal_axis("s_r")
    assert axis.varied is True
    assert axis.comparable_pairs == 4410
    assert axis.verdict_changing_pairs == 0
    assert axis.inert is True
    assert baseline_signal_axis("s_c").inert is False


def test_three_of_seven_gates_reject_no_wrong_allocation_rule() -> None:
    capacities = {item.check_id: item for item in measure_gate_capacities()}
    assert set(capacities) == set(GATE_IDS)
    unfalsifiable = {name for name, item in capacities.items() if item.blocks}
    assert unfalsifiable == set(STRUCTURALLY_UNFALSIFIABLE)
    for name in STRUCTURALLY_UNFALSIFIABLE:
        assert capacities[name].refuted == ()
        assert len(capacities[name].survivors) == len(FALSE_THEORIES)
        assert capacities[name].inert_theories == ()
    for name in set(GATE_IDS) - STRUCTURALLY_UNFALSIFIABLE:
        assert capacities[name].outcome is Outcome.PASS
        assert len(capacities[name].refuted) == len(FALSE_THEORIES)
