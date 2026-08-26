#!/usr/bin/env python3
"""Fail-closed verifier for the frozen CR-A/CR-B rank-two control receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import control_replay as replay


class ControlReceiptMismatch(RuntimeError):
    pass


REQUIRED_FIELDS = {
    "schema",
    "scientific_subject",
    "custody_parent",
    "scope",
    "grammar",
    "engine_independence",
    "engine_a_pass_sha256",
    "engine_b_pass_sha256",
    "reference_pass_sha256",
    "case_count",
    "positive_count",
    "negative_count",
    "mismatch_count",
    "cases_sha256",
    "orbit_range_sha256",
    "cases",
    "disagreements",
    "terminal",
    "full_census_executed",
    "d2_d3_replay_complete",
    "d4_c5_cubed",
    "science_terminal",
    "independence_terminal",
    "authority_ceiling",
    "receipt_sha256",
}


def verify_control_protocol(protocol: Mapping[str, Any], receipt: Mapping[str, Any]) -> None:
    if protocol.get("schema") != "ORION.NQ.R9.CRABRank2ControlProtocol.v1":
        raise ControlReceiptMismatch("control protocol schema mismatch")
    if protocol.get("scientific_subject") != replay.SCIENTIFIC_SUBJECT:
        raise ControlReceiptMismatch("control protocol scientific subject mismatch")
    if protocol.get("custody_parent") != replay.CUSTODY_PARENT:
        raise ControlReceiptMismatch("control protocol custody parent mismatch")
    if protocol.get("allowed_terminal") != replay.PASS_TERMINAL:
        raise ControlReceiptMismatch("control protocol terminal mismatch")
    if protocol.get("authority_ceiling") != replay.AUTHORITY_CEILING:
        raise ControlReceiptMismatch("control protocol authority ceiling mismatch")
    if protocol.get("lunarc_submission_authorized") is not False:
        raise ControlReceiptMismatch("control protocol unexpectedly authorizes LUNARC")
    if protocol.get("full_census_authorized") is not False:
        raise ControlReceiptMismatch("control protocol unexpectedly authorizes full census")
    expected = protocol.get("expected_control")
    observed = {
        key: receipt[key]
        for key in (
            "case_count",
            "positive_count",
            "negative_count",
            "mismatch_count",
            "cases_sha256",
            "engine_a_pass_sha256",
            "engine_b_pass_sha256",
            "orbit_range_sha256",
            "receipt_sha256",
            "reference_pass_sha256",
        )
    }
    if expected != observed:
        raise ControlReceiptMismatch("receipt does not match frozen protocol expectations")


def verify_control_receipt(receipt: Mapping[str, Any], *, rerun: bool = True) -> None:
    if type(receipt) is not dict or set(receipt) != REQUIRED_FIELDS:
        raise ControlReceiptMismatch("control receipt fields are not exact")
    if receipt["schema"] != "ORION.NQ.R9.CRABRank2ControlReceipt.v1":
        raise ControlReceiptMismatch("control receipt schema mismatch")
    if receipt["scientific_subject"] != replay.SCIENTIFIC_SUBJECT:
        raise ControlReceiptMismatch("scientific subject mismatch")
    if receipt["custody_parent"] != replay.CUSTODY_PARENT:
        raise ControlReceiptMismatch("custody parent mismatch")
    expected_digest = replay._sha256(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )
    if receipt["receipt_sha256"] != expected_digest:
        raise ControlReceiptMismatch("control receipt digest mismatch")
    if receipt["terminal"] != replay.PASS_TERMINAL or receipt["mismatch_count"] != 0:
        raise ControlReceiptMismatch("two-engine control did not reach the frozen PASS terminal")
    if receipt["disagreements"] != []:
        raise ControlReceiptMismatch("PASS receipt retains disagreement witnesses")
    if receipt["positive_count"] + receipt["negative_count"] != receipt["case_count"]:
        raise ControlReceiptMismatch("control denominator counts do not add up")
    if receipt["case_count"] != len(receipt["cases"]):
        raise ControlReceiptMismatch("control case denominator mismatch")
    if any(case.get("agreement") is not True for case in receipt["cases"]):
        raise ControlReceiptMismatch("control case agreement is not exact")
    if (
        receipt["full_census_executed"] is not False
        or receipt["d2_d3_replay_complete"] is not False
        or receipt["d4_c5_cubed"] != "OPEN"
        or receipt["science_terminal"] != "CANNOT_CHECK"
        or receipt["independence_terminal"] != "CANNOT_CHECK"
        or receipt["authority_ceiling"] != replay.AUTHORITY_CEILING
    ):
        raise ControlReceiptMismatch("control receipt exceeds its authority ceiling")
    case_digests = []
    orbit_bindings = []
    engine_a_records = []
    engine_b_records = []
    reference_records = []
    for case in receipt["cases"]:
        if type(case) is not dict or "case_sha256" not in case:
            raise ControlReceiptMismatch("control case is malformed")
        observed = replay._sha256(
            {key: value for key, value in case.items() if key != "case_sha256"}
        )
        if observed != case["case_sha256"]:
            raise ControlReceiptMismatch(f"case digest mismatch: {case.get('record_id')}")
        case_digests.append(case["case_sha256"])
        engine_a_records.append(case["engine_a_record_sha256"])
        engine_b_records.append(case["engine_b_record_sha256"])
        reference_records.append(case["reference_record_sha256"])
        orbit_bindings.append(
            [
                case["record_id"],
                case["engine_b_representative_sha256"],
                case["engine_b_orbit_sha256"],
            ]
        )
    if receipt["cases_sha256"] != replay._sha256(case_digests):
        raise ControlReceiptMismatch("case-range digest mismatch")
    if receipt["orbit_range_sha256"] != replay._sha256(orbit_bindings):
        raise ControlReceiptMismatch("orbit-range digest mismatch")
    if receipt["engine_a_pass_sha256"] != replay._sha256(engine_a_records):
        raise ControlReceiptMismatch("Engine-A pass digest mismatch")
    if receipt["engine_b_pass_sha256"] != replay._sha256(engine_b_records):
        raise ControlReceiptMismatch("Engine-B pass digest mismatch")
    if receipt["reference_pass_sha256"] != replay._sha256(reference_records):
        raise ControlReceiptMismatch("reference pass digest mismatch")
    if rerun:
        expected = replay.build_control_receipt()
        if receipt != expected:
            raise ControlReceiptMismatch("receipt does not match deterministic two-engine replay")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "receipt",
        type=Path,
        nargs="?",
        default=replay.REPLAY_ROOT / "controls" / "RANK2_PREFIX_CONTROL_RECEIPT.json",
    )
    parser.add_argument("--no-rerun", action="store_true")
    parser.add_argument(
        "--protocol",
        type=Path,
        default=replay.REPLAY_ROOT / "CONTROL_PROTOCOL.json",
    )
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text())
    verify_control_receipt(receipt, rerun=not args.no_rerun)
    verify_control_protocol(json.loads(args.protocol.read_text()), receipt)
    print("NQ_CR_A_CR_B_RANK2_PREFIX_CONTROL_RECEIPT_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
