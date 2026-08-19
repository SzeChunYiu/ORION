from __future__ import annotations

from dataclasses import replace

from orion.knowledge.scientific_structure_assimilation import (
    REQUIRED_COORDINATES,
    CoordinateAssessment,
    ScientificStructureAssimilationReceipt,
    StructuralAssimilationDraft,
    StructuralAssimilationVerdict,
    StructuralAuthority,
    StructuralCoordinate,
    StructuralDisposition,
    StructuralDonorIdentity,
    StructuralHostileFindingKind,
    StructuralSourceAccess,
    StructuralSourceKind,
    build_structural_assimilation_closure,
    seal_structural_assimilation,
)

DONOR = StructuralDonorIdentity(
    donor_id="arxiv:2608.09696",
    title="Model Discovery Agent",
    source_uri="https://arxiv.org/abs/2608.09696",
    source_kind=StructuralSourceKind.PRIMARY_PAPER,
    access=StructuralSourceAccess.FULL_TEXT,
    source_scope="three bounded mechanistic discovery benchmarks",
)


def _assessments() -> tuple[CoordinateAssessment, ...]:
    return tuple(
        CoordinateAssessment(
            coordinate=coordinate,
            commitment=f"source-grounded commitment for {coordinate.value}",
            disposition=(
                StructuralDisposition.ADAPT_STRUCTURE
                if coordinate in {StructuralCoordinate.C_FAILURE_ANOMALY, StructuralCoordinate.D_REVISION}
                else StructuralDisposition.ADOPT_STRUCTURE
            ),
            donor_owner_refs=("arxiv:2608.09696",),
            orion_consequence=f"route {coordinate.value} consequence to its existing owner",
            evidence_refs=("https://arxiv.org/abs/2608.09696",),
        )
        for coordinate in REQUIRED_COORDINATES
    )


def _draft(**overrides) -> StructuralAssimilationDraft:
    base = dict(
        receipt_id="ssa:v1:mda",
        donor=DONOR,
        assessments=_assessments(),
        donor_authority=StructuralAuthority.BOUNDED,
        claimed_authority=StructuralAuthority.BOUNDED,
        representation_boundary="M-open expands a model/hypothesis class; open variables/measurement require separate ORION owners",
        preservation_rule="prior evidence is retained with provenance and affected claims are revalidated after class expansion",
        llm_involved=True,
        explicit_non_llm_machinery=("SMC", "SBI", "VoI", "predictive check"),
        llm_marginal_role_checked=True,
        donor_has_relevant_negative_result=True,
        negative_results=("LLM feedback-sensitive experimental design requires a separate anti-hype control",),
        conflict_tests=("fixed-model-class vs representation-change discriminator",),
        downstream_children=("#318", "#403", "P5"),
        mechanism_receipt_ids=("mechanism:mda:voi",),
        structural_receipt_id_for_mechanics="ssa:v1:mda",
    )
    base.update(overrides)
    return StructuralAssimilationDraft(**base)


def _kinds(draft: StructuralAssimilationDraft) -> set[StructuralHostileFindingKind]:
    return {finding.kind for finding in seal_structural_assimilation(draft).hostile_findings}


def test_clean_receipt_is_admitted_but_grants_nothing() -> None:
    receipt = seal_structural_assimilation(_draft())
    assert receipt.verdict is StructuralAssimilationVerdict.ADMITTED
    assert receipt.hostile_findings == ()
    assert len(receipt.content_hash) == 64
    assert receipt.grants_authority == "NONE"
    assert receipt.grants_novelty is False
    assert receipt.grants_donor_equivalence is False
    assert receipt.self_authorizing is False


def test_algorithm_only_absorption_is_rejected() -> None:
    assert StructuralHostileFindingKind.ALGORITHM_ONLY_ABSORPTION in _kinds(
        _draft(assessments=_assessments()[:-1])
    )


def test_philosophy_laundering_requires_donor_ownership() -> None:
    assessments = list(_assessments())
    assessments[0] = replace(assessments[0], donor_owner_refs=())
    assert StructuralHostileFindingKind.PHILOSOPHY_LAUNDERING in _kinds(
        _draft(assessments=tuple(assessments))
    )


