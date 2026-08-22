"""A preregistered gate, asked whether the protocol could have moved it either way.

The instrument is scope-general, so these fixtures are: a statistic that returns
whatever the world says, and thresholds placed inside, above and below the
values the register can produce. The P14A numbers it was written from are pinned
in ``tests/unit/study/p14/test_p14_governance_gates.py``.
"""

from __future__ import annotations

import pytest

from orion.programme.gate_attainability import (
    AdmissibleWorld,
    GateDirection,
    GateReach,
    GateReachReason,
    GateRole,
    PreregisteredGate,
    StatisticSupport,
    ThresholdReach,
    UnattainableGate,
    assess_threshold_panel,
    assess_threshold_support,
    measure_gate_attainability,
    measure_terminal_reach,
    require_reachable,
    require_supported_thresholds,
)
from orion.programme.guard_exercise import GuardVerdictReason
from orion.programme.records import Outcome


def world(world_id: str, value: float) -> AdmissibleWorld:
    return AdmissibleWorld(
        world_id=world_id, admits="a draw the frozen protocol permits", payload=value
    )


WORLDS = (world("floor", 0.01), world("middle", 0.02), world("ceiling", 0.04))


def gate(threshold: float, direction: GateDirection = GateDirection.AT_LEAST) -> PreregisteredGate:
    return PreregisteredGate(
        gate_id="discriminator-prevalence",
        reads="the discriminating state's frequency",
        threshold=threshold,
        direction=direction,
    )


def reach(threshold: float, direction: GateDirection = GateDirection.AT_LEAST) -> GateReach:
    return measure_gate_attainability(
        lambda payload: payload, gate=gate(threshold, direction), worlds=WORLDS
    )


def test_a_threshold_above_every_admissible_world_is_a_gate_that_cannot_pass() -> None:
    measured = reach(0.08)

    assert measured.reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert measured.outcome is Outcome.FAIL
    assert measured.blocks is True
    assert measured.attainable is False
    assert measured.satisfying == ()
    assert measured.refuting == ("floor", "middle", "ceiling")
    assert measured.best_value == 0.04
    assert measured.attainment_margin == pytest.approx(-0.04)


def test_a_threshold_below_every_admissible_world_is_a_gate_that_cannot_fail() -> None:
    measured = reach(0.005)

    assert measured.reason is GateReachReason.THRESHOLD_UNCONDITIONAL
    assert measured.outcome is Outcome.FAIL
    assert measured.unconditional is True
    assert measured.refuting == ()


def test_a_threshold_inside_the_support_discriminates() -> None:
    measured = reach(0.02)

    assert measured.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE
    assert measured.outcome is Outcome.PASS
    assert measured.satisfying == ("middle", "ceiling")
    assert measured.refuting == ("floor",)
    assert measured.attainment_margin == pytest.approx(0.02)


def test_an_at_most_gate_points_its_margin_the_other_way() -> None:
    unattainable = reach(0.005, GateDirection.AT_MOST)
    unconditional = reach(0.08, GateDirection.AT_MOST)

    assert unattainable.reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert unattainable.best_value == 0.01
    assert unattainable.attainment_margin == pytest.approx(-0.005)
    assert unconditional.reason is GateReachReason.THRESHOLD_UNCONDITIONAL


def test_the_attainability_half_is_a_guard_exercise_over_the_register() -> None:
    """The opportunities are the admissible worlds; the violations are the ones that fell short."""

    measured = reach(0.08)

    assert measured.exercise.opportunities == 3
    assert measured.exercise.violations == 3
    assert "the discriminating state's frequency" in measured.exercise.opportunity_definition
    assert measured.assessment.outcome is Outcome.FAIL
    assert measured.assessment.reason is GuardVerdictReason.VIOLATED


def test_an_empty_register_refuses_to_be_scored() -> None:
    with pytest.raises(UnattainableGate, match="no admissible world is registered"):
        measure_gate_attainability(lambda payload: payload, gate=gate(0.08), worlds=())


def test_a_world_must_say_why_the_protocol_admits_it() -> None:
    with pytest.raises(ValueError, match="state why the frozen protocol admits"):
        AdmissibleWorld(world_id="corner", admits="  ", payload=0.04)


