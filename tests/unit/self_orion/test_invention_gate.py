from orion.self_orion.invention_gate import (
    InventionReadinessEvidence,
    InventionTarget,
    assess_invention_readiness,
)
from orion.self_orion.rakl_donor_gate import (
    RAKL_DONOR_COMMIT,
    RaklDonorAudit,
    RaklDonorCandidate,
    RaklDonorDisposition,
    RaklDonorRouteReceipt,
    RaklDonorRouteVerdict,
    RaklDonorSearchRoute,
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


def _donor_audit(*, reusable=False):
    receipts = tuple(
        RaklDonorRouteReceipt(
            route=route,
            verdict=RaklDonorRouteVerdict.COMPLETE,
            scope=f"searched {route.value.lower()} for target mechanic",
            evidence_ids=(f"e:rakl:{route.value.lower()}",),
        )
        for route in RaklDonorSearchRoute
    )
    disposition = (
        RaklDonorDisposition.RECONSTRUCTED
        if reusable
        else RaklDonorDisposition.REJECT_WITH_REASON
    )
    return RaklDonorAudit(
        audit_id="rakl-donor-audit:test",
        target_signature="missing operator for test target",
        rakl_commit=RAKL_DONOR_COMMIT,
        route_receipts=receipts,
        candidates=(
            RaklDonorCandidate(
                donor_id="rakl:test-donor",
                source_paths=("src/rakl/test_donor.py",),
                disposition=disposition,
                evidence_ids=("e:rakl:test-donor",),
                rationale_or_trigger=(
                    "existing RAKL contract survives and should be reconstructed"
                    if reusable
                    else "candidate contract is scoped to a different state transition and is not applicable"
                ),
            ),
        ),
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
            rakl_donor_audit=_donor_audit(),
        ),
    )
    assert not report.ready
    assert report.target is InventionTarget.NONE
    assert "ordinary_failure_causes_not_excluded" in report.reasons
    assert not report.grants_invention_authority


def test_supported_method_basis_gap_can_become_operator_invention_candidate_only_after_rakl_donor_search():
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
            rakl_donor_audit=_donor_audit(),
        ),
    )
    assert report.ready
    assert report.target is InventionTarget.OPERATOR
    assert not report.grants_invention_authority
    assert not report.grants_promotion_authority


def test_missing_rakl_donor_audit_blocks_otherwise_ready_invention():
    report = assess_invention_readiness(
        _flat_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2"),
            ordinary_causes_excluded=True,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=False,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=("e:1",),
        ),
    )
    assert not report.ready
    assert "rakl_donor_audit_missing" in report.reasons


def test_surviving_rakl_donor_preempts_clean_generation_invention():
    report = assess_invention_readiness(
        _flat_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2"),
            ordinary_causes_excluded=True,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=False,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=("e:1",),
            rakl_donor_audit=_donor_audit(reusable=True),
        ),
    )
    assert not report.ready
    assert report.target is InventionTarget.NONE
    assert "rakl_surviving_donor_available:rakl:test-donor" in report.reasons


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
            rakl_donor_audit=_donor_audit(),
        ),
    )
    assert not report.ready
    assert "invention_target_responsibility_ambiguous" in report.reasons
