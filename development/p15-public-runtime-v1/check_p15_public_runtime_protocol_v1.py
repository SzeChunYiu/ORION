#!/usr/bin/env python3
"""Fail-closed checker for the P15 public-runtime no-results freeze."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "development/p15-public-runtime-v1/P15_PUBLIC_RUNTIME_PROTOCOL_V1.json"
EXPECTED_FILE_SHA256 = "39fb8a8bb8c79d0ce347b95bec5a21828556e56f9a038c4796cab4c9d108d27e"
VALID_TERMINAL = "P15_PUBLIC_RUNTIME_PROTOCOL_V1_VALID__NO_RESULTS__AUTHORITY_NONE"
NO_RESULT_TERMINAL = "P15_PUBLIC_RUNTIME_V1_CANNOT_CHECK__NO_CONTAINER_RUNTIME__NO_BUILT_IMAGES__NO_RESULTS"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
TOP_KEYS = {
    "schema", "status", "frozen_utc", "issue", "paper", "outcome_accessed",
    "results_exist", "selection_rule", "workload_sources", "workloads",
    "failure_source", "failure_cases", "runtime_image_definitions", "matched_arms",
    "gate", "execution_preflight", "authority", "non_bypass_boundaries",
}
SECTION_SHA256 = {
    "workload_sources": "8da98d4a8e68e69ebc2c1a81a0271e4ed698b561f79582133401145b9830a0a0",
    "workloads": "d885db2c610fd3a532be3d6f1f24f0bf3d8e32966eddd892edff96e5f29e3f0f",
    "failure_source": "01e1cf9e58c48b55abc7d9880f19638a2d67581ac366bd7ea030cc108462c38f",
    "failure_cases": "65b1c3b5a4788f898df1c2fb9a1d1396e4b57223b2431f05555ce6127b90d6f1",
    "runtime_image_definitions": "403b1f71087339b2bd065ffc752c571144e1959959c57fe9002377cebbf653e8",
    "matched_arms": "7362d871840ea5f194066be3668f53b37448a836b3b01a53fb2c99ddacdaeab7",
    "gate": "5ea657128d9d86f2478dd064c3953ea722b71ed97b50e4536f1c4098a6a41c3d",
    "execution_preflight": "ec10fe940d091afba743725d0de2310dac5a331f7e73208ea31cce536336e814",
    "authority": "eff3c64095de9f228e7e9c705e041a2be63aab69db6f075dc29cf08baad147bf",
    "non_bypass_boundaries": "3be59e4b5d1bfea08a74d79e062c1a04afb6861ec9e01119e0e89d4717cc9efd",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def strict_load(path: Path) -> dict[str, Any]:
    def reject_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(path.read_text(), object_pairs_hook=reject_duplicates)
    if type(value) is not dict:
        raise TypeError("protocol must be an object")
    return value


def exact(value: Any, expected: Any, label: str) -> None:
    if type(value) is not type(expected):
        raise TypeError(f"{label} exact type drift")
    if value != expected:
        raise ValueError(f"{label} value drift")


def validate(path: Path = PROTOCOL) -> dict[str, Any]:
    if digest(path) != EXPECTED_FILE_SHA256:
        raise ValueError("protocol file SHA-256 drift")
    protocol = strict_load(path)
    if set(protocol) != TOP_KEYS:
        raise ValueError("protocol top-level key drift")
    for key, expected in {
        "schema": "ORION.P15.PublicRuntimeProtocol.v1",
        "status": "FROZEN_NO_RESULTS",
        "frozen_utc": "2026-08-24T16:20:00Z",
        "issue": 1086,
        "paper": "P15_Q3_SHARED_SOFTWARE_INSTRUMENT",
        "outcome_accessed": False,
        "results_exist": False,
        "selection_rule": "first ten eligible public identities in each frozen source order; ScienceAgentBench excludes upstream-license exceptions before taking ten; Defects4J takes first four active bugs from each of five predeclared projects",
    }.items():
        exact(protocol[key], expected, key)
    for section, expected_digest in SECTION_SHA256.items():
        if semantic_digest(protocol[section]) != expected_digest:
            raise ValueError(f"{section} exact semantic digest drift")

    sources = protocol["workload_sources"]
    if type(sources) is not list or [source["id"] for source in sources] != [
        "core_bench_train", "paperbench", "scienceagentbench"
    ]:
        raise ValueError("workload source identity/order drift")
    expected_commits = {
        "core_bench_train": "e32a2980e72fe6eb04ee04eb749458f570625663",
        "paperbench": "51052cede8cc608f95bb00346635e03759013e5a",
    }
    for source in sources[:2]:
        if source["commit"] != expected_commits[source["id"]] or not HEX40.fullmatch(source["commit"]):
            raise ValueError("workload source commit drift")
        if source["code_license"] != "MIT" or not HEX64.fullmatch(source["license_sha256"]):
            raise ValueError("workload source license drift")
    sab = sources[2]
    exact(sab["code_commit"], "c26e151ed601ba109dc4d35e057ff8e73fec469d", "ScienceAgentBench code commit")
    exact(sab["dataset_commit"], "9c6e96c9e74572e979b0930ee735041cef528cb7", "ScienceAgentBench dataset commit")
    exact(sab["dataset_row_count"], 102, "ScienceAgentBench row count")
    exact(sab["dataset_parquet_sha256"], "c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147", "ScienceAgentBench parquet")
    exact(sab["selected_task_license"], "CC-BY-4.0", "ScienceAgentBench selected license")
    exact(sab["excluded_upstream_terms_instance_ids"], [3, 32, 46, 53, 54, 84], "ScienceAgentBench exclusions")

    workloads = protocol["workloads"]
    if type(workloads) is not list or len(workloads) != 30:
        raise ValueError("workload count drift")
    by_source = {name: [row for row in workloads if row.get("source") == name] for name in (
        "core_bench_train", "paperbench", "scienceagentbench"
    )}
    if any(len(rows) != 10 for rows in by_source.values()) or len({str(row["id"]) for row in workloads}) != 30:
        raise ValueError("workload balance or identity drift")
    exact([row["id"] for row in by_source["core_bench_train"]], [
        "capsule-7038571", "capsule-3137115", "capsule-5367566", "capsule-9168639",
        "capsule-9166182", "capsule-0325493", "capsule-1854976", "capsule-9022937",
        "capsule-8197429", "capsule-2916503",
    ], "CORE workload identities")
    exact([row["id"] for row in by_source["paperbench"]], [
        "adaptive-pruning", "all-in-one", "bam", "bbox", "bridging-data-gaps",
        "fre", "ftrl", "lbcs", "lca-on-the-line", "mechanistic-understanding",
    ], "PaperBench identities")
    if any(not HEX64.fullmatch(row["config_sha256"]) for row in by_source["paperbench"]):
        raise ValueError("PaperBench config digest drift")
    exact([row["id"] for row in by_source["scienceagentbench"]], [1, 2, 4, 5, 6, 7, 8, 9, 10, 11], "ScienceAgentBench identities")
    if set(sab["excluded_upstream_terms_instance_ids"]) & {row["id"] for row in by_source["scienceagentbench"]}:
        raise ValueError("excluded ScienceAgentBench task selected")

    failure_source = protocol["failure_source"]
    exact(failure_source["commit"], "8c16da8230843cdc918eaf4ddb449637f02b83c6", "Defects4J commit")
    exact(failure_source["infrastructure_license"], "MIT", "Defects4J license")
    exact(failure_source["upstream_project_terms"], "CANNOT_CHECK", "Defects4J upstream terms")
    failures = protocol["failure_cases"]
    if type(failures) is not list or len(failures) != 20 or len({row["id"] for row in failures}) != 20:
        raise ValueError("failure-case count or identity drift")
    projects = ["Chart", "Closure", "Lang", "Math", "Time"]
    if any(sum(row["id"].startswith(project + "-") for row in failures) != 4 for project in projects):
        raise ValueError("failure project balance drift")
    if any(not row["buggy"] or not row["fixed"] or row["buggy"] == row["fixed"] for row in failures):
        raise ValueError("buggy/fixed revision drift")

    images = protocol["runtime_image_definitions"]
    if type(images) is not list or len(images) != 3:
        raise ValueError("runtime image-definition count drift")
    for image in images:
        if not HEX64.fullmatch(image["source_sha256"]):
            raise ValueError("runtime source digest drift")
        exact(image["oci_digest"], "CANNOT_CHECK", "unbuilt OCI digest")
        if image["status"] not in {"SOURCE_BOUND_IMAGE_NOT_BUILT", "SOURCE_BOUND_GENERATOR_NOT_EXECUTED"}:
            raise ValueError("runtime image status falsely executed")

    exact(protocol["matched_arms"], [
        "BASELINE_HARNESS", "P15_FULL", "NO_CONTENT_BINDING",
        "NO_FAIL_CLOSED_DISPOSITION", "NO_Q3_SHARED_SURFACE",
    ], "matched arms")
    preflight = protocol["execution_preflight"]
    exact(preflight, {
        "container_runtime": "CANNOT_CHECK",
        "built_oci_image_count": 0,
        "workloads_executed": 0,
        "failure_cases_executed": 0,
        "terminal": NO_RESULT_TERMINAL,
    }, "execution preflight")
    exact(protocol["authority"], {
        "scientific_authority_delta": "NONE",
        "closes_issue_box": False,
        "independent_replication": "CANNOT_CHECK",
        "protected_custody": "CANNOT_CHECK",
        "external_adoption": "CANNOT_CHECK",
        "site_independence": "CANNOT_CHECK",
        "population_inference": False,
    }, "authority")
    if type(protocol["non_bypass_boundaries"]) is not list or len(protocol["non_bypass_boundaries"]) != 5:
        raise ValueError("non-bypass boundary drift")
    return protocol


if __name__ == "__main__":
    validate()
    print(VALID_TERMINAL)
