import json
from pathlib import Path


ROOT = Path(__file__).parents[3]
INVENTORY = ROOT / "provenance" / "rakl" / "DONOR_DISPOSITION_V3.json"
TERMINAL = {
    "EXACT_REUSE",
    "RECONSTRUCTED",
    "TESTS_RESULTS_REUSED",
    "DEFER_WITH_TRIGGER",
    "REJECT_WITH_REASON",
}
EXPECTED_PUBLIC = {
    "method_assimilation",
    "atlas_gluing",
    "backward_multiseed",
    "backward_multiseed_benchmark",
    "bridge_composition",
    "capability_shaping",
    "challenge_failure_learning",
    "claim_evidence_binding",
    "context_compiler",
    "core_projection_context_relations",
    "formalism_mechanism_verification_packets",
    "generator_transport",
    "evidence_identity",
    "identity_aware_saturation",
    "source_identity",
    "invention_positive_goal_pareto",
    "measurement_relations",
    "multiresolution_memory",
    "promotion",
    "promotion_attestation",
    "retrieval_benchmark",
    "route_family_health",
    "similarity_analogy_witnesses",
    "subject_execution_identity_attestation",
}
EXPECTED_ENGINEERING = {f"E{index}" for index in range(1, 21)}


def _inventory():
    return json.loads(INVENTORY.read_text())


def test_inventory_is_pinned_to_frozen_rakl_donor():
    payload = _inventory()
    assert payload["donor_revision"] == "70f5f7c4a6771ffd1158765b42ac9f8aee8a270f"


def test_every_public_family_has_exactly_one_terminal_disposition():
    rows = _inventory()["public_families"]
    assert {row["id"] for row in rows} == EXPECTED_PUBLIC
    assert len(rows) == len(EXPECTED_PUBLIC)
    assert all(row["disposition"] in TERMINAL for row in rows)
    assert not any("OPEN" in row["disposition"] for row in rows)


def test_every_engineering_fibre_e1_e20_has_terminal_disposition():
    rows = _inventory()["engineering_fibres"]
    assert {row["id"] for row in rows} == EXPECTED_ENGINEERING
    assert len(rows) == 20
    assert all(row["disposition"] in TERMINAL for row in rows)


def test_reuse_and_reconstruction_rows_bind_orion_evidence():
    for row in _inventory()["public_families"]:
        if row["disposition"] in {"EXACT_REUSE", "RECONSTRUCTED", "TESTS_RESULTS_REUSED"}:
            assert row.get("orion_evidence"), row["id"]


def test_deferred_rows_have_explicit_activation_trigger():
    payload = _inventory()
    for row in (*payload["public_families"], *payload["engineering_fibres"]):
        if row["disposition"] == "DEFER_WITH_TRIGGER":
            assert row.get("trigger", "").strip(), row["id"]


def test_inventory_does_not_claim_deferred_capabilities_are_implemented():
    boundary = _inventory()["closure_boundary"]
    assert "does not imply the underlying capability exists" in boundary
