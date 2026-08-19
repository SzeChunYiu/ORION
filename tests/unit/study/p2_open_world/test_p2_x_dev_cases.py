from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P2X = ROOT / "research" / "claim_expansion" / "p2"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = _load("p2x_dev_generator", P2X / "generate_p2_x_dev_cases.py")
execution = _load("p2x_execution", P2X / "p2_x_execution.py")


def test_dev_grid_is_exactly_200_cases() -> None:
    cases = generator.generate_cases()
    assert len(cases) == 200
    assert len({case["case_id"] for case in cases}) == 200
    counts = Counter((case["domain"], case["archetype"]) for case in cases)
    assert len(counts) == 5 * 8
    assert set(counts.values()) == {5}


def test_p2x_and_ideal_product_are_exact_on_dev() -> None:
    for case in generator.generate_cases():
        p2x = execution.run_arm(case, "P2X_FAIL_CLOSED_ROUTE_AUTHORITY")
        b3 = execution.run_arm(case, "B3_IDEAL_TYPED_ROUTE_PRODUCT")
        assert p2x == b3
        assert execution.score_escd(case, p2x) == 1


def test_primary_baseline_is_strong_and_only_fails_unresolved_route_authority_family() -> None:
    cases = generator.generate_cases()
    b1_correct = []
    failed_archetypes = set()
    for case in cases:
        decision = execution.run_arm(case, "B1_DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT")
        score = execution.score_escd(case, decision)
        b1_correct.append(score)
        if not score:
            failed_archetypes.add(case["archetype"])
    assert sum(b1_correct) == 125
    assert failed_archetypes == {"MATERIAL_ROUTE_UNAVAILABLE", "MATERIAL_ROUTE_CENSORED", "PROVIDER_INVALID"}


def test_global_sufficiency_baseline_is_nontrivial_but_weaker() -> None:
    cases = generator.generate_cases()
    correct = sum(
        execution.score_escd(case, execution.run_arm(case, "B2_GLOBAL_SUFFICIENCY_AGGREGATOR"))
        for case in cases
    )
    assert correct == 50


def test_unavailable_censored_provider_invalid_are_nonnegative_evidence() -> None:
    for archetype in ("MATERIAL_ROUTE_UNAVAILABLE", "MATERIAL_ROUTE_CENSORED", "PROVIDER_INVALID"):
        cases = [case for case in generator.generate_cases() if case["archetype"] == archetype]
        assert cases
        for case in cases:
            p2x = execution.run_arm(case, "P2X_FAIL_CLOSED_ROUTE_AUTHORITY")
            b1 = execution.run_arm(case, "B1_DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT")
            assert p2x["task_terminal"] == "CANNOT_CHECK"
            assert b1["task_terminal"] == "TASK_STOP"
            assert any(value == "ROUTE_CANNOT_CHECK" for value in p2x["route_decisions"].values())


def test_question_processing_is_task_level_not_route_local() -> None:
    cases = [case for case in generator.generate_cases() if case["archetype"] == "ACQUIRED_NOT_QUESTION_PROCESSED"]
    assert cases
    for case in cases:
        decision = execution.run_arm(case, "P2X_FAIL_CLOSED_ROUTE_AUTHORITY")
        assert set(decision["route_decisions"].values()) == {"ROUTE_STOP"}
        assert decision["task_terminal"] == "CONTINUE"


def test_duplicate_route_control_really_duplicates_content_identity() -> None:
    cases = [case for case in generator.generate_cases() if case["archetype"] == "DUPLICATE_ROUTE_COVERAGE"]
    assert cases
    for case in cases:
        routes = case["candidate_visible"]["routes"]
        assert routes[0]["content_items"][0]["content_id"] == routes[1]["content_items"][0]["content_id"]
        assert execution.run_arm(case, "P2X_FAIL_CLOSED_ROUTE_AUTHORITY")["task_terminal"] == "CONTINUE"


def test_clean_cases_stop_without_unnecessary_cannot_check() -> None:
    for case in generator.generate_cases():
        if case["archetype"] != "ALL_OBLIGATIONS_DISCHARGED":
            continue
        for arm_id in execution.ARM_FUNCTIONS:
            decision = execution.run_arm(case, arm_id)
            assert decision["task_terminal"] == "TASK_STOP"
            assert execution.unnecessary_cannot_check_clean(case, decision) == 0
