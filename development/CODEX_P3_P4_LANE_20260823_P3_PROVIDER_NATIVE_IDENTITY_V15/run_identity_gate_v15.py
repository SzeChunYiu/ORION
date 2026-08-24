#!/usr/bin/env python3
"""Live, fail-closed provider-native identity gate for one P3 OAEI pair.

This script intentionally does not execute a matcher or parse the reference
alignment.  It hashes the reference member only, which is sufficient to freeze
the evaluation identity before a later, separately authorized matcher run.
"""

from __future__ import annotations

import hashlib
import io
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUT = Path(__file__).resolve().parent
DEV = OUT.parent
PROTOCOL = OUT / "PROTOCOL_V15.json"
TERMINAL = (
    "P3_V15_PROVIDER_NATIVE_OAEI_101_103_IDENTITY_PASS__EXACT_VERSION_RIGHTS_"
    "ONTOLOGY_REFERENCE_AND_SAME_UNIVERSE_AML_BOUND__REFERENCE_SEMANTICS_UNPARSED_"
    "ONE_BERTMAP_SUCCESSOR_AUTHORIZED__SCIENTIFIC_READINESS_ZERO_OF_THREE_UNCHANGED"
)
USER_AGENT = "ORION-CODEX-P3-provider-native-identity-v15/1.0"
PRIOR_TECHNICAL_INVOCATIONS = 1

