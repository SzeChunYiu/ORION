import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "development/p15-public-runtime-v1"
CHECKER = BASE / "check_p15_public_runtime_protocol_v1.py"
PROTOCOL = BASE / "P15_PUBLIC_RUNTIME_PROTOCOL_V1.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("p15_public_runtime_protocol_v1", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def rebind(checker, tmp_path, mutation):
    protocol = json.loads(PROTOCOL.read_text())
    mutation(protocol)
    hostile = tmp_path / "hostile.json"
    hostile.write_text(json.dumps(protocol, indent=2) + "\n")
    checker.EXPECTED_FILE_SHA256 = hashlib.sha256(hostile.read_bytes()).hexdigest()
    return hostile


def test_protocol_is_exact_no_results_freeze_with_thirty_plus_twenty_inputs():
    protocol = load_checker().validate(PROTOCOL)
    assert len(protocol["workloads"]) == 30
    assert len(protocol["failure_cases"]) == 20
    assert len(protocol["runtime_image_definitions"]) == 3
    assert protocol["execution_preflight"]["workloads_executed"] == 0
    assert protocol["execution_preflight"]["failure_cases_executed"] == 0
    assert protocol["authority"]["scientific_authority_delta"] == "NONE"
    assert protocol["authority"]["protected_custody"] == "CANNOT_CHECK"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda p: p.__setitem__("results_exist", True),
        lambda p: p.__setitem__("outcome_accessed", True),
        lambda p: p["workloads"].pop(),
        lambda p: p["failure_cases"].pop(),
        lambda p: p["runtime_image_definitions"].pop(),
        lambda p: p["runtime_image_definitions"][0].__setitem__("oci_digest", "sha256:" + "0" * 64),
        lambda p: p["execution_preflight"].__setitem__("workloads_executed", 30),
        lambda p: p["execution_preflight"].__setitem__("built_oci_image_count", True),
        lambda p: p["authority"].__setitem__("scientific_authority_delta", "SUPPORTED"),
        lambda p: p["authority"].__setitem__("protected_custody", "PASS"),
        lambda p: p["authority"].__setitem__("closes_issue_box", True),
        lambda p: p["workloads"][20].__setitem__("id", 3),
        lambda p: p["failure_source"].__setitem__("upstream_project_terms", "MIT"),
        lambda p: p.__setitem__("result", {}),
        lambda p: p.__setitem__("frozen_utc", True),
        lambda p: p["workload_sources"][0].__setitem__("url", "https://example.invalid"),
        lambda p: p["workload_sources"][0].__setitem__("manifest_sha256", "0" * 64),
        lambda p: p["workload_sources"][0].__setitem__("upstream_capsule_terms", "MIT"),
        lambda p: p["workload_sources"][1].__setitem__("third_party_paper_asset_terms", "MIT"),
        lambda p: p["workloads"][10].__setitem__("config_sha256", "0" * 64),
        lambda p: p["workloads"][20].__setitem__("evaluator", "fabricated.py"),
        lambda p: p["workloads"][0].__setitem__("domain", "fabricated"),
        lambda p: p["failure_source"].__setitem__("license_sha256", "0" * 64),
        lambda p: p["failure_cases"][0].__setitem__("id", "Chart-999"),
        lambda p: p["failure_cases"][0].__setitem__("buggy", True),
        lambda p: p["failure_cases"][0].__setitem__("fixed", "fabricated"),
        lambda p: p["runtime_image_definitions"][0].__setitem__("id", "fake"),
        lambda p: p["runtime_image_definitions"][0].__setitem__("source_path", "fake"),
        lambda p: p["runtime_image_definitions"][0].__setitem__("status", "EXECUTED_NOT_FAILED"),
        lambda p: p["gate"].__setitem__("public_workloads", True),
        lambda p: p["gate"].__setitem__("overhead_max", 0.5),
        lambda p: p.__setitem__("non_bypass_boundaries", ["PASS"] * 5),
    ],
)
def test_rebound_semantic_mutations_fail_closed(tmp_path, mutation):
    checker = load_checker()
    hostile = rebind(checker, tmp_path, mutation)
    with pytest.raises((TypeError, ValueError)):
        checker.validate(hostile)


def test_duplicate_authority_key_fails_closed(tmp_path):
    checker = load_checker()
    raw = PROTOCOL.read_text().replace(
        '    "scientific_authority_delta": "NONE",',
        '    "scientific_authority_delta": "SUPPORTED",\n    "scientific_authority_delta": "NONE",',
        1,
    )
    hostile = tmp_path / "duplicate.json"
    hostile.write_text(raw)
    checker.EXPECTED_FILE_SHA256 = hashlib.sha256(hostile.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="duplicate JSON key"):
        checker.validate(hostile)
