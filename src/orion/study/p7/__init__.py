"""P7 instruments that make a handed-in premise report as a handed-in premise.

P7's formal authority is two deterministic checkers that enumerate a bounded
space and print a case count. Both split their claim in two and mechanize only
the easy half: the transport theorem takes target ambiguity as a keyword
argument and the closure-carrying checker takes bridge matching as a literal, so
each verifies the mapping downstream of a decision that nothing in the artifact
makes.

:mod:`closure_premises` transcribes each shipped assertion so the premise can
come from a candidate deciding rule instead of the caller's literal;
:mod:`premise_audit` runs both and blocks when a premise is supplied or when the
model cannot express what deciding it would read. The mechanism itself is
:mod:`orion.programme.decided_premises`, which builds its verdict from
:class:`orion.programme.guard_exercise.GuardExercise` and is measured beside
:mod:`orion.programme.refutation_capacity` rather than instead of it.

The failure they close is recorded under
``research/failures/2026-08-supplied-premise-unbuilt-decision/``.
"""

from __future__ import annotations

from .closure_premises import (
    BRIDGE_MATCH,
    FALSE_TRANSPORT_THEORIES,
    SHIPPED_ROWS_SHA256,
    SHIPPED_TRANSPORT_CASES,
    TARGET_AMBIGUITY,
    canonical_rows_digest,
    closure_carrying_module,
    composition_constraint,
    theory_closure_module,
    transport_constraint,
)

__all__ = [
    "BRIDGE_MATCH",
    "FALSE_TRANSPORT_THEORIES",
    "SHIPPED_ROWS_SHA256",
    "SHIPPED_TRANSPORT_CASES",
    "TARGET_AMBIGUITY",
    "canonical_rows_digest",
    "closure_carrying_module",
    "composition_constraint",
    "theory_closure_module",
    "transport_constraint",
]
