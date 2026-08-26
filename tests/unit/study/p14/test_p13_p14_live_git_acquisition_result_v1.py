import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "development/p13-p14-live-git-acquisition-v1"
CHECKER = BASE / "check_live_git_acquisition_result_v1.py"
RESULT = BASE / "LIVE_GIT_ACQUISITION_RESULT_V1.json"
CORPUS = ROOT / "papers/orion-23-responsibility-carrying-state/P13_P14_PINNED_REPOSITORY_CORPUS_V1.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("p13_p14_live_result_v1", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def documents():
    return json.loads(RESULT.read_text()), json.loads(CORPUS.read_text()), RESULT.read_bytes()


def test_immutable_adverse_receipt_passes_and_retains_every_row():
    checker = load_checker()
    result, corpus, raw = documents()
    summary = checker.validate(result, corpus, raw)
    assert summary == {
        "retained": 45,
        "objective_mismatch": 31,
        "excluded_license_cannot_check": 14,
        "verified": 0,
        "distinct_observed_license_hashes": 23,
    }


@pytest.mark.parametrize(
    "mutation, message",
    [
        (lambda r: r.__setitem__("terminal", "P13_P14_LIVE_GIT_ACQUISITION_MINIMUM_MET__CAMPAIGN_RESULT_NOT_CREATED"), "adverse terminal"),
        (lambda r: r.__setitem__("campaign_result_created", True), "campaign result"),
        (lambda r: r.__setitem__("scientific_authority_delta", "PROMOTED"), "authority"),
        (lambda r: r.__setitem__("independent_adjudication", "PASS"), "independent adjudication"),
        (lambda r: r.__setitem__("protected_custody", "PASS"), "protected custody"),
        (lambda r: r.__setitem__("verified_repository_count", 31), "verified counts"),
    ],
)
def test_authority_and_adverse_terminal_mutations_fail_closed(mutation, message):
    checker = load_checker()
    result, corpus, raw = documents()
    mutation(result)
    # Permit structural validation to reach the named mutation boundary.
    result["receipt_sha256"] = checker.digest(checker.canonical({k: v for k, v in result.items() if k != "receipt_sha256"}))
    raw = json.dumps(result, indent=2, sort_keys=True).encode() + b"\n"
    checker.EXPECTED_RESULT_SHA256 = checker.digest(raw)
    with pytest.raises(ValueError, match=message):
        checker.validate(result, corpus, raw)


def test_row_drop_and_mismatch_relabel_fail_closed():
    checker = load_checker()
    for edit, message in (
        (lambda r: r["repository_rows"].pop(), "45 frozen"),
        (lambda r: r["repository_rows"][0].__setitem__("status", "CANNOT_CHECK"), "adverse label"),
    ):
        result, corpus, _ = documents()
        edit(result)
        result["receipt_sha256"] = checker.digest(checker.canonical({k: v for k, v in result.items() if k != "receipt_sha256"}))
        raw = json.dumps(result, indent=2, sort_keys=True).encode() + b"\n"
        checker.EXPECTED_RESULT_SHA256 = checker.digest(raw)
        with pytest.raises(ValueError, match=message):
            checker.validate(result, corpus, raw)


def test_observed_digest_and_command_receipt_cannot_be_forged_together():
    checker = load_checker()
    result, corpus, _ = documents()
    changed = deepcopy(result)
    row = next(item for item in changed["repository_rows"] if item["status"] == "OBJECTIVE_MISMATCH")
    row["observed_license_sha256"] = "a" * 64
    changed["receipt_sha256"] = checker.digest(checker.canonical({k: v for k, v in changed.items() if k != "receipt_sha256"}))
    raw = json.dumps(changed, indent=2, sort_keys=True).encode() + b"\n"
    checker.EXPECTED_RESULT_SHA256 = checker.digest(raw)
    with pytest.raises(ValueError, match="license-observation receipt"):
        checker.validate(changed, corpus, raw)


