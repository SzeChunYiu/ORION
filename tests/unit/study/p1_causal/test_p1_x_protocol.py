from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P1X = ROOT / "research" / "claim_expansion" / "p1"
CHECKER = P1X / "check_p1_x_protocol.py"
PROTOCOL = P1X / "P1_X_PROTOCOL_V1.md"
SCHEMA = P1X / "SCIENTIFIC_REVISION_RESPONSIBILITY_CASE_V1.schema.json"
REGISTRY = P1X / "P1_X_BASELINE_REGISTRY_V1.json"
LEDGER = P1X / "P1_X_CLAIM_EXPANSION_LEDGER_V1.md"

_spec = importlib.util.spec_from_file_location("p1_x_protocol_checker", CHECKER)
assert _spec is not None and _spec.loader is not None
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)


def _payloads():
    return (
        PROTOCOL.read_text(),
        json.loads(SCHEMA.read_text()),
        json.loads(REGISTRY.read_text()),
        LEDGER.read_text(),
    )


def test_committed_p1_x_protocol_is_valid() -> None:
    assert checker.validate_protocol(*_payloads()) == ()


def test_result_authority_cannot_be_promoted_before_execution() -> None:
    protocol, schema, registry, ledger = _payloads()
    mutated = copy.deepcopy(registry)
    mutated["result_authority"] = "SUPPORTED"
    errors = checker.validate_protocol(protocol, schema, mutated, ledger)
    assert "registry_result_authority:SUPPORTED" in errors


def test_candidate_arm_cannot_self_promote() -> None:
    protocol, schema, registry, ledger = _payloads()
    mutated = copy.deepcopy(registry)
    p1x = next(arm for arm in mutated["arms"] if arm["id"] == "P1X_MINIMAL_SCIENTIFIC_ESCALATION")
    p1x["result_authority"] = "SUPPORTED"
    errors = checker.validate_protocol(protocol, schema, mutated, ledger)
    assert "p1x_result_authority:SUPPORTED" in errors


def test_ideal_product_boundary_cannot_be_removed() -> None:
    protocol, schema, registry, ledger = _payloads()
    mutated = copy.deepcopy(registry)
    b3 = next(arm for arm in mutated["arms"] if arm["id"] == "B3_IDEAL_TYPED_PRODUCT")
    b3["expected_relation_to_p1x"] = "P1X_SUPERIOR"
    b3["significance_test"] = True
    errors = checker.validate_protocol(protocol, schema, mutated, ledger)
    assert "b3_equivalence_boundary_missing" in errors
    assert "b3_must_not_use_significance_test" in errors


def test_protected_gold_cannot_leak_into_candidate_visible_schema() -> None:
    protocol, schema, registry, ledger = _payloads()
    mutated = copy.deepcopy(schema)
    mutated["properties"]["candidate_visible"]["properties"]["causal_responsibility_set"] = {
        "type": "array"
    }
    errors = checker.validate_protocol(protocol, mutated, registry, ledger)
    assert "protected_gold_leaked_to_candidate_visible:causal_responsibility_set" in errors


def test_unresolved_terminal_cannot_be_deleted() -> None:
    protocol, schema, registry, ledger = _payloads()
    mutated = copy.deepcopy(schema)
    terminals = mutated["properties"]["protected_gold"]["properties"]["correct_terminal"]["enum"]
    terminals.remove("UNRESOLVED")
    errors = checker.validate_protocol(protocol, mutated, registry, ledger)
    assert "terminal_enum_drift" in errors


def test_revision_responsibility_class_cannot_disappear() -> None:
    protocol, schema, registry, ledger = _payloads()
    mutated = copy.deepcopy(schema)
    classes = mutated["properties"]["revision_classes"]["items"]["enum"]
    classes.remove("EVALUATOR_AUTHORITY_REVISION")
    errors = checker.validate_protocol(protocol, mutated, registry, ledger)
    assert "revision_class_enum_drift" in errors


def test_primary_margin_cannot_be_relaxed_after_freeze() -> None:
    protocol, schema, registry, ledger = _payloads()
    mutated = copy.deepcopy(registry)
    mutated["primary_hypothesis"]["minimum_absolute_esrd_gain"] = 0.01
    errors = checker.validate_protocol(protocol, schema, mutated, ledger)
    assert "primary_practical_margin_drift" in errors


def test_protected_case_count_cannot_drift() -> None:
    protocol, schema, registry, ledger = _payloads()
    mutated = copy.deepcopy(registry)
    mutated["protected_scale"]["total_cases"] = 40
    errors = checker.validate_protocol(protocol, schema, mutated, ledger)
    assert "protected_scale_drift" in errors


def test_successor_claim_cannot_be_promoted_in_ledger() -> None:
    protocol, schema, registry, ledger = _payloads()
    mutated = ledger.replace(
        "State: `CANNOT_CHECK`.",
        "State: `SUPPORTED`.",
        1,
    )
    errors = checker.validate_protocol(protocol, schema, registry, mutated)
    assert "ledger_successor_authority_not_cannot_check:A1" in errors


def test_preoutcome_freeze_marker_cannot_disappear() -> None:
    protocol, schema, registry, ledger = _payloads()
    mutated = protocol.replace(
        "PROTOCOL_FROZEN__NO_PROTECTED_OUTCOMES_ACCESSED",
        "PROTECTED_OUTCOMES_ACCESSED",
    )
    errors = checker.validate_protocol(mutated, schema, registry, ledger)
    assert "protocol_missing_preoutcome_freeze_terminal" in errors
