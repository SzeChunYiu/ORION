from __future__ import annotations

import importlib.util
from pathlib import Path

from orion.knowledge.scientific_structure_assimilation import (
    REQUIRED_COORDINATES,
    StructuralAssimilationVerdict,
    StructuralSourceAccess,
)

ROOT = Path(__file__).resolve().parents[3]
PACKET = ROOT / "research" / "structural-assimilation-v1" / "STRUCTURAL_ASSIMILATION_RECEIPTS_V1.py"
_spec = importlib.util.spec_from_file_location("structural_assimilation_receipts_v1", PACKET)
assert _spec is not None and _spec.loader is not None
packet = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(packet)


def test_first_wave_receipt_ids_are_unique_and_content_addressed() -> None:
    ids = [receipt.receipt_id for receipt in packet.RECEIPTS]
    assert len(ids) == len(set(ids)) == 10
    assert all(len(receipt.content_hash) == 64 for receipt in packet.RECEIPTS)


def test_every_receipt_has_exactly_one_a_to_g_assessment_and_explicit_profile() -> None:
    for receipt in packet.RECEIPTS:
        assert tuple(assessment.coordinate for assessment in receipt.assessments) == REQUIRED_COORDINATES
        assert all(assessment.commitment for assessment in receipt.assessments)
        assert all(assessment.evidence_refs for assessment in receipt.assessments)
        assert all(str(value).strip() for value in receipt.assumption_profile.__dict__.values())


def test_nine_full_text_receipts_admit_and_mda_remains_cannot_check() -> None:
    admitted = [r for r in packet.RECEIPTS if r.verdict is StructuralAssimilationVerdict.ADMITTED]
    cannot_check = [r for r in packet.RECEIPTS if r.verdict is StructuralAssimilationVerdict.CANNOT_CHECK]
    blocked = [r for r in packet.RECEIPTS if r.verdict is StructuralAssimilationVerdict.BLOCKED]
    assert len(admitted) == packet.EXPECTED_ADMITTED == 9
    assert len(cannot_check) == packet.EXPECTED_CANNOT_CHECK == 1
    assert len(blocked) == packet.EXPECTED_BLOCKED == 0
    assert cannot_check[0].donor.donor_id == "arxiv:2608.09696"
    assert cannot_check[0].donor.access is StructuralSourceAccess.ABSTRACT_ONLY


def test_mda_cannot_be_silently_promoted_by_the_packet() -> None:
    mda = next(r for r in packet.RECEIPTS if r.donor.donor_id == "arxiv:2608.09696")
    assert mda.verdict is StructuralAssimilationVerdict.CANNOT_CHECK
    assert all("ABSTRACT_ONLY" in assessment.commitment for assessment in mda.assessments)
    assert packet.UNRESOLVED_KEY_DONORS == ("arxiv:2608.09696",)


def test_structural_closure_fails_closed_on_the_unresolved_key_donor() -> None:
    assert packet.CLOSURE.admitted_receipts == 9
    assert packet.CLOSURE.cannot_check_receipts == 1
    assert packet.CLOSURE.blocked_receipts == 0
    assert packet.CLOSURE.no_material_change_rounds == 2
    assert packet.CLOSURE.terminal == packet.EXPECTED_TERMINAL == "CANNOT_CHECK"
    assert packet.CLOSURE.method_disposition == packet.EXPECTED_METHOD_DISPOSITION == "CANNOT_CHECK"
    assert packet.CLOSURE.grants_authority == "NONE"
    assert packet.CLOSURE.self_authorizing is False


def test_two_no_material_change_rounds_are_explicit_and_non_authorizing() -> None:
    assert len(packet.NO_MATERIAL_CHANGE_ROUNDS) == 2
    assert all("NMC_" in round_record for round_record in packet.NO_MATERIAL_CHANGE_ROUNDS)
    assert all("MDA" in round_record or "owner" in round_record for round_record in packet.NO_MATERIAL_CHANGE_ROUNDS)


def test_no_receipt_grants_novelty_authority_or_equivalence() -> None:
    for receipt in packet.RECEIPTS:
        assert receipt.grants_authority == "NONE"
        assert receipt.grants_novelty is False
        assert receipt.grants_donor_equivalence is False
        assert receipt.self_authorizing is False
