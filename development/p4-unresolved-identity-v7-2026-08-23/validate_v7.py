#!/usr/bin/env python3
"""Packet-local invariant validator for the P4 V7 exact-identity packet."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
V6 = HERE.parent / "p4-m6-joss-bridge-repair-v6-2026-08-23"
EXPECTED_UNRESOLVED = {36, 59, 91, 108, 133, 165, 185, 190, 196, 199}
ACCEPTED_METHODS = {
    "ARCHIVE_PROVIDER_RELATED_IDENTIFIER_EXACT_TAG_TO_SAME_IMMUTABLE_COMMIT",
    "ARCHIVE_SWH_DIRECTORY_IDENTITY_EQUALS_IMMUTABLE_COMMIT_ROOT_TREE",
    "ARCHIVE_NORMALIZED_MANIFEST_EQUALS_IMMUTABLE_COMMIT_ARCHIVE_MANIFEST",
    "ARCHIVE_BYTES_EMBED_EXACT_FULL_COMMIT_SHA_RESOLVED_FROM_JOSS_TAG",
    "ARCHIVE_BYTES_EQUAL_EXACT_GITHUB_TAG_RELEASE_ASSET_BYTES",
    "V6_SOURCE_NATIVE_ARCHIVE_MANIFEST_EQUALS_GITHUB_IMMUTABLE_COMMIT_ARCHIVE_MANIFEST",
    "V6_QUALIFIED_SWHID_PATH_DIRECTORY_EQUALS_GIT_COMMIT_ROOT_TREE",
}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    checks: dict[str, bool] = {}
    required = [
        "PROTOCOL_V7.json", "PROTOCOL_FREEZE_RECEIPT_V7.json",
        "UNRESOLVED_IDENTITIES_INPUT_V7.jsonl", "run_targeted_identity_resolution_v7.py",
        "IDENTITY_RESOLUTION_ROWS_V7.jsonl", "HARVEST_RECEIPT_V7.json",
        "RESULT_V7.json", "RESULTS_V7.md", "NEGATIVE_RESULT_LEDGER_V7.json",
        "HANDOFF_V7.md", "validate_v7.py",
    ]
    checks["all_required_artifacts_present"] = all((HERE / name).is_file() for name in required)

    json_files = [
        "PROTOCOL_V7.json", "PROTOCOL_FREEZE_RECEIPT_V7.json", "HARVEST_RECEIPT_V7.json",
        "RESULT_V7.json", "NEGATIVE_RESULT_LEDGER_V7.json",
    ]
    parse_ok = True
    try:
        for name in json_files:
            load_json(HERE / name)
        load_jsonl(HERE / "UNRESOLVED_IDENTITIES_INPUT_V7.jsonl")
        load_jsonl(HERE / "IDENTITY_RESOLUTION_ROWS_V7.jsonl")
    except Exception:
        parse_ok = False
    checks["all_json_and_jsonl_parse"] = parse_ok

    protocol = load_json(HERE / "PROTOCOL_V7.json")
    freeze = load_json(HERE / "PROTOCOL_FREEZE_RECEIPT_V7.json")
    inputs = load_jsonl(HERE / "UNRESOLVED_IDENTITIES_INPUT_V7.jsonl")
    rows = load_jsonl(HERE / "IDENTITY_RESOLUTION_ROWS_V7.jsonl")
    receipt = load_json(HERE / "HARVEST_RECEIPT_V7.json")
    result = load_json(HERE / "RESULT_V7.json")
    ledger = load_json(HERE / "NEGATIVE_RESULT_LEDGER_V7.json")
    v6_rows = load_jsonl(V6 / "BRIDGE_REPAIR_ROWS_V6.jsonl")
    v6_unresolved = [row for row in v6_rows if not row.get("v6_exact_bridge_repaired")]

    input_indices = {row["frozen_index"] for row in inputs}
    row_indices = {row["frozen_index"] for row in rows}
    v6_indices = {row["frozen_index"] for row in v6_unresolved}
    input_publications = {row["publication_doi"].casefold() for row in inputs}
    row_publications = {row["publication_doi"].casefold() for row in rows}
    v6_publications = {row["publication_doi"].casefold() for row in v6_unresolved}
    input_archives = {row["archive_doi"].casefold() for row in inputs}
    row_archives = {row["archive_doi"].casefold() for row in rows}
    v6_archives = {row["archive_doi"].casefold() for row in v6_unresolved}

    checks["exactly_24_unique_frozen_inputs"] = (
        len(inputs) == len(input_indices) == len(input_publications) == len(input_archives) == 24
    )
    checks["same_exact_v6_unresolved_identity_frame"] = (
        input_indices == row_indices == v6_indices
        and input_publications == row_publications == v6_publications
        and input_archives == row_archives == v6_archives
    )
    checks["one_row_and_unit_per_publication"] = (
        len(rows) == 24 and all(row.get("counts_as_unit") == 1 for row in rows)
    )
    checks["protocol_freeze_hashes_valid"] = (
        freeze.get("status") == "PASS"
        and freeze.get("protocol_frozen_before_v7_live_harvest") is True
        and freeze.get("v7_live_network_access_performed_before_freeze") is False
        and freeze.get("protocol_sha256") == sha(HERE / "PROTOCOL_V7.json")
        and freeze.get("input_sha256") == sha(HERE / "UNRESOLVED_IDENTITIES_INPUT_V7.jsonl")
        and freeze.get("source_v6_rows_sha256") == sha(V6 / "BRIDGE_REPAIR_ROWS_V6.jsonl")
    )

    repaired = [row for row in rows if row["v7_same_identity_resolution"]]
    unresolved = [row for row in rows if not row["v7_same_identity_resolution"]]
    checks["exact_14_repaired_10_unresolved"] = len(repaired) == 14 and len(unresolved) == 10
    checks["remaining_ten_exact_indices"] = {row["frozen_index"] for row in unresolved} == EXPECTED_UNRESOLVED
    checks["positive_rows_have_every_gate"] = all(all(row["gates"].values()) for row in repaired)
    checks["negative_rows_have_a_failed_gate"] = all(not all(row["gates"].values()) for row in unresolved)
    checks["positive_identity_methods_closed"] = all(
        row.get("accepted_identity_method") in ACCEPTED_METHODS for row in repaired
    )
    checks["positive_tags_resolve_to_full_commits"] = all(
        re.fullmatch(r"[0-9a-f]{40}", (row.get("accepted_exact_tag_commit") or {}).get("commit_sha", ""))
        for row in repaired
    )
    checks["positive_archive_checksums_bound"] = all(
        row["archive_provider_evidence"].get("provider_file_checksums_bound") for row in repaired
    )
    checks["positive_archive_and_commit_rights_bound"] = all(
        row["gates"]["accepted_archive_software_rights"]
        and row["gates"]["accepted_commit_software_rights"]
        for row in repaired
    )
    checks["unique_child_selection_is_provider_history_bound"] = all(
        row["archive_provider_evidence"].get("version_selection_method")
        != "FROZEN_CONCEPT_VERSION_HISTORY_UNIQUE_JOSS_VERSION_CHILD"
        or (
            row["archive_provider_evidence"].get("selected_archive_doi")
            and sum(
                bool(member.get("version_compatible_with_publication"))
                for member in row["archive_provider_evidence"].get("version_members") or []
            ) == 1
        )
        for row in rows
    )
    checks["uppercase_prefix_not_retroactively_normalized"] = next(
        row for row in rows if row["frozen_index"] == 196
    )["gates"]["exact_frozen_archive_version_doi_relation"] is False

    counts = result["counts"]
    checks["result_counts_exact"] = counts == {
        "author_lineage_adjudications": 0,
        "eligible_natural_pairs": 0,
        "files_versions_tags_commits_requests_counted_as_units": 0,
        "final_exact_joss_bridges": 70,
        "natural_pair_adjudications": 0,
        "new_or_replacement_publication_dois": 0,
        "same_frozen_publication_dois": 200,
        "v4_provider_qualified_frozen": 80,
        "v6_exact_joss_bridges": 56,
        "v6_unresolved_entering_v7": 24,
        "v7_remaining_unresolved": 10,
        "v7_same_identity_repairs": 14,
    }
    checks["receipt_counts_exact"] = (
        receipt["status"] == "PASS"
        and receipt["counts"]["frozen_input_identities"] == 24
        and receipt["counts"]["same_identity_repairs"] == 14
        and receipt["counts"]["remaining_unresolved"] == 10
        and receipt["counts"]["new_or_replacement_publication_dois"] == 0
        and receipt["counts"]["files_versions_tags_commits_requests_counted_as_units"] == 0
    )
    checks["result_artifact_hashes_valid"] = all([
        result["artifact_hashes"]["protocol"] == sha(HERE / "PROTOCOL_V7.json"),
        result["artifact_hashes"]["protocol_freeze"] == sha(HERE / "PROTOCOL_FREEZE_RECEIPT_V7.json"),
        result["artifact_hashes"]["input"] == sha(HERE / "UNRESOLVED_IDENTITIES_INPUT_V7.jsonl"),
        result["artifact_hashes"]["runner"] == sha(HERE / "run_targeted_identity_resolution_v7.py"),
        result["artifact_hashes"]["rows"] == sha(HERE / "IDENTITY_RESOLUTION_ROWS_V7.jsonl"),
        result["artifact_hashes"]["harvest_receipt"] == sha(HERE / "HARVEST_RECEIPT_V7.json"),
        result["artifact_hashes"]["v6_rows"] == sha(V6 / "BRIDGE_REPAIR_ROWS_V6.jsonl"),
        result["artifact_hashes"]["v6_result"] == sha(V6 / "RESULT_V6.json"),
    ])
    checks["harvest_hashes_valid"] = all([
        receipt["artifact_sha256"] == sha(HERE / "IDENTITY_RESOLUTION_ROWS_V7.jsonl"),
        receipt["protocol_sha256"] == sha(HERE / "PROTOCOL_V7.json"),
        receipt["input_sha256"] == sha(HERE / "UNRESOLVED_IDENTITIES_INPUT_V7.jsonl"),
        receipt["runner_sha256"] == sha(HERE / "run_targeted_identity_resolution_v7.py"),
        receipt["token_retained"] is False,
        receipt["download_payloads_retained"] is False,
        receipt["protected_or_system_outcomes_accessed"] is False,
    ])

    primary = Counter(row["v7_primary_failure"] for row in unresolved)
    overlap = Counter(cause for row in unresolved for cause in row["v7_failure_causes"])
    checks["negative_ledger_exact"] = (
        ledger["unresolved_identity_count"] == 10
        and ledger["primary_mutually_exclusive_counts"] == dict(sorted(primary.items()))
        and ledger["overlapping_gate_counts"] == dict(sorted(overlap.items()))
        and len(ledger["row_level_unresolved"]) == 10
    )
    checks["primary_causes_partition_remaining_ten"] = sum(primary.values()) == 10
    checks["no_lineage_or_natural_pair_promotion"] = all(
        row["author_lineage_independence"] == "CANNOT_CHECK_EXTERNAL_OUTCOME_BLIND_ADJUDICATION_REQUIRED"
        and row["natural_pair_eligibility"] == "CANNOT_CHECK_EXTERNAL_OUTCOME_BLIND_ADJUDICATION_REQUIRED"
        for row in rows
    ) and protocol["preserved_boundaries"] == {
        "author_lineage_adjudications": 0,
        "author_lineage_independence": "CANNOT_CHECK_EXTERNAL_OUTCOME_BLIND_ADJUDICATION_REQUIRED",
        "eligible_natural_pairs": 0,
        "natural_pair_adjudications": 0,
        "natural_pair_eligibility": "CANNOT_CHECK_EXTERNAL_OUTCOME_BLIND_ADJUDICATION_REQUIRED",
        "programme_terminal": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK",
    }
    checks["programme_terminal_preserved"] = (
        result["programme_terminal"] == "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK"
        and ledger["preserved_programme_terminal"] == "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK"
    )
    checks["no_payload_cache_retained"] = not any(
        path.is_dir() and path.name.casefold() in {"cache", "downloads", "payloads"}
        for path in HERE.iterdir()
    )

    all_pass = all(checks.values())
    existing_for_hash = [
        path for path in HERE.iterdir()
        if path.is_file() and path.name not in {"VERIFY_RECEIPT_V7.json", "SHA256SUMS"}
    ]
    verify = {
        "schema_version": "orion.p4.targeted-identity.verify-receipt.v7",
        "created_at": now(),
        "status": "PASS" if all_pass else "FAIL",
        "checks": {**dict(sorted(checks.items())), "all_checks_pass": all_pass},
        "counts": {
            "checks": len(checks), "checks_passed": sum(checks.values()),
            "input_identities": len(inputs), "repaired": len(repaired),
            "unresolved": len(unresolved), "final_exact_joss_bridges": counts.get("final_exact_joss_bridges"),
            "author_lineage_adjudications": 0, "natural_pair_adjudications": 0,
            "eligible_natural_pairs": 0,
        },
        "artifact_hashes": {path.name: sha(path) for path in sorted(existing_for_hash)},
        "command": "python validate_v7.py",
        "pytest_or_repository_ci_used": False,
    }
    (HERE / "VERIFY_RECEIPT_V7.json").write_text(json.dumps(verify, indent=2, sort_keys=True) + "\n")

    manifest_files = [path for path in HERE.iterdir() if path.is_file() and path.name != "SHA256SUMS"]
    (HERE / "SHA256SUMS").write_text("".join(
        f"{sha(path)}  {path.name}\n" for path in sorted(manifest_files, key=lambda value: value.name)
    ))
    print(
        f"V7_VALIDATE status={verify['status']} checks={sum(checks.values())}/{len(checks)} "
        f"repaired={len(repaired)} unresolved={len(unresolved)} final_exact={counts.get('final_exact_joss_bridges')}/80"
    )
    if not all_pass:
        for name, passed in sorted(checks.items()):
            if not passed:
                print(f"FAIL {name}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
