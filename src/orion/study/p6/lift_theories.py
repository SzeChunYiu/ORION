"""P6's certificate-lifting checker, and the wrong theories it does not reject.

``research/claim_expansion/p6/check_p6_x2_certificate_lifting.py`` is the
authority behind P6.V4.6 --- "320 states, 25 minimal separations, 31 product
countermodels, 155 full revalidation successes, 1,055 proper-subset failures,
zero donor-conservativity/ideal-product violations" --- and behind the V4
headline in ``papers/orion-16-formal-epistemic-structures-and-mechanics/
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

Two of the five claims were counters rather than assertions, and both compared an
expression against a copy of itself --- ``ideal_product_mismatches`` compared
``liftable(...)`` to ``native_valid and all(science)``, the body of ``liftable``
written again, and ``donor_conservativity_violations`` compared
``projected_native = native_valid`` to ``native_valid``. Each was 0 for every
theory of lifting, right or wrong. Separately, one wrong theory walked through
all five: every assertion in the checker evaluated the rule at
``native_valid=True``, so the 32 points where the donor certificate is invalid
were enumerated into the digest and never asserted about, and
:data:`SCIENCE_LIFTS_WITHOUT_DONOR` is the rule that exploited it.

Both defects had one cause, and P6-U-T5's unblock ("treat each counterexample as
a candidate missing primitive and extend the semantics") names it: the model had
states and a verdict and **no projection**. With no map from a lifted state to
the donor certificate under it, conservativity cannot be stated about the lift at
all, only about the donor atom --- which is how T1 came to be ``x != x``, and why
the half of the space with an invalid donor certificate had nothing to say about
it. The shipped checker now carries ``project_to_donor`` and the image of
``liftable`` along it, and states T1 as the conservativity of the extension:
a donor certificate is certified by the lifted semantics exactly when it is
certified by the donor theory. That one extension gives the counter a falsifier,
covers the previously unasserted 32 states, and rejects
:data:`SCIENCE_LIFTS_WITHOUT_DONOR` --- with no rule about that theory anywhere
in the file. The ad hoc alternative is :data:`DONOR_REQUIREMENT_CHECK`, kept
below to show what was not done.

The ideal product is now the donor theory's own validator run over a requirement
set enriched by the five scientific coordinates, rather than ``liftable``
written twice. See :func:`_accepts_ideal_product_tie` for what that check does
and does not establish.

:data:`INDEPENDENT_LIFT` is the shipped "independent" verifier's rule, kept here
because it is the register's own control: it is a syntactic paraphrase, it
diverges from the reference on 0 of 320 points, and a second implementation that
cannot disagree confirms a digest rather than a theorem.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

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

    The ``ideal_product`` column is :func:`ideal_enriched_product`, which is a
    fixed function of the point rather than a second spelling of the rule, so a
    wrong theory of lifting moves the ``liftable`` column and leaves the ideal
    column where it is. Under :func:`reference_lift` the two agree everywhere and
    the digest is :data:`SHIPPED_ROWS_SHA256` byte for byte.
    """

    rows = [
        {
            "donor": point["donor"],
            "native_valid": point["native_valid"],
            "science": {name: point[name] for name in LIFT_COORDINATES},
            "liftable": rule(point),
            "ideal_product": ideal_enriched_product(point),
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


def project_to_donor(point: ModelPoint) -> tuple[str, bool]:
    """``project_to_donor`` as shipped: the donor-visible part of a lifted state.

    The scientific extension is forgotten. This is the primitive the checker did
    not have, and its absence is why T1 could only be written as an identity on
    the donor atom.
    """

    return (str(point["donor"]), bool(point["native_valid"]))


def donor_fibre(certificate: tuple[str, bool]) -> tuple[ModelPoint, ...]:
    """Every lifted state that projects onto one donor certificate."""

    donor, native_valid = certificate
    return tuple(
        {"donor": donor, "native_valid": native_valid, **dict(zip(LIFT_COORDINATES, science))}
        for science in itertools.product((False, True), repeat=len(LIFT_COORDINATES))
    )


def _accepts_donor_conservativity(rule: Rule) -> bool:
    """The shipped ``donor_conservativity_violations == 0`` counter, replayed.

    The image of the rule along :func:`project_to_donor` --- a donor certificate
    is certified by the lifted semantics when *some* scientific extension over it
    lifts --- must coincide with the donor's own verdict. Both directions carry
    content, and both are about the rule:

    * left to right, the lift never manufactures donor validity it was not given,
      which is what ``science_lifts_without_donor`` does;
    * right to left, the lift never withdraws a verdict the donor theory issues,
      which is what ``nothing_lifts`` does.

    Before the projection was a primitive this counter read ``projected_native =
    native_valid`` and then ``projected_native != native_valid`` --- ``x != x``,
    counted 320 times, with the rule never consulted.
    """

    for certificate in sorted({project_to_donor(point) for point in lifting_model_space()}):
        image = any(rule(point) for point in donor_fibre(certificate))
        if image != certificate[1]:
            return False
    return True


#: The donor theory's required-field set, enriched by the five lift coordinates.
ENRICHED_REQUIREMENTS: tuple[str, ...] = ("native_valid",) + LIFT_COORDINATES


def ideal_enriched_product(point: ModelPoint) -> bool:
    """``ideal_product`` as shipped: the donor validator over an enriched signature.

    P6.V4.5's ideal enriched donor product is the donor theory whose required
    fields have been enlarged by the five scientific coordinates, validated by
    the donor's own native validator. It is a fixed function of the point, so
    substituting a wrong theory of lifting does not co-mutate it --- which is the
    whole difference from the shipped ``ideal = native_valid and all(science)``,
    the body of ``liftable`` written a second time.
    """

    return all(bool(point[name]) for name in ENRICHED_REQUIREMENTS)


def _accepts_ideal_product_tie(rule: Rule) -> bool:
    """The shipped ``ideal_product_mismatches == 0`` counter, replayed.

    An extensional-equivalence claim is an identity test, so this check refutes
    every theory that differs from :func:`ideal_enriched_product` anywhere ---
    which, the register being live by construction, is all of them. That is
    maximal capacity earned cheaply, and it is worth saying so: what this check
    actually turns on is that the two sides have *separate constructions*, and
    the capacity measure cannot see that. The shipped script keeps a structural
    gate (``_independently_defined``) for exactly that reason, and reports
    ``CANNOT_CHECK`` rather than a clean zero if they ever collapse again.
    """

    return not any(
        rule(point) != ideal_enriched_product(point) for point in lifting_model_space()
    )


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
        asserts=(
            "the image of the lift along the donor projection is the donor-native "
            "verdict, on all 10 donor certificates and their 64-state fibres"
        ),
        accepts=_accepts_donor_conservativity,
    ),
    MechanizedCheck(
        check_id="ideal_product_mismatches",
        asserts=(
            "the donor validator over a requirement set enriched by the five scientific "
            "coordinates agrees with P6 on all 320 states"
        ),
        accepts=_accepts_ideal_product_tie,
    ),
)


