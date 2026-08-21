"""A harm rate must divide by the episodes that could have carried the harm."""

from __future__ import annotations

import pytest

from orion.programme.guard_exercise import GuardVerdictReason
from orion.programme.outcome_entailment import (
    ArmPolicy,
    EntailedOutcome,
    ReportedOutcome,
    WorldVariant,
    measure_outcome_entailment,
    require_contingent,
)
from orion.programme.records import Outcome

# A two-coordinate toy of P13A: an episode is covered or not by a certificate,
# and a reuse on an uncovered episode is the harm.
SPACE = tuple(
    {"case": case, "covered": covered}
    for case in range(4)
    for covered in (True, False)
)

SELF_SCORING = ArmPolicy(
    arm_id="self-scoring",
    decides="reuse exactly when the certificate covers the episode",
    action=lambda point: "REUSE" if point["covered"] else "REOPEN",
)
ALWAYS_REUSE = ArmPolicy(
    arm_id="always-reuse",
    decides="reuse on every episode whatever the certificate says",
    action=lambda point: "REUSE",
)
UNCOVERED_REUSE = ReportedOutcome(
    outcome_id="uncovered_reuse",
    measures="a reuse on an episode the certificate does not cover",
    holds=lambda point, decision: decision == "REUSE" and not point["covered"],
)
FLIPPED = WorldVariant(
    world_id="certificate_inverted",
    wrong="the certificate covers exactly the episodes it should refuse",
    rewrite=lambda point: {**point, "covered": not point["covered"]},
)
IDENTITY = WorldVariant(
    world_id="restated",
    wrong="the certificate is the shipped one written again",
    rewrite=lambda point: dict(point),
)


def measure(policy: ArmPolicy, **kwargs: object):
    return measure_outcome_entailment(
        UNCOVERED_REUSE, policy=policy, space=SPACE, worlds=(FLIPPED,), **kwargs
    )


def test_an_arm_scored_on_its_own_predicate_cannot_check() -> None:
    """The whole point: zero harms over zero reachable episodes is not a pass."""

    entailment = measure(SELF_SCORING)
    assert entailment.realized == 0
    assert entailment.published_rate == 0.0
    assert entailment.exercise.opportunities == 0
    assert entailment.entailed is True
    assert entailment.outcome is Outcome.CANNOT_CHECK
    assert entailment.blocks is True
    assert entailment.assessment.reason is GuardVerdictReason.NEVER_EXERCISED


def test_the_arm_moving_while_the_outcome_does_not_is_reported_as_blind() -> None:
    """An entailed outcome whose policy did respond cannot be a weak register."""

    entailment = measure(SELF_SCORING)
    assert entailment.action_contingent == len(SPACE)
    assert entailment.outcome_contingent == 0
    assert entailment.blind is True


def test_an_arm_that_can_cause_the_harm_gets_a_real_denominator() -> None:
    entailment = measure(ALWAYS_REUSE)
    assert entailment.realized == 4
    assert entailment.exercise.opportunities == len(SPACE)
    assert entailment.exercise.violation_rate == 0.5
    assert entailment.outcome is Outcome.FAIL


def test_a_realized_harm_is_never_reported_as_unreachable() -> None:
    """Reachability includes the shipped world, so a live harm always has a denominator."""

    entailment = measure_outcome_entailment(
        UNCOVERED_REUSE,
        policy=ALWAYS_REUSE,
        space=SPACE,
        # A world that touches only a coordinate no rule reads: the outcome is
        # entailed, and the arm still fails on the harms it actually caused.
        worlds=(
            WorldVariant(
                world_id="renumbered",
                wrong="the episodes are relabelled and nothing else changes",
                rewrite=lambda point: {**point, "case": -point["case"]},
            ),
        ),
    )
    assert entailment.entailed is True
    assert entailment.realized == 4
    assert entailment.exercise.opportunities == 4
    assert entailment.outcome is Outcome.FAIL


def test_a_world_that_rewrites_nothing_is_inert_not_a_denominator() -> None:
    entailment = measure_outcome_entailment(
        UNCOVERED_REUSE, policy=ALWAYS_REUSE, space=SPACE, worlds=(IDENTITY, FLIPPED)
    )
    assert entailment.inert_worlds == ("restated",)
    assert entailment.live_worlds == ("certificate_inverted",)


def test_a_register_of_restatements_refuses_to_measure() -> None:
    with pytest.raises(EntailedOutcome, match="leave every one of the 8 episodes unchanged"):
        measure_outcome_entailment(
            UNCOVERED_REUSE, policy=ALWAYS_REUSE, space=SPACE, worlds=(IDENTITY,)
        )


def test_an_empty_register_refuses_to_measure() -> None:
    with pytest.raises(EntailedOutcome, match="no alternative world is registered"):
        measure_outcome_entailment(
            UNCOVERED_REUSE, policy=ALWAYS_REUSE, space=SPACE, worlds=()
        )


def test_an_empty_space_refuses_to_measure() -> None:
    with pytest.raises(ValueError, match="empty episode space"):
        measure_outcome_entailment(
            UNCOVERED_REUSE, policy=ALWAYS_REUSE, space=(), worlds=(FLIPPED,)
        )


def test_an_unstated_rule_or_harm_or_wrongness_is_refused() -> None:
    with pytest.raises(ValueError, match="state what this arm decides"):
        ArmPolicy(arm_id="a", decides="   ", action=lambda point: "REUSE")
    with pytest.raises(ValueError, match="state what this outcome measures"):
        ReportedOutcome(outcome_id="h", measures="", holds=lambda point, decision: False)
    with pytest.raises(ValueError, match="state what this world gets wrong"):
        WorldVariant(world_id="w", wrong=" ", rewrite=lambda point: dict(point))


def test_require_contingent_names_the_entailed_pairs() -> None:
    entailments = (measure(SELF_SCORING), measure(ALWAYS_REUSE))
    with pytest.raises(EntailedOutcome) as caught:
        require_contingent(entailments, label="toy")
    message = str(caught.value)
    assert "uncovered_reuse/self-scoring" in message
    assert "moved the arm's own decision and not the outcome" in message
    assert "caused an avoidable harm" in message


def test_require_contingent_passes_only_a_measured_clean_arm() -> None:
    covered_only = tuple(point for point in SPACE if point["covered"])
    clean = measure_outcome_entailment(
        UNCOVERED_REUSE,
        policy=ALWAYS_REUSE,
        space=covered_only,
        worlds=(FLIPPED,),
    )
    assert clean.outcome is Outcome.PASS
    require_contingent((clean,), label="toy")


def test_an_empty_measurement_set_reports_nothing() -> None:
    with pytest.raises(EntailedOutcome, match="empty measurement set"):
        require_contingent((), label="toy")


def test_the_json_carries_both_denominators() -> None:
    payload = measure(SELF_SCORING).as_json()
    assert payload["published_rate"] == 0.0
    assert payload["exercise"]["opportunities"] == 0
    assert payload["exercise"]["violation_rate"] is None
    assert payload["entailed"] is True
    assert payload["blind"] is True
    assert payload["outcome"] == "CANNOT_CHECK"
