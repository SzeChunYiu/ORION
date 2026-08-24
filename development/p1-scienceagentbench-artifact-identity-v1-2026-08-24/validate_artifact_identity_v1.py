#!/usr/bin/env python3
"""Static, network-free validator for the P1 SAB PF-01 identity packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PREFLIGHT = ROOT.parent / "p1-scienceagentbench-preflight-2026-08-24"
EXPECTED_BYTES = 1_769_478_786
EXPECTED_SHA256 = "46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610"
EXPECTED_ETAG = '"{2B44EF7C-EA9A-4BB0-90A4-DF7707A497E4},3"'
EXPECTED_LAST_MODIFIED = "Wed, 29 Apr 2026 23:39:44 GMT"
EXPECTED_PREFLIGHT_MODIFIED = "2026-04-29T23:39:42Z"
EXPECTED_LANDING_URL = (
    "https://buckeyemailosu-my.sharepoint.com/:u:/g/personal/chen_8336_osu_edu/"
    "IQB870QrmuqwS5Ck33cHpJfkAVt3LsMeariREIwP3AT7byA?e=3ckueC"
)
EXPECTED_FINAL_URL = (
    "https://buckeyemailosu-my.sharepoint.com/personal/chen_8336_osu_edu/"
    "Documents/Research/benchmark_verified.zip?ga=1"
)
EXPECTED_PREFLIGHT_SHA256 = "95033900763e22c67b95104f35f18fc75d6d678d4c12e5851b848bb186b55bbf"
EXPECTED_AUDIT_START_BASE = "d4cf8c09c128c0b0331b96b45385c35a96b9427e"
EXPECTED_INTEGRATION_BASE = "e4026dc81a8ccc44841cd2d44115bb05873a03da"
EXPECTED_TERMINAL = (
    "P1_SAB_PF01_ARTIFACT_IDENTITY_CLOSED__FULL_ARCHIVE_SHA256_BOUND__"
    "1769478786_BYTES__ZERO_PAYLOAD_RETAINED__ZERO_ENTRIES_OPENED__"
    "ZERO_OUTCOMES_OPENED__ZERO_TASKS_RUN"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_checksums() -> None:
    recorded: dict[str, str] = {}
    for line in (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, separator, name = line.partition("  ")
        assert separator and len(digest) == 64 and name
        recorded[name] = digest
    expected_names = {
        path.name for path in ROOT.iterdir() if path.is_file() and path.name != "SHA256SUMS"
    }
    assert set(recorded) == expected_names
    for name, digest in recorded.items():
        assert sha256(ROOT / name) == digest


def main() -> None:
    receipt = load(ROOT / "ARTIFACT_IDENTITY_RECEIPT_V1.json")
    preflight_path = PREFLIGHT / "PREFLIGHT_RECEIPT_V1.json"
    preflight = load(preflight_path)

    assert receipt["schema_version"] == "orion.p1.scienceagentbench.artifact-identity-receipt.v1"
    assert receipt["terminal"] == EXPECTED_TERMINAL
    assert receipt["authority"].startswith("PF01_ARTIFACT_IDENTITY_ONLY")
    assert sha256(preflight_path) == EXPECTED_PREFLIGHT_SHA256
    orion = receipt["orion_binding"]
    assert orion["preflight_receipt_sha256"] == EXPECTED_PREFLIGHT_SHA256
    assert orion["audit_start_base_commit"] == EXPECTED_AUDIT_START_BASE
    assert orion["integration_base_commit"] == EXPECTED_INTEGRATION_BASE
    assert "source_revision" not in orion

    source = preflight["sources"]["full_verified_artifact"]
    identity = receipt["artifact_identity"]
    assert source["archive_bytes"] == EXPECTED_BYTES
    assert identity["observed_bytes"] == EXPECTED_BYTES
    assert identity["observed_sha256"] == EXPECTED_SHA256
    assert identity["byte_count_matches_preflight"] is True
    assert identity["byte_count_matches_http_content_length"] is True
    assert source["etag"] == EXPECTED_ETAG.strip('"')
    assert identity["etag_matches_preflight_after_http_quote_normalization"] is True
    assert source["modified"] == EXPECTED_PREFLIGHT_MODIFIED
    assert identity["preflight_modified_metadata"] == EXPECTED_PREFLIGHT_MODIFIED
    assert identity["transport_last_modified"] == EXPECTED_LAST_MODIFIED
    assert identity["http_last_modified_exactly_matches_preflight_modified_metadata"] is False
    assert identity["http_last_modified_minus_preflight_modified_metadata_seconds"] == 2
    assert identity["server_reported_stream_hash_used_as_sha256"] is False
    pin = receipt["official_source_pin"]
    assert pin["landing_url"] == source["landing_url"] == EXPECTED_LANDING_URL
    assert pin["final_url"] == EXPECTED_FINAL_URL
    assert pin["filename"] == source["filename"] == "benchmark_verified.zip"

    transport = receipt["transport_observation"]
    range_probe = transport["range_probe"]
    full = transport["full_stream"]
    assert range_probe["method"] == "HEAD"
    assert range_probe["requested_range"] == "bytes=0-0"
    assert range_probe["final_http_status"] == 206
    assert range_probe["content_range"] == "bytes 0-0/1769478786"
    assert range_probe["body_bytes_received"] == 0
    assert range_probe["content_length"] == 1
    assert range_probe["etag"] == EXPECTED_ETAG
    assert range_probe["last_modified"] == EXPECTED_LAST_MODIFIED
    assert full["method"] == "GET"
    assert full["range_header_sent"] is False
    assert full["final_http_status"] == 200
    assert full["content_length"] == EXPECTED_BYTES
    assert full["etag"] == EXPECTED_ETAG
    assert full["last_modified"] == EXPECTED_LAST_MODIFIED
    assert full["full_get_attempts"] == 1
    assert full["automatic_retries"] == 0
    assert full["curl_exit_code"] == 0
    assert range_probe["final_url"] == full["final_url"] == EXPECTED_FINAL_URL
    assert range_probe["etag"] == full["etag"]
    assert range_probe["last_modified"] == full["last_modified"]

    cd = receipt["preflight_central_directory_cross_check"]
    preflight_cd = source["central_directory"]
    assert cd["central_directory_reopened"] is False
    assert cd["preflight_central_directory_sha256"] == preflight_cd["sha256"]
    assert cd["preflight_central_directory_offset"] == preflight_cd["offset"]
    assert cd["preflight_central_directory_bytes"] == preflight_cd["bytes"]
    assert cd["offset_plus_directory_plus_end_record"] == EXPECTED_BYTES
    assert cd["equals_stream_byte_count"] is True

    boundary = receipt["inspection_and_retention_boundary"]
    assert boundary["raw_archive_bytes_processed_for_sha256_and_count_only"] is True
    for key in (
        "archive_body_retained",
        "archive_extracted",
        "archive_structure_parsed",
        "central_directory_reopened",
        "file_entry_payloads_opened_or_interpreted",
        "gold_program_bodies_opened",
        "evaluation_program_bodies_opened",
        "rubric_bodies_opened",
        "official_or_historical_outcomes_opened",
        "large_data_added_to_repository",
    ):
        assert boundary[key] is False, key
    assert boundary["tasks_executed"] == 0

    disposition = receipt["pf01_disposition"]
    assert disposition["blocker_id"] == "PF-01"
    assert disposition["status"] == "CLOSED_EXACT_ARTIFACT_IDENTITY_BOUND"
    assert disposition["remaining_preflight_blockers"] == [
        "PF-02", "PF-03", "PF-04", "PF-05", "PF-06"
    ]
    assert disposition["does_not_authorize_extraction_or_execution"] is True
    assert disposition["scientific_authority_delta"] == "NONE"

    assert max(path.stat().st_size for path in ROOT.iterdir() if path.is_file()) < 1_000_000
    validate_checksums()
    print(
        "P1_SAB_PF01_ARTIFACT_IDENTITY_STATIC_VALIDATION_PASS "
        f"bytes={EXPECTED_BYTES} sha256={EXPECTED_SHA256} "
        "payload_retained=false entries_opened=false outcomes_opened=false tasks_run=0"
    )


if __name__ == "__main__":
    main()
