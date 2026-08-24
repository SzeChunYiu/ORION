#!/usr/bin/env python3
"""Verify the frozen P4 DataCite M5 V2 mechanics-successor result."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "P4_DATACITE_M5_CENSUS_PROTOCOL_V2.json"
DISCLOSURE = ROOT / "P4_DATACITE_M5_V2_PREFREEZE_DISCLOSURE.json"
RESULT = ROOT / "P4_DATACITE_M5_CENSUS_RESULT_V2.json"
CANDIDATES = ROOT / "P4_DATACITE_M5_CANDIDATES_V2.jsonl"
V1_PROTOCOL = ROOT / "P4_DATACITE_M5_CENSUS_PROTOCOL_V1.json"
V1_RESULT = ROOT / "P4_DATACITE_M5_CENSUS_RESULT_V1.json"
V1_CANDIDATES = ROOT / "P4_DATACITE_M5_CANDIDATES_V1.jsonl"
ZENODO_V2_RESULT = ROOT.parent / "p4-scientific-ascent-2026-08-23" / "P4_ZENODO_RELATED_OBJECT_CENSUS_RESULT_V2.json"
OUT = ROOT / "VERIFICATION_RECEIPT_V2.json"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes())


def payload_hash(value: dict[str, Any], field: str) -> str:
    copy = dict(value)
    copy.pop(field, None)
    return sha256(canonical_bytes(copy))


def check(name: str, passed: bool, observed: Any, expected: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "observed": observed, "expected": expected}


def main() -> int:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    disclosure = json.loads(DISCLOSURE.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    v1_result = json.loads(V1_RESULT.read_text(encoding="utf-8"))
    zenodo_v2 = json.loads(ZENODO_V2_RESULT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    checks.extend(
        [
            check("protocol_payload_hash", payload_hash(protocol, "protocol_payload_sha256") == protocol["protocol_payload_sha256"], payload_hash(protocol, "protocol_payload_sha256"), protocol["protocol_payload_sha256"]),
            check("disclosure_payload_hash", payload_hash(disclosure, "disclosure_payload_sha256") == disclosure["disclosure_payload_sha256"], payload_hash(disclosure, "disclosure_payload_sha256"), disclosure["disclosure_payload_sha256"]),
            check("result_payload_hash", payload_hash(result, "result_payload_sha256") == result["result_payload_sha256"], payload_hash(result, "result_payload_sha256"), result["result_payload_sha256"]),
            check("protocol_file_link", file_sha256(PROTOCOL) == result["protocol_file_sha256"], file_sha256(PROTOCOL), result["protocol_file_sha256"]),
            check("disclosure_file_link", file_sha256(DISCLOSURE) == result["prefreeze_disclosure_file_sha256"] == protocol["prefreeze_disclosure"]["file_sha256"], file_sha256(DISCLOSURE), protocol["prefreeze_disclosure"]["file_sha256"]),
            check("candidate_file_link", file_sha256(CANDIDATES) == result["candidate_jsonl_sha256"], file_sha256(CANDIDATES), result["candidate_jsonl_sha256"]),
        ]
    )

    lineage = protocol["lineage"]
    lineage_observed = {
        "v1_protocol": file_sha256(V1_PROTOCOL),
        "v1_result": file_sha256(V1_RESULT),
        "v1_candidates": file_sha256(V1_CANDIDATES),
        "v1_terminal": v1_result["scientific_terminal"],
        "v1_terminal_immutable": lineage["v1_terminal_immutable"],
    }
    lineage_expected = {
        "v1_protocol": lineage["v1_protocol_file_sha256"],
        "v1_result": lineage["v1_result_file_sha256"],
        "v1_candidates": lineage["v1_candidate_file_sha256"],
        "v1_terminal": "P4_DATACITE_M5_CENSUS_V1_CANNOT_CHECK_TRANSPORT_OR_SCHEMA",
        "v1_terminal_immutable": True,
    }
    checks.extend(
        [
            check("v1_lineage_and_terminal_immutable", lineage_observed == lineage_expected, lineage_observed, lineage_expected),
            check("zenodo_negative_identities_immutable", lineage["zenodo_v1_retained_terminal"] == "P4_ZENODO_RELATED_OBJECT_CENSUS_V1_TRANSPORT_CANNOT_CHECK_HTTP_400" and lineage["zenodo_v2_retained_terminal"] == "P4_ZENODO_RELATED_OBJECT_V2_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_PROVIDER" and lineage["negative_identities_immutable"] is True, {"v1": lineage["zenodo_v1_retained_terminal"], "v2": lineage["zenodo_v2_retained_terminal"], "immutable": lineage["negative_identities_immutable"]}, {"v1": "P4_ZENODO_RELATED_OBJECT_CENSUS_V1_TRANSPORT_CANNOT_CHECK_HTTP_400", "v2": "P4_ZENODO_RELATED_OBJECT_V2_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_PROVIDER", "immutable": True}),
        ]
    )

    disclosed = disclosure["all_disclosed_dois"]
    checks.extend(
        [
            check("v1_disclosure_query_rows", disclosure["query_specific_identity_rows"] == 4000, disclosure["query_specific_identity_rows"], 4000),
            check("v1_disclosure_unique_dois", disclosure["unique_disclosed_dois"] == len(disclosed) == len(set(disclosed)) == 3479, {"declared": disclosure["unique_disclosed_dois"], "rows": len(disclosed), "unique": len(set(disclosed))}, {"declared": 3479, "rows": 3479, "unique": 3479}),
            check("v1_disclosure_cross_query_dois", disclosure["cross_query_disclosed_dois"] == 468, disclosure["cross_query_disclosed_dois"], 468),
            check("disclosure_no_content_or_outcomes", disclosure["metadata_descriptions_accessed"] is False and disclosure["content_files_accessed"] is False and disclosure["outcomes_accessed"] is False, {"descriptions": disclosure["metadata_descriptions_accessed"], "files": disclosure["content_files_accessed"], "outcomes": disclosure["outcomes_accessed"]}, {"descriptions": False, "files": False, "outcomes": False}),
        ]
    )

    receipts = result["query_receipts"]
    expected_counts = {
        "DATACITE_EARTH_DATA_V2": {"raw": 1000, "prefreeze": 299, "provider": 701, "rights": 678, "content_url": 0},
        "DATACITE_LIFE_DATA_V2": {"raw": 1000, "prefreeze": 424, "provider": 576, "rights": 525, "content_url": 0},
        "DATACITE_PHYSICAL_DATA_V2": {"raw": 1000, "prefreeze": 132, "provider": 868, "rights": 762, "content_url": 0},
        "DATACITE_SOFTWARE_DATA_V2": {"raw": 1000, "prefreeze": 113, "provider": 887, "rights": 754, "content_url": 0},
    }
    observed_counts = {
        row["query_id"]: {
            "raw": row.get("raw_hits", 0),
            "prefreeze": row.get("v1_prefreeze_exclusions", 0),
            "provider": row.get("provider_disjoint_eligible", 0),
            "rights": row.get("exact_rights_declaration_eligible", 0),
            "content_url": row.get("public_content_url_eligible", 0),
        }
        for row in receipts
    }
    response_hashes = [row["raw_response_sha256"] for row in receipts]
    expected_hashes = [
        "c60bb9f374cb8c8714dd6857177c22261627fa0a7ac58227a42f09a3120f3011",
        "47c164e88c1403788502a8c9903449acaee2192275c9c659806ca956cf0d108e",
        "041ad76f5659a4f19971588a37f3dab9661fa709e87314cfb65ea407fa09d01d",
        "eab2efc83cecdf88ec23dde4339ad2dc11216534dc4ca20b92999d0ac9386e6c",
    ]
    aggregate = {
        "raw": sum(row.get("raw_hits", 0) for row in receipts),
        "prefreeze": sum(row.get("v1_prefreeze_exclusions", 0) for row in receipts),
        "missing_client": sum(row.get("missing_client_exclusions", 0) for row in receipts),
        "provider": sum(row.get("provider_disjoint_eligible", 0) for row in receipts),
        "rights": sum(row.get("exact_rights_declaration_eligible", 0) for row in receipts),
        "content_url": sum(row.get("public_content_url_eligible", 0) for row in receipts),
        "typed_relation": sum(row.get("accepted_typed_relation_eligible", 0) for row in receipts),
        "publication_typed": sum(row.get("publication_typed_relation_eligible", 0) for row in receipts),
    }
    checks.extend(
        [
            check("four_query_page_receipts", len(receipts) == result["query_count"] == result["raw_response_count"] == 4, len(receipts), 4),
            check("all_evidence_assertions_pass", len(result["evidence_records"]) == 4 and all(row["all_assertions_present"] for row in result["evidence_records"]), {"records": len(result["evidence_records"]), "pass": sum(row["all_assertions_present"] for row in result["evidence_records"])}, {"records": 4, "pass": 4}),
            check("provider_schema_and_pagination", result["provider_schema_passed"] is True and result["pagination_integrity_passed"] is True and all(row["schema_passed"] and row["pagination_passed"] for row in receipts), {"schema": result["provider_schema_passed"], "pagination": result["pagination_integrity_passed"]}, {"schema": True, "pagination": True}),
            check("exact_per_query_counts", observed_counts == expected_counts, observed_counts, expected_counts),
            check("exact_aggregate_counts", aggregate == {"raw": 4000, "prefreeze": 968, "missing_client": 0, "provider": 3032, "rights": 2719, "content_url": 0, "typed_relation": 0, "publication_typed": 0}, aggregate, {"raw": 4000, "prefreeze": 968, "missing_client": 0, "provider": 3032, "rights": 2719, "content_url": 0, "typed_relation": 0, "publication_typed": 0}),
            check("raw_response_hashes", response_hashes == expected_hashes, response_hashes, expected_hashes),
            check("zero_admitted_candidates", result["candidate_rows"] == result["unique_candidate_dois"] == 0 and CANDIDATES.read_bytes() == b"", {"rows": result["candidate_rows"], "unique": result["unique_candidate_dois"], "file_bytes": CANDIDATES.stat().st_size}, {"rows": 0, "unique": 0, "file_bytes": 0}),
        ]
    )

    observed_m5 = {
        domain: {
            "zenodo": cell["zenodo_v2_signal_count"],
            "datacite": cell["datacite_disjoint_signal_count"],
            "combined": cell["combined_unique_signal_count"],
            "delta": cell["deficit_or_surplus_to_48"],
        }
        for domain, cell in result["per_cell"].items()
    }
    expected_m5 = {
        "EARTH_ENVIRONMENT": {"zenodo": 37, "datacite": 0, "combined": 37, "delta": -11},
        "LIFE_BIOMEDICAL": {"zenodo": 44, "datacite": 0, "combined": 44, "delta": -4},
        "PHYSICAL_ENGINEERING": {"zenodo": 29, "datacite": 0, "combined": 29, "delta": -19},
        "SCIENTIFIC_SOFTWARE": {"zenodo": 30, "datacite": 0, "combined": 30, "delta": -18},
    }
    observed_m6 = {
        "EARTH_ENVIRONMENT": zenodo_v2["per_cell"]["EARTH_SOFTWARE"]["publication_typed_relation_candidates"],
        "LIFE_BIOMEDICAL": zenodo_v2["per_cell"]["LIFE_SOFTWARE"]["publication_typed_relation_candidates"],
        "PHYSICAL_ENGINEERING": zenodo_v2["per_cell"]["PHYSICAL_SOFTWARE"]["publication_typed_relation_candidates"],
        "SCIENTIFIC_SOFTWARE": zenodo_v2["per_cell"]["SCIENTIFIC_SOFTWARE"]["publication_typed_relation_candidates"],
    }
    expected_m6 = {"EARTH_ENVIRONMENT": 6, "LIFE_BIOMEDICAL": 10, "PHYSICAL_ENGINEERING": 10, "SCIENTIFIC_SOFTWARE": 7}
    checks.extend(
        [
            check("unchanged_m5_48_signal_shortfalls", observed_m5 == expected_m5, observed_m5, expected_m5),
            check("unchanged_m6_48_signal_shortfalls", observed_m6 == expected_m6 and all(value < 48 for value in observed_m6.values()), observed_m6, expected_m6),
            check("no_m5_m6_gate_passes", result["all_four_m5_cells_pass_combined_frozen_signal_gate"] is False and all(not cell["passes_combined_frozen_signal_gate"] for cell in result["per_cell"].values()), result["all_four_m5_cells_pass_combined_frozen_signal_gate"], False),
        ]
    )

    no_access = {
        "metadata_descriptions": result["metadata_descriptions_requested_or_accessed"] is False,
        "candidate_content_bytes": result["candidate_content_bytes_requested_or_accessed"] is False,
        "files": result["files_downloaded"] is False,
        "outcomes": result["case_outcomes_accessed"] is False,
        "models": result["model_outcomes_executed"] is False,
    }
    checks.extend(
        [
            check("no_content_or_outcome_access", all(no_access.values()), no_access, "all true"),
            check("metadata_only_rights_boundary", result["metadata_permission"] == "DATACITE_METADATA_CC0_ROOT_BOUND" and result["dataset_content_permission"] == "DECLARED_PERMISSION_AUTHORITY_UNVERIFIED" and result["linked_publication_rights"] == "CANNOT_CHECK" and result["natural_pair_eligibility"] == "NOT_ADJUDICATED", {"metadata": result["metadata_permission"], "dataset": result["dataset_content_permission"], "linked": result["linked_publication_rights"], "eligibility": result["natural_pair_eligibility"]}, {"metadata": "DATACITE_METADATA_CC0_ROOT_BOUND", "dataset": "DECLARED_PERMISSION_AUTHORITY_UNVERIFIED", "linked": "CANNOT_CHECK", "eligibility": "NOT_ADJUDICATED"}),
            check("exact_source_shortfall_terminal", result["scientific_terminal"] == "P4_NATURAL_PAIR_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_SOURCE_UNIVERSE", result["scientific_terminal"], "P4_NATURAL_PAIR_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_SOURCE_UNIVERSE"),
        ]
    )

    failures = [row["check"] for row in checks if not row["passed"]]
    receipt: dict[str, Any] = {
        "schema_version": "orion.p4.datacite-m5-census-verification.v2",
        "verified_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "verification_scope": "STRUCTURAL_INTEGRITY_MECHANICS_REPAIR_AND_RETAINED_SOURCE_SHORTFALL_ONLY",
        "verification_status": "PASS_STRUCTURAL_INTEGRITY_WITH_RETAINED_SOURCE_SIGNAL_SHORTFALL" if not failures else "FAIL_STRUCTURAL_INTEGRITY",
        "hard_failure_count": len(failures),
        "hard_failures": failures,
        "checks": checks,
        "summary": {
            "provider_count": 1,
            "queries": len(receipts),
            "pages": len(receipts),
            "aggregate_counts": aggregate,
            "candidate_rows": result["candidate_rows"],
            "m5_cells": observed_m5,
            "unchanged_m6_signal_counts": observed_m6,
            "all_eight_m5_m6_cells_pass": False,
            "scientific_terminal": result["scientific_terminal"],
        },
        "input_file_sha256": {
            PROTOCOL.name: file_sha256(PROTOCOL),
            DISCLOSURE.name: file_sha256(DISCLOSURE),
            RESULT.name: file_sha256(RESULT),
            CANDIDATES.name: file_sha256(CANDIDATES),
            V1_PROTOCOL.name: file_sha256(V1_PROTOCOL),
            V1_RESULT.name: file_sha256(V1_RESULT),
            ZENODO_V2_RESULT.name: file_sha256(ZENODO_V2_RESULT),
        },
        "explicit_nonclaim": "V2 repairs client/evidence mechanics but yields no candidate after the unchanged HTTPS contentUrl gate; it does not establish repository-content rights, natural-pair eligibility, or scientific performance.",
    }
    receipt["verification_receipt_payload_sha256"] = sha256(canonical_bytes(receipt))
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt[key] for key in ("verification_status", "hard_failure_count", "summary", "verification_receipt_payload_sha256")}, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
