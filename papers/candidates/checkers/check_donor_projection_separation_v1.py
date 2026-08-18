#!/usr/bin/env python3
"""Finite witnesses for donor-projection insufficiency on cross-structure tasks."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class P6State:
    bare_transition: tuple[int, int]
    dependency_view: str
    computation_reusable: bool
    hard_obligation_satisfied: bool
    authority_valid: bool


def p6_projection(s: P6State):
    return (s.bare_transition, s.dependency_view, s.computation_reusable)


def p6_gold(s: P6State) -> str:
    if not s.hard_obligation_satisfied:
        return "CANNOT_CHECK"
    if not s.authority_valid:
        return "DENIED"
    return "AUTHORIZED"


@dataclass(frozen=True)
class P7State:
    history: tuple[str, ...]
    evidence_id: str
    evidence_value: int
    route_state: str
    obligation_threshold: int


def p7_projection(s: P7State):
    return (s.history, s.evidence_id, s.evidence_value, s.route_state)


def p7_gold(s: P7State) -> str:
    return "TASK_STOP" if s.evidence_value > s.obligation_threshold else "CONTINUE"


@dataclass(frozen=True)
class P8State:
    principal: str
    effect: str
    generic_grant_valid: bool
    generic_blocker: bool
    scientific_discharge: str  # SAT | UNKNOWN | FAIL


def p8_projection(s: P8State):
    return (s.principal, s.effect, s.generic_grant_valid, s.generic_blocker)


def p8_gold(s: P8State) -> str:
    if s.generic_blocker or not s.generic_grant_valid:
        return "DENIED"
    if s.scientific_discharge == "UNKNOWN":
        return "CANNOT_CHECK"
    if s.scientific_discharge == "FAIL":
        return "DENIED"
    return "AUTHORIZED"


def pair_forces_error(projection, gold, left, right) -> bool:
    assert projection(left) == projection(right)
    assert gold(left) != gold(right)
    # Any deterministic isolated donor g receives one identical projected input,
    # so it can emit only one output and must be wrong on at least one member.
    return True


def joint_separates(left, right) -> bool:
    return left != right


def main() -> int:
    p6a = P6State((0, 1), "same-dependency", True, True, True)
    p6b = P6State((0, 1), "same-dependency", True, False, True)
    assert pair_forces_error(p6_projection, p6_gold, p6a, p6b)
    assert joint_separates(p6a, p6b)

    p7a = P7State(("q", "e"), "e1", 5, "routes-flat", 3)
    p7b = P7State(("q", "e"), "e1", 5, "routes-flat", 7)
    assert pair_forces_error(p7_projection, p7_gold, p7a, p7b)
    assert joint_separates(p7a, p7b)

    p8a = P8State("agent", "assert", True, False, "SAT")
    p8b = P8State("agent", "assert", True, False, "UNKNOWN")
    assert pair_forces_error(p8_projection, p8_gold, p8a, p8b)
    assert joint_separates(p8a, p8b)

    print("DONOR PROJECTION SEPARATION V1: PASS")
    print("P6 isolated repair/computation projection: indistinguishable pair, different scientific authority")
    print("P7 isolated navigation/evidence projection: indistinguishable pair, different transformed closure")
    print("P8 isolated generic-authorization projection: indistinguishable pair, different scientific discharge")
    print("joint donor-complete envelope separates all 3 pairs")
    print("claim boundary: strict over isolated projections; ideal donor product with joint semantics may tie")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