def test_a_gate_must_name_the_statistic_it_reads() -> None:
    with pytest.raises(ValueError, match="state which statistic this gate reads"):
        PreregisteredGate(gate_id="g", reads="", threshold=0.08)


def test_duplicate_world_ids_are_refused() -> None:
    with pytest.raises(ValueError, match="world ids must be distinct"):
        measure_gate_attainability(
            lambda payload: payload,
            gate=gate(0.08),
            worlds=(world("corner", 0.01), world("corner", 0.04)),
        )


def test_a_terminal_whose_conjunction_no_world_clears_has_one_word() -> None:
    terminal = measure_terminal_reach(
        (
            measure_gate_attainability(
                lambda payload: payload,
                gate=PreregisteredGate(gate_id="reachable", reads="value", threshold=0.02),
                worlds=WORLDS,
            ),
            measure_gate_attainability(
                lambda payload: payload,
                gate=PreregisteredGate(gate_id="unreachable", reads="value", threshold=0.08),
                worlds=WORLDS,
            ),
        ),
        label="frozen terminal",
    )

    assert terminal.unattainable == ("unreachable",)
    assert terminal.clearing == ()
    assert terminal.distinct_terminals == 1
    assert terminal.outcome is Outcome.FAIL
    with pytest.raises(UnattainableGate, match="no admissible world satisfies unreachable"):
        require_reachable(terminal)


def test_individually_reachable_gates_can_still_have_no_world_in_common() -> None:
    """The reason the terminal is asked separately: attainability does not compose."""

    low = measure_gate_attainability(
        lambda payload: payload,
        gate=PreregisteredGate(gate_id="at-least", reads="value", threshold=0.04),
        worlds=WORLDS,
    )
    high = measure_gate_attainability(
        lambda payload: payload,
        gate=PreregisteredGate(
            gate_id="at-most", reads="value", threshold=0.01, direction=GateDirection.AT_MOST
        ),
        worlds=WORLDS,
    )
    terminal = measure_terminal_reach((low, high), label="frozen terminal")

    assert low.outcome is Outcome.PASS
    assert high.outcome is Outcome.PASS
    assert terminal.unattainable == ()
    assert terminal.clearing == ()
    assert terminal.distinct_terminals == 1
    assert terminal.outcome is Outcome.FAIL


def test_a_terminal_both_of_whose_words_are_reachable_passes() -> None:
    terminal = measure_terminal_reach(
        (
            measure_gate_attainability(
                lambda payload: payload,
                gate=PreregisteredGate(gate_id="first", reads="value", threshold=0.02),
                worlds=WORLDS,
            ),
            measure_gate_attainability(
                lambda payload: payload,
                gate=PreregisteredGate(gate_id="second", reads="value", threshold=0.015),
                worlds=WORLDS,
            ),
        ),
        label="frozen terminal",
    )

    assert terminal.clearing == ("middle", "ceiling")
    assert terminal.distinct_terminals == 2
    assert terminal.outcome is Outcome.PASS
    require_reachable(terminal)


def test_a_terminal_every_world_clears_also_has_one_word() -> None:
    terminal = measure_terminal_reach((reach(0.005),), label="frozen terminal")

    assert terminal.unconditional == ("discriminator-prevalence",)
    assert terminal.clearing == ("floor", "middle", "ceiling")
    assert terminal.distinct_terminals == 1
    with pytest.raises(UnattainableGate, match="every admissible world satisfies"):
        require_reachable(terminal)


def test_gates_measured_over_different_registers_cannot_be_intersected() -> None:
    other = measure_gate_attainability(
        lambda payload: payload,
        gate=PreregisteredGate(gate_id="elsewhere", reads="value", threshold=0.02),
        worlds=(world("only", 0.03),),
    )

    with pytest.raises(ValueError, match="measured over the same admissible worlds"):
        measure_terminal_reach((reach(0.02), other), label="frozen terminal")


