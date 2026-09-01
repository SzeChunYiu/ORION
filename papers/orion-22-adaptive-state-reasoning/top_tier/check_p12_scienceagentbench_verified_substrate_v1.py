#!/usr/bin/env python3
"""Verify the frozen ScienceAgentBench verified split and clean-license census.

This checker reads only the public annotation Parquet. It does not run agents,
load protected outcomes, or evaluate generated code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def evaluate_rows(rows: list[dict[str, Any]], freeze: dict[str, Any]) -> dict[str, Any]:
    declared_rows = freeze["dataset"]["declared_rows"]
    excluded = set(freeze["clean_license_exclusion"]["instance_ids"])
    if len(rows) != declared_rows:
        raise ValueError(f"verified row count mismatch: {len(rows)} != {declared_rows}")

    ids: list[int] = []
    normalized: list[dict[str, Any]] = []
    for row in rows:
        iid = row.get("instance_id")
        if isinstance(iid, bool) or not isinstance(iid, int):
            raise ValueError("instance_id must be integer")
        ids.append(iid)
        normalized.append({
            "instance_id": iid,
            "domain": clean_text(row.get("domain"), "domain"),
            "github_name": clean_text(row.get("github_name"), "github_name"),
        })
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate instance_id in verified split")
    missing_exclusions = sorted(excluded - set(ids))
    if missing_exclusions:
        raise ValueError(f"frozen exclusions absent from verified split: {missing_exclusions}")

    clean = [r for r in normalized if r["instance_id"] not in excluded]
    clean_ids = {r["instance_id"] for r in clean}
    if clean_ids & excluded:
        raise AssertionError("excluded instance survived clean-license filter")
    expected_clean_tasks = declared_rows - len(excluded)
    if len(clean) != expected_clean_tasks:
        raise ValueError(f"clean task count mismatch: {len(clean)} != {expected_clean_tasks}")

    family_counts = Counter(r["github_name"] for r in clean)
    domain_counts = Counter(r["domain"] for r in clean)
    min_families = freeze["dataset_only_scope_gate"]["minimum_task_families"]
    min_domains = freeze["dataset_only_scope_gate"]["minimum_domains"]
    dataset_only_pass = len(family_counts) >= min_families and len(domain_counts) >= min_domains

    return {
        "schema": "ORION.A2.ScienceAgentBenchVerifiedSubstrateCensusResult.v1",
        "verified_rows": len(rows),
        "excluded_instance_ids": sorted(excluded),
        "clean_tasks": len(clean),
        "task_family_key": freeze["scientific_unit"]["family_key"],
        "task_families": len(family_counts),
        "domains": len(domain_counts),
        "family_counts": dict(sorted(family_counts.items())),
        "domain_counts": dict(sorted(domain_counts.items())),
        "dataset_only_minimums": {
            "task_families_at_least_20": len(family_counts) >= min_families,
            "domains_at_least_3": len(domain_counts) >= min_domains,
            "clean_tasks_exactly_96": len(clean) == 96,
        },
        "dataset_only_scope_precondition_pass": dataset_only_pass,
        "model_family_execution_requirement_satisfied": False,
        "campaign_executed": False,
        "protected_outcomes_accessed": False,
        "scientific_authority_delta": "NONE__SUBSTRATE_AND_CENSUS_PREFLIGHT_ONLY",
    }


def verify(freeze_path: Path, parquet_path: Path) -> dict[str, Any]:
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze["schema"] != "ORION.A2.ScienceAgentBenchVerifiedSubstrateFreeze.v1":
        raise ValueError("freeze schema mismatch")
    if freeze["protected_outcomes_accessed"] is not False or freeze["campaign_executed"] is not False:
        raise ValueError("substrate freeze launders campaign/outcome authority")
    expected_hash = freeze["dataset"]["verified_parquet_sha256"]
    observed_hash = sha256(parquet_path)
    if observed_hash != expected_hash:
        raise ValueError(f"verified parquet sha256 mismatch: {observed_hash}")
    if parquet_path.stat().st_size != freeze["dataset"]["verified_parquet_bytes"]:
        raise ValueError("verified parquet byte-size mismatch")

    table = pq.read_table(parquet_path, columns=["instance_id", "domain", "github_name"])
    rows = table.to_pylist()
    result = evaluate_rows(rows, freeze)
    result["verified_parquet_sha256"] = observed_hash
    result["verified_split_commit"] = freeze["dataset"]["verified_split_introducing_commit"]
    return result


def self_test() -> dict[str, Any]:
    freeze = {
        "dataset": {"declared_rows": 102},
        "clean_license_exclusion": {"instance_ids": [3, 32, 46, 53, 54, 84]},
        "scientific_unit": {"family_key": "github_name"},
        "dataset_only_scope_gate": {"minimum_task_families": 20, "minimum_domains": 3},
    }
    rows = []
    for i in range(1, 103):
        rows.append({
            "instance_id": i,
            "domain": f"D{(i - 1) % 4}",
            "github_name": f"org/repo{(i - 1) % 30}",
        })
    good = evaluate_rows(rows, freeze)
    assert good["clean_tasks"] == 96
    assert good["dataset_only_scope_precondition_pass"] is True

    hostile = json.loads(json.dumps(freeze))
    hostile["clean_license_exclusion"]["instance_ids"] = [3, 32, 46, 53, 54, 999]
    try:
        evaluate_rows(rows, hostile)
    except ValueError as exc:
        assert "absent" in str(exc)
    else:
        raise AssertionError("missing frozen exclusion was accepted")
    return {"decision": "GREEN", "hostile_missing_exclusion_rejected": True}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", type=Path)
    ap.add_argument("--parquet", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if args.freeze is None or args.parquet is None:
        ap.error("--freeze and --parquet are required unless --self-test is used")
    try:
        result = verify(args.freeze, args.parquet)
    except Exception as exc:
        print(json.dumps({"decision": "REJECT", "reason": str(exc)}, indent=2, sort_keys=True))
        return 1
    result["decision"] = "GREEN" if result["dataset_only_scope_precondition_pass"] else "CANNOT_CHECK_DATASET_SCOPE_SHORTFALL"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] == "GREEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
