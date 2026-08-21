"""P6's certificate-lifting checker, and the wrong theories it does not reject.

``research/claim_expansion/p6/check_p6_x2_certificate_lifting.py`` is the
authority behind P6.V4.6 --- "320 states, 25 minimal separations, 31 product
countermodels, 155 full revalidation successes, 1,055 proper-subset failures,
zero donor-conservativity/ideal-product violations" --- and behind the V4
headline in ``papers/paper-06-formal-epistemic-structures-and-mechanics/
README.md``. Its entire theory is one line::

    def liftable(native_valid, science):
        return native_valid and all(science)

This module re-enumerates that checker's own model space, transcribes the five
claims it reports as :class:`~orion.programme.refutation_capacity.MechanizedCheck`
predicates over a supplied rule, and registers the wrong theories of lifting a
reviewer would want rejected. The fidelity anchor is
:data:`SHIPPED_ROWS_SHA256`: :func:`canonical_rows_digest` rebuilds the shipped
row list byte for byte, so the instrument is pointed at the published artifact
rather than at a fixture of its own.

Two of the five claims are counters rather than assertions, and both compare an
expression against a copy of itself:

* ``ideal_product_mismatches`` compares ``liftable(...)`` to ``native_valid and
  all(science)``, which is the body of ``liftable`` written again. P6.V4.5 is a
  "NEGATIVE EQUIVALENCE THEOREM" about an ideal donor product with *identical*
  scientific rules, so co-mutating both sides is the faithful reading --- and
  under it no theory of lifting, however wrong, moves the count off zero.
* ``donor_conservativity_violations`` compares ``projected_native = native_valid``
  to ``native_valid``.

The remaining three do have falsifiers, and one wrong theory still walks through
all of them: every assertion in the shipped checker evaluates the rule at
``native_valid=True``, so the 32 points of the space where the donor certificate
is invalid are enumerated into the digest and never asserted about.
:data:`SCIENCE_LIFTS_WITHOUT_DONOR` is the rule that exploits it.

:data:`INDEPENDENT_LIFT` is the shipped "independent" verifier's rule, kept here
because it is the register's own control: it is a syntactic paraphrase, it
diverges from the reference on 0 of 320 points, and a second implementation that
cannot disagree confirms a digest rather than a theorem.
"""

from __future__ import annotations

import hashlib
import itertools
import json

from orion.programme.refutation_capacity import (
    FalseTheory,
    MechanizedCheck,
    ModelPoint,
    Rule,
)

#: The five registered scientific lift coordinates, in the shipped checker's order.
LIFT_COORDINATES: tuple[str, ...] = (
    "claim_content_binding",
    "measurement_semantics",
    "evidence_semantics",
    "inferential_obligation",
    "scientific_epoch",
)

#: The five donor certificate families the shipped checker loops over.
DONOR_FAMILIES: tuple[str, ...] = (
    "POE",
    "PCE",
    "PCAA",
    "WORKFLOW_SIGNATURE",
    "CERTIFIED_PURITY",
)

#: ``canonical_rows_sha256`` as published in ``P6_X2_CERTIFICATE_LIFTING_RESULT_V1.json``.
SHIPPED_ROWS_SHA256 = "e1e3c48bcefea3750d952c6b0ff37ac660a2e21f9823fdfdeb50bb62e819ff93"

REFERENCE_ID = "check_p6_x2_certificate_lifting.liftable"


def lifting_model_space() -> tuple[ModelPoint, ...]:
    """The shipped checker's enumerated space, in its emission order.

    The donor axis is enumerated first because the shipped row list is built in
    that order and the digest depends on it.
    """

    return tuple(
        {
            "donor": donor,
            "native_valid": native_valid,
            **dict(zip(LIFT_COORDINATES, science)),
        }
        for donor in DONOR_FAMILIES
        for native_valid in (False, True)
        for science in itertools.product((False, True), repeat=len(LIFT_COORDINATES))
    )


def reference_lift(point: ModelPoint) -> bool:
    """``liftable(native_valid, science)`` as shipped."""

    return bool(point["native_valid"]) and all(point[name] for name in LIFT_COORDINATES)


def independent_lift(point: ModelPoint) -> bool:
    """``independent_lift`` from the shipped independent verifier, transcribed.

    An early-return loop instead of ``all``. The paraphrase is the point: this is
    the rule the repository's independent audit ran, and it is extensionally the
    reference.
    """

    if not point["native_valid"]:
        return False
    for name in LIFT_COORDINATES:
        if point[name] is not True:
            return False
    return True


def canonical_rows_digest(rule: Rule = reference_lift) -> str:
    """Rebuild the shipped row list under a supplied rule and hash it as shipped.

    The shipped ``ideal_product`` column is the body of ``liftable`` written
    again, so it tracks the rule here for the same reason.
    """

    rows = [
        {
            "donor": point["donor"],
            "native_valid": point["native_valid"],
            "science": {name: point[name] for name in LIFT_COORDINATES},
            "liftable": rule(point),
            "ideal_product": rule(point),
        }
        for point in lifting_model_space()
    ]
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def _full_science(point: ModelPoint, **overrides: bool) -> dict[str, object]:
    """A point with every lift coordinate satisfied, then the named ones broken."""

    return {
        **dict(point),
        "native_valid": True,
        **dict.fromkeys(LIFT_COORDINATES, True),
        **overrides,
    }