def test_a_terminal_needs_gates_and_a_label() -> None:
    with pytest.raises(ValueError, match="not a conjunction"):
        measure_terminal_reach((), label="frozen terminal")
    with pytest.raises(ValueError, match="label is required"):
        measure_terminal_reach((reach(0.02),), label=" ")


def test_json_carries_the_margin_and_the_register() -> None:
    payload = measure_terminal_reach((reach(0.08),), label="frozen terminal").as_json()

    assert payload["outcome"] == "FAIL"
    assert payload["distinct_terminals"] == 1
    assert payload["unattainable"] == ["discriminator-prevalence"]
    assert payload["gates"][0]["attainment_margin"] == pytest.approx(-0.04)
    assert [item["world_id"] for item in payload["gates"][0]["readings"]] == [
        "floor",
        "middle",
        "ceiling",
    ]


def test_a_reach_must_carry_the_worlds_it_was_measured_over() -> None:
    measured = reach(0.08)

    with pytest.raises(ValueError, match="must carry the worlds"):
        GateReach(gate=measured.gate, readings=(), exercise=measured.exercise)


# --- the pre-run half: a threshold against the interval its statistic can occupy ---
#
# `measure_gate_attainability` needs a register of worlds and a run of each, so
# it can only be asked after a campaign is built. A bound needs the
# preregistration alone, which is the only moment at which an unattainable
# threshold costs a sentence instead of a published result.


def support(
    infimum: float = 0.009085200732011248, supremum: float = 0.04232587750858594
) -> StatisticSupport:
    return StatisticSupport(
        statistic="the discriminating state's frequency over the declared sampling box",
        infimum=infimum,
        supremum=supremum,
        derivation="a product of eight factors each monotone in a different declared uniform",
    )


def threshold_reach(
    value: float,
    *,
    direction: GateDirection = GateDirection.AT_LEAST,
    role: GateRole = GateRole.HYPOTHESIS,
    bounds: StatisticSupport | None = None,
) -> ThresholdReach:
    return assess_threshold_support(
        PreregisteredGate(
            gate_id="discriminator-prevalence",
            reads="the discriminating state's frequency",
            threshold=value,
            direction=direction,
            role=role,
        ),
        support=bounds or support(),
    )


def test_a_threshold_above_the_statistics_ceiling_is_caught_before_the_run() -> None:
    """P14A's ``0.08`` against a supremum of ``0.042326``: no seed had to be drawn."""

    reached = threshold_reach(0.08)

    assert reached.reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert reached.outcome is Outcome.FAIL
    assert reached.blocks is True
    assert reached.discriminates is False
    assert reached.best_value == pytest.approx(0.04232587750858594)
    assert reached.attainment_margin == pytest.approx(-0.03767412249141406)


def test_a_threshold_inside_the_interval_can_go_either_way() -> None:
    reached = threshold_reach(0.02)

    assert reached.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE
    assert reached.outcome is Outcome.PASS
    assert reached.discriminates is True
    assert reached.attainment_margin > 0.0
    assert reached.refutation_margin < 0.0


def test_a_threshold_the_whole_interval_clears_decides_a_hypothesis_in_advance() -> None:
    reached = threshold_reach(0.005)

    assert reached.reason is GateReachReason.THRESHOLD_UNCONDITIONAL
    assert reached.outcome is Outcome.FAIL
    assert reached.refutation_margin == pytest.approx(0.004085200732011248)


def test_a_precondition_may_hold_in_every_admissible_world_but_may_not_be_unreachable() -> None:
    """The asymmetry: an instrument certificate is allowed to be certain, a claim is not."""

    certain = threshold_reach(0.005, role=GateRole.PRECONDITION)
    unreachable = threshold_reach(0.08, role=GateRole.PRECONDITION)

    assert certain.reason is GateReachReason.THRESHOLD_UNCONDITIONAL
    assert certain.outcome is Outcome.PASS
    assert unreachable.reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert unreachable.outcome is Outcome.FAIL


def test_an_at_most_gate_reads_the_other_end_of_the_interval() -> None:
    unreachable = threshold_reach(0.005, direction=GateDirection.AT_MOST)
    reachable = threshold_reach(0.02, direction=GateDirection.AT_MOST)

    assert unreachable.reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert unreachable.best_value == pytest.approx(0.009085200732011248)
    assert reachable.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE


