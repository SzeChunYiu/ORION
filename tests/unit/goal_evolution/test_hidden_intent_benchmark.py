"""Hidden-intent benchmark remains CANNOT_CHECK until real tasks are bound."""
from __future__ import annotations

from orion.goal_evolution.benchmark import (
    HiddenIntentBenchmark,
    load_hidden_intent_benchmark,
)
from orion.goal_evolution.protocol import load_protocol


def test_scaffold_covers_at_least_three_domains_and_required_misspecification_classes() -> None:
    benchmark = load_hidden_intent_benchmark()
    assert isinstance(benchmark, HiddenIntentBenchmark)
    domains = {family.domain for family in benchmark.families}
    assert {
        "scientific_design",
        "retrieval_research",
        "semantic_integration",
        "software_optimization",
    }.issubset(domains)
    classes = {family.misspecification_class for family in benchmark.families}
    assert {
        "adequate",
        "noisy_but_adequate",
        "incomplete_proxy",
        "perverse_proxy",
        "missing_constraint",
        "overconstrained",
        "wrong_measurement",
        "negative_control_implementation",
    }.issubset(classes)
    assert all(family.tasks_bound is False for family in benchmark.families)
    assert all(family.intent_hidden is True for family in benchmark.families)


def test_candidate_view_excludes_hidden_intent_and_protected_metric() -> None:
    benchmark = load_hidden_intent_benchmark()
    for family in benchmark.families:
        view = benchmark.candidate_view(family.family_id)
        assert "hidden_intent" not in view
        assert "protected_metric" not in view
        assert "protected_intent_labels" not in view
        assert view["operational_objective"]
        assert view["tasks_bound"] is False


def test_benchmark_and_protocol_remain_cannot_check_until_real_tasks_bound() -> None:
    benchmark = load_hidden_intent_benchmark()
    protocol = load_protocol()
    assert benchmark.status == "CANNOT_CHECK"
    assert protocol["scientific_terminal"] == "CANNOT_CHECK"
    assert protocol["benchmark"]["status"] == "CANNOT_CHECK"
    assert protocol["benchmark"]["task_bindings"] == "UNBOUND"
    score = benchmark.protected_intent_score("family:scientific_design:perverse_proxy")
    assert score.status == "CANNOT_CHECK"
    assert score.value is None
    assert "PROTECTED_GOAL_EVOLUTION_SUPPORTED" not in {
        benchmark.status,
        protocol["scientific_terminal"],
        score.status,
    }
