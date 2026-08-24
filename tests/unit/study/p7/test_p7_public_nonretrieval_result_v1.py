import importlib.util
import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "development/p7-public-nonretrieval-v1"
CHECKER = BASE / "check_p7_public_nonretrieval_result_v1.py"
RESULT = BASE / "P7_PUBLIC_NONRETRIEVAL_RESULT_V1.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("p7_public_nonretrieval_result_v1", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_result_passes_exact_validator_and_retains_adverse_donor_result():
    checker = load_checker()
    result = checker.validate_result(RESULT, ROOT)
    assert result["data_coverage_gate"] == "MET"
    assert result["strongest_donor_result"] == "EXTENSIONALLY_EQUIVALENT"
    assert result["scientific_superiority_gate"] == "NOT_MET"
    assert result["independent_adjudication"] == "CANNOT_CHECK"
    assert result["scientific_authority_delta"] == "P7_DATA_COVERAGE_BOX_ONLY"
    assert checker.EXPECTED_SEAL["authority"]["protected_custody"] == "CANNOT_CHECK"


def test_result_is_bound_to_exact_clean_main_execution_and_bytes():
    checker = load_checker()
    result = checker.validate_result(RESULT, ROOT)
    assert checker.file_digest(RESULT) == checker.EXPECTED_RESULT_FILE_SHA256
    assert result["source_branch"] == "main"
    assert result["source_commit"] == checker.EXPECTED_SOURCE_COMMIT
    assert result["committed_blob_equality"]


def test_every_domain_has_fifty_unique_balanced_contracts_and_zero_false_closure():
    checker = load_checker()
    result = checker.validate_result(RESULT, ROOT)
    assert result["domain_count"] == 2
    assert result["unique_directed_transition_count"] == 100
    for domain in result["domains"]:
        exact = domain["metrics"]["EXACT_CONTAINMENT"]
        assert domain["unique_directed_transition_count"] == 50
        assert exact["preserve_count"] == exact["reopen_count"] == 25
        assert exact["false_closure_retention"] == 0
        assert exact == domain["metrics"]["PARTITION_REFINEMENT_ORACLE"]


def rebind_hostile(checker, tmp_path, mutation):
    result = json.loads(RESULT.read_text())
    mutation(result)
    without_receipt = dict(result)
    without_receipt.pop("receipt_sha256", None)
    runner = checker.load_runner()
    result["receipt_sha256"] = runner.digest(runner.canonical(without_receipt))
    hostile = tmp_path / "hostile.json"
    hostile.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    checker.EXPECTED_RESULT_FILE_SHA256 = hashlib.sha256(hostile.read_bytes()).hexdigest()
    return hostile


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r.__setitem__("scientific_superiority_gate", "MET"),
        lambda r: r.__setitem__("independent_adjudication", "PASS"),
        lambda r: r.__setitem__("population_inference", True),
        lambda r: r.__setitem__("unique_directed_transition_count", 100.0),
        lambda r: r.__setitem__("protected_custody", "PASS"),
        lambda r: r.__setitem__("issue_box_closed_beyond_coverage", True),
        lambda r: r.__setitem__("observed_environment", {"python": "networked", "python_implementation": "fake", "dependencies": "unknown"}),
        lambda r: r["transition_rows"][0].__setitem__("partition_ordinal", True),
        lambda r: r["transition_rows"][0].__setitem__("source_obligation_count", 21.0),
        lambda r: r["domains"][0].__setitem__("partition_count", 25.0),
        lambda r: r["domains"][0]["metrics"]["EXACT_CONTAINMENT"].__setitem__("false_closure_retention", False),
    ],
)
def test_semantically_rebound_mutations_fail_closed(tmp_path, mutation):
    checker = load_checker()
    hostile = rebind_hostile(checker, tmp_path, mutation)
    with pytest.raises((TypeError, ValueError)):
        checker.validate_result(hostile, ROOT)


def test_rebound_parent_commit_without_source_paths_fails_historical_git_check(tmp_path):
    checker = load_checker()
    parent_without_p7 = "5d3005a54dd916bbdaea178b1c7198e53b5e7bd7"
    hostile = rebind_hostile(
        checker,
        tmp_path,
        lambda result: result.__setitem__("source_commit", parent_without_p7),
    )
    checker.EXPECTED_SOURCE_COMMIT = parent_without_p7
    with pytest.raises(ValueError, match="historical source path unavailable"):
        checker.validate_result(hostile, ROOT)


def test_authority_seal_mutations_fail_closed(tmp_path):
    checker = load_checker()
    seal = json.loads(checker.SEAL.read_text())
    seal["authority"]["protected_custody"] = "PASS"
    hostile_seal = tmp_path / "hostile-seal.json"
    hostile_seal.write_text(json.dumps(seal, indent=2) + "\n")
    with pytest.raises(ValueError):
        checker.validate_result(RESULT, ROOT, hostile_seal)
