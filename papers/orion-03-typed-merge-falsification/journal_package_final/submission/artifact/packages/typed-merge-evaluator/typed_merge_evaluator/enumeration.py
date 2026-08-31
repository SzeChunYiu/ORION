"""Exhaustive fixed-point enumeration (validation only).

MANUSCRIPT_V2.md section 11 states the calculus's own validation standard:
"iterative evaluation is compared against exhaustive enumeration of all fixed
points to identify the unique least one". This module implements that check.

The enumeration is exponential in |Q| and |Lambda| and is intended only for the
small random systems used in the test suite.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, List, Mapping

from .core import Instance, transfer


def all_fixed_points(instance: Instance) -> List[Mapping[str, FrozenSet[str]]]:
    """Exhaustively enumerate every fixed point of F_R.

    Used only by the validation described in MANUSCRIPT_V2.md section 11
    ("iterative evaluation is compared against exhaustive enumeration of all
    fixed points to identify the unique least one"). Exponential; small systems
    only.
    """
    claims = sorted(instance.claims)
    licenses = sorted(instance.licenses)
    subsets = []
    for mask in range(1 << len(licenses)):
        subsets.append(frozenset(licenses[i] for i in range(len(licenses)) if mask >> i & 1))
    found: List[Mapping[str, FrozenSet[str]]] = []

    def step(assignment: Dict[str, FrozenSet[str]]) -> Dict[str, FrozenSet[str]]:
        out: Dict[str, FrozenSet[str]] = {}
        for claim in claims:
            if claim in instance.refuted:
                out[claim] = frozenset()
                continue
            value = set(instance.seed_of(claim))
            for rule in instance.rules:
                if rule.head == claim:
                    value |= transfer(rule, assignment)
            out[claim] = frozenset(value)
        return out

    def rec(index: int, partial: Dict[str, FrozenSet[str]]) -> None:
        if index == len(claims):
            if step(partial) == partial:
                found.append(dict(partial))
            return
        for subset in subsets:
            partial[claims[index]] = subset
            rec(index + 1, partial)
        partial.pop(claims[index], None)

    rec(0, {})
    return found
