"""Deterministic, dependency-light transforms for evidence displays."""

from __future__ import annotations

from statistics import NormalDist
from typing import Collection, Hashable, Iterable, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _numeric_array(values: ArrayLike, *, name: str) -> NDArray[np.float64]:
    raw = np.asarray(values)
    if raw.dtype.kind not in "iuf":
        raise TypeError(f"{name} must contain only real numeric values (not bools or strings)")
    result = np.asarray(raw, dtype=np.float64)
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


def as_finite_1d(
    values: ArrayLike, *, name: str = "values", allow_empty: bool = False
) -> NDArray[np.float64]:
    """Return a finite float vector, rejecting booleans, strings, NaN and inf."""

    result = _numeric_array(values, name=name)
    if result.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if not allow_empty and result.size == 0:
        raise ValueError(f"{name} must not be empty")
    return result


def as_finite_2d(
    values: ArrayLike, *, name: str = "values", allow_empty: bool = False
) -> NDArray[np.float64]:
    """Return a finite float matrix with strict numeric-type validation."""

    result = _numeric_array(values, name=name)
    if result.ndim != 2:
        raise ValueError(f"{name} must be two-dimensional")
    if not allow_empty and result.size == 0:
        raise ValueError(f"{name} must not be empty")
    return result


def wilson_interval(successes: int, total: int, *, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    A zero denominator is rejected rather than plotted as zero evidence.
    """

    if any(
        isinstance(value, bool) or not isinstance(value, (int, np.integer))
        for value in (successes, total)
    ):
        raise TypeError("successes and total must be integers")
    successes, total = int(successes), int(total)
    if total <= 0:
        raise ValueError("total must be positive")
    if successes < 0 or successes > total:
        raise ValueError("successes must satisfy 0 <= successes <= total")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise TypeError("confidence must be numeric")
    confidence = float(confidence)
    if not np.isfinite(confidence) or not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be finite and between zero and one")

    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    proportion = successes / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2.0 * total)) / denominator
    radius = (
        z
        * np.sqrt(proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total))
        / denominator
    )
    return max(0.0, float(centre - radius)), min(1.0, float(centre + radius))


def jaccard_similarity(
    left: Collection[Hashable] | Iterable[Hashable],
    right: Collection[Hashable] | Iterable[Hashable],
    *,
    empty_value: float = 1.0,
) -> float:
    """Set Jaccard similarity, with an explicit both-empty convention."""

    left_set, right_set = set(left), set(right)
    union = left_set | right_set
    if not union:
        if not np.isfinite(empty_value) or not 0.0 <= empty_value <= 1.0:
            raise ValueError("empty_value must be finite and in [0, 1]")
        return float(empty_value)
    return len(left_set & right_set) / len(union)


def ecdf(values: ArrayLike) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return sorted observations and right-continuous empirical probabilities."""

    ordered = np.sort(as_finite_1d(values))
    probabilities = np.arange(1, ordered.size + 1, dtype=np.float64) / ordered.size
    return ordered, probabilities


def pareto_frontier(
    points: ArrayLike, *, maximize: Sequence[bool] | None = None
) -> NDArray[np.bool_]:
    """Return a non-dominated mask; equal points remain co-frontier witnesses."""

    matrix = as_finite_2d(points, name="points")
    if matrix.shape[1] == 0:
        raise ValueError("points must have at least one objective")
    if maximize is None:
        directions = np.ones(matrix.shape[1], dtype=bool)
    else:
        if len(maximize) != matrix.shape[1] or any(
            not isinstance(item, (bool, np.bool_)) for item in maximize
        ):
            raise ValueError("maximize must contain one boolean per objective")
        directions = np.asarray(maximize, dtype=bool)
    oriented = np.where(directions, matrix, -matrix)
    frontier = np.ones(matrix.shape[0], dtype=bool)
    for index, point in enumerate(oriented):
        dominates = np.all(oriented >= point, axis=1) & np.any(oriented > point, axis=1)
        if np.any(dominates):
            frontier[index] = False
    return frontier
