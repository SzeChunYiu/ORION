import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "development/p13-p14-public-lifecycle-v1"
PROTOCOL = BASE / "P13_P14_PUBLIC_LIFECYCLE_PROTOCOL_V1.json"
RUNNER = BASE / "run_p13_p14_public_lifecycle_v1.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("p13_p14_public_v1", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_protocol_freezes_30_repositories_and_license_hashes_without_orion():
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    runner.validate_manifest(protocol)
    assert protocol["status"] == "FROZEN_ACQUISITION_PILOT_AWAITING_EXECUTION"
    assert protocol["issue_1086_external_campaign_gate"] == "OPEN"
    assert protocol["repository_count"] == 30
    assert protocol["organization_count"] == 26
    assert len({row["repository"] for row in protocol["records"]}) == 30
    assert all(row["repository"].lower() != "szechunyiu/orion" for row in protocol["records"])
    assert all(len(row["license"]["sha256"]) == 64 for row in protocol["records"])
    assert all(row["license"]["full_text_redistributed"] is False for row in protocol["records"])
    assert protocol["boundaries"]["public_data_confers_independence"] is False
    assert protocol["boundaries"]["scientific_authority_delta"] == "NONE"
    assert protocol["boundaries"]["objective_gold_authority"].startswith("CANNOT_CHECK")
    assert protocol["boundaries"]["inferential_promotion_authority"] is False
    assert protocol["acquisition_requirement"]["live_git_required"] is True
    assert protocol["acquisition_requirement"]["manifest_only_gold_prohibited"] is True


def test_case_generation_is_complete_and_reference_gold_ignores_family_label():
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    refs = {row["repository"]: row for row in protocol["records"]}
    cases = runner.cases_for(protocol)
    assert len(cases) == 210
    assert {case["family"] for case in cases} == set(protocol["case_families"])
    assert sum(runner.reference_match(case, refs) for case in cases) == 30
    clean = next(case for case in cases if case["family"] == "CLEAN")
    relabelled = {**clean, "family": "FORGED_HEAD"}
    assert runner.reference_match(clean, refs) is True
    assert runner.reference_match(relabelled, refs) is True


def test_fail_closed_validator_rejects_orion_and_license_hash_loss():
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    protocol["records"][0]["repository"] = "SzeChunYiu/ORION"
    with pytest.raises(ValueError, match="ORION/duplicate"):
        runner.validate_manifest(protocol)
    protocol = json.loads(PROTOCOL.read_text())
    protocol["records"][0]["license"]["sha256"] = "CANNOT_CHECK"
    with pytest.raises(ValueError, match="license SHA-256"):
        runner.validate_manifest(protocol)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda p: p["records"][0].__setitem__("source_url", "https://github.com/SzeChunYiu/ORION"), "source_url"),
        (lambda p: p["records"][0].__setitem__("commit_url", "https://example.invalid/commit"), "commit_url"),
        (lambda p: p["records"][0]["license"].__setitem__("url", "https://example.invalid/license"), "license URL"),
        (lambda p: p["records"][0]["license"].__setitem__("declared_spdx", ""), "SPDX"),
        (lambda p: p["records"][0]["license"].__setitem__("path", "../LICENSE"), "license path"),
        (lambda p: p["records"][0]["license"].__setitem__("bytes", -1), "byte count"),
        (lambda p: p["records"][0]["license"].__setitem__("bytes", True), "byte count"),
        (lambda p: p["records"][0]["ancestry_probe"].__setitem__("ahead_by", True), "ahead count"),
        (lambda p: p["records"][0]["retrieval"].__setitem__("date", "9999-01-01"), "retrieval date"),
        (lambda p: p["records"][0]["retrieval"].__setitem__("operations", ["fetch_file"]), "operations"),
        (lambda p: p["runner"].__setitem__("sha256", "0" * 64), "runner bytes"),
        (lambda p: p.__setitem__("issue_1086_external_campaign_gate", "PASS"), "cannot close"),
        (lambda p: p.__setitem__("issue", 999), "issue identity"),
        (lambda p: p.__setitem__("issue", 1086.0), "issue identity"),
        (lambda p: p.__setitem__("repository_count", 30.0), "repository count"),
        (lambda p: p.__setitem__("organization_count", 26.0), "organization count"),
        (lambda p: p.__setitem__("inference_unit", "repository"), "inference authority"),
        (lambda p: p["acquisition_requirement"].__setitem__("live_git_required", False), "live Git"),
        (lambda p: p["acquisition_requirement"].__setitem__("result_creation_in_this_increment", "ALLOWED"), "result creation"),
        (lambda p: p["acquisition_requirement"].__setitem__("later_receipt_must_bind", []), "receipt bindings"),
        (lambda p: p["bootstrap"].__setitem__("authority", "AUTHORIZED_EXTERNAL_INFERENCE"), "bootstrap authority"),
        (lambda p: p["boundaries"].__setitem__("objective_gold_authority", "PASS"), "objective gold"),
        (lambda p: p["boundaries"].__setitem__("external_git_reverification", "PASS"), "reverification"),
        (lambda p: p["boundaries"].__setitem__("repository_bootstrap_inference", "AUTHORIZED"), "bootstrap inference"),
        (lambda p: p["boundaries"].__setitem__("issue_1086_gate_authority", True), "issue-gate authority"),
    ],
)
def test_manifest_relational_and_authority_tampering_fails_closed(mutate, message):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    mutate(protocol)
    with pytest.raises((TypeError, ValueError), match=message):
        runner.validate_manifest(protocol)


