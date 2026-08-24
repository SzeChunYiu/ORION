#!/usr/bin/env python3
"""Execute the frozen P7 class-partition conformance study."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "development/p7-public-nonretrieval-v1"
PROTOCOL_PATH = "development/p7-public-nonretrieval-v1/P7_PUBLIC_NONRETRIEVAL_PROTOCOL_V1.json"
RUNNER_PATH = "development/p7-public-nonretrieval-v1/run_p7_public_nonretrieval_v1.py"
RESULT_SCHEMA = "ORION.P7.PublicNonretrievalResult.v1"
PARTITION_COUNT = 25


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def dataset_rows() -> list[dict[str, Any]]:
    return [
        {
            "id": "uci_zoo_class_ontology",
            "domain": "animal_taxonomy",
            "class_labels": ["1", "2", "3", "4", "5", "6", "7"],
            "class_count": 7,
            "class_labels_sha256": "3b771ad062cb1aa864f86075e4d2534b2f5a027932a3159b0376c1c3a0456d6c",
            "source_url": "https://archive.ics.uci.edu/dataset/111/zoo",
            "license_evidence_url": "https://archive.ics.uci.edu/dataset/111/zoo",
            "license_verified_utc": "2026-08-24T14:33:56Z",
            "source_doi": "10.24432/C5R59V",
            "data_license": "CC-BY-4.0",
            "upstream_rows_downloaded": False,
            "upstream_rows_redistributed": False,
        },
        {
            "id": "uci_letter_recognition_class_ontology",
            "domain": "character_recognition",
            "class_labels": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            "class_count": 26,
            "class_labels_sha256": "1988ff86892c1a3f51ad2568e2136d764f867999951006113a2d74ce96015f05",
            "source_url": "https://archive.ics.uci.edu/dataset/59/letter+recognition",
            "license_evidence_url": "https://archive.ics.uci.edu/dataset/59/letter+recognition",
            "license_verified_utc": "2026-08-24T14:33:56Z",
            "source_doi": "10.24432/C5ZP40",
            "data_license": "CC-BY-4.0",
            "upstream_rows_downloaded": False,
            "upstream_rows_redistributed": False,
        },
    ]


def expected_protocol(root: Path = ROOT) -> dict[str, Any]:
    return {
        "schema": "ORION.P7.PublicNonretrievalProtocol.v1",
        "status": "FROZEN_NO_RESULTS",
        "frozen_utc": "2026-08-24T14:33:56Z",
        "issue": 1086,
        "paper": "P7_COMPONENT_OF_P6_P8_UNIFIED_CALCULUS",
        "outcome_accessed": False,
        "results_exist": False,
        "primary_system": "EXACT_CONTAINMENT",
        "comparators": ["PARTITION_REFINEMENT_ORACLE", "NO_BRIDGE_REOPEN_CONTROL", "ALWAYS_PRESERVE"],
        "exact_rule": "PRESERVE iff every target separation obligation is present in the source contract; otherwise REOPEN",
        "dataset_contract": {
            "public_material_used": "class-vocabulary metadata only; no observations or features",
            "fine_partition": "one singleton block per public class label",
            "coarse_partitions": "first 25 canonical nontrivial bipartitions with the first label fixed in block A",
            "obligation": "an unordered class-label pair in different partition blocks",
            "directions": ["FINE_TO_COARSE", "COARSE_TO_FINE"],
            "gold": "objective set inclusion over the frozen source and target separation obligations",
            "gold_independence_boundary": "gold and implementation instantiate the same mathematical predicate; accuracy is conformance, not external construct validation",
        },
        "datasets": dataset_rows(),
        "runtime": {"python": "3.12", "dependencies": "stdlib_only"},
        "estimand": {
            "inference_unit": "dataset_domain",
            "minimum_domain_count": 2,
            "partition_count_per_domain": 25,
            "minimum_unique_directed_transitions_per_domain": 50,
            "transition_identity": "source partition, target partition, and direction; never an observation index",
            "row_counts_are_not_independent_replications": True,
            "structural_family_count": 1,
            "population_inference": False,
        },
        "data_coverage_gate": {
            "minimum_domain_count": 2,
            "minimum_unique_directed_transitions_per_domain": 50,
            "every_transition_contract_unique_within_domain": True,
            "exact_false_closure_retention": 0,
            "preserve_and_reopen_in_every_domain": True,
            "all_mutations_killed": True,
        },
        "scientific_superiority_gate": {
            "strongest_donor": "PARTITION_REFINEMENT_ORACLE",
            "required": "EXACT_CONTAINMENT must have fewer unnecessary reopenings than the strongest donor in every domain",
            "pre_execution_relation": "The donor computes the same frozen set-inclusion predicate, so equivalence rather than superiority is expected and must be retained.",
        },
        "retention": {
            "every_partition_and_directed_transition": True,
            "null_harmful_and_failed_rows": True,
            "raw_features_labels_or_observations": False,
            "public_class_vocabulary_metadata": True,
        },
        "runner": {"path": RUNNER_PATH, "sha256": digest((root / RUNNER_PATH).read_bytes())},
        "authority": {
            "closes_issue_box": False,
            "scientific_authority_delta": "NONE",
            "independent_adjudication": "CANNOT_CHECK",
            "population_inference": False,
            "family_boundary": "Zoo and Letter Recognition are two public subject domains but one constructed classification-partition structural family; they do not establish cross-family generality or independent replication.",
        },
        "non_bypass_boundaries": [
            "The transitions are deterministic prospective constructions over public class vocabularies, not observed upstream ontology changes.",
            "Public metadata does not create independent adjudication, protected custody, or outcome confirmation.",
            "Fifty directed transitions per domain do not create fifty independent inference units.",
            "The partition-refinement oracle is extensionally equivalent under equal information; no novelty or superiority over partition lattices is claimed.",
            "The protocol closes no issue box; a later unchanged clean-main execution and review are required.",
        ],
    }


def assert_exact(observed: Any, expected: Any, path: str = "protocol") -> None:
    if type(observed) is not type(expected):
        raise TypeError(f"{path}: exact type drift")
    if isinstance(expected, dict):
        if observed.keys() != expected.keys():
            raise ValueError(f"{path}: key/order drift")
        for key in expected:
            assert_exact(observed[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if len(observed) != len(expected):
            raise ValueError(f"{path}: list-length drift")
        for index, (left, right) in enumerate(zip(observed, expected)):
            assert_exact(left, right, f"{path}[{index}]")
    elif observed != expected:
        raise ValueError(f"{path}: value drift")


def validate_protocol(protocol: Mapping[str, Any], root: Path = ROOT) -> None:
    if not isinstance(protocol, dict):
        raise TypeError("protocol must be a dictionary")
    assert_exact(protocol, expected_protocol(root))
    for row in protocol["datasets"]:
        if digest(canonical(row["class_labels"])) != row["class_labels_sha256"]:
            raise ValueError("class-vocabulary digest drift")
        if len(row["class_labels"]) != row["class_count"]:
            raise ValueError("class-vocabulary count drift")
        if len(canonical_partitions(row["class_labels"], PARTITION_COUNT)) != PARTITION_COUNT:
            raise ValueError("insufficient unique canonical partitions")


def validate_execution_source(root: Path = ROOT) -> dict[str, Any]:
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=root).strip():
        raise ValueError("execution requires a clean working tree")
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip()
    if branch != "main":
        raise ValueError("execution requires branch main")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    committed: dict[str, str] = {}
    for relative in (PROTOCOL_PATH, RUNNER_PATH):
        raw = subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=root)
        current = (root / relative).read_bytes()
        if raw != current:
            raise ValueError(f"committed byte equality failed: {relative}")
        committed[relative] = digest(raw)
    return {"source_branch": branch, "source_commit": commit, "committed_blob_equality": committed}


def canonical_partitions(labels: Sequence[str], count: int = PARTITION_COUNT) -> list[list[list[str]]]:
    if type(count) is not int or count < 1:
        raise TypeError("partition count must be a positive exact integer")
    ordered = list(labels)
    if len(ordered) != len(set(ordered)) or len(ordered) < 2:
        raise ValueError("labels must be unique and contain at least two values")
    partitions: list[list[list[str]]] = []
    for mask in range(1, 1 << len(ordered)):
        if not (mask & 1):
            continue
        left = [label for index, label in enumerate(ordered) if mask & (1 << index)]
        right = [label for index, label in enumerate(ordered) if not mask & (1 << index)]
        if right:
            partitions.append([left, right])
        if len(partitions) == count:
            return partitions
    raise ValueError("requested more unique canonical bipartitions than available")


def fine_partition(labels: Sequence[str]) -> list[list[str]]:
    return [[label] for label in labels]


def obligations(partition: Sequence[Sequence[str]]) -> tuple[str, ...]:
    membership: dict[str, int] = {}
    for block_index, block in enumerate(partition):
        if not block:
            raise ValueError("partition blocks must be nonempty")
        for label in block:
            if label in membership:
                raise ValueError("partition labels must occur once")
            membership[label] = block_index
    return tuple(
        f"{left}|{right}"
        for left, right in itertools.combinations(sorted(membership), 2)
        if membership[left] != membership[right]
    )


def contract_digest(values: Sequence[str]) -> str:
    return digest(canonical(list(values)))


def transition_rows(dataset: Mapping[str, Any]) -> list[dict[str, Any]]:
    labels = dataset["class_labels"]
    fine = fine_partition(labels)
    fine_obligations = obligations(fine)
    rows: list[dict[str, Any]] = []
    for ordinal, coarse in enumerate(canonical_partitions(labels), start=1):
        coarse_obligations = obligations(coarse)
        partition_hash = digest(canonical(coarse))
        for direction, source_partition, target_partition, source, target in (
            ("FINE_TO_COARSE", fine, coarse, fine_obligations, coarse_obligations),
            ("COARSE_TO_FINE", coarse, fine, coarse_obligations, fine_obligations),
        ):
            source_set = set(source)
            target_set = set(target)
            contains = target_set <= source_set
            decision = "PRESERVE" if contains else "REOPEN"
            rows.append(
                {
                    "transition_id": f"{dataset['id']}:partition-{ordinal:02d}:{direction.lower()}",
                    "partition_ordinal": ordinal,
                    "direction": direction,
                    "coarse_partition": coarse,
                    "coarse_partition_sha256": partition_hash,
                    "source_partition_sha256": digest(canonical(source_partition)),
                    "target_partition_sha256": digest(canonical(target_partition)),
                    "source_obligation_count": len(source),
                    "source_obligation_sha256": contract_digest(source),
                    "target_obligation_count": len(target),
                    "target_obligation_sha256": contract_digest(target),
                    "containment_violation_count": len(target_set - source_set),
                    "gold_provenance": "OBJECTIVE_PARTITION_SET_INCLUSION",
                    "gold": decision,
                    "EXACT_CONTAINMENT": decision,
                    "PARTITION_REFINEMENT_ORACLE": decision,
                    "NO_BRIDGE_REOPEN_CONTROL": "REOPEN",
                    "ALWAYS_PRESERVE": "PRESERVE",
                }
            )
    identities = {(row["source_partition_sha256"], row["target_partition_sha256"], row["direction"]) for row in rows}
    if len(rows) != 2 * PARTITION_COUNT or len(identities) != len(rows):
        raise ValueError("directed transition identity collision")
    return rows


def metrics(rows: Sequence[Mapping[str, Any]], system: str) -> dict[str, Any]:
    correct = sum(row[system] == row["gold"] for row in rows)
    return {
        "conformance_accuracy": correct / len(rows),
        "correct": correct,
        "false_closure_retention": sum(row[system] == "PRESERVE" and row["gold"] == "REOPEN" for row in rows),
        "unnecessary_reopen": sum(row[system] == "REOPEN" and row["gold"] == "PRESERVE" for row in rows),
        "preserve_count": sum(row[system] == "PRESERVE" for row in rows),
        "reopen_count": sum(row[system] == "REOPEN" for row in rows),
    }


def mutation_audit(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    systems = {
        "REVERSE_CONTAINMENT_DIRECTION": [{**row, "MUTANT": "REOPEN" if row["EXACT_CONTAINMENT"] == "PRESERVE" else "PRESERVE"} for row in rows],
        "ALWAYS_TRUE_CONTAINMENT": [{**row, "MUTANT": "PRESERVE"} for row in rows],
        "ALWAYS_FALSE_CONTAINMENT": [{**row, "MUTANT": "REOPEN"} for row in rows],
    }
    killed = {name: metrics(mutant, "MUTANT")["conformance_accuracy"] < 1.0 for name, mutant in systems.items()}
    return {"mutations": killed, "killed": sum(killed.values()), "total": len(killed)}


def execute(protocol: Mapping[str, Any], root: Path = ROOT) -> dict[str, Any]:
    validate_protocol(protocol, root)
    source = validate_execution_source(root)
    if f"{sys.version_info.major}.{sys.version_info.minor}" != protocol["runtime"]["python"]:
        raise ValueError("observed Python runtime differs from freeze")
    domains: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []
    for dataset in protocol["datasets"]:
        rows = transition_rows(dataset)
        systems = (protocol["primary_system"], *protocol["comparators"])
        domains.append({
            "dataset_id": dataset["id"],
            "domain": dataset["domain"],
            "class_count": dataset["class_count"],
            "partition_count": PARTITION_COUNT,
            "unique_directed_transition_count": len(rows),
            "metrics": {system: metrics(rows, system) for system in systems},
            "mutation_audit": mutation_audit(rows),
        })
        all_rows.extend(rows)
    minimum = protocol["estimand"]["minimum_unique_directed_transitions_per_domain"]
    coverage_met = len(domains) >= protocol["estimand"]["minimum_domain_count"] and all(
        domain["unique_directed_transition_count"] >= minimum
        and domain["metrics"]["EXACT_CONTAINMENT"]["false_closure_retention"] == 0
        and domain["metrics"]["EXACT_CONTAINMENT"]["preserve_count"] > 0
        and domain["metrics"]["EXACT_CONTAINMENT"]["reopen_count"] > 0
        and domain["mutation_audit"]["killed"] == domain["mutation_audit"]["total"]
        for domain in domains
    )
    strongest_donor_equivalent = all(domain["metrics"]["EXACT_CONTAINMENT"] == domain["metrics"]["PARTITION_REFINEMENT_ORACLE"] for domain in domains)
    superiority_met = coverage_met and all(
        domain["metrics"]["EXACT_CONTAINMENT"]["unnecessary_reopen"]
        < domain["metrics"]["PARTITION_REFINEMENT_ORACLE"]["unnecessary_reopen"]
        for domain in domains
    )
    result = {
        "schema": RESULT_SCHEMA,
        "protocol_file_sha256": digest((root / PROTOCOL_PATH).read_bytes()),
        "protocol_sha256": digest(canonical(protocol)),
        "runner_sha256": digest((root / RUNNER_PATH).read_bytes()),
        **source,
        "observed_environment": {"python": platform.python_version(), "python_implementation": platform.python_implementation(), "dependencies": "stdlib_only"},
        "domain_count": len(domains),
        "unique_directed_transition_count": len(all_rows),
        "domains": domains,
        "transition_rows": all_rows,
        "inference_unit": "dataset_domain",
        "structural_family_count": 1,
        "constructed_transition_boundary": "prospective class-partition constructions; not observed upstream ontology changes",
        "upstream_rows_downloaded_or_redistributed": False,
        "conformance_boundary": "gold and system instantiate the same predicate; accuracy is not independent construct validation",
        "issue_box_candidate": "P7_USE_GE_2_NONRETRIEVAL_DOMAINS_AND_GE_50_TRANSITIONS_PER_DOMAIN",
        "data_coverage_gate": "MET" if coverage_met else "NOT_MET",
        "strongest_donor_result": "EXTENSIONALLY_EQUIVALENT" if strongest_donor_equivalent else "DIFFERENT",
        "scientific_superiority_gate": "MET" if superiority_met else "NOT_MET",
        "independent_adjudication": "CANNOT_CHECK",
        "population_inference": False,
        "scientific_authority_delta": "P7_DATA_COVERAGE_BOX_ONLY" if coverage_met else "NONE",
        "terminal": (
            "P7_PUBLIC_NONRETRIEVAL_V1_DATA_COVERAGE_MET__STRONGEST_DONOR_EQUIVALENT"
            if coverage_met and strongest_donor_equivalent and not superiority_met
            else "P7_PUBLIC_NONRETRIEVAL_V1_GATE_NOT_MET"
        ),
    }
    result["receipt_sha256"] = digest(canonical(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("refusing to overwrite an existing result")
    protocol = json.loads(args.protocol.read_text())
    result = execute(protocol)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["terminal"])
    return 0 if "DATA_COVERAGE_MET" in result["terminal"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
