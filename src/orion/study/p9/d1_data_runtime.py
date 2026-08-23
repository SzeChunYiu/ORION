"""Execution data adapter for P9 D1 protocol v1.2.

The original D1 generator remains preserved as pre-outcome failure history.  This
adapter patches only dependency-mutation generation: reverse the currently
stored directed dependency edges and fail closed if the canonical topology does
not change.
"""

from __future__ import annotations

from . import d1 as _base
from .d1 import (
    COMPARISON_COORDINATES,
    D1Dataset,
    D1Domain,
    D1Instance,
    D1Label,
    D1Split,
    D1View,
    DOUBLE_MUTATIONS,
    SINGLE_MUTATIONS,
    classify_methods,
)


_ORIGINAL_MUTATED_VALUE = _base._mutated_value
_ORIGINAL_MUTATE_METHOD = _base.mutate_method


def _mutated_value_v12(method, coordinate: str, salt: str):
    if coordinate != "dependencies":
        return _ORIGINAL_MUTATED_VALUE(method, coordinate, salt)
    if not method.dependencies:
        raise ValueError("D1 dependency mutation requires at least one directed edge")
    reversed_edges = tuple((right, left) for left, right in method.dependencies)
    if all(left == right for left, right in method.dependencies):
        raise ValueError("D1 dependency mutation cannot use self-loop-only seed")
    return reversed_edges


def mutate_method(method, *, coordinates, seed: str):
    before = _base._dependency_signature(method)
    out = _ORIGINAL_MUTATE_METHOD(method, coordinates=coordinates, seed=seed)
    if "dependencies" in set(coordinates):
        after = _base._dependency_signature(out)
        if after == before:
            raise ValueError("D1 dependency mutation did not change topology")
    return out


# Generation helpers in d1.py resolve these globals dynamically.
_base._mutated_value = _mutated_value_v12
_base.mutate_method = mutate_method

generate_d1_dataset = _base.generate_d1_dataset
unresolved_method = _base.unresolved_method


__all__ = [
    "COMPARISON_COORDINATES",
    "D1Dataset",
    "D1Domain",
    "D1Instance",
    "D1Label",
    "D1Split",
    "D1View",
    "DOUBLE_MUTATIONS",
    "SINGLE_MUTATIONS",
    "classify_methods",
    "generate_d1_dataset",
    "mutate_method",
    "unresolved_method",
]
