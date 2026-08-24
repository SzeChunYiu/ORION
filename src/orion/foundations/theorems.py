"""Deterministic local theorem and countermodel suite for issue #1220."""

from __future__ import annotations

from collections.abc import Callable

from .theorem_capability import (
    theorem_t12_open_world,
    theorem_t13_transport,
    theorem_t14_diagnosis,
    theorem_t15_method_expansion,
    theorem_t16_placement,
    theorem_t17_allocation,
    theorem_t18_responsibility,
)
from .theorem_discharge import (
    theorem_t4_t5_discharge,
    theorem_t6_t8_normal_form,
    theorem_t9_full_abstraction,
    theorem_t10_t11_composition_revocation,
)
from .theorem_integrity import (
    answer_laundering_control,
    theorem_t19_self_promotion,
    theorem_t20_integrity,
    theorem_t21_governed_evolution,
    theorem_t22_synthesis_checking_gap,
    theorem_t23_coupled_advance,
)
from .theorem_semantics import (
    theorem_t0_non_tautological,
    theorem_t1_native_conservativity,
    theorem_t2_fibre,
    theorem_t3_risk,
)
from .theorem_types import TheoremResult


def run_local_theorems() -> tuple[TheoremResult, ...]:
    results: list[TheoremResult] = []
    producers: tuple[Callable[[], TheoremResult | list[TheoremResult]], ...] = (
        theorem_t0_non_tautological,
        theorem_t1_native_conservativity,
        theorem_t2_fibre,
        theorem_t3_risk,
        theorem_t4_t5_discharge,
        theorem_t6_t8_normal_form,
        theorem_t9_full_abstraction,
        theorem_t10_t11_composition_revocation,
        theorem_t12_open_world,
        theorem_t13_transport,
        theorem_t14_diagnosis,
        theorem_t15_method_expansion,
        theorem_t16_placement,
        theorem_t17_allocation,
        theorem_t18_responsibility,
        theorem_t19_self_promotion,
        theorem_t20_integrity,
        theorem_t21_governed_evolution,
        theorem_t22_synthesis_checking_gap,
        theorem_t23_coupled_advance,
        answer_laundering_control,
    )
    for producer in producers:
        produced = producer()
        if isinstance(produced, list):
            results.extend(produced)
        else:
            results.append(produced)
    return tuple(results)


__all__ = ["TheoremResult", "run_local_theorems"]
