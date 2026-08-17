from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKER = ROOT / "research" / "revival" / "p1" / "check_p1_assimilation.py"
LEDGER = ROOT / "research" / "revival" / "p1" / "P1_DONOR_ASSIMILATION_LEDGER_V1.json"

_spec = importlib.util.spec_from_file_location("p1_assimilation_checker", CHECKER)
assert _spec is not None and _spec.loader is not None
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)


def _payload() -> dict:
    return json.loads(LEDGER.read_text())


def _rehash(receipt: dict) -> None:
    receipt["receipt_hash"] = checker.canonical_receipt_hash(receipt)


def test_committed_p1_assimilation_ledger_is_valid() -> None:
    assert checker.validate_ledger(_payload()) == ()


def test_receipt_hash_tampering_is_rejected() -> None:
    payload = _payload()
    payload["receipts"][0]["adaptation_delta"] += " tampered"
    errors = checker.validate_ledger(payload)
    assert "receipt[0]:receipt_hash_mismatch" in errors


def test_source_substitution_is_rejected_even_with_fresh_hash() -> None:
    payload = _payload()
    receipt = payload["receipts"][0]
    receipt["source_url"] = "https://arxiv.org/abs/2606.08275"
    _rehash(receipt)
    errors = checker.validate_ledger(payload)
    assert "receipt[0]:source_identity_mismatch" in errors


def test_donor_signal_cannot_escalate_orion_authority() -> None:
    payload = _payload()
    receipt = payload["receipts"][1]
    receipt["orion_authority_escalation"] = True
    _rehash(receipt)
    errors = checker.validate_ledger(payload)
    assert "receipt[1]:authority_escalation" in errors


def test_adopt_or_adapt_requires_direct_ablation() -> None:
    payload = _payload()
    receipt = payload["receipts"][2]
    receipt["direct_ablation"] = ""
    _rehash(receipt)
    errors = checker.validate_ledger(payload)
    assert "receipt[2]:missing_direct_ablation" in errors


def test_negative_history_cannot_be_deleted() -> None:
    payload = _payload()
    receipt = payload["receipts"][3]
    receipt["negative_history"]["retained"] = False
    _rehash(receipt)
    errors = checker.validate_ledger(payload)
    assert "receipt[3]:negative_history_not_retained" in errors


def test_false_saturation_is_rejected() -> None:
    payload = copy.deepcopy(_payload())
    payload["saturation_claim"] = "ABSORPTION_SATURATED"
    errors = checker.validate_ledger(payload)
    assert "false_saturation_without_two_round_receipt" in errors
