import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "development/p7-public-nonretrieval-v1"
PROTOCOL = BASE / "P7_PUBLIC_NONRETRIEVAL_PROTOCOL_V1.json"
RUNNER = BASE / "run_p7_public_nonretrieval_v1.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("p7_public_nonretrieval_v1", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_protocol_freezes_two_rights_valid_domains_without_results():
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    runner.validate_protocol(protocol, ROOT)
    assert [row["class_count"] for row in protocol["datasets"]] == [7, 26]
    assert all(row["data_license"] == "CC-BY-4.0" for row in protocol["datasets"])
    assert protocol["runtime"] == {"python": "3.12", "dependencies": "stdlib_only"}
    assert protocol["authority"]["scientific_authority_delta"] == "NONE"
    assert protocol["results_exist"] is False


@pytest.mark.parametrize(
    "mutation",
    [
        lambda p: p.__setitem__("status", "EXECUTED"),
        lambda p: p.__setitem__("outcome_accessed", True),
        lambda p: p.__setitem__("exact_rule", "PRESERVE"),
        lambda p: p["dataset_contract"].__setitem__("gold", "self report"),
        lambda p: p["datasets"][0].__setitem__("data_license", "UNKNOWN"),
        lambda p: p["datasets"][1].__setitem__("class_count", 26.0),
        lambda p: p["estimand"].__setitem__("minimum_unique_directed_transitions_per_domain", 50.0),
        lambda p: p["estimand"].__setitem__("inference_unit", "transition_row"),
        lambda p: p["data_coverage_gate"].__setitem__("all_mutations_killed", False),
        lambda p: p["scientific_superiority_gate"].__setitem__("strongest_donor", "NO_BRIDGE_REOPEN_CONTROL"),
        lambda p: p["retention"].__setitem__("null_harmful_and_failed_rows", False),
        lambda p: p["authority"].__setitem__("closes_issue_box", True),
        lambda p: p["authority"].__setitem__("independent_adjudication", "PASS"),
        lambda p: p["runner"].__setitem__("sha256", "0" * 64),
    ],
)
def test_protocol_mutations_fail_closed(mutation):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    mutation(protocol)
    with pytest.raises((TypeError, ValueError)):
        runner.validate_protocol(protocol, ROOT)


def test_partitions_are_distinct_constructs_not_index_renamings():
    runner = load_runner()
    for dataset in runner.dataset_rows():
        partitions = runner.canonical_partitions(dataset["class_labels"])
        assert len(partitions) == 25
        assert len({runner.digest(runner.canonical(row)) for row in partitions}) == 25
        rows = runner.transition_rows(dataset)
        identities = {
            (row["source_partition_sha256"], row["target_partition_sha256"], row["direction"])
            for row in rows
        }
        assert len(rows) == len(identities) == 50
        assert all("sample_index" not in row for row in rows)


def test_both_directions_are_exercised_and_oracle_equivalence_is_retained():
    runner = load_runner()
    rows = runner.transition_rows(runner.dataset_rows()[0])
    assert {row["EXACT_CONTAINMENT"] for row in rows} == {"PRESERVE", "REOPEN"}
    exact = runner.metrics(rows, "EXACT_CONTAINMENT")
    assert exact["conformance_accuracy"] == 1.0
    assert exact["false_closure_retention"] == 0
    assert runner.metrics(rows, "PARTITION_REFINEMENT_ORACLE") == exact
    assert runner.metrics(rows, "NO_BRIDGE_REOPEN_CONTROL")["unnecessary_reopen"] > 0
    assert runner.metrics(rows, "ALWAYS_PRESERVE")["false_closure_retention"] > 0


def test_all_registered_mutations_are_killed():
    runner = load_runner()
    rows = runner.transition_rows(runner.dataset_rows()[0])
    assert runner.mutation_audit(rows) == {
        "mutations": {
            "REVERSE_CONTAINMENT_DIRECTION": True,
            "ALWAYS_TRUE_CONTAINMENT": True,
            "ALWAYS_FALSE_CONTAINMENT": True,
        },
        "killed": 3,
        "total": 3,
    }


def test_transition_rows_are_deterministic_and_retain_no_upstream_rows():
    runner = load_runner()
    dataset = runner.dataset_rows()[1]
    first = runner.transition_rows(dataset)
    second = runner.transition_rows(deepcopy(dataset))
    assert first == second
    assert all("features" not in row and "raw_label_array" not in row for row in first)