def _accepts_single_coordinate_separations(rule: Rule) -> bool:
    """The shipped ``single_coordinate_separation_witnesses`` block, replayed."""

    for donor in DONOR_FAMILIES:
        base = _full_science({"donor": donor})
        if not rule(base):
            return False
        for coordinate in LIFT_COORDINATES:
            if rule({**base, coordinate: False}):
                return False
    return True


def _accepts_product_countermodels(rule: Rule) -> bool:
    """The shipped ``certificate_product_countermodels`` block, replayed."""

    for science in itertools.product((False, True), repeat=len(LIFT_COORDINATES)):
        if all(science):
            continue
        point = {
            "donor": DONOR_FAMILIES[0],
            "native_valid": True,
            **dict(zip(LIFT_COORDINATES, science)),
        }
        if rule(point):
            return False
    return True


def _accepts_selective_revalidation(rule: Rule) -> bool:
    """The shipped 155-success / 1,055-failure revalidation block, replayed."""

    indices = range(len(LIFT_COORDINATES))
    for donor in DONOR_FAMILIES:
        base = _full_science({"donor": donor})
        for size in range(1, len(LIFT_COORDINATES) + 1):
            for changed in itertools.combinations(indices, size):
                damaged = {
                    **base,
                    **{LIFT_COORDINATES[index]: False for index in changed},
                }
                if rule(damaged):
                    return False
                if not rule(base):
                    return False
                for repaired_size in range(len(changed)):
                    for repaired in itertools.combinations(changed, repaired_size):
                        partial = {
                            **damaged,
                            **{LIFT_COORDINATES[index]: True for index in repaired},
                        }
                        if rule(partial):
                            return False
    return True


def _accepts_donor_conservativity(rule: Rule) -> bool:
    """The shipped ``donor_conservativity_violations == 0`` counter, replayed.

    ``projected_native`` is assigned from ``native_valid`` on the line above the
    comparison, so the condition is ``x != x`` and the rule is never consulted.
    The unused parameter is kept so the check has the same shape as the others
    and the measurement reads the same way.
    """

    del rule
    violations = 0
    for point in lifting_model_space():
        projected_native = point["native_valid"]
        if projected_native != point["native_valid"]:
            violations += 1
    return violations == 0


def _accepts_ideal_product_tie(rule: Rule) -> bool:
    """The shipped ``ideal_product_mismatches == 0`` counter, replayed.

    P6.V4.5 claims an ideal donor product with *identical* scientific fields and
    rules ties P6 extensionally, so the ideal is the rule.
    """

    ideal = rule
    return not any(ideal(point) != rule(point) for point in lifting_model_space())


SHIPPED_CHECKS: tuple[MechanizedCheck, ...] = (
    MechanizedCheck(
        check_id="single_coordinate_separation_witnesses",
        asserts=(
            "a fully satisfied state lifts, and breaking any one of the five coordinates "
            "stops it (25 witnesses)"
        ),
        accepts=_accepts_single_coordinate_separations,
    ),
    MechanizedCheck(
        check_id="certificate_product_countermodels",
        asserts=(
            "no product of donor-valid certificates lifts while any scientific coordinate "
            "is missing (31 countermodels)"
        ),
        accepts=_accepts_product_countermodels,
    ),
    MechanizedCheck(
        check_id="selective_revalidation",
        asserts=(
            "revalidating every changed coordinate restores lifting and every proper "
            "subset fails (155 successes, 1,055 failures)"
        ),
        accepts=_accepts_selective_revalidation,
    ),
    MechanizedCheck(
        check_id="donor_conservativity_violations",
        asserts="projection preserves the donor-native verdict on all 320 states",
        accepts=_accepts_donor_conservativity,
    ),
    MechanizedCheck(
        check_id="ideal_product_mismatches",
        asserts="an ideal enriched donor product agrees with P6 on all 320 states",
        accepts=_accepts_ideal_product_tie,
    ),
)


def _accepts_donor_requirement(rule: Rule) -> bool:
    """The assertion the shipped checker omits: nothing lifts without a valid donor.

    Every assertion in ``check_p6_x2_certificate_lifting.py`` evaluates the rule
    at ``native_valid=True``. The other 160 rows are enumerated into the digest
    and never asserted about, which is why a theory that drops the donor
    certificate entirely walks through all three of the shipped assertion blocks.
    This is one line, and it closes that half of the space.
    """

    return not any(rule(point) for point in lifting_model_space() if not point["native_valid"])


#: The check that would make the shipped panel refutation-complete against the
#: register. Not shipped: registered here so the repair is code rather than prose.
DONOR_REQUIREMENT_CHECK = MechanizedCheck(
    check_id="donor_certificate_required",
    asserts="no state with an invalid donor certificate lifts (the 160 unasserted rows)",
    accepts=_accepts_donor_requirement,
)


