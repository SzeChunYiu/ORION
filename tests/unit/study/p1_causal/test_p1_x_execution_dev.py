from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P1X = ROOT / "research" / "claim_expansion" / "p1"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = _load("p1_x_dev_generator_exec", P1X / "generate_p1_x_dev_cases.py")
execution = _load("p1_x_execution", P1X / "p1_x_execution.py")


def test_p1x_is_exact_on_non_authorizing_dev_contracts() -> None:
    cases = generator.generate_dev_cases()
    scores = [
        execution.score_esrd(case, execution.run_arm(case, "P1X_MINIMAL_SCIENTIFIC_ESCALATION"))
        for case in cases
    ]
    assert sum(scores) == len(cases) == 200


def test_ideal_product_is_extensionally_equal_on_all_dev_cases() -> None:
    for case in generator.generate_dev_cases():
        p1x = execution.run_arm(case, "P1X_MINIMAL_SCIENTIFIC_ESCALATION")
        b3 = execution.run_arm(case, "B3_IDEAL_TYPED_PRODUCT")
        assert b3 == p1x


def test_primary_donor_product_is_strong_but_not_identical_on_dev() -> None:
    cases = generator.generate_dev_cases()
    p1x = [execution.score_esrd(case, execution.run_arm(case, "P1X_MINIMAL_SCIENTIFIC_ESCALATION")) for case in cases]
    b1 = [execution.score_esrd(case, execution.run_arm(case, "B1_DONOR_COMPLETE_GREEDY")) for case in cases]
    assert sum(b1) > 0
    assert sum(p1x) - sum(b1) >= 20


def test_success_authorizes_reframe_has_false_high_level_controls() -> None:
    total = 0
    for case in generator.generate_dev_cases():
        decision = execution.run_arm(case, "B2_SUCCESS_AUTHORIZES_REFRAME")
        total += execution.false_high_level_reframe(case, decision)
    assert total > 0


def test_all_arms_respect_frozen_intervention_budget_on_dev() -> None:
    for case in generator.generate_dev_cases():
        max_checks = case["budget"]["max_interventions"]
        for arm_id in execution.ARM_FUNCTIONS:
            decision = execution.run_arm(case, arm_id)
            assert decision["checks_used"] <= max_checks


def test_p1x_never_executes_on_nonaction_terminals() -> None:
    for case in generator.generate_dev_cases():
        decision = execution.run_arm(case, "P1X_MINIMAL_SCIENTIFIC_ESCALATION")
        if decision["terminal"] not in execution.ACTION_TERMINALS:
            assert decision["revision_class"] is None
            assert decision["reopen_set"] == []
