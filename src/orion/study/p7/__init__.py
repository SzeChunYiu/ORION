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
would read.

A decided premise is not the only way a checker can publish a number it could
not have got otherwise, and the closure-carrying checker shipped the other way
too: ``donor_conservativity_violations`` was ``0`` from ``projected_native =
native_valid`` followed by ``if projected_native != native_valid``, so the guard
could not fire and the count was 0 under every theory of carrying. The checker
now applies the projection to the *carrying predicate* --- a donor transform is
closure-carrying when some closure vector over it carries, and conservativity is
the equality of that image with the donor's own verdict --- and the count rejects
four registered false theories, reporting 5 violations and a FAIL terminal on the
one the shipped script used to run to completion on.
:func:`closure_premises.identity_guards` stays armed so the old shape cannot come
back green, and :func:`closure_premises.published_count_multiplicity` reports each
published count beside the number of distinct facts behind it, because the donor
axis is a five-fold multiplier and not a dimension. The mechanism itself is
:mod:`orion.programme.decided_premises`, which builds its verdict from
:class:`orion.programme.guard_exercise.GuardExercise` and is measured beside
:mod:`orion.programme.refutation_capacity` rather than instead of it.

The failure they close is recorded under
``research/failures/2026-08-supplied-premise-unbuilt-decision/``.
"""

from __future__ import annotations

from .closure_premises import (
    BRIDGE_MATCH,
    FALSE_CARRYING_THEORIES,
    FALSE_TRANSPORT_THEORIES,
    SHIPPED_ROWS_SHA256,
    SHIPPED_TRANSPORT_CASES,
    TARGET_AMBIGUITY,
    canonical_rows_digest,
    closure_carrying_capacities,
    closure_carrying_module,
    composition_constraint,
    donor_conservativity_capacity,
    identity_guards,
    published_count_multiplicity,
    theory_closure_module,
    transport_authority,
    transport_constraint,
    witness_only_transport_constraint,
    witness_only_transport_undecidability,
)

__all__ = [
    "BRIDGE_MATCH",
    "FALSE_CARRYING_THEORIES",
    "FALSE_TRANSPORT_THEORIES",
    "SHIPPED_ROWS_SHA256",
    "SHIPPED_TRANSPORT_CASES",
    "TARGET_AMBIGUITY",
    "canonical_rows_digest",
    "closure_carrying_capacities",
    "closure_carrying_module",
    "composition_constraint",
    "donor_conservativity_capacity",
    "identity_guards",
    "published_count_multiplicity",
    "theory_closure_module",
    "transport_authority",
    "transport_constraint",
    "witness_only_transport_constraint",
    "witness_only_transport_undecidability",
]
