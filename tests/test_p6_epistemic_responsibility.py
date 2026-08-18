from __future__ import annotations

import pytest

from orion.transfer.v2.epistemic_responsibility import (
    ResponsibilityStatus,
    assess_responsibility,
    build_responsibility_hypothesis,
)


def hypothesis(name: str, expected: dict[str, tuple[str, ...]], *, claim: str = "claim:demo"):
    return build_responsibility_hypothesis(
        hypothesis_id=name,
        claim_id=claim,
        expected_observations=expected,
        support_evidence_ids=(f"evidence:{name}",),
    )


def test_identical_predictions_remain_ambiguous() -> None:
    left = hypothesis("evidence-gap", {"probe:1": ("FAIL",)})
    right = hypothesis("model-gap", {"probe:1": ("FAIL",)})

    report = assess_responsibility(
        (left, right), observed_outcomes={"probe:1": "FAIL"}
    )

    assert report.status is ResponsibilityStatus.AMBIGUOUS
    assert report.identified_hypothesis_id is None
    assert set(report.surviving_hypothesis_ids) == {"evidence-gap", "model-gap"}
    assert report.grants_revision_authority is False


def test_discriminator_can_identify_one_survivor() -> None:
    evidence_gap = hypothesis("evidence-gap", {"probe:source": ("FOUND",)})
    model_gap = hypothesis("model-gap", {"probe:source": ("NOT_FOUND",)})

    report = assess_responsibility(
        (evidence_gap, model_gap),
        observed_outcomes={"probe:source": "FOUND"},
    )

    assert report.status is ResponsibilityStatus.IDENTIFIED
    assert report.identified_hypothesis_id == "evidence-gap"
    assert report.surviving_hypothesis_ids == ("evidence-gap",)
    assert "model-gap" in report.defeated_hypothesis_ids


def test_missing_required_discriminator_remains_unresolved() -> None:
    candidate = hypothesis(
        "representation-gap",
        {
            "probe:transform": ("RECOVERS",),
            "probe:native": ("FAILS",),
        },
    )

    report = assess_responsibility(
        (candidate,), observed_outcomes={"probe:transform": "RECOVERS"}
    )

    assert report.status is ResponsibilityStatus.UNRESOLVED
    assert report.identified_hypothesis_id is None
    assert report.missing_discriminator_ids == ("probe:native",)


def test_all_hypotheses_can_be_defeated_without_forced_revision() -> None:
    left = hypothesis("left", {"probe:x": ("A",)})
    right = hypothesis("right", {"probe:x": ("B",)})

    report = assess_responsibility(
        (left, right), observed_outcomes={"probe:x": "C"}
    )

    assert report.status is ResponsibilityStatus.NO_SURVIVING
    assert report.identified_hypothesis_id is None
    assert report.surviving_hypothesis_ids == ()
    assert set(report.defeated_hypothesis_ids) == {"left", "right"}


def test_duplicate_ids_and_cross_claim_mixtures_are_rejected() -> None:
    one = hypothesis("same", {"p": ("A",)})
    duplicate = hypothesis("same", {"p": ("A",)})
    other_claim = hypothesis("other", {"p": ("A",)}, claim="claim:other")

    with pytest.raises(ValueError, match="duplicate responsibility hypothesis"):
        assess_responsibility((one, duplicate), observed_outcomes={"p": "A"})

    with pytest.raises(ValueError, match="claim-relative"):
        assess_responsibility((one, other_claim), observed_outcomes={"p": "A"})


def test_unregistered_observation_does_not_create_authority() -> None:
    candidate = hypothesis("candidate", {"probe:registered": ("YES",)})

    report = assess_responsibility(
        (candidate,),
        observed_outcomes={"probe:registered": "YES", "probe:extra": "SURPRISE"},
    )

    assert report.status is ResponsibilityStatus.IDENTIFIED
    assert report.unmodeled_discriminator_ids == ("probe:extra",)
    assert report.grants_revision_authority is False
