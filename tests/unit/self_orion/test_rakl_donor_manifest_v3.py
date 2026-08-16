import json
from pathlib import Path


MANIFEST = Path("provenance/rakl/DONOR_MANIFEST_V3.json")
EXPECTED_PUBLIC = {
    "assimilation",
    "atlas_gluing",
    "backward_multiseed",
    "backward_multiseed_benchmark",
    "bridge_composition",
    "capability",
    "challenge_learning",
    "claim_evidence",
    "context_compiler",
    "core",
    "formalism",
    "generator_transport",
    "identity",
    "identity_saturation",
    "source_identity",
    "invention",
    "measurement",
    "multires_memory",
    "promotion",
    "promotion_attestation",
    "retrieval_benchmark",
    "route_family_health",
    "similarity",
    "subject_identity",
}
TERMINAL = {
    "EXACT_REUSE",
    "RECONSTRUCTED",
    "TESTS_RESULTS_REUSED",
    "DEFER_WITH_TRIGGER",
    "REJECT_WITH_REASON",
}


def _manifest():
    return json.loads(MANIFEST.read_text())


def test_manifest_is_pinned_to_frozen_rakl_public_api():
    data = _manifest()
    assert data["frozen_rakl_commit"] == "70f5f7c4a6771ffd1158765b42ac9f8aee8a270f"
    assert data["public_api_blob_sha"] == "c2c06a3df1c2a6856eb65886e5c431fc9eb96291"


def test_every_frozen_public_family_has_exactly_one_terminal_disposition():
    rows = _manifest()["public_families"]
    names = [row["family"] for row in rows]
    assert len(names) == len(set(names))
    assert set(names) == EXPECTED_PUBLIC
    assert all(row["status"] in TERMINAL for row in rows)
    assert all(row["orion"].strip() for row in rows)


def test_engineering_waves_have_terminal_dispositions_and_real_triggers_when_deferred():
    rows = _manifest()["engineering_waves"]
    assert len(rows) == 10
    assert all(row["status"] in TERMINAL for row in rows)
    for row in rows:
        if row["status"] == "DEFER_WITH_TRIGGER":
            assert row["trigger"] and row["trigger"].strip()


def test_manifest_does_not_claim_repository_wide_saturation_from_public_api_coverage():
    boundary = _manifest()["closure_boundary"]
    assert "remains open" in boundary
    assert "non-public" in boundary
