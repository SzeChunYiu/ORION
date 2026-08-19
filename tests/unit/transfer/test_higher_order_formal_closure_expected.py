from __future__ import annotations

import json
from pathlib import Path

from orion.transfer.v2.higher_order_formal_closure import (
    build_formal_closure_report,
    formal_parent_dispositions,
    run_finite_formal_closure_checks,
)


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "extensions" / "p6-higher-order-epistemic-mechanics"
EXPECTED = RESEARCH / "FORMAL_CLOSURE_EXPECTED_V1.json"
PARENT_MAP = RESEARCH / "FORMAL_PARENT_MAP_V1.json"


def test_formal_closure_matches_pre_frozen_exact_counts_and_terminal() -> None:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    finite = run_finite_formal_closure_checks()
    closure = build_formal_closure_report()

    assert finite.generated_revision_signatures == expected["generated_revision_signatures"]
    assert finite.preorder_reflexive_cases == expected["expected_preorder_reflexive_cases"]
    assert finite.preorder_transitivity_checks == expected["expected_preorder_transitivity_checks"]
    assert finite.strict_minimality_checks == expected["expected_strict_minimality_checks"]
    for field, value in expected["required_invariants"].items():
        assert getattr(finite, field) is value

    assert closure.parent_component_count == expected["expected_parent_component_count"]
    assert closure.new_unified_primitive_count == expected["expected_new_unified_primitive_count"]
    assert closure.recommendation.value == expected["expected_recommendation"]
    assert closure.grants_scientific_authority is False
    assert closure.grants_novelty_authority is False
    assert closure.grants_paper_promotion_authority is False


def test_formal_checker_parent_dispositions_match_frozen_parent_map() -> None:
    frozen = json.loads(PARENT_MAP.read_text(encoding="utf-8"))
    code = {item.component_id: item for item in formal_parent_dispositions()}
    mapped = {item["component_id"]: item for item in frozen["components"]}

    assert set(code) == set(mapped)
    for component_id, item in code.items():
        row = mapped[component_id]
        assert list(item.parent_source_ids) == row["parents"]
        assert item.disposition == row["disposition"]
        assert item.new_unified_primitive_required is False
    assert frozen["new_unified_primitive_count"] == 0
    assert frozen["unified_calculus_novelty"] == "STRUCK"
