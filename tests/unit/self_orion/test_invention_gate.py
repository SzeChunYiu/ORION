from orion.self_orion.invention_gate import (
    InventionReadinessEvidence,
    InventionTarget,
    assess_invention_readiness,
)
from orion.self_orion.saturation_vector import (
    DevelopmentNoveltyRound,
    DevelopmentSaturationAxis,
    assess_development_saturation,
)


def _flat_report():
    zero = tuple((axis, 0) for axis in DevelopmentSaturationAxis)
    return assess_development_saturation(
        (
            DevelopmentNoveltyRound("r1", "function-only", True, zero),
            DevelopmentNoveltyRound("r2", "cross-domain", True, zero),
        )
    )


def test_repeated_failure_does_not_license_invention_until_ordinary_causes_and_target_are_discriminated():
    report = assess_invention_readiness(
        _flat_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2"),
            ordinary_causes_excluded=False,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=False,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=("e:discriminator",),
        ),
    )
    assert not report.ready
    assert report.target is InventionTarget.NONE
    assert "ordinary_failure_causes_not_excluded" in report.reasons
    assert not report.grants_invention_authority


def test_supported_method_basis_gap_can_become_operator_invention_candidate_but_not_authority():
    report = assess_invention_readiness(
        _flat_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2", "v3"),
            ordinary_causes_excluded=True,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=False,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=("e:1", "e:2"),
        ),
    )
    assert report.ready
    assert report.target is InventionTarget.OPERATOR
    assert not report.grants_invention_authority
    assert not report.grants_promotion_authority


def test_ambiguous_representation_and_operator_gap_stays_blocked():
    report = assess_invention_readiness(
        _flat_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2"),
            ordinary_causes_excluded=True,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=True,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=("e:1",),
        ),
    )
    assert not report.ready
    assert "invention_target_responsibility_ambiguous" in report.reasons
