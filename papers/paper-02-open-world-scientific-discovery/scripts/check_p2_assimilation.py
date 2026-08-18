#!/usr/bin/env python3
"""Validate the P2 donor-assimilation ledger.

This is intentionally stdlib-only so the publication gate can run in clean CI.
It checks source identity, canonical receipt hashes, disposition semantics, and
the hostile anti-rebranding/authority-escalation invariants from issue #318.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "protocol" / "P2_DONOR_ASSIMILATION_LEDGER_V1.json"

REQUIRED = {
    "receipt_id",
    "donor_title",
    "source_id",
    "source_url",
    "checked_at",
    "stage",
    "assumptions",
    "donor_authority",
    "donor_output",
    "task_mapping",
    "overlap_type",
    "disposition",
    "adaptation_delta",
    "official_baseline",
    "direct_baseline",
    "direct_ablation",
    "residual_orion_claim",
    "novelty_effect",
    "failure_modes",
    "negative_history",
    "reopen_triggers",
    "orion_authority_escalation",
    "receipt_hash",
}
DISPOSITIONS = {"ADOPT", "ADAPT", "COMPOSE", "DEFER", "REJECT"}
OVERLAPS = {"IDENTICAL", "SUBSUMES_ORION", "ORION_SUBSUMES", "PARTIAL", "COMPLEMENTARY", "CONFLICTING"}
AUTHORITIES = {"relevance", "utility", "coverage", "evidence_sufficiency", "none"}
ARXIV_RE = re.compile(r"^arXiv:(\d{4}\.\d{5})$")


def canonical_hash(receipt: dict[str, Any]) -> str:
    payload = {k: v for k, v in receipt.items() if k != "receipt_hash"}
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(x, str) and x.strip() for x in value)


def validate_receipt(receipt: dict[str, Any]) -> list[str]:
    rid = str(receipt.get("receipt_id", "<missing>"))
    errors: list[str] = []

    missing = sorted(REQUIRED - receipt.keys())
    if missing:
        errors.append(f"{rid}: missing fields: {', '.join(missing)}")
        return errors

    if receipt["disposition"] not in DISPOSITIONS:
        errors.append(f"{rid}: invalid disposition {receipt['disposition']!r}")
    if receipt["overlap_type"] not in OVERLAPS:
        errors.append(f"{rid}: invalid overlap_type {receipt['overlap_type']!r}")
    if receipt["donor_authority"] not in AUTHORITIES:
        errors.append(f"{rid}: invalid donor_authority {receipt['donor_authority']!r}")

    match = ARXIV_RE.match(str(receipt["source_id"]))
    if not match:
        errors.append(f"{rid}: source_id must be an arXiv identity")
    elif str(receipt["source_url"]).rstrip("/") != f"https://arxiv.org/abs/{match.group(1)}":
        errors.append(f"{rid}: source_url does not match source_id (source substitution attack)")

    for field in ("stage", "assumptions", "failure_modes", "reopen_triggers"):
        if not _nonempty_list(receipt[field]):
            errors.append(f"{rid}: {field} must be a non-empty string list")

    if receipt["orion_authority_escalation"] is not False:
        errors.append(f"{rid}: donor signal may not be escalated to ORION task-closure authority")

    baseline = receipt["official_baseline"]
    if not isinstance(baseline, dict):
        errors.append(f"{rid}: official_baseline must be an object")
    else:
        runnable = baseline.get("runnable")
        label = baseline.get("label")
        blocker = str(baseline.get("blocker", "")).strip()
        reopen = str(baseline.get("reopen", "")).strip()
        if runnable is True and label != "OFFICIAL":
            errors.append(f"{rid}: runnable official baseline cannot be weakened/relabelled")
        if runnable is False and (not blocker or not reopen):
            errors.append(f"{rid}: unavailable official baseline needs blocker and reopen condition")

    history = receipt["negative_history"]
    if not isinstance(history, dict) or history.get("retained") is not True or not isinstance(history.get("items"), list):
        errors.append(f"{rid}: negative history must be explicitly retained")

    if receipt["overlap_type"] == "IDENTICAL" and receipt["novelty_effect"] != "REMOVE":
        errors.append(f"{rid}: identical donor mechanic must remove ORION novelty (rename attack)")

    if receipt["disposition"] == "COMPOSE":
        components = receipt.get("components", [])
        if not isinstance(components, list) or len(components) < 2:
            errors.append(f"{rid}: COMPOSE requires at least two named components")
        ablation = str(receipt["direct_ablation"]).lower()
        if "component" not in ablation or "full" not in ablation:
            errors.append(f"{rid}: COMPOSE requires component and full-composition ablations")

    expected = canonical_hash(receipt)
    if receipt["receipt_hash"] != expected:
        errors.append(f"{rid}: receipt_hash mismatch")

    return errors


def validate_ledger(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "MechanismAssimilationReceipt.p2.v1":
        errors.append("ledger: unexpected schema_version")
    if data.get("saturation_claim") != "NOT_CLAIMED":
        errors.append("ledger: fast-moving 2026-08 literature may not be labelled saturated")
    if data.get("terminal") != "P2_NARROWED":
        errors.append("ledger: this freeze is bound to the narrowed P2 terminal")
    if not _nonempty_list(data.get("reopen_triggers")):
        errors.append("ledger: top-level reopen_triggers must be non-empty")

    receipts = data.get("receipts")
    if not isinstance(receipts, list) or not receipts:
        return errors + ["ledger: receipts must be a non-empty list"]

    seen: set[str] = set()
    for receipt in receipts:
        if not isinstance(receipt, dict):
            errors.append("ledger: every receipt must be an object")
            continue
        rid = str(receipt.get("receipt_id", "<missing>"))
        if rid in seen:
            errors.append(f"{rid}: duplicate receipt_id")
        seen.add(rid)
        errors.extend(validate_receipt(receipt))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    args = parser.parse_args()

    data = json.loads(args.ledger.read_text(encoding="utf-8"))
    errors = validate_ledger(data)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"P2 assimilation ledger valid: {len(data['receipts'])} receipts; saturation NOT_CLAIMED; terminal P2_NARROWED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