def _accepts_donor_requirement(rule: Rule) -> bool:
    """The ad hoc repair, kept unshipped so the difference is legible.

    One line --- nothing lifts where ``native_valid`` is false --- and it does
    close the coverage hole ``science_lifts_without_donor`` walked through. It is
    an exception rather than an extension: it adds a rule *about the theory that
    got through*, and the next counterexample needs the next line. Nothing in it
    is a new primitive, and it says nothing about what the model was missing.

    The shipped repair is the other one. Stating T1 as the conservativity of the
    lift along :func:`project_to_donor` rejects this theory as a consequence of
    an equality the semantics could not previously express, covers the same 160
    rows, and additionally rejects ``nothing_lifts`` and ``everything_lifts``
    from the other direction of the same equality. Kept here as the comparison,
    not as a fallback: adding it to the panel would double-count the coverage the
    conservativity check already earns.
    """

    return not any(rule(point) for point in lifting_model_space() if not point["native_valid"])


#: The ad hoc alternative to the projection primitive, not shipped and not in the
#: panel. Registered so "extend the semantics rather than add an exception" is a
#: comparison a reader can run rather than a claim they have to take.
DONOR_REQUIREMENT_CHECK = MechanizedCheck(
    check_id="donor_certificate_required",
    asserts="no state with an invalid donor certificate lifts (the 160 once-unasserted rows)",
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

UNBRIDGED_DONOR_DISCHARGES_COORDINATE = FalseTheory(
    theory_id="unbridged_donor_discharges_coordinate",
    breaks=(
        "the theorem family's own third falsifier and P6.V4.3 non-laundering: one donor "
        "family would discharge evidence_semantics with no bridge rule binding it, so a "
        "coordinate the checker must treat as unresolved would count as true"
    ),
    rule=lambda point: bool(point["native_valid"])
    and all(
        point[name]
        for name in LIFT_COORDINATES
        if not (point["donor"] == "CERTIFIED_PURITY" and name == "evidence_semantics")
    ),
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
    UNBRIDGED_DONOR_DISCHARGES_COORDINATE,
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

#: The shipped checker's published result, whose ``donor_axis`` block the checker
#: computes and :func:`published_count_multiplicity` reads back.
X2_RESULT_PATH = (
    Path(__file__).resolve().parents[4]
    / "research/claim_expansion/p6/P6_X2_CERTIFICATE_LIFTING_RESULT_V1.json"
)


def published_count_multiplicity() -> tuple[dict[str, Any], ...]:
    """Every published count beside the number of distinct facts behind it.

    ``axis_sensitivity`` says the donor axis is inert and every count under it is
    repeated five times; this says which counts and to what. ``320`` reads as 320
    observations and is 64 observed once per donor family; ``25`` minimal
    separations is 5 observed five times; only the 31 product countermodels are 31
    distinct facts, because their loop does not range over donors.

    Read off the shipped artifact's own ``donor_axis`` block rather than recomputed
    here, so a reader is looking at the number the paper published.
    """

    published = json.loads(X2_RESULT_PATH.read_text(encoding="utf-8"))
    axis = published["donor_axis"]
    pairs = (
        ("state_evaluations", "distinct_state_evaluations"),
        ("single_coordinate_separation_witnesses", "distinct_separation_witnesses"),
        ("certificate_product_countermodels", "distinct_product_countermodels"),
        ("full_revalidation_successes", "distinct_full_revalidation_successes"),
        ("partial_revalidation_failures", "distinct_partial_revalidation_failures"),
    )
    return tuple(
        {
            "count": name,
            "published": published[name],
            "distinct": axis[distinct_name],
            "factor": published[name] // axis[distinct_name],
        }
        for name, distinct_name in pairs
    )


__all__ = [
    "ANY_COORDINATE_SUFFICES",
    "DONOR_FAMILIES",
    "DONOR_FAMILY_DECIDES",
    "DONOR_REQUIREMENT_CHECK",
    "ENRICHED_REQUIREMENTS",
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
    "UNBRIDGED_DONOR_DISCHARGES_COORDINATE",
    "X2_RESULT_PATH",
    "canonical_rows_digest",
    "donor_fibre",
    "ideal_enriched_product",
    "independent_lift",
    "lifting_model_space",
    "project_to_donor",
    "published_count_multiplicity",
    "reference_lift",
]
