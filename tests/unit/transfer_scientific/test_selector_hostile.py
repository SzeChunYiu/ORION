"""Hostile negative-transfer cases must not be admitted by the evidence-bound selector."""

from __future__ import annotations

from orion.transfer.scientific.selector import (
    SelectorKind,
    TransferDecision,
    select_transfer,
    surface_similarity,
)
from orion.transfer.scientific.toy_fixture import (
    TARGET_SIGNATURE,
    hostile_cases,
    negative_transfer_cases,
    positive_source_object,
    target_evidence,
)
from orion.transfer.v2.canonical import content_digest


def test_assumption_mismatch_is_refused_even_when_surface_similarity_is_high() -> None:
    source = positive_source_object()
    target = TARGET_SIGNATURE
    score = surface_similarity(source.problem_signature, target)
    assert score >= 0.5
    receipt = select_transfer(
        source,
        target,
        evidence=target_evidence(assumptions={"probes_are_reversible": False}),
        selector=SelectorKind.EVIDENCE_BOUND_CONTRACT,
    )
    assert receipt.status is TransferDecision.REFUSED_ASSUMPTION_MISMATCH
    assert receipt.admitted is False
    assert receipt.surface_similarity == score
    assert receipt.harmful_candidate_retained is True
    assert "ASSUMPTION_FALSE:probes_are_reversible" in receipt.reason_codes


def test_surface_similarity_selector_is_baseline_not_authority() -> None:
    source = positive_source_object()
    receipt = select_transfer(
        source,
        TARGET_SIGNATURE,
        evidence=target_evidence(),
        selector=SelectorKind.SURFACE_SIMILARITY_BASELINE,
    )
    assert receipt.status is TransferDecision.RANKED_FOR_INSPECTION
    assert receipt.admitted is False
    assert receipt.selector_kind is SelectorKind.SURFACE_SIMILARITY_BASELINE
    assert receipt.authority == "LOCAL_ENGINEERING_ONLY"


def test_negative_transfer_hostiles_are_refused_and_retained() -> None:
    statuses: set[TransferDecision] = set()
    kinds = {case.kind for case in negative_transfer_cases()}
    assert {
        "same_terms_incompatible_assumptions",
        "omitted_precondition",
        "stale_source_evidence",
        "unavailable_tool",
        "corrupted_falsifier",
    } <= kinds
    for case in negative_transfer_cases():
        receipt = select_transfer(
            case.source,
            case.target,
            evidence=case.evidence,
            selector=SelectorKind.EVIDENCE_BOUND_CONTRACT,
        )
        assert receipt.admitted is False, case.kind
        assert receipt.harmful_candidate_retained is True
        assert receipt.status is not TransferDecision.ADMITTED
        statuses.add(receipt.status)
    assert TransferDecision.REFUSED_ASSUMPTION_MISMATCH in statuses
    assert TransferDecision.REFUSED_PRECONDITION_OMITTED in statuses
    assert TransferDecision.REFUSED_STALE_EVIDENCE in statuses
    assert TransferDecision.REFUSED_UNAVAILABLE_TOOL in statuses
    assert TransferDecision.REFUSED_CORRUPTED_FALSIFIER in statuses


def test_matching_contract_can_admit_in_toy_fixture_only() -> None:
    receipt = select_transfer(
        positive_source_object(),
        TARGET_SIGNATURE,
        evidence=target_evidence(),
        selector=SelectorKind.EVIDENCE_BOUND_CONTRACT,
    )
    assert receipt.status is TransferDecision.ADMITTED
    assert receipt.evidence_level == "LOCAL_ENGINEERING_ONLY"
    assert receipt.scientific_authority is False


def test_receipt_is_content_addressed() -> None:
    receipt = select_transfer(
        positive_source_object(),
        TARGET_SIGNATURE,
        evidence=target_evidence(),
        selector=SelectorKind.EVIDENCE_BOUND_CONTRACT,
    )
    receipt.verify()
    unsigned = receipt.unsigned_payload()
    assert receipt.receipt_digest == content_digest(unsigned)


def test_different_terms_same_mechanic_is_not_blocked_by_surface_mismatch() -> None:
    cases = {case.kind: case for case in hostile_cases()}
    case = cases["different_terms_same_mechanic"]
    score = surface_similarity(case.source.problem_signature, case.target)
    assert score < 0.5
    receipt = select_transfer(
        case.source,
        case.target,
        evidence=case.evidence,
        selector=SelectorKind.EVIDENCE_BOUND_CONTRACT,
    )
    assert receipt.status is TransferDecision.ADMITTED
    assert receipt.admitted is True
