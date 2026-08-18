from __future__ import annotations

from dataclasses import replace

import pytest

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p4_method_authority import (
    MethodAuthorityCoordinate as C,
    MethodAuthorityState as S,
    build_method_transfer_receipt,
    claim_is_promotable,
    derive_method_authority,
)


def digest(label: str) -> str:
    return content_digest({"label": label})


def receipt(**changes: object):
    payload: dict[str, object] = {
        "method_id": "method:m1",
        "target_id": "target:t1",
        "target_digest": digest("target"),
        "donor_ids": ("donor:d1",),
        "donor_digests": (digest("donor"),),
        "structural_signature_digest": digest("signature"),
        "assumptions_retained": ("finite_state",),
        "assumptions_dropped": (),
        "assumptions_modified": (),
        "adaptation_steps": ("rename_state",),
        "predicted_effects": ("reduce_search",),
        "reconstruction": "lift_solution",
        "source_lineage_valid": True,
        "assumptions_preserved": True,
        "reconstruction_valid": True,
        "visible_result_pass": True,
        "protected_result_pass": True,
        "evaluator_independent": True,
        "evaluator_digest": digest("evaluator"),
        "generator_accessed_evaluator": False,
        "novelty_search_digest": digest("novelty-search"),
        "prior_art_found": False,
        "claims_new_primitive": False,
        "known_composition": False,
    }
    payload.update(changes)
    return build_method_transfer_receipt(**payload)


def test_clean_transfer_has_separate_coordinate_authority_and_no_adoption():
    record = derive_method_authority(receipt())
    assert record.state(C.VALIDITY) is S.SUPPORTED
    assert record.state(C.APPLICABILITY) is S.SUPPORTED
    assert record.state(C.TRANSFER) is S.SUPPORTED
    assert record.state(C.NOVELTY) is S.SUPPORTED
    assert record.state(C.UTILITY) is S.SUPPORTED
    assert record.state(C.ADOPTION) is S.CANNOT_CHECK
    assert claim_is_promotable(record, (C.VALIDITY, C.APPLICABILITY, C.TRANSFER, C.UTILITY))
    assert not claim_is_promotable(record, (C.ADOPTION,))


def test_useful_known_donor_can_be_valid_but_not_novel():
    record = derive_method_authority(receipt(prior_art_found=True))
    assert record.state(C.VALIDITY) is S.SUPPORTED
    assert record.state(C.TRANSFER) is S.SUPPORTED
    assert record.state(C.UTILITY) is S.SUPPORTED
    assert record.state(C.NOVELTY) is S.BLOCKED
    assert "PRIOR_ART_FOUND" in record.reasons(C.NOVELTY)
    assert claim_is_promotable(record, (C.VALIDITY, C.TRANSFER, C.UTILITY))
    assert not claim_is_promotable(record, (C.NOVELTY,))


def test_erased_donor_assumption_blocks_applicability_and_transfer():
    record = derive_method_authority(
        receipt(
            assumptions_retained=(),
            assumptions_dropped=("finite_state",),
            assumptions_preserved=False,
        )
    )
    assert record.state(C.APPLICABILITY) is S.BLOCKED
    assert record.state(C.TRANSFER) is S.BLOCKED
    assert not claim_is_promotable(record, (C.TRANSFER,))


def test_invalid_reconstruction_blocks_validity_and_transfer():
    record = derive_method_authority(receipt(reconstruction_valid=False))
    assert record.state(C.VALIDITY) is S.BLOCKED
    assert record.state(C.TRANSFER) is S.BLOCKED
    assert "RECONSTRUCTION_INVALID" in record.reasons(C.VALIDITY)


def test_visible_success_cannot_override_protected_failure():
    record = derive_method_authority(
        receipt(visible_result_pass=True, protected_result_pass=False)
    )
    assert record.state(C.VALIDITY) is S.BLOCKED
    assert record.state(C.UTILITY) is S.BLOCKED
    assert not claim_is_promotable(record, (C.VALIDITY, C.UTILITY))


def test_missing_protected_evidence_is_cannot_check_even_with_visible_success():
    record = derive_method_authority(
        receipt(
            visible_result_pass=True,
            protected_result_pass=None,
            evaluator_digest="",
        )
    )
    assert record.state(C.VALIDITY) is S.CANNOT_CHECK
    assert record.state(C.UTILITY) is S.CANNOT_CHECK


def test_evaluator_feedback_leakage_blocks_validity_and_utility():
    record = derive_method_authority(receipt(generator_accessed_evaluator=True))
    assert record.state(C.VALIDITY) is S.BLOCKED
    assert record.state(C.UTILITY) is S.BLOCKED
    assert record.reasons(C.VALIDITY) == ("EVALUATOR_LEAKAGE",)


def test_known_composition_cannot_be_laundered_into_new_primitive():
    record = derive_method_authority(
        receipt(
            prior_art_found=False,
            claims_new_primitive=True,
            known_composition=True,
        )
    )
    assert record.state(C.NOVELTY) is S.BLOCKED
    assert "KNOWN_COMPOSITION_NOT_NEW_PRIMITIVE" in record.reasons(C.NOVELTY)


def test_semantic_distance_or_generation_cannot_replace_novelty_search():
    record = derive_method_authority(
        receipt(
            novelty_search_digest="",
            prior_art_found=None,
            claims_new_primitive=True,
        )
    )
    assert record.state(C.NOVELTY) is S.CANNOT_CHECK
    assert "NOVELTY_SEARCH_INCOMPLETE" in record.reasons(C.NOVELTY)


def test_wrong_source_lineage_blocks_transfer_without_erasing_other_coordinates():
    record = derive_method_authority(receipt(source_lineage_valid=False))
    assert record.state(C.TRANSFER) is S.BLOCKED
    assert record.state(C.VALIDITY) is S.SUPPORTED
    assert record.state(C.UTILITY) is S.SUPPORTED


def test_receipt_is_content_bound_and_tampering_is_detected():
    original = receipt()
    original.verify()
    with pytest.raises(ValueError):
        replace(original, target_digest=digest("substituted-target")).verify()


def test_record_is_content_bound_and_cannot_be_scalarized_into_adoption():
    record = derive_method_authority(receipt())
    record.verify()
    with pytest.raises(ValueError):
        replace(record, authority_terminal="AUTHORIZED").verify()


def test_empty_required_coordinate_set_is_rejected():
    with pytest.raises(ValueError):
        claim_is_promotable(derive_method_authority(receipt()), ())
