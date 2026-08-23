#!/usr/bin/env python3
"""Post-freeze checker for the P15 Scientific Execution Integrity V1 fault study."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
CASES_PATH = HERE / "sei_fault_cases_v1.jsonl"
GOLD_PATH = HERE / "sei_fault_gold_v1.json"
PROTOCOL_PATH = HERE / "P15_SEI_FAULT_PROTOCOL_V1.md"

DISPOSITIONS = {
    "AUTHORIZED_SCIENCE",
    "VALID_BUT_NOT_AUTHORIZED",
    "INVALID_SCIENCE",
    "EXECUTION_INVALID",
    "CANNOT_CHECK",
}


def load_cases() -> list[dict[str, Any]]:
    cases = [json.loads(line) for line in CASES_PATH.read_text().splitlines() if line.strip()]
    assert len(cases) == 18
    assert len({c["id"] for c in cases}) == 18
    return cases


def load_gold() -> dict[str, str]:
    gold = json.loads(GOLD_PATH.read_text())
    assert set(gold.values()) <= DISPOSITIONS
    return gold


def plain_logs(c: dict[str, Any]) -> str:
    # Common nominal-success semantics: process exists, exits 0, emits something.
    if not c["spawn_ok"] or c["timeout"] or not c["exit_zero"] or not c["output_present"]:
        return "EXECUTION_INVALID"
    return "AUTHORIZED_SCIENCE"


def execution_integrity(c: dict[str, Any]) -> bool:
    return all((
        c["spawn_ok"],
        c["host_ok"],
        not c["timeout"],
        c["exit_zero"],
        c["output_present"],
        c["output_complete"],
        c["reaped"],
        c["finalized_after_reap"],
        c["cleanup_complete"],
        c["retry_accounting_valid"],
        c["invocation_match"],
        c["input_digest_match"],
        c["result_digest_match"],
        c["occurrence_unique"],
        c["fresh"],
        c["coverage_complete"],
    ))


def structured_receipt(c: dict[str, Any]) -> str:
    if not execution_integrity(c):
        return "EXECUTION_INVALID"
    # Structured execution provenance says execution is bound/complete; this comparator
    # intentionally demonstrates that doing so cannot promote scientific validity.
    return "AUTHORIZED_SCIENCE"


def replay_agreement_product(c: dict[str, Any]) -> str:
    if not execution_integrity(c):
        return "EXECUTION_INVALID"
    if not c["replay_match"]:
        return "CANNOT_CHECK"
    if c["lane_applicable"] and not c["lane_agree"]:
        return "CANNOT_CHECK"
    return "AUTHORIZED_SCIENCE"


def sei(c: dict[str, Any]) -> str:
    if not execution_integrity(c):
        return "EXECUTION_INVALID"
    if not c["scientific_contract_available"]:
        return "CANNOT_CHECK"
    if not c["scientific_contract_valid"]:
        return "INVALID_SCIENCE"
    if not c["claim_authority_available"]:
        return "CANNOT_CHECK"
    if not c["claim_authority"]:
        return "VALID_BUT_NOT_AUTHORIZED"
    return "AUTHORIZED_SCIENCE"


def evaluate(cases: list[dict[str, Any]], gold: dict[str, str], fn: Callable[[dict[str, Any]], str]) -> dict[str, Any]:
    rows = []
    false_authorized = 0
    false_execution_science = 0
    invalid_science_as_success = 0
    valid_noauth_laundering = 0
    false_reject_clean_auth = 0
    correct_cannot_check = 0
    for c in cases:
        expected = gold[c["id"]]
        predicted = fn(c)
        assert predicted in DISPOSITIONS
        if predicted == "AUTHORIZED_SCIENCE" and expected != "AUTHORIZED_SCIENCE":
            false_authorized += 1
        if expected == "EXECUTION_INVALID" and predicted == "AUTHORIZED_SCIENCE":
            false_execution_science += 1
        if expected == "INVALID_SCIENCE" and predicted == "AUTHORIZED_SCIENCE":
            invalid_science_as_success += 1
        if expected == "VALID_BUT_NOT_AUTHORIZED" and predicted == "AUTHORIZED_SCIENCE":
            valid_noauth_laundering += 1
        if expected == "AUTHORIZED_SCIENCE" and predicted != "AUTHORIZED_SCIENCE":
            false_reject_clean_auth += 1
        if expected == "CANNOT_CHECK" and predicted == "CANNOT_CHECK":
            correct_cannot_check += 1
        rows.append({
            "id": c["id"],
            "expected": expected,
            "predicted": predicted,
            "correct": predicted == expected,
        })
    return {
        "accuracy": sum(r["correct"] for r in rows) / len(rows),
        "false_authorized": false_authorized,
        "false_execution_science": false_execution_science,
        "invalid_science_as_success": invalid_science_as_success,
        "valid_noauth_laundering": valid_noauth_laundering,
        "false_reject_authorized_science": false_reject_clean_auth,
        "correct_cannot_check": correct_cannot_check,
        "prediction_counts": dict(Counter(r["predicted"] for r in rows)),
        "rows": rows,
    }


def formal_invariants(cases: list[dict[str, Any]], gold: dict[str, str]) -> dict[str, Any]:
    by_id = {c["id"]: c for c in cases}

    # H15.1: all execution-invalid gold cases are barred by execution integrity.
    execution_invalid_ids = [cid for cid, disposition in gold.items() if disposition == "EXECUTION_INVALID"]
    assert execution_invalid_ids
    assert all(not execution_integrity(by_id[cid]) for cid in execution_invalid_ids)

    # H15.2 exact binding witnesses.
    for cid in ("SEI-STALE-REPLAY", "SEI-DUP-OCCURRENCE", "SEI-DIGEST-FORGE", "SEI-TRUNCATED"):
        assert not execution_integrity(by_id[cid])

    # H15.3 publication atomicity witnesses.
    for cid in ("SEI-PRE-REAP-FINAL", "SEI-CLEANUP-OMIT", "SEI-RETRY-CORRUPT"):
        assert not execution_integrity(by_id[cid])

    # H15.4 identical execution properties, different science validity.
    left = by_id["SEI-CLEAN-AUTH"]
    right = by_id["SEI-COMPLETE-INVALID-SCIENCE"]
    execution_keys = (
        "spawn_ok", "host_ok", "timeout", "exit_zero", "output_present", "output_complete",
        "reaped", "finalized_after_reap", "cleanup_complete", "retry_accounting_valid",
        "invocation_match", "input_digest_match", "result_digest_match", "occurrence_unique",
        "fresh", "coverage_complete", "replay_match", "lane_applicable", "lane_agree",
    )
    assert tuple(left[k] for k in execution_keys) == tuple(right[k] for k in execution_keys)
    assert left["scientific_contract_valid"] is True and right["scientific_contract_valid"] is False
    assert gold[left["id"]] != gold[right["id"]]

    # H15.5 agreement is not validity.
    agree_wrong = by_id["SEI-DUAL-AGREE-WRONG"]
    assert agree_wrong["lane_agree"] is True
    assert agree_wrong["replay_match"] is True
    assert agree_wrong["scientific_contract_valid"] is False
    assert gold[agree_wrong["id"]] == "INVALID_SCIENCE"

    # Agreement is also not necessary for correctness if independent verifier resolves it.
    disagree_verified = by_id["SEI-DUAL-DISAGREE-VERIFIED"]
    assert disagree_verified["lane_agree"] is False
    assert disagree_verified["scientific_contract_valid"] is True
    assert gold[disagree_verified["id"]] == "AUTHORIZED_SCIENCE"

    return {
        "H15.1_host_science_separation": True,
        "H15.2_exact_binding": True,
        "H15.3_publication_atomicity": True,
        "H15.4_coverage_receipt_not_validity": {
            "same_execution_pair": [left["id"], right["id"]],
        },
        "H15.5_agreement_not_validity": {
            "agree_wrong": agree_wrong["id"],
            "disagree_verified": disagree_verified["id"],
        },
    }


def main() -> int:
    cases = load_cases()
    gold = load_gold()
    assert set(gold) == {c["id"] for c in cases}
    invariants = formal_invariants(cases, gold)

    systems = {
        "plain_logs": evaluate(cases, gold, plain_logs),
        "structured_receipt": evaluate(cases, gold, structured_receipt),
        "replay_agreement": evaluate(cases, gold, replay_agreement_product),
        "sei": evaluate(cases, gold, sei),
    }

    sei_result = systems["sei"]
    positive = (
        sei_result["false_authorized"] == 0
        and sei_result["false_reject_authorized_science"] == 0
        and sei_result["invalid_science_as_success"] == 0
        and sei_result["valid_noauth_laundering"] == 0
        and sei_result["accuracy"] == 1.0
        and systems["structured_receipt"]["invalid_science_as_success"] > 0
        and systems["replay_agreement"]["invalid_science_as_success"] > 0
    )

    receipt = {
        "protocol": "P15_SEI_FAULT_PROTOCOL_V1",
        "protocol_sha256": hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest(),
        "cases_sha256": hashlib.sha256(CASES_PATH.read_bytes()).hexdigest(),
        "gold_sha256": hashlib.sha256(GOLD_PATH.read_bytes()).hexdigest(),
        "case_count": len(cases),
        "invariants": invariants,
        "systems": systems,
        "positive_gate": positive,
        "terminal": "P15_SEI_BOUNDED_FAULT_V1_GREEN" if positive else "P15_SEI_BOUNDED_FAULT_V1_GATE_NOT_MET",
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(receipt, sort_keys=True, indent=2))
    assert positive, receipt
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
