#!/usr/bin/env python3
"""Fail-closed structural verifier for the rights/history successor lane.

This verifier checks artifact integrity and negative-result provenance.  A
successful run is not a positive rights, eligibility, or scientific result.
"""

from __future__ import annotations

import collections
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parent
PARENT = ROOT.parent / "provider-diverse-metadata-census-2026-08-23" / "SOURCE_CENSUS_V1.json"
PROTOCOL = ROOT / "PROTOCOL_V1.json"
EVIDENCE = ROOT / "EVIDENCE_SNAPSHOT_V1.json"
LEDGER = ROOT / "ROOT_RIGHTS_HISTORY_LEDGER_V1.json"
GAPS = ROOT / "SUCCESSOR_GAP_LEDGER_V1.json"
OUT = ROOT / "VERIFICATION_RECEIPT_V1.json"

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

RIGHTS_TO_GAP_CELL = {
    "CROSSREF_REST_API": {
        "provider_metadata_record": "PROVIDER_METADATA_REUSE",
        "article_body": "ARTICLE_BODY_RIGHTS",
        "supplement_or_attachment": "SUPPLEMENT_ATTACHMENT_RIGHTS",
        "case_eligibility": "CASE_ELIGIBILITY",
    },
    "ZENODO_REST_API": {
        "dataset_files": "DATASET_FILE_UPLOADER_AUTHORITY",
        "linked_or_derived_attachments": "LINKED_DERIVED_ATTACHMENT_RIGHTS",
        "case_eligibility": "CASE_ELIGIBILITY",
    },
    "GITLAB_COM_REST_API_V4": {
        "provider_project_metadata": "PROJECT_METADATA_REUSE",
        "issue_or_comment_text": "ISSUE_COMMENT_RIGHTS",
        "issue_attachment": "ISSUE_ATTACHMENT_RIGHTS",
        "case_eligibility": "CASE_ELIGIBILITY",
    },
    "NASA_ESDIS_CMR_SEARCH_API": {
        "provider_collection_metadata": "NOAA_COLLECTION_METADATA_RIGHTS",
        "collection_data_files": "NOAA_COLLECTION_FILE_RIGHTS",
        "documentation_or_third_party_attachment": "DOCUMENTATION_THIRD_PARTY_ATTACHMENT_RIGHTS",
        "case_eligibility": "CASE_ELIGIBILITY",
    },
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: pathlib.Path) -> str:
    return sha256(path.read_bytes())


def payload_hash(value: dict[str, Any], field: str) -> str:
    copy = dict(value)
    copy.pop(field, None)
    return sha256(canonical_bytes(copy))


def check(name: str, passed: bool, observed: Any, expected: Any) -> dict[str, Any]:
    return {
        "check": name,
        "passed": bool(passed),
        "observed": observed,
        "expected": expected,
    }


def valid_success_receipt(receipt: dict[str, Any]) -> bool:
    status = receipt.get("http_status")
    if not isinstance(status, int) or not (200 <= status < 400):
        return True
    if receipt.get("method") == "HEAD":
        return receipt.get("response_bytes") == 0 and receipt.get("response_sha256") is None
    size = receipt.get("response_bytes")
    digest = receipt.get("response_sha256")
    return isinstance(size, int) and size > 0 and isinstance(digest, str) and bool(SHA256_RE.fullmatch(digest))


