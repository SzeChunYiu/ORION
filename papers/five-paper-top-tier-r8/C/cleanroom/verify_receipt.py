#!/usr/bin/env python3
"""Verify clean-room source and sealed result bindings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import fiberguard_cleanroom as fg


class ReceiptMismatch(RuntimeError):
    pass


def verify_receipt(
    *,
    root: Path,
    manifest: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> None:
    fg.verify_manifest(root, manifest)
    if not fg.verify_sealed_payload(receipt):
        raise ReceiptMismatch("sealed receipt payload hash mismatch")
    if receipt["binding"]["manifest_sha256"] != manifest["manifest_sha256"]:
        raise ReceiptMismatch("receipt manifest binding mismatch")
    if receipt["authority"]["independence_terminal"] != "CANNOT_CHECK":
        raise ReceiptMismatch("receipt overstates clean-room independence")


def parse_args() -> argparse.Namespace:
    cleanroom = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=cleanroom)
    parser.add_argument("--manifest", type=Path, default=cleanroom / "SOURCE_MANIFEST.json")
    parser.add_argument("--receipt", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    verify_receipt(
        root=args.root,
        manifest=json.loads(args.manifest.read_text()),
        receipt=json.loads(args.receipt.read_text()),
    )
    print("FIBERGUARD_CLEANROOM_RECEIPT_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