def test_zero_object_identities_fail_closed():
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    protocol["records"][0]["head_sha"] = "0" * 40
    protocol["records"][0]["commit_url"] = "https://github.com/psf/requests/commit/" + "0" * 40
    protocol["records"][0]["ancestry_probe"]["base_expression"] = "0" * 40 + "^"
    with pytest.raises(ValueError, match="zero Git"):
        runner.validate_manifest(protocol)
    protocol = json.loads(PROTOCOL.read_text())
    protocol["records"][0]["license"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="zero license"):
        runner.validate_manifest(protocol)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("head_sha", int("1" * 40), "head_sha"),
        ("parent_sha", int("2" * 40), "parent_sha"),
    ],
)
def test_git_commit_identities_require_exact_strings(field, value, message):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    protocol["records"][0][field] = value
    with pytest.raises(ValueError, match=message):
        runner.validate_manifest(protocol)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("git_blob_sha1", int("3" * 40), "blob identity"),
        ("sha256", int("4" * 64), "SHA-256"),
    ],
)
def test_license_identities_require_exact_strings(field, value, message):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    protocol["records"][0]["license"][field] = value
    with pytest.raises(ValueError, match=message):
        runner.validate_manifest(protocol)


def test_no_result_creation_interface_exists_in_acquisition_pilot():
    runner = load_runner()
    assert not hasattr(runner, "evaluate")
    assert not hasattr(runner, "RESULT_SCHEMA")


def test_hostile_cases_are_rejected_without_using_case_family():
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    refs = {row["repository"]: row for row in protocol["records"]}
    cases = runner.cases_for(protocol)
    for case in cases:
        accepted, checks = runner.lifecycle_selective(case, refs, protocol["freeze_epoch"])
        assert accepted is runner.reference_match(case, refs)
        assert 1 <= checks <= 6


def test_selective_cost_counts_only_predicates_actually_evaluated(monkeypatch):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    refs = {row["repository"]: row for row in protocol["records"]}
    forged = next(
        case for case in runner.cases_for(protocol) if case["family"] == "FORGED_HEAD"
    )

    def should_not_run(_value):
        raise RuntimeError("later timestamp predicate was evaluated")

    monkeypatch.setattr(runner, "parse_epoch", should_not_run)
    accepted, checks = runner.lifecycle_selective(forged, refs, protocol["freeze_epoch"])
    assert accepted is False
    assert checks == 2
    with pytest.raises(RuntimeError, match="later timestamp"):
        runner.always_full(forged, refs, protocol["freeze_epoch"])
