import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "development/p6-public-selective-revalidation-v1"
CHECKER = BASE / "check_p6_public_selective_revalidation_result_v1.py"
RESULT = BASE / "P6_PUBLIC_SELECTIVE_REVALIDATION_RESULT_V1.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("p6_public_selective_result_v1", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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


def test_result_passes_and_retains_equivalent_donor_and_authority_boundary():
    checker = load_checker()
    result = checker.validate_result(RESULT, ROOT)
    assert result["domain_count"] == 3
    assert result["change_set_count"] == 300
    assert result["strongest_donor_result"] == "EXTENSIONALLY_EQUIVALENT"
    assert result["scientific_superiority_gate"] == "NOT_MET"
    assert result["simultaneous_95pct_inferential_gate"] == "CANNOT_CHECK"
    assert result["historical_native_build_test_replay"] == "CANNOT_CHECK"
    assert result["independent_adjudication"] == result["protected_custody"] == "CANNOT_CHECK"
    assert result["scientific_authority_delta"] == "P6_DATA_AND_COMPARATOR_EXECUTION_ONLY"


def test_all_three_domains_retain_one_hundred_change_sets_and_unresolved_imports():
    result = load_checker().validate_result(RESULT, ROOT)
    assert [len(domain["rows"]) for domain in result["domains"]] == [100, 100, 100]
    assert sum(domain["import_resolution_audit"]["unresolved_import_count"] for domain in result["domains"]) == 188
    assert all(domain["selective_native_exact_agreement"] for domain in result["domains"])


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r.__setitem__("scientific_superiority_gate", "MET"),
        lambda r: r.__setitem__("protected_custody", "PASS"),
        lambda r: r.__setitem__("independent_adjudication", "PASS"),
        lambda r: r.__setitem__("population_inference", True),
        lambda r: r.__setitem__("change_set_count", 300.0),
        lambda r: r.__setitem__("extra_authority", True),
        lambda r: r["domains"][0].__setitem__("artifact_count", True),
        lambda r: r["domains"][0].__setitem__("mean_savings_vs_full_reset", 1),
        lambda r: r["domains"][0]["rows"][0].__setitem__("native_selected_count", False),
        lambda r: r["domains"][0]["rows"][0].__setitem__("savings_vs_full_reset", 1),
        lambda r: r["domains"][0]["rows"][0]["mutation_disagreements"].__setitem__("OMITTED_READ", 1),
        lambda r: r["domains"][0]["acquisition"].__setitem__("observed_materialized_head", "0" * 40),
        lambda r: r["domains"][1]["import_resolution_audit"].__setitem__("unresolved_import_count", 140),
        lambda r: r["domains"][0].__setitem__("artifact_universe_sha256", "0" * 64),
        lambda r: r["domains"][0].__setitem__("dependency_edges_sha256", "0" * 64),
        lambda r: r["domains"][0]["rows"][0].__setitem__("commit", "0" * 40),
        lambda r: r["domains"][0]["rows"][0].__setitem__("parent", "1" * 40),
        lambda r: r["domains"][0]["rows"][0].__setitem__("changed_paths", ["fabricated.nf"]),
        lambda r: r["domains"][0]["rows"][0].__setitem__("native_selected_sha256", "2" * 64),
        lambda r: r["domains"][1]["acquisition"].__setitem__("remote_branch_moved_during_acquisition", False),
    ],
)
def test_semantically_rebound_mutations_fail_closed(tmp_path, mutation):
    checker = load_checker()
    hostile = rebind_hostile(checker, tmp_path, mutation)
    with pytest.raises((TypeError, ValueError)):
        checker.validate_result(hostile, ROOT)


def test_rebound_parent_with_different_protocol_fails_historical_source_check(tmp_path):
    checker = load_checker()
    parent_without_protocol = "bae81f6a1b5f9f395508deedf6034b97ee36135a"
    hostile = rebind_hostile(checker, tmp_path, lambda r: r.__setitem__("source_commit", parent_without_protocol))
    checker.EXPECTED_SOURCE_COMMIT = parent_without_protocol
    with pytest.raises(ValueError, match="historical (source path unavailable|committed byte equality failed)"):
        checker.validate_result(hostile, ROOT)


def test_rebound_row_tuple_swap_and_mutation_movement_fail_closed(tmp_path):
    def swap_rows(result):
        rows = result["domains"][0]["rows"]
        fields = (
            "native_selected_count", "native_selected_sha256", "selective_selected_count",
            "selective_selected_sha256", "savings_vs_full_reset",
        )
        for field in fields:
            rows[0][field], rows[1][field] = rows[1][field], rows[0][field]

    def move_mutation(result):
        rows = result["domains"][0]["rows"]
        name = "OMITTED_READ"
        killed = next(index for index, row in enumerate(rows) if row["mutation_disagreements"][name])
        survived = next(index for index, row in enumerate(rows) if not row["mutation_disagreements"][name])
        rows[killed]["mutation_disagreements"][name] = False
        rows[survived]["mutation_disagreements"][name] = True

    for mutation in (swap_rows, move_mutation):
        checker = load_checker()
        hostile = rebind_hostile(checker, tmp_path, mutation)
        with pytest.raises((TypeError, ValueError)):
            checker.validate_result(hostile, ROOT)


@pytest.mark.parametrize(
    "needle,replacement",
    [
        (
            '  "scientific_superiority_gate": "NOT_MET",',
            '  "scientific_superiority_gate": "MET",\n  "scientific_superiority_gate": "NOT_MET",',
        ),
        (
            '        "remote_branch_moved_during_acquisition": false,',
            '        "remote_branch_moved_during_acquisition": true,\n        "remote_branch_moved_during_acquisition": false,',
        ),
        (
            '          "native_selected_count":',
            '          "native_selected_count": 999,\n          "native_selected_count":',
        ),
    ],
)
def test_conflicting_duplicate_json_keys_fail_closed(tmp_path, needle, replacement):
    checker = load_checker()
    raw = RESULT.read_text()
    assert needle in raw
    hostile = tmp_path / "duplicate.json"
    hostile.write_text(raw.replace(needle, replacement, 1))
    checker.EXPECTED_RESULT_FILE_SHA256 = hashlib.sha256(hostile.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="duplicate JSON key"):
        checker.validate_result(hostile, ROOT)
