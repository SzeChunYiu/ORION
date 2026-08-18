"""Frozen statistics for P1 epistemic-mutation necessity v2.2.3.

Standard-library only and independent of candidate policies.  The primary H1
parent set is deliberately generic: later pre-outcome donor absorption may add
strong parents without changing the statistical semantics or dropping earlier
comparators.
"""

from __future__ import annotations

from math import comb
import random
from typing import Mapping, Sequence


def exact_mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    lo = min(b, c)
    tail = sum(comb(n, i) for i in range(lo + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def paired_bootstrap(
    left: Sequence[float],
    right: Sequence[float],
    *,
    seed: int,
    resamples: int = 10000,
) -> dict[str, float | int]:
    if len(left) != len(right) or not left:
        raise ValueError("paired bootstrap requires equal non-empty vectors")
    n = len(left)
    observed = sum(a - b for a, b in zip(left, right, strict=True)) / n
    rng = random.Random(seed)
    draws = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(n):
            i = rng.randrange(n)
            total += left[i] - right[i]
        draws.append(total / n)
    draws.sort()
    lo = draws[max(0, int(0.025 * resamples))]
    hi = draws[min(resamples - 1, int(0.975 * resamples) - 1)]
    return {
        "n": n,
        "difference": observed,
        "ci95_low": lo,
        "ci95_high": hi,
        "seed": seed,
        "resamples": resamples,
    }


def _by_arm(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, Mapping[str, object]]]:
    out: dict[str, dict[str, Mapping[str, object]]] = {}
    for row in rows:
        arm = str(row["arm_id"])
        task = str(row["task_id"])
        if task in out.setdefault(arm, {}):
            raise ValueError(f"duplicate arm/task row:{arm}:{task}")
        out[arm][task] = row
    return out


def _paired_rows(
    rows: Sequence[Mapping[str, object]],
    left_arm: str,
    right_arm: str,
    *,
    subset_field: str | None = None,
) -> tuple[list[Mapping[str, object]], list[Mapping[str, object]]]:
    by_arm = _by_arm(rows)
    if left_arm not in by_arm or right_arm not in by_arm:
        raise ValueError("missing arm")
    left_map = by_arm[left_arm]
    right_map = by_arm[right_arm]
    if set(left_map) != set(right_map):
        raise ValueError("paired task sets differ")
    left: list[Mapping[str, object]] = []
    right: list[Mapping[str, object]] = []
    for task_id in sorted(left_map):
        a, b = left_map[task_id], right_map[task_id]
        if subset_field is not None:
            a_in = bool(a[subset_field])
            b_in = bool(b[subset_field])
            if a_in != b_in:
                raise ValueError(f"candidate-dependent subset:{subset_field}")
            if not a_in:
                continue
        left.append(a)
        right.append(b)
    if not left:
        raise ValueError("empty paired subset")
    return left, right


def binary_contrast(
    rows: Sequence[Mapping[str, object]],
    *,
    left_arm: str,
    right_arm: str,
    field: str,
    subset_field: str | None,
    seed: int,
    resamples: int,
) -> dict[str, object]:
    left_rows, right_rows = _paired_rows(
        rows,
        left_arm,
        right_arm,
        subset_field=subset_field,
    )
    left = [1.0 if bool(item[field]) else 0.0 for item in left_rows]
    right = [1.0 if bool(item[field]) else 0.0 for item in right_rows]
    boot = paired_bootstrap(left, right, seed=seed, resamples=resamples)
    b = sum(a > c for a, c in zip(left, right, strict=True))
    c = sum(c > a for a, c in zip(left, right, strict=True))
    return {
        **boot,
        "field": field,
        "subset_field": subset_field,
        "left_rate": sum(left) / len(left),
        "right_rate": sum(right) / len(right),
        "mcnemar_b": b,
        "mcnemar_c": c,
        "mcnemar_p": exact_mcnemar_p(b, c),
    }


def continuous_contrast(
    rows: Sequence[Mapping[str, object]],
    *,
    left_arm: str,
    right_arm: str,
    field: str,
    subset_field: str | None,
    seed: int,
    resamples: int,
) -> dict[str, object]:
    left_rows, right_rows = _paired_rows(
        rows,
        left_arm,
        right_arm,
        subset_field=subset_field,
    )
    left = [float(item[field]) for item in left_rows]
    right = [float(item[field]) for item in right_rows]
    return {
        **paired_bootstrap(left, right, seed=seed, resamples=resamples),
        "field": field,
        "subset_field": subset_field,
        "left_mean": sum(left) / len(left),
        "right_mean": sum(right) / len(right),
    }


def holm_many(
    pvalues: Sequence[float],
    *,
    alpha: float = 0.05,
) -> dict[str, object]:
    """Holm step-down family-wise correction for an arbitrary parent set."""

    if not pvalues:
        raise ValueError("Holm requires at least one p-value")
    indexed = sorted(enumerate(float(p) for p in pvalues), key=lambda item: item[1])
    passed = [False] * len(pvalues)
    stopped = False
    thresholds = [0.0] * len(pvalues)
    for rank, (index, pvalue) in enumerate(indexed):
        threshold = alpha / float(len(pvalues) - rank)
        thresholds[index] = threshold
        if stopped or pvalue > threshold:
            stopped = True
            passed[index] = False
        else:
            passed[index] = True
    return {
        "alpha": alpha,
        "pvalues": [float(item) for item in pvalues],
        "thresholds_by_input": thresholds,
        "passes_by_input": passed,
        "all_pass": all(passed),
    }


def holm_two(
    p1: float,
    p2: float,
    *,
    alpha: float = 0.05,
) -> dict[str, object]:
    """Compatibility wrapper retained for the earlier frozen tests."""

    result = holm_many((p1, p2), alpha=alpha)
    passes = result["passes_by_input"]
    assert isinstance(passes, list)
    return {
        "alpha": alpha,
        "p1_pass": bool(passes[0]),
        "p2_pass": bool(passes[1]),
        "all_pass": bool(result["all_pass"]),
    }


def analyze_necessity_campaign(
    rows: Sequence[Mapping[str, object]],
    *,
    full_arm: str,
    h1_parents: Sequence[str],
    control_parent: str,
    parameters: Mapping[str, object],
) -> dict[str, object]:
    parents = tuple(str(item) for item in h1_parents)
    if not parents:
        raise ValueError("at least one frozen H1 parent is required")
    if len(set(parents)) != len(parents):
        raise ValueError("duplicate H1 parent")
    if full_arm in parents:
        raise ValueError("full arm cannot be its own parent")

    seed = int(parameters["bootstrap_seed"])
    resamples = int(parameters.get("bootstrap_resamples", 10000))
    margin = float(parameters["H1_superiority_margin_each_parent"])
    ni = float(parameters["H2_control_protected_success_noninferiority_margin"])
    whole_ni = float(parameters["total_protected_success_noninferiority_margin"])
    cost_margin = float(parameters["cost_noninferiority_margin_units"])

    h1 = []
    for index, parent in enumerate(parents):
        contrast = binary_contrast(
            rows,
            left_arm=full_arm,
            right_arm=parent,
            field="protected_root_task_success",
            subset_field="hidden_shift",
            seed=seed + index,
            resamples=resamples,
        )
        h1.append({"parent": parent, **contrast})
    holm = holm_many([float(item["mcnemar_p"]) for item in h1])

    control_success = binary_contrast(
        rows,
        left_arm=full_arm,
        right_arm=control_parent,
        field="protected_root_task_success",
        subset_field="negative_control",
        seed=seed + 100,
        resamples=resamples,
    )
    full_control, _ = _paired_rows(
        rows,
        full_arm,
        control_parent,
        subset_field="negative_control",
    )
    unnecessary_count = sum(
        bool(item["unnecessary_high_level_reframe"])
        for item in full_control
    )

    whole_grid = []
    cost = []
    for index, parent in enumerate(parents):
        whole_grid.append(
            {
                "parent": parent,
                **binary_contrast(
                    rows,
                    left_arm=full_arm,
                    right_arm=parent,
                    field="protected_root_task_success",
                    subset_field=None,
                    seed=seed + 200 + index,
                    resamples=resamples,
                ),
            }
        )
        cost.append(
            {
                "parent": parent,
                **continuous_contrast(
                    rows,
                    left_arm=full_arm,
                    right_arm=parent,
                    field="spent_budget",
                    subset_field=None,
                    seed=seed + 300 + index,
                    resamples=resamples,
                ),
            }
        )

    full_all, _ = _paired_rows(rows, full_arm, parents[0])
    sibling_regressions = sum(
        bool(item["protected_sibling_regression"])
        for item in full_all
    )
    forbidden = sum(
        bool(item["forbidden_high_level_mutation"])
        for item in full_all
    )
    full_cost_mean = float(cost[0]["left_mean"])
    strongest_parent_cost_mean = max(float(item["right_mean"]) for item in cost)
    cost_guard = {
        "full_mean": full_cost_mean,
        "maximum_strong_parent_mean": strongest_parent_cost_mean,
        "margin_units": cost_margin,
        "difference_from_maximum_parent": full_cost_mean - strongest_parent_cost_mean,
    }

    gates = {
        "h1_each_parent_practical": all(
            float(item["difference"]) >= margin for item in h1
        ),
        "h1_each_parent_ci_positive": all(
            float(item["ci95_low"]) > 0.0 for item in h1
        ),
        "h1_holm": bool(holm["all_pass"]),
        "h2_zero_unnecessary_reframe": unnecessary_count == 0,
        "h2_control_success_noninferior": (
            float(control_success["ci95_low"]) >= -ni
        ),
        "whole_grid_success_noninferior": all(
            float(item["ci95_low"]) >= -whole_ni for item in whole_grid
        ),
        "zero_protected_sibling_regression": sibling_regressions == 0,
        "zero_forbidden_high_level_mutation": forbidden == 0,
        "cost_within_margin": (
            float(cost_guard["difference_from_maximum_parent"]) <= cost_margin
        ),
    }
    return {
        "full_arm": full_arm,
        "h1_parents": list(parents),
        "h1_hidden_shift": h1,
        "h1_holm": holm,
        "h2_control_parent": control_parent,
        "h2_control_success": control_success,
        "h2_full_unnecessary_reframe_count": unnecessary_count,
        "whole_grid_success": whole_grid,
        "cost": cost,
        "cost_guard": cost_guard,
        "full_protected_sibling_regression_count": sibling_regressions,
        "full_forbidden_high_level_mutation_count": forbidden,
        "gates": gates,
        "all_support_gates_pass": all(gates.values()),
    }


__all__ = [
    "analyze_necessity_campaign",
    "binary_contrast",
    "continuous_contrast",
    "exact_mcnemar_p",
    "holm_many",
    "holm_two",
    "paired_bootstrap",
]
