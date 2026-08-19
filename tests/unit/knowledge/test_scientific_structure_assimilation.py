from __future__ import annotations

from dataclasses import replace

from orion.knowledge.mechanism_assimilation import AssimilationAuthority
from orion.knowledge.scientific_structure_assimilation import (
    ScientificStructureAssimilationDraft,
    StructuralAssimilationVerdict,
    StructuralCoordinate,
    StructuralDisposition,
    StructuralFindingKind,
    StructuralScope,
    StructuralSource,
    StructuralSourceAccess,
    seal_structural_assimilation,
)


def _clean() -> ScientificStructureAssimilationDraft:
    return ScientificStructureAssimilationDraft(
        receipt_id="mw-001",
        source=StructuralSource(
            source_id="arxiv:2607.12474v2",
            title="Mechanistic World Models",
            version="v2",
            source_uri="arxiv:2607.12474v2",
            access=StructuralSourceAccess.FULL_TEXT_PRIMARY,
            source_scope=StructuralScope.MULTI_DOMAIN,
        ),
        scientific_ontology=("entities, variables, and reusable mechanisms are discovery objects",),
        explanation_commitments=("prediction alone is not scientific explanation",),
        failure_semantics=("predictive residual does not uniquely identify the responsible layer",),
        revision_semantics=("mechanisms and variables may be revised locally",),
        inquiry_semantics=("interventions identify mechanisms beyond passive prediction",),
        evidence_authority_semantics=("predictive/interventional fit is evidence, not ORION adoption authority",),
        preservation_obligations=("preserve or explicitly reopen previously validated old-regime successes",),
        coordinates=(
            StructuralCoordinate(
                coordinate_id="mechanism-centric-ontology",
                donor_commitment="reusable modular mechanisms organize scientific knowledge",
                disposition=StructuralDisposition.ADOPT_STRUCTURE,
                rationale="generic mechanism-centric organization is donor-owned",
            ),
        ),
        adopted_donor_claims=("mechanism-centric world models",),
        retained_orion_residuals=("typed preservation and protected authority boundary",),
        downstream_consequences=("remove broad mechanism-centric novelty from P9",),
        donor_authority=AssimilationAuthority.BOUNDED,
        claimed_orion_authority=AssimilationAuthority.BOUNDED,
        claimed_orion_scope=StructuralScope.MULTI_DOMAIN,
    )


def _kinds(draft: ScientificStructureAssimilationDraft) -> set[StructuralFindingKind]:
    return {finding.kind for finding in seal_structural_assimilation(draft).findings}


def test_clean_primary_full_text_receipt_is_admitted_but_non_authorizing() -> None:
    receipt = seal_structural_assimilation(_clean())
    assert receipt.verdict is StructuralAssimilationVerdict.ADMITTED
    assert receipt.grants_scientific_authority is False
    assert receipt.grants_novelty_authority is False
    assert receipt.self_authorizing is False
    assert len(receipt.content_hash) == 64


def test_abstract_only_source_stays_cannot_check() -> None:
    draft = _clean()
    draft = replace(draft, source=replace(draft.source, access=StructuralSourceAccess.PRIMARY_RECORD_ONLY))
    assert seal_structural_assimilation(draft).verdict is StructuralAssimilationVerdict.CANNOT_CHECK


def test_algorithm_only_absorption_is_blocked() -> None:
    assert StructuralFindingKind.ALGORITHM_ONLY_ABSORPTION in _kinds(
        replace(_clean(), explanation_commitments=())
    )


def test_donor_philosophy_cannot_be_rebranded_as_orion_residual() -> None:
    assert StructuralFindingKind.PHILOSOPHY_LAUNDERING in _kinds(
        replace(_clean(), retained_orion_residuals=("mechanism-centric world models",))
    )


def test_conflict_requires_discriminator() -> None:
    assert StructuralFindingKind.CONFLICT_WITHOUT_DISCRIMINATOR in _kinds(
        replace(_clean(), conflicts=("passive representation vs enactive coupling",))
    )


def test_authority_cannot_escalate_during_absorption() -> None:
    assert StructuralFindingKind.AUTHORITY_ESCALATION in _kinds(
        replace(
            _clean(),
            donor_authority=AssimilationAuthority.DESCRIPTIVE,
            claimed_orion_authority=AssimilationAuthority.GENERAL,
        )
    )


def test_revision_requires_preservation_or_reopen_statement() -> None:
    assert StructuralFindingKind.PRESERVATION_ERASURE in _kinds(
        replace(_clean(), preservation_obligations=())
    )


def test_domain_specific_source_cannot_mint_general_framework_claim() -> None:
    draft = _clean()
    draft = replace(
        draft,
        source=replace(draft.source, source_scope=StructuralScope.DOMAIN_SPECIFIC),
        claimed_orion_scope=StructuralScope.GENERAL_FRAMEWORK,
    )
    assert StructuralFindingKind.SCOPE_LAUNDERING in _kinds(draft)


def test_citation_only_receipt_is_rejected() -> None:
    assert StructuralFindingKind.CITATION_ONLY_RECEIPT in _kinds(
        replace(_clean(), downstream_consequences=(), no_change_reason="")
    )


def test_explicit_no_change_reason_is_not_citation_only() -> None:
    draft = replace(
        _clean(),
        downstream_consequences=(),
        no_change_reason="already fully represented by the current owner",
    )
    assert StructuralFindingKind.CITATION_ONLY_RECEIPT not in _kinds(draft)
