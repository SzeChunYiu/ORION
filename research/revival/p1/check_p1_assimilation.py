#!/usr/bin/env python3
"""Fail-closed checks for P1 donor-assimilation ledgers.

The ledgers are research evidence about prior-art boundaries, not scientific
promotion authority. This checker validates identity, canonical receipt hashes,
explicit direct-baseline/ablation obligations, and the non-escalation boundary.
It does not decide novelty or saturation by itself.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ALLOWED_DISPOSITIONS = frozenset({"ADOPT", "ADAPT", "COMPOSE", "DEFER", "REJECT"})
ALLOWED_OVERLAPS = frozenset(
    {
        "IDENTICAL",
        "SUBSUMES_ORION",
        "ORION_SUBSUMES",
        "PARTIAL",
        "COMPLEMENTARY",
        "CONFLICTING",
        "SUBSUMES_GENERIC_INTERVENTION_ATTRIBUTION",
        "SUBSUMES_GENERIC_CAUSAL_REPLAY_ATTRIBUTION",
    }
)


def canonical_receipt_hash(receipt: dict[str, Any]) -> str:
    payload = copy.deepcopy(receipt)
    payload.pop("receipt_hash", None)
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _source_url_matches_id(source_id: str, source_url: str) -> bool:
    if source_id.startswith("arXiv:"):
        return source_url.rstrip("/").endswith(source_id.split(":", 1)[1])
    return bool(source_id.strip() and source_url.strip())


def validate_ledger(payload: dict[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if payload.get("schema_version") != "MechanismAssimilationReceipt.p1.v1":
        errors.append("schema_version")
    receipts = payload.get("receipts")
    if not isinstance(receipts, list) or not receipts:
        return tuple((*errors, "receipts_empty"))

    seen: set[str] = set()
    for index, receipt in enumerate(receipts):
        prefix = f"receipt[{index}]"
        if not isinstance(receipt, dict):
            errors.append(f"{prefix}:not_object")
            continue
        receipt_id = str(receipt.get("receipt_id", ""))
        if not receipt_id:
            errors.append(f"{prefix}:missing_receipt_id")
        elif receipt_id in seen:
            errors.append(f"{prefix}:duplicate_receipt_id:{receipt_id}")
        else:
            seen.add(receipt_id)

        source_id = str(receipt.get("source_id", ""))
        source_url = str(receipt.get("source_url", ""))
        if not _source_url_matches_id(source_id, source_url):
            errors.append(f"{prefix}:source_identity_mismatch")

        disposition = str(receipt.get("disposition", ""))
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"{prefix}:bad_disposition:{disposition}")
        overlap = str(receipt.get("overlap_type", ""))
        if overlap not in ALLOWED_OVERLAPS:
            errors.append(f"{prefix}:bad_overlap:{overlap}")

        if receipt.get("orion_authority_escalation") is not False:
            errors.append(f"{prefix}:authority_escalation")

        if disposition in {"ADOPT", "ADAPT", "COMPOSE"}:
            for field in (
                "adaptation_delta",
                "direct_baseline",
                "direct_ablation",
                "residual_orion_claim",
                "novelty_effect",
            ):
                if not str(receipt.get(field, "")).strip():
                    errors.append(f"{prefix}:missing_{field}")

        negative_history = receipt.get("negative_history")
        if not isinstance(negative_history, dict) or negative_history.get("retained") is not True:
            errors.append(f"{prefix}:negative_history_not_retained")

        official = receipt.get("official_baseline")
        if not isinstance(official, dict):
            errors.append(f"{prefix}:official_baseline_missing")
        elif official.get("runnable") is False and not str(official.get("blocker", "")).strip():
            errors.append(f"{prefix}:unrunnable_without_blocker")

        expected = canonical_receipt_hash(receipt)
        if receipt.get("receipt_hash") != expected:
            errors.append(f"{prefix}:receipt_hash_mismatch")

    saturation = str(payload.get("saturation_claim", ""))
    if saturation == "ABSORPTION_SATURATED":
        errors.append("false_saturation_without_cross_round_receipt")
    if not saturation.startswith("ROUND_"):
        errors.append("saturation_round_state_missing")
    terminal = str(payload.get("terminal", ""))
    if not terminal:
        errors.append("terminal_missing")
    return tuple(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.ledger.read_text())
    errors = validate_ledger(payload)
    print(json.dumps({"valid": not errors, "errors": list(errors)}, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
