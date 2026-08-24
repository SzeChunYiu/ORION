import copy
import json
from pathlib import Path

from orion.publication.recursive_resolution_ledger import EXPECTED_PAPERS, validate_ledger


LEDGER_PATH = Path(
    "research/paper-programme-v1/P1_P15_RECURSIVE_RESOLUTION_LEDGER_2026-08-23.json"
)


def _ledger():
    return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))


def _first_item(document, category):
    return next(
        item
        for paper in document["papers"]
        for item in paper["items"]
        if item["category"] == category
    )


def test_programme_ledger_is_complete_and_valid():
    document = _ledger()
    assert [paper["paper_id"] for paper in document["papers"]] == EXPECTED_PAPERS
    assert validate_ledger(document, repo_root=Path.cwd()) == []


def test_validator_rejects_missing_paper():
    document = _ledger()
    document["papers"].pop(9)
    assert any("exactly" in error for error in validate_ledger(document))


def test_validator_rejects_mutable_adverse_history():
    document = _ledger()
    _first_item(document, "HISTORICAL_ADVERSE_RESULT")["immutable"] = False
    assert any("immutable" in error for error in validate_ledger(document))


def test_validator_rejects_authority_from_unexecuted_successor():
    document = _ledger()
    _first_item(document, "PROSPECTIVE_SUCCESSOR_REQUIRED")[
        "positive_authority_granted"
    ] = True
    assert any("positive_authority_granted" in error for error in validate_ledger(document))


def test_validator_rejects_existing_pr_without_verification_identity():
    document = _ledger()
    _first_item(document, "FIXED_BY_EXISTING_PR")["existing_pr"].pop("url")
    assert any("existing_pr.url" in error for error in validate_ledger(document))


def test_validator_rejects_item_level_relabel_permission():
    document = copy.deepcopy(_ledger())
    document["papers"][0]["items"][0]["post_hoc_relabeling_prohibited"] = False
    assert any("post_hoc_relabeling_prohibited" in error for error in validate_ledger(document))


def test_validator_checks_base_source_existence(tmp_path):
    document = _ledger()
    errors = validate_ledger(document, repo_root=tmp_path)
    assert any("does not exist on the base revision" in error for error in errors)


def test_validator_requires_steps_for_remaining_integration_blockers():
    # The committed ledger currently carries no open integration blockers, so
    # the rule is exercised by injecting them. Mutating committed data stopped
    # working once every blocker was resolved, and quietly skipping the rule
    # would leave the validator untested against its own fail-closed branch.
    document = _ledger()
    item = _first_item(document, "PROSPECTIVE_SUCCESSOR_REQUIRED")
    item["remaining_integration_blockers"] = [
        {"blocker": "successor protocol not yet authored", "next_executable_step": ""}
    ]
    assert any("remaining_integration_blockers" in error for error in validate_ledger(document))
    item = _first_item(document, "FIXED_BY_EXISTING_PR")
    item["remaining_integration_blockers"] = [
        {"blocker": "synthetic validator fixture", "next_executable_step": ""}
    ]
    assert any("remaining_integration_blockers" in error for error in validate_ledger(document))


def test_executed_successors_are_positive_only_at_their_bounded_claim_leaves():
    document = _ledger()
    items = {
        item["item_id"]: item
        for paper in document["papers"]
        for item in paper["items"]
    }
    assert items["P12.B.CAPABILITY_MATCHED.ACTIVE"]["authority_artifact"].endswith(
        "P12_ACTIVE_CLAIM_AUTHORITY_V3.json"
    )
    assert items["P13.B.AUTHENTICATED.CORRUPTION.ACTIVE"][
        "authority_artifact"
    ].endswith("P13_ACTIVE_CLAIM_AUTHORITY_V2.json")
    assert items["P9.D1V1_2.LOCKED_ENV.HISTORICAL"]["immutable"] is True
    assert items["P10.CLAIM_AUTHORITY.PR972"]["category"] == "FIXED_BY_EXISTING_PR"