def test_frozen_corpus_digest_mutation_fails_even_with_immutable_result():
    checker = load_checker()
    result, corpus, raw = documents()
    row = next(item for item in corpus["entries"] if item["gold_eligible"] is True)
    row["license"]["evidence_fetch_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="provided corpus object"):
        checker.validate(result, corpus, raw)


@pytest.mark.parametrize("field", ["runner_sha256", "protocol_file_sha256"])
def test_result_source_binding_mutation_fails_after_outer_hash_recomputed(field):
    checker = load_checker()
    result, corpus, _ = documents()
    result[field] = "0" * 64
    result["receipt_sha256"] = checker.digest(checker.canonical({k: v for k, v in result.items() if k != "receipt_sha256"}))
    raw = json.dumps(result, indent=2, sort_keys=True).encode() + b"\n"
    checker.EXPECTED_RESULT_SHA256 = checker.digest(raw)
    with pytest.raises(ValueError, match="file binding drift"):
        checker.validate(result, corpus, raw)


def test_failed_fake_fetch_cannot_pass_after_all_nested_hashes_recomputed():
    checker = load_checker()
    result, corpus, _ = documents()
    row = next(item for item in result["repository_rows"] if item["status"] == "OBJECTIVE_MISMATCH")
    fetch = row["command_receipts"][2]
    fetch["argv"] = ["not-git", "not-fetch"]
    fetch["attempted"] = False
    fetch["exit_code"] = 99
    row["command_receipts_sha256"] = checker.digest(checker.canonical(row["command_receipts"]))
    result["receipt_sha256"] = checker.digest(checker.canonical({k: v for k, v in result.items() if k != "receipt_sha256"}))
    raw = json.dumps(result, indent=2, sort_keys=True).encode() + b"\n"
    checker.EXPECTED_RESULT_SHA256 = checker.digest(raw)
    with pytest.raises(ValueError, match="attempted and successful"):
        checker.validate(result, corpus, raw)


@pytest.mark.parametrize("alias", [False, 0.0])
def test_boolean_or_float_exit_code_alias_cannot_pass(alias):
    checker = load_checker()
    result, corpus, _ = documents()
    row = next(item for item in result["repository_rows"] if item["status"] == "OBJECTIVE_MISMATCH")
    row["command_receipts"][2]["exit_code"] = alias
    row["command_receipts_sha256"] = checker.digest(checker.canonical(row["command_receipts"]))
    result["receipt_sha256"] = checker.digest(checker.canonical({k: v for k, v in result.items() if k != "receipt_sha256"}))
    raw = json.dumps(result, indent=2, sort_keys=True).encode() + b"\n"
    checker.EXPECTED_RESULT_SHA256 = checker.digest(raw)
    with pytest.raises(ValueError, match="attempted and successful"):
        checker.validate(result, corpus, raw)


@pytest.mark.parametrize("field", ["retained_repository_count", "verified_repository_count", "verified_organization_count"])
@pytest.mark.parametrize("alias", [False, 0.0])
def test_boolean_or_float_count_alias_cannot_pass(field, alias):
    checker = load_checker()
    result, corpus, _ = documents()
    result[field] = alias
    result["receipt_sha256"] = checker.digest(checker.canonical({k: v for k, v in result.items() if k != "receipt_sha256"}))
    raw = json.dumps(result, indent=2, sort_keys=True).encode() + b"\n"
    checker.EXPECTED_RESULT_SHA256 = checker.digest(raw)
    message = "45 frozen" if field == "retained_repository_count" else "verified counts"
    with pytest.raises(ValueError, match=message):
        checker.validate(result, corpus, raw)


def test_forged_observation_and_show_receipt_still_fail_sequence_binding():
    checker = load_checker()
    result, corpus, _ = documents()
    row = next(item for item in result["repository_rows"] if item["status"] == "OBJECTIVE_MISMATCH")
    show = next(receipt for receipt in row["command_receipts"] if receipt["argv"][0:2] == ["git", "show"] and len(receipt["argv"]) == 3)
    row["observed_license_sha256"] = "a" * 64
    show["stdout_sha256"] = "a" * 64
    show["argv"] = ["git", "show", f"{row['pinned_sha']}:FORGED_LICENSE"]
    row["command_receipts_sha256"] = checker.digest(checker.canonical(row["command_receipts"]))
    result["receipt_sha256"] = checker.digest(checker.canonical({k: v for k, v in result.items() if k != "receipt_sha256"}))
    raw = json.dumps(result, indent=2, sort_keys=True).encode() + b"\n"
    checker.EXPECTED_RESULT_SHA256 = checker.digest(raw)
    with pytest.raises(ValueError, match="license or final-HEAD command drift"):
        checker.validate(result, corpus, raw)
