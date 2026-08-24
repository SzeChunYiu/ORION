#!/usr/bin/env python3
"""Direct verification for the P1 V8 semantic adjudication packet."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
USER_AGENT = "orion-p1-v8-verifier/1.0"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def fetch(url: str) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def all_keys(obj: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(obj, dict):
        keys.update(obj)
        for value in obj.values(): keys.update(all_keys(value))
    elif isinstance(obj, list):
        for value in obj: keys.update(all_keys(value))
    return keys


def verify_predecessor(predecessor: Path) -> tuple[int, list[str]]:
    failures = []
    lines = (predecessor / "SHA256SUMS").read_text().splitlines()
    for line in lines:
        digest, relative = line.split("  ", 1)
        path = predecessor / relative
        if not path.is_file() or sha(path) != digest:
            failures.append(relative)
    return len(lines), failures


def enumerate_matrix(matrix: dict) -> dict:
    sources = list(matrix["matrix"])
    targets = list(next(iter(matrix["matrix"].values())))
    counts = Counter()
    for values in itertools.product(targets, repeat=len(sources)):
        statuses = [matrix["matrix"][s][t]["status"] for s, t in zip(sources, values, strict=True)]
        if len(set(values)) != len(values) or "REJECT" in statuses:
            counts["known_rejected"] += 1
        elif all(status == "PASS" for status in statuses):
            counts["fully_certified"] += 1
        else:
            counts["not_disproved_but_uncertified"] += 1
    counts["total"] = sum(counts.values())
    return {
        "fully_certified": counts["fully_certified"],
        "known_rejected": counts["known_rejected"],
        "not_disproved_but_uncertified": counts["not_disproved_but_uncertified"],
        "total": counts["total"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--predecessor", type=Path, required=True)
    parser.add_argument("--online", action="store_true")
    args = parser.parse_args()
    predecessor = args.predecessor.resolve()

    json_paths = sorted(HERE.glob("*.json"))
    parsed = {path.name: load(path) for path in json_paths}
    protocol = parsed["P1_V8_PROTOCOL.json"]
    source = parsed["P1_V8_PUBLIC_TARGET_SOURCE_REGISTRY.json"]
    rights = parsed["P1_V8_RIGHTS_REGISTRY.json"]
    semantic = parsed["P1_V8_TARGET_SEMANTIC_REGISTRY.json"]
    adapters = parsed["P1_V8_720_ADAPTER_REGISTRY.json"]
    adjudication = parsed["P1_V8_ADAPTER_ADJUDICATION_RESULT.json"]
    theorem = parsed["P1_V8_CONDITIONAL_EQUIVALENCE_THEOREM.json"]
    result = parsed["P1_RESULT_V8.json"]
    schema = parsed["P1_V8_REQUIRED_OWNER_ALGEBRA_SCHEMA.json"]
    custodians = parsed["P1_V8_REQUIRED_FIELD_CUSTODIAN_REGISTRY.json"]

    checks = {}
    checks["json_parse"] = {"passed": True, "file_count_before_receipt": len(json_paths)}
    checks["protocol_boundary"] = {
        "passed": all(value is False for value in protocol["outcome_boundary"].values()),
        "outcome_boundary": protocol["outcome_boundary"],
    }
    predecessor_count, predecessor_failures = verify_predecessor(predecessor)
    checks["predecessor_manifest"] = {
        "passed": not predecessor_failures and sha(HERE / "PREDECESSOR_R7_SHA256SUMS") == protocol["predecessor"]["manifest_sha256"],
        "entry_count": predecessor_count,
        "failures": predecessor_failures,
    }

    commit = protocol["frozen_public_target_corpus"]["commit"]
    tree = subprocess.check_output(["git", "-C", str(args.repo_root), "rev-parse", f"{commit}^{{tree}}"], text=True).strip()
    source_failures = []
    online_failures = []
    for row in source["files"]:
        body = subprocess.check_output(["git", "-C", str(args.repo_root), "show", f"{commit}:{row['path']}"])
        if hashlib.sha256(body).hexdigest() != row["sha256"] or len(body) != row["bytes"] or row["payload_retained_in_handoff"] is not False:
            source_failures.append(row["path"])
        if args.online:
            status, remote = fetch(row["public_raw_url"])
            if status != 200 or remote != body:
                online_failures.append(row["path"])
    checks["public_source_bytes"] = {
        "passed": tree == protocol["frozen_public_target_corpus"]["tree"] and not source_failures and not online_failures,
        "file_count": len(source["files"]),
        "local_failures": source_failures,
        "online_checked": args.online,
        "online_failures": online_failures,
        "tree": tree,
    }
    if args.online:
        repo_status, repo_body = fetch("https://api.github.com/repos/SzeChunYiu/ORION")
        license_status, _ = fetch("https://api.github.com/repos/SzeChunYiu/ORION/license")
        repo_meta = json.loads(repo_body)
        rights_online = repo_status == 200 and repo_meta["private"] is False and repo_meta.get("license") is None and license_status == 404
    else:
        repo_status = license_status = None
        rights_online = True
    checks["rights_boundary"] = {
        "passed": rights_online
        and rights["target_repository"]["reuse_or_redistribution_licence_status"] == "NO_REUSE_LICENCE_FOUND__CANNOT_CHECK_PERMISSION"
        and rights["target_repository"]["applicable_target_corpus_license_file_count"] == 0,
        "online_checked": args.online,
        "repository_status": repo_status,
        "license_status": license_status,
    }

    forbidden_payload_keys = {"body", "body_base64", "content", "line_text", "case_text", "outcome_row", "protected_payload"}
    source_keys = all_keys(source)
    payload_files = [p.name for p in HERE.iterdir() if p.is_file() and p.suffix.lower() in {".html", ".pdf", ".response", ".zip", ".tar", ".gz"}]
    checks["payload_nonretention"] = {
        "passed": not (forbidden_payload_keys & source_keys) and not payload_files
        and source["payload_policy"]["remote_bodies_written_to_handoff"] is False
        and source["payload_policy"]["source_line_payloads_written_to_handoff"] is False,
        "forbidden_keys_present": sorted(forbidden_payload_keys & source_keys),
        "payload_files": payload_files,
    }

    target_ids = [row["target_id"] for row in semantic["targets"]]
    actionable = [row for row in semantic["targets"] if row["target_id"] != "UNRESOLVED"]
    checks["semantic_registry"] = {
        "passed": len(target_ids) == len(set(target_ids)) == 7
        and semantic["actionable_targets_with_complete_postpublication_denotation"] == 0
        and all(row["licensed_postpublication_operations"] == "UNBOUND" for row in actionable)
        and semantic["decision_probe_typing_result"]["one_to_one_bridge"] is False,
        "target_count": len(target_ids),
        "actionable_complete_postpublication_denotations": semantic["actionable_targets_with_complete_postpublication_denotation"],
    }
    for target in target_ids:
        assert source["occurrence_census"][target]["occurrence_count"] > 0

    source_ids = list(parsed_matrix := load(predecessor / "ADAPTER_COMPATIBILITY_MATRIX_V2.json")["matrix"])
    target_set = set(next(iter(parsed_matrix.values())))
    adapter_failures = []
    seen_ids = set()
    seen_mappings = set()
    for row in adapters["rows"]:
        mapping = row["mapping"]
        mapping_key = json.dumps(mapping, sort_keys=True)
        valid = (
            row["adapter_id"] not in seen_ids
            and mapping_key not in seen_mappings
            and set(mapping) == set(source_ids)
            and set(mapping.values()) <= target_set
            and len(set(mapping.values())) == len(mapping)
            and mapping["UNRESOLVED"] == "UNRESOLVED"
            and row["actionable_image_count"] == 5
            and len(row["essential_fields_still_missing_for_every_actionable_image"]) == 5
        )
        if not valid: adapter_failures.append(row["adapter_id"])
        seen_ids.add(row["adapter_id"]); seen_mappings.add(mapping_key)
    checks["adapter_registry"] = {
        "passed": adapters["row_count"] == len(adapters["rows"]) == 720 and not adapter_failures,
        "row_count": len(adapters["rows"]),
        "failures": adapter_failures,
    }

    matrix = load(predecessor / "ADAPTER_COMPATIBILITY_MATRIX_V2.json")
    enumeration = enumerate_matrix(matrix)
    checks["independent_enumeration"] = {
        "passed": enumeration == {
            "fully_certified": 0,
            "known_rejected": 116929,
            "not_disproved_but_uncertified": 720,
            "total": 117649,
        },
        "counts": enumeration,
    }
    checks["adjudication"] = {
        "passed": adjudication["pair_matrix"]["status_counts"] == {"CANNOT_CHECK": 30, "PASS": 1, "REJECT": 11}
        and adjudication["not_disproved_adapter_disposition"] == {
            "authoritatively_rejected_by_v8_public_evidence": 0,
            "certified_by_v8_public_evidence": 0,
            "input_count": 720,
            "minimum_missing_actionable_images_per_map": 5,
            "reason": adjudication["not_disproved_adapter_disposition"]["reason"],
            "remain_cannot_check": 720,
        },
        "pair_status_counts": adjudication["pair_matrix"]["status_counts"],
        "survivor_disposition": adjudication["not_disproved_adapter_disposition"],
    }
    required_owner_fields = set(schema["required"])
    schema_targets = schema["properties"]["targets"]["items"]["properties"]["decision_id"]["enum"]
    checks["owner_algebra_schema"] = {
        "passed": len(required_owner_fields) == 10 and set(schema_targets) == target_set and len(custodians["requirements"]) == 12,
        "required_top_level_fields": sorted(required_owner_fields),
        "custodian_requirement_count": len(custodians["requirements"]),
    }
    binding_failures = [
        name for name, digest in result["artifact_bindings"].items()
        if not (HERE / name).is_file() or sha(HERE / name) != digest
    ]
    checks["result_boundary"] = {
        "passed": not binding_failures
        and result["terminal"] == protocol["terminals"]["cannot_check"]
        and result["adapter_result"]["remain_cannot_check"] == 720
        and result["preserved_r7_negatives"]["not_disproved_but_uncertified"] == 720
        and result["preserved_r7_negatives"]["conditional_full_withdrawal_impossibility_only"] is True
        and result["manuscript_integration"]["warranted"] is False
        and theorem["parts"][3]["status"] == "CONDITIONAL_EQUIVALENCE",
        "terminal": result["terminal"],
        "artifact_binding_failures": binding_failures,
        "manuscript_integration_warranted": result["manuscript_integration"]["warranted"],
    }

    passed = all(row["passed"] for row in checks.values())
    receipt = {
        "schema_version": "orion.p1.source-native-target-semantics-verification-receipt.v8",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority": "DIRECT_JSON_HASH_SOURCE_ENUMERATION_RIGHTS_AND_NONLEAKAGE_VERIFICATION_ONLY",
        "checks": checks,
        "passed": passed,
        "pytest_or_ci_run": False,
        "case_text_or_outcomes_accessed": False,
        "terminal": result["terminal"],
    }
    (HERE / "VERIFY_RECEIPT_V8.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "passed": passed,
        "check_count": len(checks),
        "json_files_before_receipt": len(json_paths),
        "predecessor_entries": predecessor_count,
        "public_sources": len(source["files"]),
        "online": args.online,
        "adapter_rows": len(adapters["rows"]),
        "enumeration": enumeration,
        "payload_files": payload_files,
        "terminal": result["terminal"],
    }, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
