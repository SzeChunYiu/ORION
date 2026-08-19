from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P2X = ROOT / "research" / "claim_expansion" / "p2"
CHECKER = P2X / "check_p2_x_protocol.py"
PROTOCOL = P2X / "P2_X_PROTOCOL_V1.md"
SCHEMA = P2X / "P2_X_CASE_V1.schema.json"
REGISTRY = P2X / "P2_X_BASELINE_REGISTRY_V1.json"

spec = importlib.util.spec_from_file_location("p2_x_checker", CHECKER)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def _payloads():
    return PROTOCOL.read_text(), json.loads(SCHEMA.read_text()), json.loads(REGISTRY.read_text())


def test_committed_protocol_is_valid() -> None:
    assert checker.validate_protocol(*_payloads()) == ()


def test_p2x_cannot_self_promote_before_execution() -> None:
    protocol, schema, registry = _payloads()
    mutated = copy.deepcopy(registry)
    mutated["result_authority"] = "SUPPORTED"
    arm = next(item for item in mutated["arms"] if item["id"] == "P2X_FAIL_CLOSED_ROUTE_AUTHORITY")
    arm["result_authority"] = "SUPPORTED"
    errors = checker.validate_protocol(protocol, schema, mutated)
    assert "registry_result_not_cannot_check" in errors
    assert "p2x_result_not_cannot_check" in errors


def test_ideal_product_equivalence_boundary_cannot_be_removed() -> None:
    protocol, schema, registry = _payloads()
    mutated = copy.deepcopy(registry)
    arm = next(item for item in mutated["arms"] if item["id"] == "B3_IDEAL_TYPED_ROUTE_PRODUCT")
    arm["expected_relation_to_p2x"] = "P2X_SUPERIOR"
    arm["significance_test"] = True
    errors = checker.validate_protocol(protocol, schema, mutated)
    assert "b3_equivalence_boundary_missing" in errors
    assert "b3_significance_forbidden" in errors


def test_protected_scale_factorization_is_frozen() -> None:
    protocol, schema, registry = _payloads()
    mutated = copy.deepcopy(registry)
    mutated["protected_scale"].update({"domains": 4, "archetypes_per_domain": 10, "variants_per_archetype": 10, "total_cases": 400})
    assert "protected_scale_drift" in checker.validate_protocol(protocol, schema, mutated)


def test_unavailable_and_censored_states_cannot_disappear() -> None:
    protocol, schema, registry = _payloads()
    mutated = copy.deepcopy(schema)
    enum = mutated["properties"]["candidate_visible"]["properties"]["routes"]["items"]["properties"]["state"]["enum"]
    enum.remove("CENSORED")
    assert "route_state_enum_drift" in checker.validate_protocol(protocol, mutated, registry)


def test_question_processing_coordinate_is_mandatory() -> None:
    protocol, schema, registry = _payloads()
    mutated = copy.deepcopy(schema)
    content = mutated["properties"]["candidate_visible"]["properties"]["routes"]["items"]["properties"]["content_items"]["items"]
    content["required"].remove("question_processed")
    assert "content_processing_contract_drift" in checker.validate_protocol(protocol, mutated, registry)


def test_primary_margin_cannot_be_relaxed() -> None:
    protocol, schema, registry = _payloads()
    mutated = copy.deepcopy(registry)
    mutated["primary_hypothesis"]["minimum_absolute_escd_gain"] = 0.01
    assert "primary_margin_drift" in checker.validate_protocol(protocol, schema, mutated)


def test_route_cannot_check_terminal_cannot_be_deleted() -> None:
    protocol, schema, registry = _payloads()
    mutated = copy.deepcopy(schema)
    enum = mutated["properties"]["protected_gold"]["properties"]["route_decisions"]["additionalProperties"]["enum"]
    enum.remove("ROUTE_CANNOT_CHECK")
    assert "route_terminal_enum_drift" in checker.validate_protocol(protocol, mutated, registry)
