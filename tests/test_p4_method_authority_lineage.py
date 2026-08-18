from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p4_method_authority import build_method_transfer_receipt


def digest(label: str) -> str:
    return content_digest({"label": label})


def test_multi_donor_ids_keep_their_own_digests_when_canonicalized():
    d_a = digest("A")
    d_b = digest("B")
    receipt = build_method_transfer_receipt(
        method_id="method:multi",
        target_id="target:multi",
        target_digest=digest("target"),
        donor_ids=("donor:B", "donor:A"),
        donor_digests=(d_b, d_a),
        structural_signature_digest=digest("signature"),
        assumptions_retained=("finite_state",),
        reconstruction="lift",
        source_lineage_valid=True,
        assumptions_preserved=True,
        reconstruction_valid=True,
        visible_result_pass=True,
        protected_result_pass=True,
        evaluator_independent=True,
        evaluator_digest=digest("evaluator"),
        novelty_search_digest=digest("novelty"),
        prior_art_found=False,
    )
    assert receipt.donor_lineage == (("donor:A", d_a), ("donor:B", d_b))
    payload = receipt.unsigned_payload()
    assert payload["donor_lineage"] == [
        {"donor_id": "donor:A", "donor_digest": d_a},
        {"donor_id": "donor:B", "donor_digest": d_b},
    ]
