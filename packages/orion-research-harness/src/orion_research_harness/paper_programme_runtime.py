from __future__ import annotations

import math
from enum import Enum
from typing import Mapping


# P11 — State as Computation -------------------------------------------------

def p11_accessible_rank_dimension(d: int, s: int) -> int:
    """Exact size-s parity-query accessible-rank lower bound: binom(d, s)."""

    if isinstance(d, bool) or isinstance(s, bool) or not isinstance(d, int) or not isinstance(s, int):
        raise TypeError("d and s must be integers")
    if d < 1 or s < 1 or s > d:
        raise ValueError("require d >= s >= 1")
    return math.comb(d, s)


def p11_one_step_future_coverage(*, retained: int, universe: int) -> float:
    if isinstance(retained, bool) or isinstance(universe, bool) or not isinstance(retained, int) or not isinstance(universe, int):
        raise TypeError("retained and universe must be integers")
    if universe < 1 or retained < 0 or retained > universe:
        raise ValueError("require 0 <= retained <= universe and universe > 0")
    return retained / universe


def p11_cached_future_coverage(*, retained: int, universe: int, cache_count: int) -> float:
    if isinstance(cache_count, bool) or not isinstance(cache_count, int):
        raise TypeError("cache_count must be an integer")
    if cache_count < 0:
        raise ValueError("cache_count must be non-negative")
    one = p11_one_step_future_coverage(retained=retained, universe=universe)
    return 1.0 - (1.0 - one) ** cache_count


def p11_expected_distinct_requests(*, universe: int, query_count: int) -> float:
    if isinstance(universe, bool) or isinstance(query_count, bool) or not isinstance(universe, int) or not isinstance(query_count, int):
        raise TypeError("universe and query_count must be integers")
    if universe < 1 or query_count < 0:
        raise ValueError("universe must be positive and query_count non-negative")
    return universe * (1.0 - (1.0 - 1.0 / universe) ** query_count)


# P12 — Adaptive State–Reasoning Co-Design ----------------------------------
_P12_OPTIONS = ((0, 0), (1, 1), (2, 0), (0, 2))


def p12_success(allocation: tuple[int, int], requirement: tuple[int, int]) -> bool:
    if len(allocation) != 2 or len(requirement) != 2:
        raise ValueError("allocation and requirement must have two coordinates")
    return allocation[0] >= requirement[0] and allocation[1] >= requirement[1]


def p12_joint_alloc(state_signal: float, reasoning_signal: float, *, budget: int = 2) -> tuple[int, int]:
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 0:
        raise ValueError("budget must be a non-negative integer")
    if isinstance(state_signal, bool) or isinstance(reasoning_signal, bool) or not isinstance(state_signal, (int, float)) or not isinstance(reasoning_signal, (int, float)):
        raise TypeError("allocation signals must be numeric")
    options = tuple(option for option in _P12_OPTIONS if sum(option) <= budget)
    if not options:
        return (0, 0)
    distances = [
        ((float(state_signal) - state_cost) ** 2 + (float(reasoning_signal) - reason_cost) ** 2, index, (state_cost, reason_cost))
        for index, (state_cost, reason_cost) in enumerate(options)
    ]
    return min(distances)[2]


# P13 — Responsibility-Carrying State ---------------------------------------
class P13Action(str, Enum):
    REUSE = "REUSE"
    REOPEN = "REOPEN"
    CANNOT_CHECK = "CANNOT_CHECK"


_P13_TASKS = ("PREDICT", "DECIDE", "INTERVENE", "VERIFY", "REPAIR")
_P13_SUPPORT = {
    "Z1": frozenset(("PREDICT", "DECIDE")),
    "Z2": frozenset(("PREDICT", "DECIDE", "INTERVENE", "VERIFY")),
    "Z3": frozenset(_P13_TASKS),
}


def p13_responsibility_supported(state_class: str, task: str) -> bool:
    if state_class not in _P13_SUPPORT:
        raise ValueError(f"unknown responsibility-carrying state class: {state_class}")
    if task not in _P13_TASKS:
        raise ValueError(f"unknown downstream responsibility: {task}")
    return task in _P13_SUPPORT[state_class]


def p13_rcs_action(state_class: str, task: str, *, recoverable: bool) -> P13Action:
    if not isinstance(recoverable, bool):
        raise TypeError("recoverable must be boolean")
    if p13_responsibility_supported(state_class, task):
        return P13Action.REUSE
    return P13Action.REOPEN if recoverable else P13Action.CANNOT_CHECK


# P14 — ORION-RSE specification-separated governance ------------------------
_P14_PRIVATE_KEYS = frozenset(("case_id", "stratum", "gold_disposition", "rationale"))
_P14_REQUIRED_FACTS = frozenset(
    (
        "evidence_integrity",
        "frozen_protocol",
        "identifiable",
        "positive",
        "donor_owned",
        "interaction_only",
        "live_negative_history",
        "material_new_evidence",
    )
)


def p14_governance_disposition(case_facts: Mapping[str, object]) -> str:
    """The P14C gold-stripped full governance policy.

    Gold/private adjudication fields are rejected rather than silently ignored so
    the shared harness cannot accidentally turn an evaluator fixture into policy
    input.
    """

    keys = set(case_facts)
    leaked = sorted(keys & _P14_PRIVATE_KEYS)
    if leaked:
        raise ValueError("private/gold adjudication fields cannot enter policy input: " + ",".join(leaked))
    missing = sorted(_P14_REQUIRED_FACTS - keys)
    if missing:
        raise ValueError("missing P14 governance facts: " + ",".join(missing))
    facts: dict[str, bool] = {}
    for key in _P14_REQUIRED_FACTS:
        value = case_facts[key]
        if not isinstance(value, bool):
            raise TypeError(f"P14 fact {key} must be boolean")
        facts[key] = value

    if not facts["evidence_integrity"] or not facts["frozen_protocol"] or not facts["identifiable"]:
        return "CANNOT_CHECK"
    if not facts["positive"]:
        return "NEGATIVE"
    if facts["donor_owned"]:
        return "SUBSUMED"
    if facts["interaction_only"]:
        return "INTERACTION_ONLY"
    if facts["live_negative_history"] and not facts["material_new_evidence"]:
        return "RETAIN_NEGATIVE"
    return "SUPPORTED_RESIDUAL"


__all__ = [
    "P13Action",
    "p11_accessible_rank_dimension",
    "p11_cached_future_coverage",
    "p11_expected_distinct_requests",
    "p11_one_step_future_coverage",
    "p12_joint_alloc",
    "p12_success",
    "p13_rcs_action",
    "p13_responsibility_supported",
    "p14_governance_disposition",
]