def test_the_measured_register_and_the_declared_bound_agree_on_the_same_gate() -> None:
    """One reason function serves both, so the two halves cannot drift apart."""

    bounds = support(infimum=0.01, supremum=0.04)
    for threshold in (0.005, 0.02, 0.08):
        assert reach(threshold).reason is threshold_reach(threshold, bounds=bounds).reason


def test_a_bound_that_cannot_be_re_derived_is_refused() -> None:
    with pytest.raises(ValueError, match="derivation is required"):
        StatisticSupport(statistic="x", infimum=0.0, supremum=1.0, derivation="  ")
    with pytest.raises(ValueError, match="statistic is required"):
        StatisticSupport(statistic=" ", infimum=0.0, supremum=1.0, derivation="d")
    with pytest.raises(ValueError, match="an empty interval bounds nothing"):
        StatisticSupport(statistic="x", infimum=0.5, supremum=0.4, derivation="d")
    with pytest.raises(ValueError, match="supremum must be finite"):
        StatisticSupport(statistic="x", infimum=0.0, supremum=float("inf"), derivation="d")


def test_one_unattainable_threshold_blocks_the_whole_preregistration() -> None:
    """P14A's battery, asked at freeze time: two gates, both above the ceiling."""

    difficulty = assess_threshold_support(
        PreregisteredGate(
            gate_id="strongest_baseline_false_promotion_ge_0_05",
            reads="strongest non-ORION baseline false promotion rate",
            threshold=0.05,
            role=GateRole.PRECONDITION,
        ),
        support=support(),
    )
    panel = assess_threshold_panel(
        (difficulty, threshold_reach(0.08)),
        label="P14A aggregate superiority thresholds",
    )

    assert panel.outcome is Outcome.FAIL
    assert panel.unattainable == (
        "strongest_baseline_false_promotion_ge_0_05",
        "discriminator-prevalence",
    )
    assert panel.discriminating == ()
    with pytest.raises(UnattainableGate, match="no admissible value satisfies"):
        require_supported_thresholds(panel)


def test_a_panel_of_preconditions_alone_carries_no_claim() -> None:
    """Relabelling every hypothesis a precondition empties the panel, it does not clear it."""

    panel = assess_threshold_panel(
        (
            assess_threshold_support(
                PreregisteredGate(
                    gate_id="benchmark-is-hard-enough",
                    reads="strongest baseline error rate",
                    threshold=0.005,
                    role=GateRole.PRECONDITION,
                ),
                support=support(),
            ),
        ),
        label="preconditions only",
    )

    assert panel.discriminating == ()
    assert panel.outcome is Outcome.FAIL
    with pytest.raises(UnattainableGate, match="no hypothesis gate discriminates"):
        require_supported_thresholds(panel)


def test_a_panel_with_a_live_hypothesis_and_reachable_bars_passes() -> None:
    panel = assess_threshold_panel(
        (
            assess_threshold_support(
                PreregisteredGate(
                    gate_id="benchmark-is-hard-enough",
                    reads="strongest baseline error rate",
                    threshold=0.005,
                    role=GateRole.PRECONDITION,
                ),
                support=support(),
            ),
            threshold_reach(0.02),
        ),
        label="a battery that could have said two things",
    )

    assert panel.outcome is Outcome.PASS
    assert panel.unattainable == ()
    assert panel.discriminating == ("discriminator-prevalence",)
    require_supported_thresholds(panel)
    assert panel.as_json()["outcome"] == "PASS"


def test_a_panel_needs_gates_distinct_ids_and_a_label() -> None:
    with pytest.raises(ValueError, match="preregisters nothing"):
        assess_threshold_panel((), label="empty")
    with pytest.raises(ValueError, match="label is required"):
        assess_threshold_panel((threshold_reach(0.02),), label=" ")
    with pytest.raises(ValueError, match="gate ids must be distinct"):
        assess_threshold_panel((threshold_reach(0.02), threshold_reach(0.03)), label="duplicated")