def iso_timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def main() -> int:
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    gaps = json.loads(GAPS.read_text(encoding="utf-8"))

    checks: list[dict[str, Any]] = []
    checks.extend(
        [
            check(
                "parent_census_payload_hash",
                payload_hash(parent, "snapshot_payload_sha256") == parent["snapshot_payload_sha256"],
                payload_hash(parent, "snapshot_payload_sha256"),
                parent["snapshot_payload_sha256"],
            ),
            check(
                "protocol_payload_hash",
                payload_hash(protocol, "protocol_payload_sha256") == protocol["protocol_payload_sha256"],
                payload_hash(protocol, "protocol_payload_sha256"),
                protocol["protocol_payload_sha256"],
            ),
            check(
                "evidence_payload_hash",
                payload_hash(evidence, "evidence_payload_sha256") == evidence["evidence_payload_sha256"],
                payload_hash(evidence, "evidence_payload_sha256"),
                evidence["evidence_payload_sha256"],
            ),
            check(
                "root_ledger_payload_hash",
                payload_hash(ledger, "ledger_payload_sha256") == ledger["ledger_payload_sha256"],
                payload_hash(ledger, "ledger_payload_sha256"),
                ledger["ledger_payload_sha256"],
            ),
            check(
                "gap_ledger_payload_hash",
                payload_hash(gaps, "gap_ledger_payload_sha256") == gaps["gap_ledger_payload_sha256"],
                payload_hash(gaps, "gap_ledger_payload_sha256"),
                gaps["gap_ledger_payload_sha256"],
            ),
        ]
    )

    cross_links = {
        "protocol_parent": protocol["parent_census_payload_sha256"] == parent["snapshot_payload_sha256"],
        "ledger_parent": ledger["parent_census_payload_sha256"] == parent["snapshot_payload_sha256"],
        "ledger_protocol": ledger["protocol_payload_sha256"] == protocol["protocol_payload_sha256"],
        "ledger_evidence": ledger["evidence_payload_sha256"] == evidence["evidence_payload_sha256"],
    }
    checks.append(check("cross_artifact_payload_links", all(cross_links.values()), cross_links, "all true"))

    roots = ledger["roots"]
    root_ids = [root["root_id"] for root in roots]
    crossref_roots = [root for root in roots if root["metadata_provider_id"] == "CROSSREF_REST_API"]
    checks.extend(
        [
            check("root_count", len(roots) == ledger["root_count"] == protocol["root_count"] == 16, len(roots), 16),
            check("unique_root_ids", len(set(root_ids)) == len(root_ids), len(set(root_ids)), 16),
            check("crossref_root_count", len(crossref_roots) == protocol["crossref_history_root_count"] == 8, len(crossref_roots), 8),
        ]
    )

    observed_rights = collections.Counter(
        cell["status"] for root in roots for cell in root["content_class_rights"].values()
    )
    expected_rights = {
        "ROOT_BOUND_PERMISSION": 8,
        "DECLARED_PERMISSION_AUTHORITY_UNVERIFIED": 10,
        "ACCESS_ONLY_NOT_REUSE": 2,
        "CANNOT_CHECK": 30,
        "NOT_ACCESSED": 16,
    }
    checks.extend(
        [
            check("rights_cell_count", sum(observed_rights.values()) == ledger["content_class_cell_count"] == 66, sum(observed_rights.values()), 66),
            check("rights_status_counts", dict(observed_rights) == ledger["rights_status_counts"] == expected_rights, dict(observed_rights), expected_rights),
        ]
    )

    observed_history = collections.Counter(
        root["historical_byte_provenance"]["status"]
        for root in crossref_roots
        if root["historical_byte_provenance"] is not None
    )
    checks.extend(
        [
            check(
                "crossref_history_negatives",
                observed_history == {"CANNOT_CHECK_EXACT_CROSSREF_HISTORICAL_BYTES": 8},
                dict(observed_history),
                {"CANNOT_CHECK_EXACT_CROSSREF_HISTORICAL_BYTES": 8},
            ),
            check(
                "crossref_exact_pre_cutoff_bytes",
                ledger["crossref_history_status_counts"].get("EXACT_PRE_CUTOFF_BYTES") == 0
                and evidence["crossref_history_counts"].get("exact_pre_cutoff_bytes") == 0,
                {
                    "ledger": ledger["crossref_history_status_counts"].get("EXACT_PRE_CUTOFF_BYTES"),
                    "evidence": evidence["crossref_history_counts"].get("exact_pre_cutoff_bytes"),
                },
                {"ledger": 0, "evidence": 0},
            ),
        ]
    )

    expected_gap_keys: list[tuple[str, str, str]] = []
    for root in roots:
        provider = root["metadata_provider_id"]
        for cell_name, cell in root["content_class_rights"].items():
            if cell["status"] == "ROOT_BOUND_PERMISSION":
                continue
            expected_gap_cell = RIGHTS_TO_GAP_CELL[provider].get(cell_name)
            if expected_gap_cell is None:
                raise AssertionError(f"unmapped unresolved rights cell: {provider}/{cell_name}")
            expected_gap_keys.append((root["root_id"], expected_gap_cell, cell["status"]))
        if root["historical_byte_provenance"] is not None:
            expected_gap_keys.append(
                (
                    root["root_id"],
                    "EXACT_PRE_CUTOFF_METADATA_BYTES",
                    root["historical_byte_provenance"]["status"],
                )
            )

    actual_gap_keys = [
        (item["root_id"], item["unresolved_cell"], item["current_status"])
        for item in gaps["gaps"]
    ]
    actual_counts = collections.Counter(actual_gap_keys)
    successor_ids = [item["successor_identity"] for item in gaps["gaps"]]
    complete_discriminators = all(
        all(item.get(field) for field in ("next_discriminator", "positive_condition", "negative_condition", "cannot_check_condition"))
        for item in gaps["gaps"]
    )
    checks.extend(
        [
            check("successor_gap_count", len(gaps["gaps"]) == gaps["gap_count"] == 66, len(gaps["gaps"]), 66),
            check(
                "every_unresolved_cell_exactly_one_successor",
                collections.Counter(expected_gap_keys) == actual_counts and all(count == 1 for count in actual_counts.values()),
                {"expected_unique": len(set(expected_gap_keys)), "actual_unique": len(actual_counts), "duplicates": sum(v - 1 for v in actual_counts.values())},
                {"expected_unique": 66, "actual_unique": 66, "duplicates": 0},
            ),
            check("unique_successor_identities", len(successor_ids) == len(set(successor_ids)), len(set(successor_ids)), 66),
            check("complete_successor_discriminators", complete_discriminators, complete_discriminators, True),
        ]
    )

    no_access = {
        "protocol_outcomes": protocol["outcomes_accessed"] is False,
        "protocol_protected_fields": protocol["protected_case_fields_accessed"] is False,
        "evidence_outcomes": evidence["outcomes_accessed"] is False,
        "evidence_protected_fields": evidence["protected_case_fields_accessed"] is False,
        "root_case_content": all(root["case_content_accessed"] is False for root in roots),
        "root_eligibility": all(root["case_eligibility_assessed"] is False for root in roots),
        "root_labels_outcomes": all(root["labels_or_outcomes_accessed"] is False for root in roots),
        "evidence_bodies_unarchived": all(record["body_archived"] is False for record in evidence["evidence_records"]),
        "archive_replay_bodies_unfetched": all(query["archive_body_fetched"] is False for query in evidence["internet_archive_queries"]),
    }
    checks.append(check("no_protected_content_label_or_outcome_access", all(no_access.values()), no_access, "all true"))

    evidence_records = evidence["evidence_records"]
    evidence_ids = [record["evidence_id"] for record in evidence_records]
    official_records = [record for record in evidence_records if "assertions" in record]
    declared_urls = [record for record in evidence_records if record["kind"] == "DECLARED_LICENSE_OR_TDM_POLICY_URL"]
    evidence_receipt_complete = all(
        record.get("url")
        and iso_timestamp(record.get("captured_at_utc"))
        and record.get("receipt", {}).get("request_url") == record.get("url")
        and valid_success_receipt(record["receipt"])
        for record in evidence_records
    )
    checks.extend(
        [
            check("unique_evidence_ids", len(evidence_ids) == len(set(evidence_ids)), len(set(evidence_ids)), len(evidence_ids)),
            check("official_assertions", len(official_records) == 21 and all(record["all_assertions_present"] for record in official_records), {"records": len(official_records), "all_present": sum(record["all_assertions_present"] for record in official_records)}, {"records": 21, "all_present": 21}),
            check("evidence_url_hash_timestamp_completeness", evidence_receipt_complete, evidence_receipt_complete, True),
            check("declared_licence_url_liveness", len(declared_urls) == 12 and all(record["live"] for record in declared_urls), {"records": len(declared_urls), "live": sum(record["live"] for record in declared_urls)}, {"records": 12, "live": 12}),
        ]
    )

    torrent = next(record for record in evidence_records if record["evidence_id"] == "CR_2025_PUBLIC_FILE_TORRENT")
    january = next(record for record in evidence_records if record["evidence_id"] == "CR_2026_01_SNAPSHOT_HEAD")
    checks.extend(
        [
            check("crossref_2025_torrent_infohash", torrent["infohash_match"] is True, torrent["observed_infohash_sha1"], torrent["expected_infohash_sha1"]),
            check("crossref_2025_torrent_root_membership_unchecked", torrent["root_membership_checked"] is False, torrent["root_membership_status"], "CANNOT_CHECK_WITHOUT_197GB_CORPUS_EXTRACTION_OR_PROVIDER_INDEX"),
            check("crossref_2026_01_snapshot_unavailable", january["receipt"]["http_status"] == 404 and january["historical_bytes_obtained"] is False, january["receipt"]["http_status"], 404),
        ]
    )

    archive_statuses = collections.Counter()
    archive_receipts_valid = True
    for query in evidence["internet_archive_queries"]:
        receipt = query["receipt"]
        if receipt.get("http_status") == 200 and query["parse_error"] is None:
            archive_statuses["HTTP_200_WITH_CAPTURE" if query["capture_count"] else "HTTP_200_EMPTY"] += 1
        elif receipt.get("http_status") is None:
            archive_statuses["REQUEST_ERROR_CANNOT_CHECK"] += 1
        elif query["parse_error"] is not None:
            archive_statuses["PARSE_ERROR_CANNOT_CHECK"] += 1
        else:
            archive_statuses[f"HTTP_{receipt.get('http_status')}_CANNOT_CHECK"] += 1
        archive_receipts_valid &= query.get("query_url") == receipt.get("request_url")
        archive_receipts_valid &= valid_success_receipt(receipt)
        archive_receipts_valid &= query["archive_body_fetched"] is False
    checks.extend(
        [
            check("internet_archive_query_count", len(evidence["internet_archive_queries"]) == 16, len(evidence["internet_archive_queries"]), 16),
            check("internet_archive_receipt_integrity", archive_receipts_valid, archive_receipts_valid, True),
            check("internet_archive_confirmed_captures", archive_statuses["HTTP_200_WITH_CAPTURE"] == 0, archive_statuses["HTTP_200_WITH_CAPTURE"], 0),
        ]
    )

    current_crossref_receipts = [
        root["historical_byte_provenance"]["current_sparse_metadata_receipt"]["receipt"]
        for root in crossref_roots
    ]
    checks.append(
        check(
            "current_crossref_receipt_hash_completeness",
            len(current_crossref_receipts) == 8 and all(valid_success_receipt(receipt) for receipt in current_crossref_receipts),
            {"records": len(current_crossref_receipts), "complete": sum(valid_success_receipt(receipt) for receipt in current_crossref_receipts)},
            {"records": 8, "complete": 8},
        )
    )

    terminals = {
        "root_ledger": ledger["scientific_terminal"],
        "gap_ledger": gaps["overall_terminal"],
        "protocol": protocol["fail_closed_terminals"]["overall"],
    }
    checks.append(
        check(
            "scientific_terminal_preserved",
            set(terminals.values()) == {"CANNOT_CHECK_RIGHTS_AND_HISTORY_BINDING"},
            terminals,
            "CANNOT_CHECK_RIGHTS_AND_HISTORY_BINDING",
        )
    )

    hard_failures = [item["check"] for item in checks if not item["passed"]]
    verified_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    receipt: dict[str, Any] = {
        "schema_version": "orion.provider-rights-history-successor.verification.v1",
        "verified_at_utc": verified_at,
        "verification_scope": "STRUCTURAL_INTEGRITY_NEGATIVE_PROVENANCE_AND_NO_ACCESS_BOUNDARIES_ONLY",
        "verification_status": (
            "PASS_STRUCTURAL_INTEGRITY_WITH_SCIENTIFIC_CANNOT_CHECK"
            if not hard_failures
            else "FAIL_STRUCTURAL_INTEGRITY"
        ),
        "scientific_terminal": "CANNOT_CHECK_RIGHTS_AND_HISTORY_BINDING",
        "hard_failure_count": len(hard_failures),
        "hard_failures": hard_failures,
        "checks": checks,
        "summary": {
            "roots": len(roots),
            "rights_cells": sum(observed_rights.values()),
            "rights_status_counts": dict(sorted(observed_rights.items())),
            "crossref_history_cannot_check": observed_history["CANNOT_CHECK_EXACT_CROSSREF_HISTORICAL_BYTES"],
            "crossref_exact_pre_cutoff_bytes": 0,
            "successor_gaps": len(gaps["gaps"]),
            "official_assertion_records": len(official_records),
            "declared_licence_urls_live": sum(record["live"] for record in declared_urls),
            "internet_archive_query_status_counts": dict(sorted(archive_statuses.items())),
        },
        "input_file_sha256": {
            PARENT.name: file_sha256(PARENT),
            PROTOCOL.name: file_sha256(PROTOCOL),
            EVIDENCE.name: file_sha256(EVIDENCE),
            LEDGER.name: file_sha256(LEDGER),
            GAPS.name: file_sha256(GAPS),
        },
        "explicit_nonclaim": "A passing structural receipt does not establish reuse permission, case eligibility, historical Crossref bytes, empirical transport, or a positive scientific result.",
    }
    receipt["verification_receipt_payload_sha256"] = sha256(canonical_bytes(receipt))
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt[key] for key in ("verification_status", "scientific_terminal", "hard_failure_count", "summary", "verification_receipt_payload_sha256")}, indent=2, sort_keys=True))
    return 1 if hard_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
