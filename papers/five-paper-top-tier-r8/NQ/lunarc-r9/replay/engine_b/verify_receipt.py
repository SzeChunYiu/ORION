#!/usr/bin/env python3
"""Verify hash and authority boundaries of an NQ Engine B receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

import engine_b as eb


class ReceiptMismatch(RuntimeError):
    pass


SHA256 = re.compile(r"[0-9a-f]{64}")
ALLOWED_INTERNAL_TERMINALS = {
    "NQ_ENGINE_B_NON_OUTCOME_FIXTURES_VALIDATED",
    "NQ_ENGINE_B_STRUCTURAL_EXECUTION_COMPLETE",
    "CANNOT_CHECK_RESOURCE_BOUND",
    "CANNOT_CHECK_ENVIRONMENT",
}


def verify_receipt(receipt: Mapping[str, Any], *, expected_manifest_sha256: str) -> None:
    if type(receipt) is not dict or set(receipt) != {
        "schema",
        "subject_commit",
        "payload",
        "bindings",
        "authority",
        "receipt_sha256",
    }:
        raise ReceiptMismatch("receipt fields are not exact")
    if receipt.get("schema") != "ORION.NQ.EngineB.Receipt.v1":
        raise ReceiptMismatch("receipt schema mismatch")
    if receipt.get("subject_commit") != eb.SUBJECT_COMMIT:
        raise ReceiptMismatch("receipt subject mismatch")
    expected = hashlib.sha256(
        eb.canonical_json_bytes(
            {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        )
    ).hexdigest()
    if receipt.get("receipt_sha256") != expected:
        raise ReceiptMismatch("receipt digest mismatch")
    if not SHA256.fullmatch(expected_manifest_sha256):
        raise ReceiptMismatch("expected source manifest digest is invalid")
    bindings = receipt.get("bindings", {})
    if type(bindings) is not dict:
        raise ReceiptMismatch("receipt bindings are malformed")
    if bindings.get("source_manifest_sha256") != expected_manifest_sha256:
        raise ReceiptMismatch("receipt source manifest mismatch")
    authority = receipt.get("authority", {})
    payload = receipt.get("payload", {})
    if authority != {
        "blinded_independence": "NOT_CLAIMED",
        "d4_c5_cubed": "OPEN",
        "paper_authority_delta": "NONE",
        "scientific_authority_delta": "NONE",
    }:
        raise ReceiptMismatch("receipt authority fields are not exact")
    if type(payload) is not dict or payload.get("terminal") not in ALLOWED_INTERNAL_TERMINALS:
        raise ReceiptMismatch("receipt terminal is not an allowed Engine B internal terminal")
    if authority.get("d4_c5_cubed") != "OPEN" or payload.get("d4_c5_cubed") != "OPEN":
        raise ReceiptMismatch("receipt overstates the open D4 claim")
    if authority.get("blinded_independence") != "NOT_CLAIMED":
        raise ReceiptMismatch("receipt overstates blinded independence")
    if (
        payload.get("terminal") == "CANNOT_CHECK_RESOURCE_BOUND"
        and payload.get("full_strata_closed") is not False
    ):
        raise ReceiptMismatch("resource-bound receipt does not preserve open strata")
    terminal = payload["terminal"]
    if terminal in {
        "NQ_ENGINE_B_STRUCTURAL_EXECUTION_COMPLETE",
        "CANNOT_CHECK_RESOURCE_BOUND",
        "CANNOT_CHECK_ENVIRONMENT",
    }:
        if not SHA256.fullmatch(bindings.get("input_manifest_sha256", "")):
            raise ReceiptMismatch("execution receipt lacks its input manifest binding")
        if payload.get("full_strata_closed") is not False:
            raise ReceiptMismatch("execution receipt overstates full-strata closure")
    if terminal == "NQ_ENGINE_B_STRUCTURAL_EXECUTION_COMPLETE":
        if payload.get("processed_records") != payload.get("total_records"):
            raise ReceiptMismatch("structural execution terminal has an incomplete denominator")
        if payload.get("unsat_proofs_requiring_external_check") != 0:
            raise ReceiptMismatch("structural execution terminal retains unchecked UNSAT proofs")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--source-manifest", type=Path, default=root / "SOURCE_MANIFEST.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_manifest = json.loads(args.source_manifest.read_text())
    verify_receipt(
        json.loads(args.receipt.read_text()),
        expected_manifest_sha256=source_manifest["manifest_sha256"],
    )
    print("NQ_ENGINE_B_RECEIPT_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
