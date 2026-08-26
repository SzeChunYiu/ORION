#!/usr/bin/env python3
"""Verify hash and authority boundaries of an NQ Engine B receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import engine_b as eb


class ReceiptMismatch(RuntimeError):
    pass


def verify_receipt(receipt: Mapping[str, Any], *, expected_manifest_sha256: str) -> None:
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
    if receipt.get("bindings", {}).get("source_manifest_sha256") != expected_manifest_sha256:
        raise ReceiptMismatch("receipt source manifest mismatch")
    authority = receipt.get("authority", {})
    payload = receipt.get("payload", {})
    if authority.get("d4_c5_cubed") != "OPEN" or payload.get("d4_c5_cubed") != "OPEN":
        raise ReceiptMismatch("receipt overstates the open D4 claim")
    if authority.get("blinded_independence") != "NOT_CLAIMED":
        raise ReceiptMismatch("receipt overstates blinded independence")
    if (
        payload.get("terminal") == "CANNOT_CHECK_RESOURCE_BOUND"
        and payload.get("full_strata_closed") is not False
    ):
        raise ReceiptMismatch("resource-bound receipt does not preserve open strata")


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
