"""P7 instruments that make a handed-in premise report as a handed-in premise.

P7's formal authority is two deterministic checkers that enumerate a bounded
space and print a case count. Both split their claim in two and once mechanized
only the easy half: the transport theorem took target ambiguity as a keyword
argument and the closure-carrying checker took bridge matching as a literal, so
each verified the mapping downstream of a decision nothing in the artifact made.

Both premises are now decided by the artifacts. ``check_support_transport``
enumerates an admissible target completion class beside each transport witness
and reads Definition 14 off it with the ``extension_ambiguous`` it already
shipped, which moves its enumeration from 64 states with 1 decided case to 960
cases all of which decide the premise; ``bridge_match`` is computed from the
donor pair and the registered bridge relation.

:mod:`closure_premises` transcribes each shipped assertion so the premise can
come from a candidate deciding rule instead of the caller's literal, keeps the
pre-repair transport model measurable beside the shipped one, and reports what
the verdict still does not establish; :mod:`premise_audit` runs both and blocks
when a premise is supplied or when the model cannot express what deciding it
would read. The mechanism itself is
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
    transport_authority,
    transport_constraint,
    witness_only_transport_constraint,
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
    "transport_authority",
    "transport_constraint",
    "witness_only_transport_constraint",
]