FILES = {
    "v14_result": DEV / "p3-public-reference-alignment-v14-2026-08-23" / "RESULT_V14.json",
    "oaei_rights": DEV / "p3-oaei-public-development-execution-2026-08-23" / "OAEI_RIGHTS_AND_ATTRIBUTION_RECEIPT_V1.json",
    "oaei_case_universe": DEV / "p3-oaei-public-development-execution-2026-08-23" / "CASE_UNIVERSE_RECEIPT_V2.json",
    "oaei_gold_join": DEV / "p3-oaei-public-development-execution-2026-08-23" / "PUBLIC_GOLD_JOIN_RECEIPT_V2.json",
    "aml_binding": DEV / "p3-oaei-public-development-execution-2026-08-23" / "AML_V3_2_BINDING_RECEIPT_V1.json",
    "aml_output_manifest": DEV / "p3-oaei-public-development-execution-2026-08-23" / "AML_OUTPUT_FREEZE_MANIFEST_V1.json",
    "v7_protocol": DEV / "p3-bertmap-execution-binding-v7-2026-08-23" / "PROTOCOL_V7.json",
    "v8_patch": DEV / "p3-full-native-runtime-v12-2026-08-23" / "V8_TABLE_READER_EXACT.patch",
    "v11_receipt": DEV / "p3-logmap-manifest-classpath-v11-2026-08-23" / "RECEIPT_V11.json",
    "v12_protocol": DEV / "p3-full-native-runtime-v12-2026-08-23" / "PROTOCOL_V12.json",
    "v12_receipt": DEV / "p3-full-native-runtime-v12-2026-08-23" / "NATIVE_EXECUTION_RECEIPT_V12.json",
    "v13_protocol": DEV / "p3-optional-wrapper-typed-decoder-v13-2026-08-23" / "PROTOCOL_V13.json",
    "v13_receipt": DEV / "p3-optional-wrapper-typed-decoder-v13-2026-08-23" / "RECEIPT_V13.json",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def fetch(url: str, timeout: int = 120) -> tuple[bytes, dict[str, Any]]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json, */*"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
        return body, {
            "requested_url": url,
            "final_url": response.geturl(),
            "http_status": response.status,
            "content_type": response.headers.get("Content-Type"),
            "content_length_header": response.headers.get("Content-Length"),
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "body_bytes": len(body),
            "body_sha256": sha256_bytes(body),
        }


def ensure(condition: bool, name: str, checks: list[dict[str, Any]], evidence: Any = None) -> None:
    checks.append({"check": name, "pass": bool(condition), "evidence": evidence})
    if not condition:
        raise AssertionError(f"V15 gate failed: {name}: {evidence!r}")


def main() -> None:
    started_wall = datetime.now(timezone.utc)
    started_ns = time.monotonic_ns()
    checks: list[dict[str, Any]] = []

    protocol = read_json(PROTOCOL)
    provider = protocol["provider_record"]
    pair = protocol["selected_provider_native_pair"]
    comparator = protocol["same_universe_comparator"]

    ensure(protocol["frozen_before_execution"] is True, "protocol_prefrozen", checks)
    protocol_sha = sha256_file(PROTOCOL)
    for name, path in FILES.items():
        ensure(path.is_file(), f"input_exists::{name}", checks, str(path))

    metadata_body, metadata_http = fetch(provider["api_url"], timeout=60)
    metadata = json.loads(metadata_body)
    ensure(metadata.get("id") == provider["expected_record_id"], "provider_record_id", checks, metadata.get("id"))
    ensure((metadata.get("doi") or metadata["metadata"].get("doi")) == provider["expected_doi"], "provider_doi", checks)
    ensure(metadata["metadata"].get("title") == provider["expected_title"], "provider_title", checks)
    ensure(metadata["metadata"].get("publication_date") == provider["expected_publication_date"], "provider_publication_date", checks)
    license_value = metadata["metadata"].get("license")
    license_id = license_value.get("id") if isinstance(license_value, dict) else license_value
    ensure(license_id == provider["expected_license_id"], "provider_license", checks, license_id)

    provider_files = [row for row in metadata.get("files", []) if row.get("key") == provider["archive_key"]]
    ensure(len(provider_files) == 1, "unique_provider_archive", checks, len(provider_files))
    archive_meta = provider_files[0]
    ensure(archive_meta.get("size") == provider["archive_size"], "provider_archive_size", checks, archive_meta.get("size"))
    ensure(archive_meta.get("checksum") == f"md5:{provider['archive_md5']}", "provider_archive_md5", checks, archive_meta.get("checksum"))
    archive_url = archive_meta.get("links", {}).get("self") or archive_meta.get("links", {}).get("content")
    ensure(isinstance(archive_url, str) and archive_url.startswith("https://zenodo.org/"), "provider_archive_url", checks, archive_url)

    archive_body, archive_http = fetch(archive_url, timeout=120)
    ensure(len(archive_body) == provider["archive_size"], "downloaded_archive_size", checks, len(archive_body))
    ensure(hashlib.md5(archive_body).hexdigest() == provider["archive_md5"], "downloaded_archive_md5", checks)
    ensure(sha256_bytes(archive_body) == provider["archive_sha256"], "downloaded_archive_sha256", checks)

    with zipfile.ZipFile(io.BytesIO(archive_body)) as archive:
        names = set(archive.namelist())
        member_receipts: dict[str, dict[str, Any]] = {}
        member_bytes: dict[str, bytes] = {}
        for role in ("source", "target", "reference"):
            spec = pair[role]
            ensure(spec["member"] in names, f"archive_member_present::{role}", checks, spec["member"])
            body = archive.read(spec["member"])
            member_bytes[role] = body
            member_receipts[role] = {
                "member": spec["member"],
                "bytes": len(body),
                "sha256": sha256_bytes(body),
            }
            ensure(len(body) == spec["bytes"], f"archive_member_bytes::{role}", checks, len(body))
            ensure(sha256_bytes(body) == spec["sha256"], f"archive_member_sha256::{role}", checks, sha256_bytes(body))

        index_bytes = archive.read("index.html")
        index_text = index_bytes.decode("latin-1", errors="replace")
        selection_marker = "103) Concept test: Language generalisation"
        ensure(selection_marker in index_text, "provider_index_test_103_description", checks, selection_marker)
        index_receipt = {
            "member": "index.html",
            "bytes": len(index_bytes),
            "sha256": sha256_bytes(index_bytes),
            "selection_marker": selection_marker,
            "selection_marker_occurrences": index_text.count(selection_marker),
        }

    # Input ontologies are safe to parse; the public reference is deliberately
    # not sent to an XML parser and is used above only as bytes for hashing.
    for role in ("source", "target"):
        root = ET.fromstring(member_bytes[role])
        ensure(root.tag.endswith("RDF"), f"ontology_xml_root::{role}", checks, root.tag)

    v14 = read_json(FILES["v14_result"])
    ensure(v14["admission"]["exact_provider_native_case_found"] is False, "predecessor_identity_gap_present", checks)
    rights = read_json(FILES["oaei_rights"])
    ensure(rights["doi"] == provider["expected_doi"], "rights_doi", checks)
    ensure(rights["license"] == protocol["rights_gate"]["expected_license"], "rights_license", checks)
    ensure(set(protocol["rights_gate"]["required_conditions"]).issubset(rights["conditions"]), "rights_conditions", checks)
    ensure(set(protocol["rights_gate"]["allowed_operations"]).issubset(rights["operations"]), "rights_operations", checks)
    ensure(rights["provider_checksum"] == f"md5:{provider['archive_md5']}", "rights_provider_checksum", checks)

    case_universe = read_json(FILES["oaei_case_universe"])
    case_hashes = {row["member"]: row["member_sha256"] for row in case_universe["member_receipts"]}
    ensure(case_hashes[pair["source"]["member"]] == pair["source"]["sha256"], "prior_source_inventory_agrees", checks)
    ensure(case_hashes[pair["target"]["member"]] == pair["target"]["sha256"], "prior_target_inventory_agrees", checks)

    gold_join = read_json(FILES["oaei_gold_join"])
    reference_hashes = {row["member"]: row["sha256"] for row in gold_join["reference_members"]}
    ensure(reference_hashes[pair["reference"]["member"]] == pair["reference"]["sha256"], "prior_reference_inventory_agrees", checks)

    v7 = read_json(FILES["v7_protocol"])
    source_identity = v7["authoritative_source"]
    candidate = protocol["candidate_identity"]
    ensure(source_identity["paper"]["doi"] == candidate["paper_doi"], "bertmap_paper_doi", checks)
    ensure(source_identity["canonical_original"]["commit"] == candidate["original_commit"], "bertmap_original_commit", checks)
    ensure(source_identity["maintained_implementation"]["commit"] == candidate["maintained_commit"], "bertmap_maintained_commit", checks)
    ensure(source_identity["maintained_implementation"]["package_version"] == candidate["package_version"], "deeponto_package_version", checks)

    v12 = read_json(FILES["v12_protocol"])
    ensure(v12["frozen_runtime"]["v8_table_patch_sha256"] == sha256_file(FILES["v8_patch"]), "v8_patch_identity", checks)
    ensure(v12["frozen_runtime"]["installed_logmap_manifest_classpath"] == "90/90 exact V11 hashes", "v11_classpath_lineage", checks)
    ensure(v12["source_changes"]["other_source_changes_forbidden"] is True, "v12_source_change_boundary", checks)
    ensure("--add-opens=java.base/java.lang=ALL-UNNAMED" in v12["source_changes"]["v12_runtime_adapter"][0], "v12_java_adapter_lineage", checks)

    v13 = read_json(FILES["v13_protocol"])
    ensure(v13["protocol_id"] == "P3_V13_NO_GOLD_TYPED_OPTIONAL_WRAPPER_DECODER_MICROGATE", "v13_decoder_lineage", checks)
    ensure(v13["execution"]["gold_or_reference_opened"] is False, "v13_no_gold_boundary", checks)

    aml_binding = read_json(FILES["aml_binding"])
    aml_manifest = read_json(FILES["aml_output_manifest"])
    ensure(aml_binding["system_id"] == comparator["system_id"], "aml_system_id", checks)
    ensure(aml_binding["tag_commit"] == comparator["tag_commit"], "aml_tag_commit", checks)
    ensure(aml_binding["license"] == comparator["license"], "aml_license", checks)
    ensure(aml_binding["jar_sha256"] == comparator["jar_sha256"], "aml_jar_sha256", checks)
    ensure(aml_binding["release_asset_sha256"] == comparator["release_asset_sha256"], "aml_release_sha256", checks)
    ensure(aml_binding["reference_alignment_argument_supplied"] is False, "aml_no_reference_argument", checks)
    aml_inputs = {row["member"]: row["sha256"] for row in aml_manifest["input_members"]}
    ensure(aml_inputs[pair["source"]["member"]] == pair["source"]["sha256"], "aml_same_source_input", checks)
    ensure(aml_inputs[pair["target"]["member"]] == pair["target"]["sha256"], "aml_same_target_input", checks)
    aml_103 = [row for row in aml_manifest["targets"] if row["target_test"] == "103"]
    ensure(len(aml_103) == 1, "aml_unique_target_103_output", checks, len(aml_103))
    ensure(aml_103[0]["status"] == "EXECUTED", "aml_target_103_executed", checks)
    ensure(aml_103[0]["byte_identical"] is True, "aml_target_103_replay_identical", checks)
    ensure(aml_103[0]["output_sha256"] == comparator["expected_target_103_output_sha256"], "aml_target_103_output_sha256", checks)
    ensure(aml_manifest["public_reference_content_opened"] is False, "aml_output_frozen_pre_reference", checks)

    archive_body = b""  # explicit release; no provider archive is written to disk
    member_bytes.clear()
    finished_ns = time.monotonic_ns()
    finished_wall = datetime.now(timezone.utc)

    input_receipts = {name: {"path": str(path), "sha256": sha256_file(path)} for name, path in FILES.items()}
    result = {
        "schema_version": "orion.p3.provider-native-identity.result.v15",
        "protocol_id": protocol["protocol_id"],
        "terminal": TERMINAL,
        "authority": "LIVE_PROVIDER_AND_LOCAL_RECEIPT_BOUND_PUBLIC_DEVELOPMENT_IDENTITY_ONLY__NOT_PROTECTED_CONFIRMATION",
        "provider_identity": {
            "record_id": provider["expected_record_id"],
            "doi": provider["expected_doi"],
            "title": provider["expected_title"],
            "publication_date": provider["expected_publication_date"],
            "license": protocol["rights_gate"]["expected_license"],
            "archive": provider["archive_key"],
            "archive_bytes": provider["archive_size"],
            "archive_md5": provider["archive_md5"],
            "archive_sha256": provider["archive_sha256"],
            "live_metadata_body_sha256": metadata_http["body_sha256"],
        },
        "provider_native_pair": {
            "pair_id": pair["pair_id"],
            "source": member_receipts["source"],
            "target": member_receipts["target"],
            "reference": {**member_receipts["reference"], "semantics_parsed_by_v15": False},
            "provider_index": index_receipt,
            "source_xml_parse": "PASS",
            "target_xml_parse": "PASS",
            "independence_warning": pair["independence_warning"],
        },
        "candidate_identity": {
            **candidate,
            "lineage_receipts": {
                "v7_protocol_sha256": input_receipts["v7_protocol"]["sha256"],
                "v8_patch_sha256": input_receipts["v8_patch"]["sha256"],
                "v11_receipt_sha256": input_receipts["v11_receipt"]["sha256"],
                "v12_protocol_sha256": input_receipts["v12_protocol"]["sha256"],
                "v12_execution_receipt_sha256": input_receipts["v12_receipt"]["sha256"],
                "v13_protocol_sha256": input_receipts["v13_protocol"]["sha256"],
                "v13_receipt_sha256": input_receipts["v13_receipt"]["sha256"],
            },
        },
        "same_universe_comparator": {
            **comparator,
            "source_member_sha256": pair["source"]["sha256"],
            "target_member_sha256": pair["target"]["sha256"],
            "pre_reference_output": aml_103[0],
            "binding_receipt_sha256": input_receipts["aml_binding"]["sha256"],
            "output_manifest_sha256": input_receipts["aml_output_manifest"]["sha256"],
        },
        "admission": {
            "exact_provider_native_case_found": True,
            "exact_version_bound": True,
            "rights_bound": True,
            "source_ontology_hash_bound": True,
            "target_ontology_hash_bound": True,
            "reference_hash_bound": True,
            "same_universe_comparator_identity_bound": True,
            "one_separate_bertmap_successor_authorized": True,
        },
        "execution_boundary": {
            "downloads": 2,
            "archive_written_to_disk": False,
            "reference_bytes_accessed_for_hash": True,
            "reference_semantics_parsed": False,
            "public_gold_rows_interpreted": 0,
            "matcher_attempts": 0,
            "java_attempts": 0,
            "training_attempts": 0,
            "prediction_attempts": 0,
            "repair_attempts": 0,
            "scientific_scoring_performed": False,
            "metrics_computed": 0,
        },
        "blocker_delta": {
            "provider_native_pair_identity": "CANNOT_CHECK_TO_BOUND",
            "same_universe_comparator_identity": "CANNOT_CHECK_TO_BOUND",
            "authorized_prospective_runs": "ZERO_TO_ONE",
            "scientific_comparator_readiness": "0/3_TO_0/3",
            "top_tier_submission_ready": False,
        },
        "claim_boundary": {
            "mapping_truth": "CANNOT_CHECK",
            "performance": "CANNOT_CHECK",
            "harm": "CANNOT_CHECK",
            "coverage": "CANNOT_CHECK",
            "transport": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
            "protected_confirmation": "CANNOT_CHECK",
        },
        "next_discriminator": "Freeze a new execution protocol from this exact identity, run one no-feedback BERTMap attempt on 101/onto.rdf to 103/onto.rdf, freeze all artifacts and typed-decoder receipts before semantically parsing 103/refalign.rdf, then score BERTMap and the frozen AML output under one declared pair-set metric contract.",
    }
    write_json(OUT / "RESULT_V15.json", result)
    (OUT / "TERMINAL_V15.txt").write_text(TERMINAL + "\n", encoding="utf-8")

    receipt = {
        "schema_version": "orion.p3.provider-native-identity.receipt.v15",
        "protocol_id": protocol["protocol_id"],
        "terminal": TERMINAL,
        "success": True,
        "started_at": started_wall.isoformat(),
        "finished_at": finished_wall.isoformat(),
        "runtime_nanoseconds": finished_ns - started_ns,
        "runtime_seconds": (finished_ns - started_ns) / 1_000_000_000,
        "identity_gate_invocations_total": PRIOR_TECHNICAL_INVOCATIONS + 1,
        "prior_technical_invocations": {
            "count": PRIOR_TECHNICAL_INVOCATIONS,
            "artifact": "ATTEMPT_1_FAILURE.txt",
            "outcomes_opened": False,
            "failure": "Runner addressed the V13 no-gold field through a nonexistent outcome_boundary key; corrected to the frozen execution.gold_or_reference_opened field before the successful invocation."
        },
        "protocol_sha256": protocol_sha,
        "checks_passed": sum(row["pass"] for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "http_receipts": {"metadata": metadata_http, "archive": archive_http},
        "input_receipts": input_receipts,
        "outputs": {
            "result": {"path": str(OUT / "RESULT_V15.json"), "sha256": sha256_file(OUT / "RESULT_V15.json")},
            "terminal": {"path": str(OUT / "TERMINAL_V15.txt"), "sha256": sha256_file(OUT / "TERMINAL_V15.txt")},
        },
    }
    write_json(OUT / "RECEIPT_V15.json", receipt)
    print(json.dumps({
        "terminal": TERMINAL,
        "runtime_seconds": receipt["runtime_seconds"],
        "checks": f"{receipt['checks_passed']}/{receipt['checks_total']}",
        "protocol_sha256": protocol_sha,
        "receipt_sha256": sha256_file(OUT / "RECEIPT_V15.json"),
        "result_sha256": sha256_file(OUT / "RESULT_V15.json"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