def test_conflict_requires_a_discriminator_not_a_prose_blend() -> None:
    assessments = list(_assessments())
    assessments[3] = replace(assessments[3], disposition=StructuralDisposition.CONFLICT)
    assert StructuralHostileFindingKind.INCOMPATIBLE_BLEND in _kinds(
        _draft(assessments=tuple(assessments), conflict_tests=())
    )
    assert StructuralHostileFindingKind.INCOMPATIBLE_BLEND not in _kinds(
        _draft(assessments=tuple(assessments), conflict_tests=("countermodel:R1-vs-R2",))
    )


def test_absorption_cannot_escalate_scientific_authority() -> None:
    assert StructuralHostileFindingKind.AUTHORITY_ESCALATION in _kinds(
        _draft(claimed_authority=StructuralAuthority.GENERAL)
    )


def test_representation_boundary_cannot_be_erased() -> None:
    assert StructuralHostileFindingKind.REPRESENTATION_ERASURE in _kinds(
        _draft(representation_boundary="")
    )


def test_revision_must_record_preservation_or_revalidation() -> None:
    assert StructuralHostileFindingKind.PRESERVATION_ERASURE in _kinds(
        _draft(preservation_rule="")
    )


def test_cross_domain_scope_claim_requires_an_explicit_rationale() -> None:
    assert StructuralHostileFindingKind.SCOPE_LAUNDERING in _kinds(
        _draft(claims_cross_domain_generalization=True, scope_extension_rationale="")
    )
    assert StructuralHostileFindingKind.SCOPE_LAUNDERING not in _kinds(
        _draft(
            claims_cross_domain_generalization=True,
            scope_extension_rationale="only the receipt schema generalizes; scientific results remain benchmark-scoped",
        )
    )


def test_llm_mystification_is_blocked_when_explicit_machinery_is_omitted() -> None:
    assert StructuralHostileFindingKind.LLM_MYSTIFICATION in _kinds(
        _draft(explicit_non_llm_machinery=())
    )
    assert StructuralHostileFindingKind.LLM_MYSTIFICATION in _kinds(
        _draft(llm_marginal_role_checked=False)
    )


def test_known_negative_result_cannot_be_deleted() -> None:
    assert StructuralHostileFindingKind.NEGATIVE_RESULT_DELETION in _kinds(
        _draft(negative_results=())
    )


def test_citation_only_receipt_requires_downstream_change_or_no_change_reason() -> None:
    assert StructuralHostileFindingKind.CITATION_ONLY_RECEIPT in _kinds(
        _draft(downstream_children=(), explicit_no_change_reason="")
    )
    assert StructuralHostileFindingKind.CITATION_ONLY_RECEIPT not in _kinds(
        _draft(downstream_children=(), explicit_no_change_reason="donor structure already represented by P3/P7")
    )


def test_material_mechanics_require_upstream_structure_identity() -> None:
    assert StructuralHostileFindingKind.MISSING_UPSTREAM_STRUCTURE in _kinds(
        _draft(structural_receipt_id_for_mechanics="")
    )


def test_secondary_and_incomplete_sources_cannot_be_admitted() -> None:
    secondary = replace(DONOR, source_kind=StructuralSourceKind.SECONDARY)
    assert StructuralHostileFindingKind.UNGROUNDED_SOURCE in _kinds(_draft(donor=secondary))

    abstract_only = replace(DONOR, access=StructuralSourceAccess.ABSTRACT_ONLY)
    receipt = seal_structural_assimilation(_draft(donor=abstract_only))
    assert receipt.verdict is StructuralAssimilationVerdict.CANNOT_CHECK


def test_two_no_material_change_rounds_earn_saturation_not_method_superiority() -> None:
    receipts = tuple(
        seal_structural_assimilation(replace(_draft(), receipt_id=f"ssa:v1:{i}"))
        for i in range(3)
    )
    report = build_structural_assimilation_closure(receipts, no_material_change_rounds=2)
    assert report.terminal == "STRUCTURAL_ASSIMILATION_SATURATED"
    assert report.method_disposition == "USEFUL_PROCESS_NOT_NOVEL"
    assert report.grants_authority == "NONE"
    assert report.self_authorizing is False


def test_blocked_or_incompletely_grounded_receipt_prevents_saturation() -> None:
    good = seal_structural_assimilation(_draft())
    bad = seal_structural_assimilation(replace(_draft(), receipt_id="bad", preservation_rule=""))
    assert build_structural_assimilation_closure((good, bad), no_material_change_rounds=2).terminal == "CANNOT_CHECK"
