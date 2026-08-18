"""Hostile tests for the P2 MechanismAssimilationReceipt ledger."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_p2_assimilation.py"
LEDGER = ROOT / "protocol" / "P2_DONOR_ASSIMILATION_LEDGER_V1.json"

spec = importlib.util.spec_from_file_location("check_p2_assimilation", SCRIPT)
assert spec and spec.loader
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def load_ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def rehash(receipt):
    receipt["receipt_hash"] = checker.canonical_hash(receipt)
    return receipt


def test_committed_ledger_is_valid():
    assert checker.validate_ledger(load_ledger()) == []


def test_hash_tamper_fails():
    data = load_ledger()
    data["receipts"][0]["residual_orion_claim"] += " tampered"
    errors = checker.validate_ledger(data)
    assert any("receipt_hash mismatch" in e for e in errors)


def test_source_substitution_fails_even_when_rehashed():
    data = load_ledger()
    receipt = data["receipts"][0]
    receipt["source_url"] = "https://arxiv.org/abs/9999.99999"
    rehash(receipt)
    errors = checker.validate_ledger(data)
    assert any("source substitution attack" in e for e in errors)


def test_authority_escalation_fails_even_when_rehashed():
    data = load_ledger()
    receipt = data["receipts"][0]
    receipt["orion_authority_escalation"] = True
    rehash(receipt)
    errors = checker.validate_ledger(data)
    assert any("task-closure authority" in e for e in errors)


def test_baseline_weakening_fails_even_when_rehashed():
    data = load_ledger()
    receipt = next(r for r in data["receipts"] if r["official_baseline"]["runnable"])
    receipt["official_baseline"]["label"] = "PROXY"
    rehash(receipt)
    errors = checker.validate_ledger(data)
    assert any("cannot be weakened" in e for e in errors)


def test_negative_history_deletion_fails_even_when_rehashed():
    data = load_ledger()
    receipt = data["receipts"][0]
    receipt["negative_history"]["retained"] = False
    rehash(receipt)
    errors = checker.validate_ledger(data)
    assert any("negative history" in e for e in errors)


def test_false_saturation_claim_fails():
    data = load_ledger()
    data["saturation_claim"] = "SATURATED"
    errors = checker.validate_ledger(data)
    assert any("may not be labelled saturated" in e for e in errors)
