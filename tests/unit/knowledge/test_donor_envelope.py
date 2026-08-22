from __future__ import annotations

import pytest

from orion.knowledge.donor_envelope import (
    SCHEMA_ID,
    DonorEnvelopeCase,
    DonorEnvelopeVerdict,
    IdealDonorProductRelation,
    assess_donor_envelope,
)


def _case(**overrides: object) -> DonorEnvelopeCase:
    values: dict[str, object] = {
        "case_id": "P1.SAGE.envelope.v1",
        "donor_ids": ("SAGE:2606.31478",),
        "admitted_absorption_receipt_ids": ("receipt:sage-routing",),
        "donor_claim_ids": ("claim:typed-failure-routing",),
        "donor_assumption_ids": ("assumption:verified-category-severity",),
        "donor_coordinate_ids": ("failure-level", "failure-category", "severity"),
        "donor_reconstruction_ids": ("test:sage-faithful-router",),
        "embedding_map_id": "map:sage-to-protected-escalation",
        "preservation_obligation_ids": ("preserve:sage-route",),
        "added_coordinate_ids": ("protected-sibling-invariants",),
        "strict_separation_ids": ("witness:same-task-recovery",),
        "ideal_product_relation": IdealDonorProductRelation.ENVELOPE_STRICTLY_SEPARATES,
        "ideal_product_evidence_ids": ("test:information-matched-ideal-product",),
        "falsifier_ids": ("mutant:drop-protected-sibling",),
        "fresh_evaluation_ids": ("study:new-hidden-episodes",),
        "historical_negative_ids": ("P1.R6.native.NOT_SUPPORTED",),
        "derived_from_negative": True,
    }
    values.update(overrides)
    return DonorEnvelopeCase(**values)


@pytest.mark.parametrize(
    ("overrides", "verdict"),
    [
        (
            {"admitted_absorption_receipt_ids": ()},
            DonorEnvelopeVerdict.BLOCKED_ABSORPTION_INCOMPLETE,
        ),
        (
            {"donor_reconstruction_ids": ()},
            DonorEnvelopeVerdict.BLOCKED_DONOR_RECONSTRUCTION,
        ),
        (
            {"embedding_map_id": ""},
            DonorEnvelopeVerdict.BLOCKED_CONSERVATIVE_EMBEDDING,
        ),
        (
            {"preservation_obligation_ids": ()},
            DonorEnvelopeVerdict.BLOCKED_CONSERVATIVE_EMBEDDING,
        ),
    ],
)
def test_envelope_fails_closed_before_donor_is_reconstructed_and_embedded(
    overrides: dict[str, object], verdict: DonorEnvelopeVerdict
) -> None:
    assert assess_donor_envelope(_case(**overrides)).verdict is verdict


def test_exact_donor_reconstruction_is_a_useful_absorbed_special_case() -> None:
    assessment = assess_donor_envelope(
        _case(
            added_coordinate_ids=(),
            strict_separation_ids=(),
            ideal_product_relation=IdealDonorProductRelation.UNTESTED,
            ideal_product_evidence_ids=(),
        )
    )

    assert assessment.verdict is DonorEnvelopeVerdict.ABSORBED_SPECIAL_CASE
    assert assessment.publication_novelty_authorized is False


def test_added_structure_without_separation_remains_a_conservative_envelope() -> None:
    assessment = assess_donor_envelope(_case(strict_separation_ids=()))

    assert assessment.verdict is DonorEnvelopeVerdict.CONSERVATIVE_ENVELOPE
    assert assessment.added_coordinate_count == 1


def test_strict_witness_must_face_the_strongest_ideal_donor_product() -> None:
    assessment = assess_donor_envelope(
        _case(
            ideal_product_relation=IdealDonorProductRelation.UNTESTED,
            ideal_product_evidence_ids=(),
        )
    )

    assert assessment.verdict is DonorEnvelopeVerdict.BLOCKED_IDEAL_DONOR_PRODUCT


def test_ideal_product_tie_is_an_equivalence_boundary_not_superiority() -> None:
    assessment = assess_donor_envelope(
        _case(ideal_product_relation=IdealDonorProductRelation.TIES_ENVELOPE)
    )

    assert assessment.verdict is DonorEnvelopeVerdict.IDEAL_DONOR_PRODUCT_EQUIVALENCE
    assert assessment.publication_novelty_authorized is False
    assert "not inherent superiority" in assessment.reasons[-1]


@pytest.mark.parametrize(
    ("overrides", "verdict"),
    [
        (
            {"unresolved_route_ids": ("route:current-primary-sources",)},
            DonorEnvelopeVerdict.BLOCKED_OPEN_ROUTES,
        ),
        ({"falsifier_ids": ()}, DonorEnvelopeVerdict.BLOCKED_NO_FALSIFIER),
        (
            {"fresh_evaluation_ids": ()},
            DonorEnvelopeVerdict.BLOCKED_NO_FRESH_EVALUATION,
        ),
    ],
)
def test_strict_envelope_promotion_requires_closed_routes_falsifiers_and_fresh_data(
    overrides: dict[str, object], verdict: DonorEnvelopeVerdict
) -> None:
    assert assess_donor_envelope(_case(**overrides)).verdict is verdict


def test_complete_case_reports_only_a_candidate_strict_envelope() -> None:
    assessment = assess_donor_envelope(_case())

    assert assessment.verdict is DonorEnvelopeVerdict.CANDIDATE_STRICT_ENVELOPE
    assert assessment.publication_novelty_authorized is False
    assert assessment.scientific_truth_authorized is False
    assert assessment.schema_id == SCHEMA_ID
    assert assessment.grants_authority == "NONE"
    assert assessment.self_authorizing is False
    assert assessment.preserves_historical_negative is True


def test_added_coordinates_cannot_rebrand_donor_coordinates() -> None:
    with pytest.raises(ValueError, match="distinct from donor coordinates"):
        _case(added_coordinate_ids=("severity",))


def test_strict_separation_requires_an_added_coordinate() -> None:
    with pytest.raises(ValueError, match="strict separation requires"):
        _case(added_coordinate_ids=())


def test_tested_ideal_product_requires_evidence() -> None:
    with pytest.raises(ValueError, match="requires evidence"):
        _case(ideal_product_evidence_ids=())


def test_negative_derived_successor_must_preserve_negative_identity() -> None:
    with pytest.raises(ValueError, match="preserve the historical negative"):
        _case(historical_negative_ids=())


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("donor_ids", ("SAGE", "SAGE")),
        ("falsifier_ids", ("",)),
    ],
)
def test_evidence_identity_lists_are_nonblank_and_unique(
    field_name: str, value: tuple[str, ...]
) -> None:
    with pytest.raises(ValueError):
        _case(**{field_name: value})
