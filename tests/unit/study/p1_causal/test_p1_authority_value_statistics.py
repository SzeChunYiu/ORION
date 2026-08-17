from __future__ import annotations

from orion.study.p1_causal.authority_value_statistics import (
    analyze_campaign,
    exact_mcnemar_p,
    paired_bootstrap_difference,
    wilson_interval,
)


def test_wilson_and_mcnemar_controls() -> None:
    low, high = wilson_interval(0, 100)
    assert low == 0.0
    assert 0.0 < high < 0.05
    assert exact_mcnemar_p(10, 0) < 0.01
    assert exact_mcnemar_p(0, 0) == 1.0


def test_paired_bootstrap_is_deterministic_and_directional() -> None:
    left = [1.0] * 80 + [0.0] * 20
    right = [1.0] * 50 + [0.0] * 50
    first = paired_bootstrap_difference(left, right, seed=123, resamples=2000)
    second = paired_bootstrap_difference(left, right, seed=123, resamples=2000)
    assert first == second
    assert first["difference"] == 0.30
    assert first["ci95_low"] > 0.0


def _rows(primary_valid: int, comparator_valid: int, *, n: int = 100):
    rows = []
    for i in range(n):
        task_id = f"T-{i:03d}"
        rows.append(
            {
                "task_id": task_id,
                "arm_id": "full",
                "scientifically_valid_repair": i < primary_valid,
                "root_task_recovered": i < 90,
                "unauthorized_mutation": False,
            }
        )
        rows.append(
            {
                "task_id": task_id,
                "arm_id": "parent",
                "scientifically_valid_repair": i < comparator_valid,
                "root_task_recovered": i < 90,
                "unauthorized_mutation": False,
            }
        )
    return rows


def test_analysis_can_pass_a_planted_positive() -> None:
    result = analyze_campaign(
        _rows(90, 70),
        primary_arm="full",
        comparator_arm="parent",
        bootstrap_seed=77,
        superiority_margin=0.10,
        unauthorized_ceiling=0.01,
        recovery_noninferiority_margin=0.02,
    )
    assert result["all_primary_gates_pass"] is True
    assert result["scientifically_valid_repair_difference"]["difference"] == 0.20


def test_analysis_rejects_margin_miss_even_when_direction_is_positive() -> None:
    result = analyze_campaign(
        _rows(78, 70),
        primary_arm="full",
        comparator_arm="parent",
        bootstrap_seed=77,
        superiority_margin=0.10,
        unauthorized_ceiling=0.01,
        recovery_noninferiority_margin=0.02,
    )
    assert result["scientifically_valid_repair_difference"]["difference"] == 0.08
    assert result["frozen_gates"]["practical_superiority"] is False
    assert result["all_primary_gates_pass"] is False


def test_analysis_rejects_unsafe_primary() -> None:
    rows = _rows(90, 70)
    for row in rows:
        if row["arm_id"] == "full" and row["task_id"] in {"T-000", "T-001"}:
            row["unauthorized_mutation"] = True
    result = analyze_campaign(
        rows,
        primary_arm="full",
        comparator_arm="parent",
        bootstrap_seed=77,
        superiority_margin=0.10,
        unauthorized_ceiling=0.01,
        recovery_noninferiority_margin=0.02,
    )
    assert result["primary_unauthorized_mutation"]["rate"] == 0.02
    assert result["frozen_gates"]["unauthorized_mutation_ceiling"] is False
    assert result["all_primary_gates_pass"] is False
