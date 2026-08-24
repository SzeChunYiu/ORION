#!/usr/bin/env python3
"""Fail-closed validator for the retained P6 public execution result."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "development/p6-public-selective-revalidation-v1"
PROTOCOL = BASE / "P6_PUBLIC_SELECTIVE_REVALIDATION_PROTOCOL_V1.json"
RUNNER = BASE / "run_p6_public_selective_revalidation_v1.py"
RESULT = BASE / "P6_PUBLIC_SELECTIVE_REVALIDATION_RESULT_V1.json"
EXPECTED_RESULT_FILE_SHA256 = "73ec37165e29f53e16206e69722589335205fda969da8deb2803d24236e8beba"
EXPECTED_SOURCE_COMMIT = "573e69d232a20bf62f1a18095d3bdc9b35924f0d"
VALID_TERMINAL = "P6_PUBLIC_SELECTIVE_REVALIDATION_RESULT_V1_VALID__DATA_AND_COMPARATOR_EXECUTION_ONLY"
RESULT_KEYS = {
    "change_set_count", "committed_blob_equality", "data_coverage_gate", "domain_count",
    "domains", "historical_native_build_test_replay", "independent_adjudication",
    "mutation_gate", "mutation_kill_counts", "native_conformance_gate", "observed_runtime",
    "population_inference", "protected_custody", "protocol_file_sha256", "protocol_sha256",
    "receipt_sha256", "runner_sha256", "savings_gate", "schema", "scientific_authority_delta",
    "scientific_superiority_gate", "simultaneous_95pct_inferential_gate", "source_branch",
    "source_commit", "strongest_donor_result", "terminal",
}
DOMAIN_KEYS = {
    "acquisition", "artifact_count", "artifact_universe_sha256", "block_resampling_lower_quantile",
    "change_set_count", "dataset_id", "dependency_edge_count", "dependency_edges_sha256", "domain",
    "import_resolution_audit", "invalid_certificate_count", "mean_savings_vs_full_reset", "rows",
    "selective_native_exact_agreement", "status", "unnecessary_revalidation_count_vs_native",
}
ACQUISITION_KEYS = {
    "fetch_argv", "fetch_exit_code", "license_git_blob_sha1", "materialize_argv",
    "materialize_exit_code", "materialize_stderr_sha256", "observed_fetch_head",
    "observed_frozen_ref", "observed_materialized_head", "remote_branch_moved_during_acquisition",
    "remote_branch_post_sha256", "remote_branch_pre_sha256", "stderr_sha256",
}
ROW_KEYS = {
    "changed_path_count", "changed_paths", "commit", "full_reset_count", "invalid_certificate_count",
    "mutation_disagreements", "native_selected_count", "native_selected_sha256", "parent",
    "savings_vs_full_reset", "selective_selected_count", "selective_selected_sha256",
    "unnecessary_revalidation_count_vs_native",
}
SUMMARY = {
    "nfcore_rnaseq_nextflow": ("scientific_workflow", 247, 181, 0.9556275303643724, 0.9122267206477733, (241, 233, 8, 0)),
    "mathlib4_lean": ("formal_mathematics", 8388, 553, 0.9988483547925608, 0.9975274201239867, (696, 555, 141, 0)),
    "geneontology_go_ontology": ("versioned_ontology", 67, 46, 0.9832835820895522, 0.9817910447761194, (85, 46, 39, 0)),
}
PROVENANCE = {
    "nfcore_rnaseq_nextflow": {
        "artifact_universe_sha256": "05dd81a8586b867408b692eb6d1dcafaa50cdfa58609b6f713ee2c46ff7744d2",
        "dependency_edges_sha256": "d0a506885eb8d62f0e7b26246e5daa7d59be413ea0ff69bd25b47e21ccca72ae",
        "acquisition_sha256": "3c1b5e9f9ee95f996ac361e2d8ad52586ec147448ed13f9e4593a9e5e2fda583",
        "rows_sha256": "774a463331af7b7d4e1a7b33c69e22f9b205cdcfd8424254f39fe745f82b6412",
    },
    "mathlib4_lean": {
        "artifact_universe_sha256": "016494d55d149491925f16ef80cf429625e09f1285b6dba1c923107db0fcdd5b",
        "dependency_edges_sha256": "0e1f438bf1e6bf5104ccfdf6477597cb29b3a44c7e080517084156be5927c190",
        "acquisition_sha256": "6c654a4737638362bf52154716ca34533f7be3e8168a73731f2bd05f5cb45fe8",
        "rows_sha256": "cde9f781951330916d9cd153ba95ddd9f4a6a269f34af680c017c17f7061aaef",
    },
    "geneontology_go_ontology": {
        "artifact_universe_sha256": "b6cebde1c773aa39fa35c9ca066177d7915c8d8b3e4d6ed2ba74333bc417d50d",
        "dependency_edges_sha256": "4fcb8e309a869d5ec4c3ea109930858c8df09056851a5732f374918913330c6d",
        "acquisition_sha256": "b78623c4fce68292585a7cd1278c4571b99ecc22fecd53276695de32d0bd3dd7",
        "rows_sha256": "6c36142995ddf8f579cfc6808b0eea5973921d49c0462db077512d2bbc7f357b",
    },
}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_runner():
    spec = importlib.util.spec_from_file_location("p6_public_selective_v1", RUNNER)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError("runner loader unavailable")
    spec.loader.exec_module(module)
    return module


def strict_json(path: Path) -> Any:
    def reject_duplicates(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    return json.loads(path.read_text(), object_pairs_hook=reject_duplicates)


def exact_int(value: Any, expected: int | None = None, label: str = "integer") -> int:
    if type(value) is not int or (expected is not None and value != expected):
        raise TypeError(f"{label} exact integer drift")
    return value


def exact_float(value: Any, expected: float | None = None, label: str = "float") -> float:
    if type(value) is not float or (expected is not None and value != expected):
        raise TypeError(f"{label} exact float drift")
    return value


def validate_result(result_path: Path = RESULT, root: Path = ROOT) -> dict[str, Any]:
    if file_digest(result_path) != EXPECTED_RESULT_FILE_SHA256:
        raise ValueError("result file SHA-256 drift")
    result = strict_json(result_path)
    runner = load_runner()
    protocol = strict_json(PROTOCOL)
    runner.validate_protocol(protocol, root)
    if set(result) != RESULT_KEYS:
        raise ValueError("result top-level key set drift")

    receipt = result["receipt_sha256"]
    without_receipt = dict(result)
    without_receipt.pop("receipt_sha256")
    if receipt != runner.digest(runner.canonical(without_receipt)):
        raise ValueError("result receipt drift")
    expected_blobs = {runner.PROTOCOL_PATH: file_digest(PROTOCOL), runner.RUNNER_PATH: file_digest(RUNNER)}
    required = {
        "schema": runner.RESULT_SCHEMA,
        "protocol_file_sha256": file_digest(PROTOCOL),
        "protocol_sha256": runner.digest(runner.canonical(protocol)),
        "runner_sha256": file_digest(RUNNER),
        "source_branch": "main",
        "source_commit": EXPECTED_SOURCE_COMMIT,
        "committed_blob_equality": expected_blobs,
        "observed_runtime": protocol["runtime"],
        "domain_count": 3,
        "change_set_count": 300,
        "mutation_kill_counts": {"ALTERNATIVE_SUPPORT_ALL_DEPENDENCIES": 45, "OMITTED_EDGE": 51, "OMITTED_READ": 53},
        "data_coverage_gate": "MET",
        "native_conformance_gate": "MET",
        "savings_gate": "MET",
        "mutation_gate": "MET",
        "strongest_donor_result": "EXTENSIONALLY_EQUIVALENT",
        "scientific_superiority_gate": "NOT_MET",
        "simultaneous_95pct_inferential_gate": "CANNOT_CHECK",
        "historical_native_build_test_replay": "CANNOT_CHECK",
        "independent_adjudication": "CANNOT_CHECK",
        "protected_custody": "CANNOT_CHECK",
        "population_inference": False,
        "scientific_authority_delta": "P6_DATA_AND_COMPARATOR_EXECUTION_ONLY",
        "terminal": "P6_PUBLIC_SELECTIVE_REVALIDATION_V1_COVERAGE_AND_SAVINGS_MET__NATIVE_EQUIVALENT__SUPERIORITY_NOT_MET",
    }
    for key, expected in required.items():
        runner.assert_exact(result[key], expected, f"result.{key}")
    for relative, expected_digest in expected_blobs.items():
        try:
            committed = subprocess.check_output(["git", "show", f"{result['source_commit']}:{relative}"], cwd=root, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as error:
            raise ValueError(f"historical source path unavailable: {relative}") from error
        if runner.digest(committed) != expected_digest or committed != (root / relative).read_bytes():
            raise ValueError(f"historical committed byte equality failed: {relative}")

    datasets = protocol["datasets"]
    if [domain.get("dataset_id") for domain in result["domains"]] != [row["id"] for row in datasets]:
        raise ValueError("domain order or identity drift")
    kills = {name: 0 for name in protocol["gate"]["mutations_killed_globally"]}
    unresolved_total = 0
    for domain, dataset in zip(result["domains"], datasets):
        if set(domain) != DOMAIN_KEYS:
            raise ValueError("domain key set drift")
        expected_domain, artifacts, edges, mean, lower, audit_counts = SUMMARY[dataset["id"]]
        runner.assert_exact(domain["dataset_id"], dataset["id"], "domain.dataset_id")
        runner.assert_exact(domain["domain"], expected_domain, "domain.domain")
        runner.assert_exact(domain["status"], "EXECUTED", "domain.status")
        exact_int(domain["artifact_count"], artifacts, "artifact_count")
        exact_int(domain["dependency_edge_count"], edges, "dependency_edge_count")
        exact_int(domain["change_set_count"], 100, "change_set_count")
        exact_float(domain["mean_savings_vs_full_reset"], mean, "mean_savings")
        exact_float(domain["block_resampling_lower_quantile"], lower, "lower_quantile")
        provenance = PROVENANCE[dataset["id"]]
        for key in ("artifact_universe_sha256", "dependency_edges_sha256"):
            if domain[key] != provenance[key]:
                raise ValueError(f"frozen {key} drift")
        exact_int(domain["invalid_certificate_count"], 0, "invalid_certificate_count")
        exact_int(domain["unnecessary_revalidation_count_vs_native"], 0, "unnecessary_count")
        runner.assert_exact(domain["selective_native_exact_agreement"], True, "domain.agreement")

        audit = domain["import_resolution_audit"]
        if set(audit) != {"candidate_import_count", "resolved_import_count", "unresolved_import_count", "ambiguous_import_count"}:
            raise ValueError("import audit key drift")
        candidate, resolved, unresolved, ambiguous = audit_counts
        for key, expected in zip(("candidate_import_count", "resolved_import_count", "unresolved_import_count", "ambiguous_import_count"), audit_counts):
            exact_int(audit[key], expected, f"audit.{key}")
        if candidate != resolved + unresolved + ambiguous:
            raise ValueError("import audit arithmetic drift")
        unresolved_total += unresolved

        acquisition = domain["acquisition"]
        if set(acquisition) != ACQUISITION_KEYS:
            raise ValueError("acquisition key set drift")
        expected_fetch = ["git", "fetch", "--quiet", "--filter=blob:none", "--depth", str(dataset["history_depth"]), "origin", dataset["head_commit"]]
        runner.assert_exact(acquisition["fetch_argv"], expected_fetch, "acquisition.fetch_argv")
        runner.assert_exact(acquisition["materialize_argv"], ["git", "checkout", "--quiet", "--detach", "refs/heads/frozen"], "acquisition.materialize_argv")
        exact_int(acquisition["fetch_exit_code"], 0, "fetch_exit_code")
        exact_int(acquisition["materialize_exit_code"], 0, "materialize_exit_code")
        for key in ("observed_fetch_head", "observed_frozen_ref", "observed_materialized_head"):
            if not HEX40.fullmatch(acquisition[key]) or acquisition[key] != dataset["head_commit"]:
                raise ValueError(f"{key} drift")
        runner.assert_exact(acquisition["license_git_blob_sha1"], dataset["license_git_blob_sha1"], "license blob")
        if type(acquisition["remote_branch_moved_during_acquisition"]) is not bool:
            raise TypeError("remote movement flag type drift")
        for key in ("materialize_stderr_sha256", "remote_branch_post_sha256", "remote_branch_pre_sha256", "stderr_sha256"):
            if not HEX64.fullmatch(acquisition[key]):
                raise ValueError(f"{key} digest drift")
        if acquisition["remote_branch_moved_during_acquisition"] != (
            acquisition["remote_branch_pre_sha256"] != acquisition["remote_branch_post_sha256"]
        ):
            raise ValueError("remote movement flag/digest contradiction")
        if runner.digest(runner.canonical(acquisition)) != provenance["acquisition_sha256"]:
            raise ValueError("frozen acquisition receipt drift")

        rows = domain["rows"]
        if type(rows) is not list or len(rows) != 100:
            raise ValueError("row count drift")
        commits: set[str] = set()
        savings = []
        for row in rows:
            if set(row) != ROW_KEYS:
                raise ValueError("row key set drift")
            if not HEX40.fullmatch(row["commit"]) or not HEX40.fullmatch(row["parent"]):
                raise ValueError("row commit identity drift")
            commits.add(row["commit"])
            if type(row["changed_paths"]) is not list or not row["changed_paths"] or row["changed_paths"] != sorted(row["changed_paths"]):
                raise ValueError("changed paths drift")
            exact_int(row["changed_path_count"], len(row["changed_paths"]), "changed_path_count")
            native_count = exact_int(row["native_selected_count"], label="native_selected_count")
            exact_int(row["selective_selected_count"], native_count, "selective_selected_count")
            exact_int(row["full_reset_count"], artifacts, "full_reset_count")
            exact_int(row["invalid_certificate_count"], 0, "row invalid count")
            exact_int(row["unnecessary_revalidation_count_vs_native"], 0, "row unnecessary count")
            if row["native_selected_sha256"] != row["selective_selected_sha256"] or not HEX64.fullmatch(row["native_selected_sha256"]):
                raise ValueError("row selector digest disagreement")
            expected_savings = 1.0 - native_count / artifacts
            exact_float(row["savings_vs_full_reset"], expected_savings, "row savings")
            savings.append(row["savings_vs_full_reset"])
            disagreements = row["mutation_disagreements"]
            if set(disagreements) != set(protocol["gate"]["mutations_killed_globally"]):
                raise ValueError("mutation disagreement key drift")
            for name, killed in disagreements.items():
                if type(killed) is not bool:
                    raise TypeError("mutation flag type drift")
                kills[name] += int(killed)
        if len(commits) != 100:
            raise ValueError("duplicate retained commits")
        if runner.digest(runner.canonical(rows)) != provenance["rows_sha256"]:
            raise ValueError("frozen retained-row set drift")
        exact_float(domain["mean_savings_vs_full_reset"], sum(savings) / len(savings), "recomputed mean")
    if unresolved_total != 188:
        raise ValueError("unresolved import total drift")
    runner.assert_exact(result["mutation_kill_counts"], kills, "result.mutation_kill_counts")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, default=RESULT)
    args = parser.parse_args()
    validate_result(args.result)
    print(VALID_TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
