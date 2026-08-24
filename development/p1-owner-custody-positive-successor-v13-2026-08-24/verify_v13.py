#!/usr/bin/env python3
"""Read-only validator for the P1 V13 external execution packet."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[1]
TERMINAL = (
    "P1_V13_VALIDATION_PASS__PROVIDER_READY_PACKET_AND_THREE_INPUT_ALLOWLIST_"
    "BYTE_BOUND__ZERO_EXTERNAL_SIGNATURES__ZERO_OF_FOUR_ACTS__720_MAPS_UNCHANGED"
)


def load(name):
    return json.loads((LANE / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def must(condition, message):
    if not condition:
        raise AssertionError(message)


def verify():
    protocol = load("PROTOCOL_V13.json")
    manifest = load("EXECUTION_PACKET_MANIFEST_V13.json")
    freeze = load("PROTOCOL_FREEZE_RECEIPT_V13.json")
    status = load("AUTHORITY_EXECUTION_STATUS_V13.json")
    delegation = load("OWNER_DELEGATION_AND_ACCEPTANCE_TEMPLATE_V13.json")
    custody = load("ADAPTER_BLIND_CUSTODY_TEMPLATE_V13.json")
    coversheet = load("OWNER_ALGEBRA_COMPLETION_COVERSHEET_V13.json")
    host_rights = load("HOST_AND_RIGHTS_ACCEPTANCE_TEMPLATE_V13.json")
    review = load("INDEPENDENT_SEMANTIC_REVIEW_TEMPLATE_V13.json")
    signing = load("SIGNING_CANONICALIZATION_V13.json")
    result = load("RESULT_V13.json")
    successor = load("NEXT_DISCRIMINATOR_V14.json")

    must(sha(LANE / "PROTOCOL_V13.json") == freeze["protocol_sha256"], "protocol freeze")
    must(sha(LANE / "EXECUTION_PACKET_MANIFEST_V13.json") == freeze["execution_packet_manifest_sha256"], "manifest freeze")
    must(freeze["external_execution_started"] is False and freeze["external_outputs_received"] == 0, "pre-execution freeze")

    components = manifest["administrative_packet_components"]
    inputs = manifest["semantic_inputs"]
    must(len(components) == 8 and len(inputs) == 3, "packet/input counts")
    for item in components:
        path = LANE / item["path"]
        must(path.exists() and path.stat().st_size == item["bytes"] and sha(path) == item["sha256"], f"component {path}")
    for item in inputs:
        path = ROOT / item["path"]
        must(path.exists() and path.stat().st_size == item["bytes"] and sha(path) == item["sha256"], f"input {path}")
    must(inputs == protocol["immutable_allowlisted_semantic_inputs"], "protocol manifest semantic inputs")

    targets = protocol["targets"]
    must(len(targets) == 7 and len(set(targets)) == 7, "seven unique targets")
    must(signing["canonicalization"]["algorithm"] == "RFC8785_JSON_CANONICALIZATION_SCHEME" and signing["canonicalization"]["hash"] == "SHA-256", "canonicalization")
    must(signing["algebra_binding"]["ratifiable_payload_excludes_top_level_keys"] == ["ratification"], "non-self-referential algebra projection")
    must(set(signing["record_types"]) == {"ACCEPTANCE", "ALGEBRA_ENVELOPE", "ALGEBRA_PAYLOAD", "CUSTODY_STAGE_A", "CUSTODY_STAGE_B", "DELEGATION", "HOST_AUTHORITY", "INDEPENDENT_REVIEW", "RIGHTS_GRANT"}, "signing domains")
    must(delegation["delegation_payload"]["scope"] == targets, "delegation exact scope")
    must(delegation["delegation_payload"]["powers"] == ["COMPLETE_CLOSED_WORLD_V8_ALGEBRA", "RATIFY_EXACT_CONTENT_HASH"], "delegation powers")
    must(all(delegation["delegation_payload"][key] is None for key in ("delegate_identity", "delegator_identity", "effective_at_utc", "expiry_or_revocation_rule")), "delegation payload unsigned")
    must(delegation["delegation_payload_sha256"] is None and all(value is None for value in delegation["delegation_signature"].values()), "delegation signature absent")
    must(delegation["acceptance_payload_sha256"] is None and all(value is None for value in delegation["acceptance_signature"].values()), "acceptance signature absent")
    must(all(value is None for value in delegation["delegation_payload"]["ownership_basis"].values()), "ownership basis absent")

    allowlist_hashes = [item["sha256"] for item in inputs]
    must(custody["exact_semantic_input_allowlist"] == allowlist_hashes, "custody allowlist")
    must(len(custody["stage_a_receipts"]) == 2, "two stage-A recipients")
    must(all(receipt["stage_a_receipt_payload_sha256"] is None and receipt["stage_a_receipt_payload"]["recipient_identity"] is None and receipt["stage_a_receipt_payload"]["delivered_artifact_sha256_list"] == [] and all(value is None for value in receipt["signature"].values()) for receipt in custody["stage_a_receipts"]), "stage-A unsigned")
    stage_b = custody["stage_b_reviewer_delivery"]
    must(stage_b["stage_b_receipt_payload_sha256"] is None and all(value is None or value == [] for value in stage_b["stage_b_receipt_payload"].values()) and all(value is None for value in stage_b["signature"].values()), "stage-B unsigned")

    must(coversheet["completion_requirements"]["required_unique_targets"] == targets and coversheet["completion_requirements"]["required_unique_target_count"] == 7, "coversheet targets")
    must(coversheet["ratifiable_algebra_payload"] is None and coversheet["ratifiable_algebra_payload_sha256"] is None and all(value is None for value in coversheet["ratifiable_payload_signature"].values()), "no algebra payload")
    must(all(value is None or key in ("filename", "detached_signature_filename") for key, value in coversheet["final_algebra_envelope"].items()), "no final algebra envelope")
    must(all(value is None or value == [] for value in host_rights["host_authority_payload"].values()) and host_rights["host_authority_payload_sha256"] is None and all(value is None for value in host_rights["host_authority_signature"].values()), "no host authority")
    must(all(value is None or value == [] or key == "granted_acts" for key, value in host_rights["rights_grant_payload"].items()) and host_rights["rights_grant_payload_sha256"] is None and all(value is None for value in host_rights["rights_grant_signature"].values()), "no rights authority")
    must(all(value is None for key, value in review["review_payload"].items() if key != "independence_attestation") and all(value is None for value in review["review_payload"]["independence_attestation"].values()) and review["review_payload_sha256"] is None and all(value is None for value in review["review_signature"].values()), "no review")

    must(status["provider_ready_packet"]["complete"] is True and status["provider_ready_packet"]["manifest_sha256"] == freeze["execution_packet_manifest_sha256"], "provider-ready status")
    must(status["external_execution"]["external_outputs_received"] == 0 and status["external_execution"]["external_outputs_required"] == 7 and status["external_execution"]["started"] is False, "external execution absent")
    must(status["closed_authority_acts"] == 0 and all(value is False for value in status["authority_acts"].values()), "zero authority acts")
    must(status["map_audit_authorized"] is False and status["frozen_counts"] == {"cannot_check_maps": 720, "certified_maps": 0, "map_space": 117649, "rejected_maps": 116929}, "map state")

    required = protocol["external_outputs_required_to_close_v13"]
    must(len(required) == 7 and required == successor["required_external_outputs"], "external output contract")
    must(all(not (LANE / name).exists() for name in required), "no fabricated external outputs")
    must(successor["current_authorization"] == {"external_bundle_acceptance": False, "map_audit": False, "manuscript_update": False}, "successor authorization")

    actions = result["actions"]
    must(all(value is False for value in actions.values()), "no prohibited actions")
    must(result["positive_result"]["provider_ready_packet_complete"] is True and result["positive_result"]["exact_allowlisted_semantic_inputs_bound"] == 3, "positive packet result")
    must(result["adverse_result"] == {"authority_acts_closed": 0, "authority_acts_required": 4, "causal_boundary": "EXTERNAL_VERIFIED_ACTORS_AND_AUTHORIZED_DELIVERY_CHANNEL_NOT_SUPPLIED", "external_outputs_received": 0, "external_outputs_required": 7, "map_audit_authorized": False}, "adverse boundary")

    for predecessor in protocol["predecessors"]:
        path = ROOT / predecessor["path"]
        must(path.exists() and sha(path) == predecessor["sha256"], f"predecessor {path}")

    report = (LANE / "SCIENTIFIC_REPORT_V13.md").read_text()
    ledger = (LANE / "NEGATIVE_RESULT_LEDGER_V13.md").read_text()
    instructions = (LANE / "EXTERNAL_EXECUTION_INSTRUCTIONS_V13.md").read_text()
    must(result["terminal"] in report and result["terminal"] in ledger, "terminal in reports")
    must("Candidate authors and AI agents must not fill" in instructions, "anti-fabrication instruction")

    return {
        "schema_version": "orion.p1.owner-custody-positive-successor.validation-receipt.v13",
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "verifier_path": str(Path(__file__).relative_to(ROOT)),
        "verifier_sha256": sha(Path(__file__)),
        "checks_passed": 31,
        "administrative_components_bound": 8,
        "signing_cycle_resolved": True,
        "semantic_inputs_bound": 3,
        "external_outputs_received": 0,
        "authority_acts_closed": 0,
        "case_or_outcome_accessed": False,
        "map_audit_rerun": False,
        "pytest_or_repository_ci_run": False,
        "terminal": TERMINAL,
    }


if __name__ == "__main__":
    try:
        receipt = verify()
        if "--write-receipt" in sys.argv:
            (LANE / "VALIDATION_RECEIPT_V13.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(TERMINAL)
    except Exception as exc:
        print(f"P1_V13_VALIDATION_FAIL__{type(exc).__name__}__{exc}", file=sys.stderr)
        raise