DONOR_VALIDITY_LIFTS_ALONE = FalseTheory(
    theory_id="donor_validity_lifts_alone",
    breaks=(
        "P6.V4.3 non-laundering: accumulated donor-native validity would infer the missing "
        "scientific lift coordinates with no bridge rule"
    ),
    rule=lambda point: bool(point["native_valid"]),
)

SCIENCE_LIFTS_WITHOUT_DONOR = FalseTheory(
    theory_id="science_lifts_without_donor",
    breaks=(
        "P6.V4.1 donor engulfment: scientific standing would be preserved with no valid "
        "lower-level certificate underneath it, so there is nothing being conservatively reused"
    ),
    rule=lambda point: all(point[name] for name in LIFT_COORDINATES),
)

EPOCH_COORDINATE_INERT = FalseTheory(
    theory_id="epoch_coordinate_inert",
    breaks=(
        "P6.V4.4 selective revalidation: scientific_epoch would not be load-bearing, so a "
        "stale epoch would never require revalidation"
    ),
    rule=lambda point: bool(point["native_valid"])
    and all(point[name] for name in LIFT_COORDINATES[:-1]),
)

MAJORITY_OF_COORDINATES_SUFFICES = FalseTheory(
    theory_id="majority_of_coordinates_suffices",
    breaks=(
        "P6.V4.4 exactness: a proper subset of the affected coordinates would restore "
        "lifting, which is the 1,055 proper-subset failures denied"
    ),
    rule=lambda point: bool(point["native_valid"])
    and sum(bool(point[name]) for name in LIFT_COORDINATES) >= 3,
)

ANY_COORDINATE_SUFFICES = FalseTheory(
    theory_id="any_coordinate_suffices",
    breaks=(
        "P6.V4.4 and the separation witnesses: one surviving coordinate would carry the "
        "whole lift"
    ),
    rule=lambda point: bool(point["native_valid"])
    and any(point[name] for name in LIFT_COORDINATES),
)

EVERYTHING_LIFTS = FalseTheory(
    theory_id="everything_lifts",
    breaks="every P6 claim at once: no state would ever fail to preserve scientific standing",
    rule=lambda point: True,
)

NOTHING_LIFTS = FalseTheory(
    theory_id="nothing_lifts",
    breaks=(
        "P6.V4.4 recovery: no revalidation would ever restore lifting, so the 155 successes "
        "would not exist"
    ),
    rule=lambda point: False,
)

DONOR_FAMILY_DECIDES = FalseTheory(
    theory_id="donor_family_decides",
    breaks=(
        "the donor-independence the enumeration silently assumes: the verdict would depend "
        "on which donor family issued the certificate rather than on the science"
    ),
    rule=lambda point: point["donor"] == "POE",
)

#: The wrong theories of certificate lifting a reviewer would want rejected.
#:
#: Every entry names the P6 claim it breaks, because a register whose entries
#: cannot be read as wrong is a mutation sweep rather than a falsifier set.
FALSE_LIFT_THEORIES: tuple[FalseTheory, ...] = (
    DONOR_VALIDITY_LIFTS_ALONE,
    SCIENCE_LIFTS_WITHOUT_DONOR,
    EPOCH_COORDINATE_INERT,
    MAJORITY_OF_COORDINATES_SUFFICES,
    ANY_COORDINATE_SUFFICES,
    EVERYTHING_LIFTS,
    NOTHING_LIFTS,
    DONOR_FAMILY_DECIDES,
)

#: The shipped independent verifier's rule, registered so its divergence is measured.
#:
#: ``breaks`` is honest about what it is: this theory breaks nothing, which is
#: precisely the finding. It is excluded from :data:`FALSE_LIFT_THEORIES` so it
#: cannot inflate the denominator of any check.
INDEPENDENT_LIFT = FalseTheory(
    theory_id="independent_check_p6_x2_certificate_lifting.independent_lift",
    breaks=(
        "nothing: transcribed from the shipped independent verifier to measure how far a "
        "second implementation departs from the first"
    ),
    rule=independent_lift,
)


#: The axes a caller should profile for inertness. The lift coordinates are
#: omitted because the separation witnesses already assert on each of them.
ENUMERATED_AXES: tuple[str, ...] = ("donor", "native_valid")


__all__ = [
    "ANY_COORDINATE_SUFFICES",
    "DONOR_FAMILIES",
    "DONOR_FAMILY_DECIDES",
    "DONOR_REQUIREMENT_CHECK",
    "DONOR_VALIDITY_LIFTS_ALONE",
    "ENUMERATED_AXES",
    "EPOCH_COORDINATE_INERT",
    "EVERYTHING_LIFTS",
    "FALSE_LIFT_THEORIES",
    "INDEPENDENT_LIFT",
    "LIFT_COORDINATES",
    "MAJORITY_OF_COORDINATES_SUFFICES",
    "NOTHING_LIFTS",
    "REFERENCE_ID",
    "SCIENCE_LIFTS_WITHOUT_DONOR",
    "SHIPPED_CHECKS",
    "SHIPPED_ROWS_SHA256",
    "canonical_rows_digest",
    "independent_lift",
    "lifting_model_space",
    "reference_lift",
]
