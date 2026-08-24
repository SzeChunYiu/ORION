#!/usr/bin/env python3
"""Validate bounded P1 V3 scientific artifacts without querying providers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


LANE = Path(__file__).resolve().parent
SCRATCH = Path(
    "/Users/billy/Documents/Codex/2026-08-23/can-x20/work/scratch/"
    "p1-structured-action-semantics-v3"
)
TERMINAL = (
    "P1_V3_THREE_STRATUM_STRUCTURED_ACTION_METADATA_FEASIBILITY_PASS__"
    "ZERO_OF_TWELVE_OWNER_ALGEBRA_FIELDS_SUFFICIENT__"
    "SCIENTIFIC_ACTION_GOLD_AND_CONSTRUCT_VALIDITY_CANNOT_CHECK"
)


def load(name: str) -> dict:
    return json.loads((LANE / name).read_text())


def digest(name: str) -> str:
    return hashlib.sha256((LANE / name).read_bytes()).hexdigest()


def main() -> None:
    protocol = load("PROTOCOL_V3.json")
    protocol_freeze = load("PROTOCOL_FREEZE_RECEIPT_V3.json")
    parser_freeze = load("PARSER_FREEZE_RECEIPT_V3.json")
    normalization_freeze = load("SOURCE_INTERFACE_NORMALIZATION_FREEZE_RECEIPT_A_V3.json")
    raw = load("PROVIDER_STRUCTURED_ACTION_CENSUS_RAW_INTERFACE_V3.json")
    census = load("PROVIDER_STRUCTURED_ACTION_CENSUS_V3.json")
    owner = load("OWNER_FIELD_FEASIBILITY_V3.json")
    rights = load("RIGHTS_AND_PROVENANCE_RECEIPT_V3.json")
    atlas = load("CONSTRUCT_VALIDITY_FAILURE_ATLAS_V3.json")
    ledger = load("NEGATIVE_RESULT_LEDGER_V3.json")
    result = load("RESULT_V3.json")

    assert protocol_freeze["protocol_sha256"] == digest("PROTOCOL_V3.json")
    assert parser_freeze["parser_rules_sha256"] == digest("PARSER_RULES_V3.json")
    assert normalization_freeze["amendment_sha256"] == digest(
        "SOURCE_INTERFACE_NORMALIZATION_AMENDMENT_A_V3.json"
    )
    assert normalization_freeze["raw_census_sha256"] == digest(
        "PROVIDER_STRUCTURED_ACTION_CENSUS_RAW_INTERFACE_V3.json"
    )
    assert digest("PROVIDER_STRUCTURED_ACTION_CENSUS_RAW_INTERFACE_V3.json") == (
        "38ce1bb820911f7813bd73d44b0597f1efb5e846c8cb1af3f7cac47f7d68dfad"
    )

    pool = census["v2_pool_reconstruction"]
    assert pool["exact_rights_relations"] == 12_038
    assert pool["exact_rights_families"] == 11_602
    assert pool["unique_notice_records"] == 11_991
    assert pool["matches_v2_relations_and_families"] is True

    record_counts = census["classified_structured_action_records"]
    assert record_counts["single_stratum_counts"] == {
        "CORRECTION_OR_ERRATUM": 256,
        "EXPRESSION_OF_CONCERN": 469,
        "RETRACTION": 11_251,
    }
    assert record_counts["ambiguous_multiple_strata"] == 0
    assert record_counts["other_or_cannot_check"] == 15
    assert sum(record_counts["single_stratum_counts"].values()) + 15 == 11_991
    assert sum(census["classified_exact_rights_relations"].values()) == 12_038

    initial = census["initial_raw_interface_comparison"]
    assert initial["artifact_sha256"] == digest(
        "PROVIDER_STRUCTURED_ACTION_CENSUS_RAW_INTERFACE_V3.json"
    )
    assert raw["cross_provider_structural_agreement"]["exact_publication_type_set_matches"] == 1
    assert raw["cross_provider_structural_agreement"]["exact_relation_type_set_matches"] == 1

    agreement = census["cross_provider_structural_agreement"]
    assert agreement["comparable_notice_records"] == 11_991
    assert agreement["normalized_exact_publication_type_set_matches"] == 740
    assert agreement["normalized_exact_relation_type_set_matches"] == 11_988
    assert agreement["epmc_added_jats_pmc_publication_type_affected_records"] == 739
    assert agreement["normalized_publication_type_epmc_only_token_frequencies"] == {
        "Retraction of Publication": 11_251
    }
    assert agreement["unmapped_epmc_relation_type_record_frequencies"] == {"Preprint in": 1}
    assert agreement["normalized_relation_type_pubmed_only_token_frequencies"] == {
        "RetractionOf": 2
    }

    assert owner["requirement_group_count"] == 12
    assert owner["sufficient_owner_field_count"] == 0
    assert owner["partial_analogue_count"] == 3
    assert len(owner["field_decisions"]) == 12
    assert all(row["sufficiency"] == "INSUFFICIENT" for row in owner["field_decisions"])
    assert all(not row["counts_as_sufficient_owner_field"] for row in owner["field_decisions"])
    assert owner["terminal"] == TERMINAL

    assert rights["target_algebra_rights_group"]["status"] == "INSUFFICIENT"
    assert not rights["target_algebra_rights_group"]["counts_as_sufficient_owner_field"]
    assert rights["boundary"]["case_identifiers_retained"] is False
    assert rights["boundary"]["raw_provider_responses_retained"] is False
    assert len(atlas["entries"]) == 14
    assert len(ledger["entries"]) == 5

    assert result["terminal"] == TERMINAL
    assert result["provider_census_sha256"] == digest("PROVIDER_STRUCTURED_ACTION_CENSUS_V3.json")
    assert result["owner_field_feasibility_sha256"] == digest("OWNER_FIELD_FEASIBILITY_V3.json")
    assert result["rights_and_provenance_sha256"] == digest(
        "RIGHTS_AND_PROVENANCE_RECEIPT_V3.json"
    )
    assert result["construct_validity_failure_atlas_sha256"] == digest(
        "CONSTRUCT_VALIDITY_FAILURE_ATLAS_V3.json"
    )
    assert result["owner_algebra"] == {
        "partial_analogues": 3,
        "requirement_groups": 12,
        "sufficient_groups": 0,
    }
    assert census["boundary"]["case_text_semantically_accessed"] is False
    assert census["boundary"]["model_or_comparator_executed"] is False
    assert census["boundary"]["protected_outcomes_accessed"] is False
    assert census["boundary"]["scientific_action_gold_assigned"] == 0
    assert census["boundary"]["owner_algebra_fields_assigned"] == 0

    assert not SCRATCH.exists()
    forbidden_suffixes = {".csv", ".html", ".dtd", ".pyc"}
    forbidden = [
        str(path.relative_to(LANE))
        for path in LANE.rglob("*")
        if path.is_file() and path.suffix in forbidden_suffixes
    ]
    assert forbidden == []
    assert not (LANE / "__pycache__").exists()
    assert not (LANE / ".git").exists()

    artifact_names = sorted(
        path.name
        for path in LANE.iterdir()
        if path.is_file()
        and path.name not in {"VALIDATION_RECEIPT_V3.json", "SHA256SUMS"}
    )
    receipt = {
        "schema_version": "orion.p1.structured-action-semantics.validation-receipt.v3",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "assertion_count": 52,
        "terminal": TERMINAL,
        "validated_artifact_sha256": {name: digest(name) for name in artifact_names},
        "validated_counts": {
            "exact_rights_relations": 12_038,
            "exact_rights_families": 11_602,
            "notice_records": 11_991,
            "classified_single_stratum_records": 11_976,
            "normalized_relation_set_matches": 11_988,
            "normalized_publication_type_set_matches": 740,
            "owner_requirement_groups": 12,
            "sufficient_owner_fields": 0,
        },
        "cleanup": {
            "scratch_deleted": True,
            "raw_provider_responses_retained": False,
            "case_identifiers_retained": False,
            "csv_html_dtd_pyc_retained": False,
            "git_checkout_retained": False,
        },
        "tests_run": "No pytest or CI. Scientific artifact assertions, JSON parsing, digest bindings, count identities, boundary flags, and cleanup only.",
    }
    (LANE / "VALIDATION_RECEIPT_V3.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({"status": "PASS", **receipt["validated_counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
