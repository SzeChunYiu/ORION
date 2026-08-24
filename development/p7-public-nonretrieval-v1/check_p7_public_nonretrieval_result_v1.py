#!/usr/bin/env python3
"""Fail-closed validator for the retained P7 public non-retrieval result."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "development/p7-public-nonretrieval-v1"
PROTOCOL = BASE / "P7_PUBLIC_NONRETRIEVAL_PROTOCOL_V1.json"
RUNNER = BASE / "run_p7_public_nonretrieval_v1.py"
RESULT = BASE / "P7_PUBLIC_NONRETRIEVAL_RESULT_V1.json"
SEAL = BASE / "P7_PUBLIC_NONRETRIEVAL_RESULT_V1_SEAL.json"
EXPECTED_RESULT_FILE_SHA256 = "115e02bc90b42aaca3df79eda21b5438a57a8722834ccae2ef33bf49479045a3"
EXPECTED_SOURCE_COMMIT = "9469c08eaa4eca3522e2dcc98b94b14084664659"
VALID_TERMINAL = "P7_PUBLIC_NONRETRIEVAL_RESULT_V1_VALID__DATA_COVERAGE_ONLY__SUPERIORITY_NOT_MET"
EXPECTED_RESULT_KEYS = {
    "committed_blob_equality",
    "conformance_boundary",
    "constructed_transition_boundary",
    "data_coverage_gate",
    "domain_count",
    "domains",
    "independent_adjudication",
    "inference_unit",
    "issue_box_candidate",
    "observed_environment",
    "population_inference",
    "protocol_file_sha256",
    "protocol_sha256",
    "receipt_sha256",
    "runner_sha256",
    "schema",
    "scientific_authority_delta",
    "scientific_superiority_gate",
    "source_branch",
    "source_commit",
    "strongest_donor_result",
    "structural_family_count",
    "terminal",
    "transition_rows",
    "unique_directed_transition_count",
    "upstream_rows_downloaded_or_redistributed",
}
EXPECTED_SEAL = {
    "schema": "ORION.P7.PublicNonretrievalResultSeal.v1",
    "raw_result_file_sha256": EXPECTED_RESULT_FILE_SHA256,
    "source_branch": "main",
    "source_commit": EXPECTED_SOURCE_COMMIT,
    "authority": {
        "scientific_authority_delta": "P7_DATA_COVERAGE_BOX_ONLY",
        "scientific_superiority_gate": "NOT_MET",
        "independent_adjudication": "CANNOT_CHECK",
        "protected_custody": "CANNOT_CHECK",
        "population_inference": False,
        "cross_family_replication": False,
    },
    "boundary": "post-execution authority seal; raw result bytes are unchanged",
}


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_runner():
    spec = importlib.util.spec_from_file_location("p7_public_nonretrieval_v1", RUNNER)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError("runner loader unavailable")
    spec.loader.exec_module(module)
    return module


def validate_result(
    result_path: Path = RESULT,
    root: Path = ROOT,
    seal_path: Path = SEAL,
) -> dict[str, Any]:
    if file_digest(result_path) != EXPECTED_RESULT_FILE_SHA256:
        raise ValueError("result file SHA-256 drift")
    result = json.loads(result_path.read_text())
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    runner.validate_protocol(protocol, root)

    if set(result) != EXPECTED_RESULT_KEYS:
        raise ValueError("result top-level key set drift")
    seal = json.loads(seal_path.read_text())
    runner.assert_exact(seal, EXPECTED_SEAL, "seal")

    receipt = result.get("receipt_sha256")
    without_receipt = dict(result)
    without_receipt.pop("receipt_sha256", None)
    if receipt != runner.digest(runner.canonical(without_receipt)):
        raise ValueError("result receipt drift")
    if result.get("schema") != runner.RESULT_SCHEMA:
        raise ValueError("result schema drift")
    if result.get("protocol_file_sha256") != file_digest(PROTOCOL):
        raise ValueError("protocol file binding drift")
    if result.get("protocol_sha256") != runner.digest(runner.canonical(protocol)):
        raise ValueError("protocol semantic binding drift")
    if result.get("runner_sha256") != file_digest(RUNNER):
        raise ValueError("runner binding drift")
    expected_blobs = {
        runner.PROTOCOL_PATH: file_digest(PROTOCOL),
        runner.RUNNER_PATH: file_digest(RUNNER),
    }
    if result.get("source_branch") != "main" or result.get("source_commit") != EXPECTED_SOURCE_COMMIT:
        raise ValueError("clean-main execution source drift")
    if result.get("committed_blob_equality") != expected_blobs:
        raise ValueError("committed byte-equality receipt drift")
    for relative, expected_digest in expected_blobs.items():
        try:
            committed = subprocess.check_output(
                ["git", "show", f"{result['source_commit']}:{relative}"],
                cwd=root,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as error:
            raise ValueError(f"historical source path unavailable: {relative}") from error
        if runner.digest(committed) != expected_digest or committed != (root / relative).read_bytes():
            raise ValueError(f"historical committed byte equality failed: {relative}")
    runner.assert_exact(
        result.get("observed_environment"),
        {"dependencies": "stdlib_only", "python": "3.12.13", "python_implementation": "CPython"},
        "result.observed_environment",
    )

    expected_rows = [
        row
        for dataset in protocol["datasets"]
        for row in runner.transition_rows(dataset)
    ]
    runner.assert_exact(result.get("transition_rows"), expected_rows, "result.transition_rows")
    expected_domains = []
    for dataset in protocol["datasets"]:
        rows = runner.transition_rows(dataset)
        systems = (protocol["primary_system"], *protocol["comparators"])
        expected_domains.append({
            "dataset_id": dataset["id"],
            "domain": dataset["domain"],
            "class_count": dataset["class_count"],
            "partition_count": runner.PARTITION_COUNT,
            "unique_directed_transition_count": len(rows),
            "metrics": {system: runner.metrics(rows, system) for system in systems},
            "mutation_audit": runner.mutation_audit(rows),
        })
    runner.assert_exact(result.get("domains"), expected_domains, "result.domains")
    if type(result.get("domain_count")) is not int or result["domain_count"] != 2:
        raise TypeError("domain count drift")
    if type(result.get("unique_directed_transition_count")) is not int or result["unique_directed_transition_count"] != 100:
        raise TypeError("transition count drift")

    required = {
        "inference_unit": "dataset_domain",
        "structural_family_count": 1,
        "constructed_transition_boundary": "prospective class-partition constructions; not observed upstream ontology changes",
        "upstream_rows_downloaded_or_redistributed": False,
        "conformance_boundary": "gold and system instantiate the same predicate; accuracy is not independent construct validation",
        "issue_box_candidate": "P7_USE_GE_2_NONRETRIEVAL_DOMAINS_AND_GE_50_TRANSITIONS_PER_DOMAIN",
        "data_coverage_gate": "MET",
        "strongest_donor_result": "EXTENSIONALLY_EQUIVALENT",
        "scientific_superiority_gate": "NOT_MET",
        "independent_adjudication": "CANNOT_CHECK",
        "population_inference": False,
        "scientific_authority_delta": "P7_DATA_COVERAGE_BOX_ONLY",
        "terminal": "P7_PUBLIC_NONRETRIEVAL_V1_DATA_COVERAGE_MET__STRONGEST_DONOR_EQUIVALENT",
    }
    for key, expected in required.items():
        runner.assert_exact(result.get(key), expected, f"result.{key}")
    if not all(
        domain["metrics"]["EXACT_CONTAINMENT"]["false_closure_retention"] == 0
        and domain["metrics"]["EXACT_CONTAINMENT"]["preserve_count"] == 25
        and domain["metrics"]["EXACT_CONTAINMENT"]["reopen_count"] == 25
        and domain["metrics"]["EXACT_CONTAINMENT"] == domain["metrics"]["PARTITION_REFINEMENT_ORACLE"]
        for domain in result["domains"]
    ):
        raise ValueError("decision balance, false closure, or donor equivalence drift")
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
