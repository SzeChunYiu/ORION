from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ADOPTION = ROOT / "papers/publication_closure/PACKAGE_ADOPTION_V2.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_adoption_names_the_manuscripts_used_by_the_recovered_packages() -> None:
    adoption = json.loads(ADOPTION.read_text())
    expected_sources = {
        "ORION-06": "papers/orion-06-recursive-recovery/MANUSCRIPT_V3.md",
        "ORION-07": "papers/orion-07-dual-instrument/MANUSCRIPT_V3.md",
        "ORION-08": "papers/orion-08-typed-state/MANUSCRIPT_V3.md",
    }

    for item in adoption["papers"]:
        bound_paths = {binding["path"] for binding in item["bindings"]}
        assert expected_sources[item["paper_id"]] in bound_paths


def test_package_adoption_is_additive_and_grants_no_submission_authority() -> None:
    adoption = json.loads(ADOPTION.read_text())

    assert adoption["schema"] == "ORION.BoundedSpecialistPackageAdoption.v2"
    assert adoption["terminal"] == (
        "PACKAGE_MATERIALIZED__FILING_VISUAL_QA_AND_FINAL_BYTE_BINDING_OPEN"
    )
    assert adoption["scientific_authority_delta"] == "NONE"
    assert {item["paper_id"] for item in adoption["papers"]} == {
        "ORION-06",
        "ORION-07",
        "ORION-08",
    }

    for item in adoption["papers"]:
        authority = item["authority"]
        assert authority["package_materialized"] is True
        assert authority["exact_submission_bytes_authorized"] is False
        assert authority["human_filing_metadata_complete"] is False
        assert authority["external_peer_review_claimed"] is False
        assert authority["journal_acceptance_claimed"] is False
        assert authority["top_tier_promotion"] is False

        for binding in item["bindings"]:
            path = ROOT / binding["path"]
            assert path.is_file(), binding["path"]
            assert path.stat().st_size == binding["bytes"]
            assert _sha256(path) == binding["sha256"]

        reproduction = item["source_reproduction"]
        assert reproduction["generated_source_byte_identical"] is True
        assert reproduction["pdf_byte_identical"] is False
        assert reproduction["recovered_pdf_sha256"] != reproduction["ci_pdf_sha256"]
