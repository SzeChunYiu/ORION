#!/usr/bin/env python3
"""Verify the frozen P4 DataCite M5 V1 negative-result artifacts."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "P4_DATACITE_M5_CENSUS_PROTOCOL_V1.json"
RESULT = ROOT / "P4_DATACITE_M5_CENSUS_RESULT_V1.json"
CANDIDATES = ROOT / "P4_DATACITE_M5_CANDIDATES_V1.jsonl"
OUT = ROOT / "VERIFICATION_RECEIPT_V1.json"
ZENODO_V2_RESULT = ROOT.parent / "p4-scientific-ascent-2026-08-23" / "P4_ZENODO_RELATED_OBJECT_CENSUS_RESULT_V2.json"


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
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    zenodo_v2 = json.loads(ZENODO_V2_RESULT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    checks.extend(
        [
            check("protocol_payload_hash", payload_hash(protocol, "protocol_payload_sha256") == protocol["protocol_payload_sha256"], payload_hash(protocol, "protocol_payload_sha256"), protocol["protocol_payload_sha256"]),
            check("result_payload_hash", payload_hash(result, "result_payload_sha256") == result["result_payload_sha256"], payload_hash(result, "result_payload_sha256"), result["result_payload_sha256"]),
            check("protocol_file_link", file_sha256(PROTOCOL) == result["protocol_file_sha256"], file_sha256(PROTOCOL), result["protocol_file_sha256"]),
            check("candidate_file_link", file_sha256(CANDIDATES) == result["candidate_jsonl_sha256"], file_sha256(CANDIDATES), result["candidate_jsonl_sha256"]),
            check("bound_zenodo_v2_result_file", file_sha256(ZENODO_V2_RESULT) == protocol["lineage"]["zenodo_v2_result_sha256"], file_sha256(ZENODO_V2_RESULT), protocol["lineage"]["zenodo_v2_result_sha256"]),
        ]
    )

    lineage = result["lineage"]
    checks.extend(
        [
            check("zenodo_v1_terminal_immutable", lineage["zenodo_v1_retained_terminal"] == "P4_ZENODO_RELATED_OBJECT_CENSUS_V1_TRANSPORT_CANNOT_CHECK_HTTP_400", lineage["zenodo_v1_retained_terminal"], "P4_ZENODO_RELATED_OBJECT_CENSUS_V1_TRANSPORT_CANNOT_CHECK_HTTP_400"),
            check("zenodo_v2_terminal_immutable", lineage["zenodo_v2_retained_terminal"] == "P4_ZENODO_RELATED_OBJECT_V2_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_PROVIDER", lineage["zenodo_v2_retained_terminal"], "P4_ZENODO_RELATED_OBJECT_V2_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_PROVIDER"),
            check("negative_identity_policy", lineage["negative_identities_immutable"] is True, lineage["negative_identities_immutable"], True),
        ]
    )

    receipts = result["query_receipts"]
    raw_hits = sum(row.get("raw_hits", 0) for row in receipts)
    disjoint_exclusions = sum(row.get("provider_or_root_disjointness_exclusions", 0) for row in receipts)
    page_schema = all(row["schema_passed"] for row in receipts)
    pagination = all(row["pagination_passed"] for row in receipts)
    response_hashes = [row["raw_response_sha256"] for row in receipts]
    expected_hashes = [
        "0eeb7b37ea34745cf9c48e0863cf5141a5a50b46b2eb4c206ea13a24f51c986c",
        "acf02d2ecd1829035d5b84ed5555b15966998c21add09fab39cba732bb6b101b",
        "a6e056829002af7349b2a3b7ad6125818a3e09274412dcefc08f98dc0e4d8e1c",
        "c644d628e7f266af8c65a5b0a6911bc347f5fadcbd5d0933f067689f8865600b",
    ]
    checks.extend(
        [
            check("four_frozen_queries", len(receipts) == result["query_count"] == 4, len(receipts), 4),
            check("four_raw_responses", result["raw_response_count"] == 4, result["raw_response_count"], 4),
            check("api_page_schema_receipts", page_schema, page_schema, True),
            check("pagination_integrity", pagination and result["pagination_integrity_passed"] is True, {"receipt_pages": pagination, "result": result["pagination_integrity_passed"]}, {"receipt_pages": True, "result": True}),
            check("raw_hits", raw_hits == 4000, raw_hits, 4000),
            check("provider_disjointness_fail_closed", disjoint_exclusions == 4000, disjoint_exclusions, 4000),
            check("raw_response_hashes", response_hashes == expected_hashes, response_hashes, expected_hashes),
            check("zero_admitted_candidates", result["candidate_rows"] == result["unique_candidate_dois"] == 0 and CANDIDATES.read_bytes() == b"", {"rows": result["candidate_rows"], "unique": result["unique_candidate_dois"], "file_bytes": CANDIDATES.stat().st_size}, {"rows": 0, "unique": 0, "file_bytes": 0}),
        ]
    )

    evidence = result["evidence_records"]
    evidence_passes = sum(row["all_assertions_present"] for row in evidence)
    failed_assertions = [
        item["assertion"]
        for row in evidence
        for item in row["assertion_checks"]
        if not item["present"]
    ]
    checks.extend(
        [
            check("official_evidence_receipts", len(evidence) == 4 and all(row["receipt"].get("http_status") == 200 for row in evidence), {"records": len(evidence), "http_200": sum(row["receipt"].get("http_status") == 200 for row in evidence)}, {"records": 4, "http_200": 4}),
            check("retained_assertion_mismatch", evidence_passes == 3 and failed_assertions == ["OpenSearch query string syntax"], {"evidence_passes": evidence_passes, "failed_assertions": failed_assertions}, {"evidence_passes": 3, "failed_assertions": ["OpenSearch query string syntax"]}),
        ]
    )

    observed_cells = {
        domain: {
            "zenodo": cell["zenodo_v2_signal_count"],
            "datacite": cell["datacite_disjoint_signal_count"],
            "combined": cell["combined_unique_signal_count"],
            "delta": cell["deficit_or_surplus_to_48"],
        }
        for domain, cell in result["per_cell"].items()
    }
    expected_cells = {
        "EARTH_ENVIRONMENT": {"zenodo": 37, "datacite": 0, "combined": 37, "delta": -11},
        "LIFE_BIOMEDICAL": {"zenodo": 44, "datacite": 0, "combined": 44, "delta": -4},
        "PHYSICAL_ENGINEERING": {"zenodo": 29, "datacite": 0, "combined": 29, "delta": -19},
        "SCIENTIFIC_SOFTWARE": {"zenodo": 30, "datacite": 0, "combined": 30, "delta": -18},
    }
    checks.append(check("unchanged_four_domain_48_signal_shortfalls", observed_cells == expected_cells, observed_cells, expected_cells))
    observed_m6 = {
        "EARTH_ENVIRONMENT": zenodo_v2["per_cell"]["EARTH_SOFTWARE"]["publication_typed_relation_candidates"],
        "LIFE_BIOMEDICAL": zenodo_v2["per_cell"]["LIFE_SOFTWARE"]["publication_typed_relation_candidates"],
        "PHYSICAL_ENGINEERING": zenodo_v2["per_cell"]["PHYSICAL_SOFTWARE"]["publication_typed_relation_candidates"],
        "SCIENTIFIC_SOFTWARE": zenodo_v2["per_cell"]["SCIENTIFIC_SOFTWARE"]["publication_typed_relation_candidates"],
    }
    expected_m6 = {"EARTH_ENVIRONMENT": 6, "LIFE_BIOMEDICAL": 10, "PHYSICAL_ENGINEERING": 10, "SCIENTIFIC_SOFTWARE": 7}
    checks.append(check("unchanged_zenodo_v2_m6_gate_still_fails", observed_m6 == expected_m6 and all(value < 48 for value in observed_m6.values()), observed_m6, expected_m6))

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
            check("exact_retained_terminal", result["scientific_terminal"] == "P4_DATACITE_M5_CENSUS_V1_CANNOT_CHECK_TRANSPORT_OR_SCHEMA", result["scientific_terminal"], "P4_DATACITE_M5_CENSUS_V1_CANNOT_CHECK_TRANSPORT_OR_SCHEMA"),
            check("not_execution_ready", result["all_four_m5_cells_pass_combined_frozen_signal_gate"] is False, result["all_four_m5_cells_pass_combined_frozen_signal_gate"], False),
        ]
    )

    failures = [row["check"] for row in checks if not row["passed"]]
    receipt: dict[str, Any] = {
        "schema_version": "orion.p4.datacite-m5-census-verification.v1",
        "verified_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "verification_scope": "STRUCTURAL_INTEGRITY_AND_RETAINED_NEGATIVE_PROVENANCE_ONLY",
        "verification_status": "PASS_STRUCTURAL_INTEGRITY_WITH_RETAINED_TRANSPORT_SCHEMA_CANNOT_CHECK" if not failures else "FAIL_STRUCTURAL_INTEGRITY",
        "hard_failure_count": len(failures),
        "hard_failures": failures,
        "checks": checks,
        "summary": {
            "queries": len(receipts),
            "raw_hits": raw_hits,
            "provider_disjointness_exclusions": disjoint_exclusions,
            "candidate_rows": result["candidate_rows"],
            "per_cell": observed_cells,
            "unchanged_m6_signal_counts": observed_m6,
            "all_eight_m5_m6_cells_pass": False,
            "scientific_terminal": result["scientific_terminal"],
        },
        "input_file_sha256": {
            PROTOCOL.name: file_sha256(PROTOCOL),
            RESULT.name: file_sha256(RESULT),
            CANDIDATES.name: file_sha256(CANDIDATES),
            ZENODO_V2_RESULT.name: file_sha256(ZENODO_V2_RESULT),
        },
        "explicit_nonclaim": "Structural verification preserves the failed census; it does not establish a DataCite source candidate, content permission, natural-pair eligibility, or scientific result.",
    }
    receipt["verification_receipt_payload_sha256"] = sha256(canonical_bytes(receipt))
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt[key] for key in ("verification_status", "hard_failure_count", "summary", "verification_receipt_payload_sha256")}, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
