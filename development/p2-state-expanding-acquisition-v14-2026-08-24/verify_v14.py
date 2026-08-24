#!/usr/bin/env python3
"""Read-only offline validator for the P2 V14 scientific packet."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[1]
TERMINAL = (
    "P2_V14_VALIDATION_PASS__FROZEN_COMMIT_PATH_IDENTITY_MISMATCH_CAUSALLY_"
    "LOCALIZED__STOPPED_BEFORE_CENSUS_AND_PERFORMANCE__ZERO_OF_THREE_CUSTODY_ROLES"
)


def load(name):
    return json.loads((LANE / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def must(condition, message):
    if not condition:
        raise AssertionError(message)


def verify():
    protocol = load("PROTOCOL_V14.json")
    implementation = load("IMPLEMENTATION_FREEZE_V14.json")
    freeze = load("PROTOCOL_FREEZE_RECEIPT_V14.json")
    online = load("ONLINE_SOURCE_RECEIPT_V14.json")
    gate = load("IDENTITY_MISMATCH_GATE_RECEIPT_V14.json")
    custody = load("CUSTODY_RECEIPT_V14.json")
    result = load("RESULT_V14.json")
    successor = load("NEXT_DISCRIMINATOR_V15.json")

    must(sha(LANE / "PROTOCOL_V14.json") == freeze["protocol_sha256"], "protocol freeze")
    must(sha(LANE / "run_identity_gate_v14.py") == freeze["runner_sha256"], "runner freeze")
    must(sha(LANE / "IMPLEMENTATION_FREEZE_V14.json") == freeze["implementation_freeze_sha256"], "implementation freeze")
    must(freeze["gate_started"] is False and freeze["online_source_receipt_exists"] is False and freeze["identity_gate_receipt_exists"] is False, "pre-gate freeze state")
    must(protocol["post_discovery_boundary"]["identity_mismatch_known_before_this_protocol_freeze"] is True, "post-discovery disclosure")

    requests = online["requests"]
    must(online["official_gate_execution_number"] == 1 and online["network_requests_in_official_gate"] == 6 and len(requests) == 6, "one six-request gate")
    must([item["kind"] for item in requests] == ["commit_metadata", "root_tree", "raw_index_bytes_not_retained"] * 2, "request order")
    must(all(item["http_status"] == 200 for item in requests), "online statuses")
    must(online["raw_index_bodies_parsed"] is False and online["raw_index_bodies_retained"] is False, "raw body boundary")
    must(online["label_values_or_class_counts_inspected_or_retained"] is False and online["review_csv_requests"] == 0, "outcome and CSV boundary")
    must(all("content" not in item and "response_body" not in item for item in requests), "no response bodies in receipt")

    frozen_expected = {
        "bytes": 23118,
        "git_blob_sha1": "ada2668adfbb33d61e11a6bec02b10637e419bde",
        "sha256": "5d829c669f744cc6e91165b15dd3364554320d684398b841764b2609bb857d4b",
    }
    frozen_observed = {
        "bytes": 22135,
        "git_blob_sha1": "f4f5007156cb71e7d54e99057037fb75d44f87c4",
        "sha256": "f34c17b3dca9d609585e5fcc9d24c5433d4ad240ef91e5c2e9a48edee1e0959a",
    }
    must(gate["frozen_expected_identity"] == frozen_expected, "frozen expected tuple")
    must(gate["frozen_route"]["raw_identity"] | {"body_parsed": False, "body_retained": False} == gate["frozen_route"]["raw_identity"], "raw flags present")
    must({key: gate["frozen_route"]["raw_identity"][key] for key in frozen_observed} == frozen_observed, "frozen observed tuple")
    must(gate["frozen_route"]["commit"] == "38b35218e4d0f99621cec5a8a25a0147bb88c654" and gate["frozen_route"]["root_tree_sha1"] == "49f437c367cc45a90867418fcef77c9ff3614456", "frozen commit tree")
    must(gate["frozen_route"]["tree_entry"]["git_blob_sha1"] == frozen_observed["git_blob_sha1"] and gate["frozen_route"]["tree_entry"]["bytes"] == frozen_observed["bytes"], "frozen tree raw binding")
    must(gate["historical_expected_identity"] == frozen_expected, "historical expected tuple")
    must({key: gate["historical_owner_route"]["raw_identity"][key] for key in frozen_expected} == frozen_expected, "historical raw tuple")
    must(gate["historical_owner_route"]["commit"] == "dc2dadfdbb98eb1b4259604789abd640aa3b693e" and gate["historical_owner_route"]["root_tree_sha1"] == "2173535d1bb1c918e127acd9145fd42d37ee82a2", "historical owner commit tree")
    must(gate["historical_owner_route"]["tree_entry"]["git_blob_sha1"] == frozen_expected["git_blob_sha1"] and gate["historical_owner_route"]["tree_entry"]["bytes"] == frozen_expected["bytes"], "historical tree raw binding")
    must(gate["diagnostic_reproduction_passed"] is True and gate["frozen_route_acquisition_passed"] is False and gate["historical_owner_provenance_passed"] is True, "identity diagnosis")
    must(gate["historical_owner_authorized_as_v14_substitute"] is False, "no substitution")
    must(gate["causal_code"] == "FROZEN_INDEX_SHA_DOES_NOT_MATCH_PINNED_COMMIT_PATH", "causal code")
    must(all(gate[key] is True for key in ("stopped_before_index_parse", "stopped_before_review_census", "stopped_before_review_csv_download", "stopped_before_labels_models_rankings_metrics")), "fail-closed stops")

    actions = result["actions"]
    zero_keys = (
        "index_json_parses",
        "learner_or_model_runs",
        "manuscript_updated",
        "metric_or_scorer_runs",
        "performance_arms",
        "protected_outcome_or_c4_runs",
        "pytest_or_repository_ci_runs",
        "ranking_runs",
        "review_csv_requests",
        "review_population_censuses",
        "shared_ledger_updated",
    )
    must(all(actions[key] == 0 or actions[key] is False for key in zero_keys), "zero prohibited actions")
    must(actions["label_values_inspected_or_retained"] is False and actions["class_counts_inspected_or_retained"] is False, "no label or class counts")
    must(result["performance_run_authorized"] is False and result["adverse_result"]["frozen_route_acquisition_passed"] is False, "adverse no performance")
    must(result["terminal"] == gate["terminal"], "terminal binding")

    must(custody["independence"] == {"closed_roles": 0, "required_roles": 3, "same_session_self_attestation_allowed": False}, "custody state")
    must(all(role["bound"] is False and role["identity"] is None for role in custody["roles"].values()), "custody roles unbound")
    must(custody["performance_authorization"] is False, "custody withholds performance")

    coherent = successor["coherent_repair_selected_by_source_authority_not_outcomes"]
    must(coherent["commit"] == gate["frozen_route"]["commit"] and coherent["root_tree_sha1"] == gate["frozen_route"]["root_tree_sha1"], "successor commit tree")
    must(coherent["index_git_blob_sha1"] == frozen_observed["git_blob_sha1"] and coherent["index_sha256"] == frozen_observed["sha256"] and coherent["index_bytes"] == frozen_observed["bytes"], "successor coherent tuple")
    must(successor["selection_rule_change"] == "NONE" and successor["no_post_census_substitution"] is True, "successor preserves selection")
    must(successor["current_authorization"] == {"independent_source_custody": False, "performance_run": False, "seven_review_census": False}, "successor authorization")

    for predecessor in protocol["predecessors"]:
        path = ROOT / predecessor["path"]
        must(path.exists() and sha(path) == predecessor["sha256"], f"predecessor {path}")

    report = (LANE / "SCIENTIFIC_REPORT_V14.md").read_text()
    ledger = (LANE / "NEGATIVE_RESULT_LEDGER_V14.md").read_text()
    must(result["terminal"] in report and result["terminal"] in ledger, "terminal in reports")
    must("does not establish that seven eligible reviews exist" in report, "claim boundary")

    return {
        "schema_version": "orion.p2.state-expanding-acquisition.validation-receipt.v14",
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "verifier_path": str(Path(__file__).relative_to(ROOT)),
        "verifier_sha256": sha(Path(__file__)),
        "checks_passed": 31,
        "official_identity_gate_executions": 1,
        "diagnostic_reproduction_passed": True,
        "frozen_route_acquisition_passed": False,
        "review_censuses": 0,
        "model_ranking_metric_runs": 0,
        "label_values_or_class_counts_inspected_or_retained": False,
        "pytest_or_repository_ci_run": False,
        "independent_custody_roles_closed": 0,
        "terminal": TERMINAL,
    }


if __name__ == "__main__":
    try:
        receipt = verify()
        if "--write-receipt" in sys.argv:
            (LANE / "VALIDATION_RECEIPT_V14.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(TERMINAL)
    except Exception as exc:
        print(f"P2_V14_VALIDATION_FAIL__{type(exc).__name__}__{exc}", file=sys.stderr)
        raise
