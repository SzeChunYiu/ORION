"""P6's 1,536-state finite-model checker, and the terminal it computes from itself.

``research/claim_expansion/p6/check_p6_x_finite_models.py`` is the artifact the
superiority ledger named as P6-U-T1's authority, and
``P6_X_FINITE_MODEL_RESULT_V1.json`` recorded ``"terminal": "PASS"`` computed
from itself::

    "terminal": "PASS" if not (t1_violations or t3_violations or t4_violations)
                and len(t2_pairs) == 96 and len(t5_countermodels) == 96 else "FAIL"

Three violation counters and two case counts, of which four could not be
non-zero for any wrong theory of scientific admissibility. Each had a missing
primitive underneath it, and P6-U-T5's unblock --- "treat each counterexample as
a candidate missing primitive and extend the semantics" --- is what the shipped
checker now does:

* ``t1`` compared ``donor_valid(s, emb)`` to the same expression recomputed
  through ``forget``, which preserves every donor field verbatim. The map was
  applied to the donor coordinates and never to the *rule*. It is now the image
  of admissibility along ``U_D``, and conservativity is the statement that that
  image is the donor's own verdict.
* ``t4`` compared ``scientific_admissible`` to ``ideal_product``, whose bodies
  were the same characters: edit one copy and it fires, edit the theory and it
  cannot. The ideal product is now the donor validator run over a requirement set
  *enriched* by the four scientific coordinates --- a construction that never
  mentions the admissibility rule, so a wrong theory cannot co-mutate it.
* ``t5`` appended its 96 unconditionally; its only assertion,
  ``assert donor_valid(changed, emb)``, was the countermodel's premise, and its
  conclusion belonged to ``t2``. The missing primitive was the *transition*: T5
  says donor-valid **recomputation** is insufficient, and nothing is recomputed
  in a pair whose donor side is held byte-identical. It is now a counter over the
  2,880 donor-valid transitions that drop a scientific coordinate.
* ``t2`` also appends its 96 unconditionally, but its in-loop assertions do bite,
  and its transcription reads them.

``t3`` needed nothing: it compared two genuinely different functions and was the
one published counter a wrong theory could always move.

This module transcribes each reported quantity as a predicate over a supplied
rule, registers the wrong theories a reviewer would want rejected, and profiles
the ``embedding`` axis, because the 96s are 4 distinct scientific separations
repeated over 24 donor-visible states.

The failure class is recorded under
``research/failures/2026-08-unfalsifiable-check-zero-refutation-capacity/``.
"""

from __future__ import annotations

import itertools
from typing import Hashable

from orion.programme.refutation_capacity import (
    FalseTheory,
    MechanizedCheck,
    ModelPoint,
    Rule,
)

#: Donor-visible coordinates, in the shipped checker's order.
DONOR_FIELDS: tuple[str, ...] = (
    "compute_valid",
    "dependency_supported",
    "effect_valid",
    "action_authorized",
    "execution_provenance_valid",
)

#: Scientific coordinates the lift is claimed to require.
SCI_FIELDS: tuple[str, ...] = (
    "evidence_version_current",
    "scientific_source_authorized",
    "claim_scope_supported",
    "verification_epoch_current",
)

#: Which donor fields each donor-theory embedding requires for native validity.
EMBEDDINGS: dict[str, tuple[str, ...]] = {
    "DEPENDENCY_MAINTENANCE": ("compute_valid", "dependency_supported"),
    "EFFECTFUL_COMPUTATION": ("compute_valid", "effect_valid"),
    "CONTINUING_AUTH_EXEC_PROVENANCE": ("action_authorized", "execution_provenance_valid"),
}

REFERENCE_ID = "check_p6_x_finite_models.scientific_admissible"


def finite_model_space() -> tuple[ModelPoint, ...]:
    """The shipped checker's 1,536 states: the full Boolean cube per embedding."""

    fields = DONOR_FIELDS + SCI_FIELDS
    return tuple(
        {"embedding": embedding, **dict(zip(fields, bits))}
        for embedding in EMBEDDINGS
        for bits in itertools.product((False, True), repeat=len(fields))
    )


def donor_valid(point: ModelPoint) -> bool:
    """``donor_valid(state, embedding)`` as shipped."""

    return all(point[name] for name in EMBEDDINGS[str(point["embedding"])])


def reference_admissible(point: ModelPoint) -> bool:
    """``scientific_admissible(state, embedding)`` as shipped."""

    return donor_valid(point) and all(point[name] for name in SCI_FIELDS)


def forget(point: ModelPoint) -> tuple[tuple[str, Hashable], ...]:
    """``U_D`` as shipped: the donor-visible part of a state, embedding included."""

    return (("embedding", point["embedding"]),) + tuple(
        (name, point[name]) for name in DONOR_FIELDS
    )


def forgetful_fibre(donor_state: tuple[tuple[str, Hashable], ...]) -> tuple[ModelPoint, ...]:
    """Every state that ``U_D`` sends to one donor-visible state."""

    base = dict(donor_state)
    return tuple(
        {**base, **dict(zip(SCI_FIELDS, bits))}
        for bits in itertools.product((False, True), repeat=len(SCI_FIELDS))
    )


def _accepts_t1_conservativity(rule: Rule) -> bool:
    """The shipped ``t1_violations == 0`` counter, replayed.

    T1 is a claim about ``U_D``, and ``U_D`` preserves the donor coordinates by
    construction, so ``donor_valid(s) == donor_valid(U_D(s))`` re-reads the values
    it just read: the counter was 0 for every rule, and the rule never entered.

    The object ``U_D`` was never applied to is ``scientific_admissible`` itself.
    Its image along ``U_D`` --- a donor-visible state is certified by the lifted
    semantics when *some* scientific enrichment over it is admissible --- must be
    the donor's own verdict. Left to right the lift may not manufacture donor
    validity (``science_without_donor``); right to left it may not withdraw a
    verdict the donor theory issues (``nothing_admissible``).
    """

    for donor_state in sorted({forget(point) for point in finite_model_space()}):
        image = any(rule(point) for point in forgetful_fibre(donor_state))
        if image != donor_valid(dict(donor_state)):
            return False
    return True


def _accepts_t3_no_alarm_preservation(rule: Rule) -> bool:
    """The shipped ``t3_violations == 0`` counter, replayed.

    Guarded by ``if all(s[f] for f in SCI_FIELDS)``, under which
    ``scientific_admissible`` reduces to ``donor_valid`` by its own definition.
    A wrong theory of admissibility is caught here only if it disagrees with
    ``donor_valid`` on a state where every scientific coordinate already holds.
    """

    violations = 0
    for point in finite_model_space():
        if not all(point[name] for name in SCI_FIELDS):
            continue
        if rule(point) != donor_valid(point):
            violations += 1
    return violations == 0


def enriched_requirements(embedding: str) -> tuple[str, ...]:
    """The embedding's required donor fields, enlarged by the four scientific ones."""

    return EMBEDDINGS[embedding] + SCI_FIELDS


def ideal_enriched_product(point: ModelPoint) -> bool:
    """``ideal_product`` as shipped: the donor validator over an enriched signature.

    T4's ideal product is the donor theory whose required-field set has been
    enlarged by the four scientific coordinates, validated by the donor's own
    native validator. It is a fixed function of the point and never mentions
    ``scientific_admissible``, so a wrong theory of admissibility does not
    co-mutate it --- which is exactly what the byte-identical copy did.
    """

    return all(point[name] for name in enriched_requirements(str(point["embedding"])))


def _accepts_t4_ideal_product(rule: Rule) -> bool:
    """The shipped ``t4_violations == 0`` counter, replayed.

    An extensional-equivalence claim is an identity test, so this refutes every
    theory that differs from :func:`ideal_enriched_product` anywhere --- which,
    the register being live by construction, is all of them. Maximal capacity
    earned cheaply, and worth naming: what the check really turns on is that the
    two sides have separate constructions, and no capacity measure can see that.
    The shipped script keeps ``_independently_defined`` for exactly that, and
    reports ``CANNOT_CHECK`` rather than a clean zero if they collapse again.
    """

    return not any(
        rule(point) != ideal_enriched_product(point) for point in finite_model_space()
    )


def _donor_valid_bases() -> tuple[ModelPoint, ...]:
    """The 24 donor-valid states with every scientific coordinate satisfied.

    These are the states the shipped separation and countermodel loops build
    from; everything else in the cube is skipped by ``if not donor_valid: continue``.
    """

    return tuple(
        {
            "embedding": embedding,
            **dict(zip(DONOR_FIELDS, donor_bits)),
            **dict.fromkeys(SCI_FIELDS, True),
        }
        for embedding in EMBEDDINGS
        for donor_bits in itertools.product((False, True), repeat=len(DONOR_FIELDS))
        if all(dict(zip(DONOR_FIELDS, donor_bits))[name] for name in EMBEDDINGS[embedding])
    )


def _accepts_t2_separation_pairs(rule: Rule) -> bool:
    """The shipped ``t2_separation_pairs`` block, replayed (96 pairs)."""

    for base in _donor_valid_bases():
        for field in SCI_FIELDS:
            changed = {**dict(base), field: False}
            if not (rule(base) and not rule(changed)):
                return False
    return True


def donor_valid_transitions() -> tuple[tuple[ModelPoint, ModelPoint], ...]:
    """T5's donor-valid transitions: both endpoints donor-valid, science only lost.

    The source is "previously admissible" --- donor-valid with every scientific
    obligation discharged. The target is any donor-valid state that drops at
    least one scientific coordinate and revalidates none. The donor-visible part
    is free to differ between the two, which is the whole point: T5's clause is
    "donor-valid **recomputation/support/authorization** alone is insufficient",
    and nothing is recomputed in a pair whose donor side is held byte-identical.
    """

    by_embedding: dict[str, list[ModelPoint]] = {}
    for point in finite_model_space():
        if donor_valid(point):
            by_embedding.setdefault(str(point["embedding"]), []).append(point)

    transitions: list[tuple[ModelPoint, ModelPoint]] = []
    for states in by_embedding.values():
        sources = [s for s in states if all(s[name] for name in SCI_FIELDS)]
        for source in sources:
            for target in states:
                dropped = any(source[name] and not target[name] for name in SCI_FIELDS)
                gained = any(target[name] and not source[name] for name in SCI_FIELDS)
                if dropped and not gained:
                    transitions.append((source, target))
    return tuple(transitions)


def _accepts_t5_preservation(rule: Rule) -> bool:
    """The shipped ``t5_violations == 0`` counter, replayed (2,880 transitions).

    The published ``t5_countermodels`` count was 96 in every completing run: the
    only assertion attached to it was ``assert donor_valid(changed, emb)``, the
    *premise* of the countermodel, and the conclusion --- that admissibility
    revokes --- was asserted a line earlier by ``t2``. So the quantity the
    terminal read had no falsifier while the claim it named did.

    The missing primitive here is the transition. The model had states; T5 is
    about a step, and about a step in which the donor side may be *recomputed*.
    Holding the donor-visible part fixed, as the 96 pairs do, deletes the clause
    T5 turns on. Over the donor-valid transition relation the conclusion becomes
    assertable and the counter can move.

    Its marginal capacity over ``t2_separation_pairs`` on this register is
    nevertheless zero: ``t2``'s pairs are a subset of these, and every theory
    caught here is caught there. That is reported rather than hidden --- a check
    can be honestly stated and still add nothing a neighbouring check did not.
    """

    for source, target in donor_valid_transitions():
        if not donor_valid(target):
            return False
        if not (rule(source) and not rule(target)):
            return False
    return True


SHIPPED_CHECKS: tuple[MechanizedCheck, ...] = (
    MechanizedCheck(
        check_id="t1_violations",
        asserts=(
            "the image of admissibility along the forgetful map is donor validity, on "
            "all 96 donor-visible states and their 16-state fibres"
        ),
        accepts=_accepts_t1_conservativity,
    ),
    MechanizedCheck(
        check_id="t3_violations",
        asserts=(
            "with every scientific coordinate satisfied, scientific admissibility agrees "
            "with donor validity (96 no-alarm states)"
        ),
        accepts=_accepts_t3_no_alarm_preservation,
    ),
    MechanizedCheck(
        check_id="t4_violations",
        asserts=(
            "the donor validator over a requirement set enriched by the four scientific "
            "coordinates agrees with P6 on all 1,536 states"
        ),
        accepts=_accepts_t4_ideal_product,
    ),
    MechanizedCheck(
        check_id="t2_separation_pairs",
        asserts=(
            "breaking any one scientific coordinate revokes admissibility while the "
            "donor-visible state is unchanged (96 pairs)"
        ),
        accepts=_accepts_t2_separation_pairs,
    ),
    MechanizedCheck(
        check_id="t5_violations",
        asserts=(
            "across every donor-valid transition that drops a scientific coordinate and "
            "revalidates none, the donor side stays valid and admissibility revokes "
            "(2,880 transitions)"
        ),
        accepts=_accepts_t5_preservation,
    ),
)


DONOR_VALIDITY_IS_ADMISSIBILITY = FalseTheory(
    theory_id="donor_validity_is_admissibility",
    breaks=(
        "P6's separation claim: a valid donor certificate would carry scientific "
        "admissibility on its own, which is the laundering the paper forbids"
    ),
    rule=donor_valid,
)

SCIENCE_WITHOUT_DONOR = FalseTheory(
    theory_id="science_without_donor",
    breaks=(
        "P6's conservativity claim: scientific admissibility would hold with no valid "
        "donor certificate underneath it"
    ),
    rule=lambda point: all(point[name] for name in SCI_FIELDS),
)

EPOCH_FIELD_INERT = FalseTheory(
    theory_id="epoch_field_inert",
    breaks=(
        "the T2 separation on verification_epoch_current: a stale verification epoch "
        "would not revoke admissibility"
    ),
    rule=lambda point: donor_valid(point)
    and all(point[name] for name in SCI_FIELDS if name != "verification_epoch_current"),
)

MAJORITY_OF_SCIENCE_SUFFICES = FalseTheory(
    theory_id="majority_of_science_suffices",
    breaks=(
        "the T2 separations: three of the four scientific coordinates would carry the lift, "
        "so no single coordinate would separate"
    ),
    rule=lambda point: donor_valid(point)
    and sum(bool(point[name]) for name in SCI_FIELDS) >= 3,
)

EVERYTHING_ADMISSIBLE = FalseTheory(
    theory_id="everything_admissible",
    breaks="every P6 claim at once: no state would ever be scientifically inadmissible",
    rule=lambda point: True,
)

NOTHING_ADMISSIBLE = FalseTheory(
    theory_id="nothing_admissible",
    breaks="the no-alarm cases: an intact certificate would never be admissible",
    rule=lambda point: False,
)

EMBEDDING_DECIDES = FalseTheory(
    theory_id="embedding_decides",
    breaks=(
        "the embedding-independence the enumeration assumes: admissibility would depend on "
        "which donor theory the certificate was embedded from"
    ),
    rule=lambda point: point["embedding"] == "DEPENDENCY_MAINTENANCE",
)

DONOR_RECOMPUTATION_LAUNDERS = FalseTheory(
    theory_id="donor_recomputation_launders",
    breaks=(
        "T5's own clause: a fully recomputed, supported and authorized donor state would "
        "carry admissibility across a scientific revocation, which is exactly the "
        "'donor-valid recomputation alone is insufficient' the theorem denies"
    ),
    rule=lambda point: donor_valid(point)
    and (
        all(point[name] for name in DONOR_FIELDS)
        or all(point[name] for name in SCI_FIELDS)
    ),
)

#: The wrong theories of scientific admissibility a reviewer would want rejected.
FALSE_ADMISSIBILITY_THEORIES: tuple[FalseTheory, ...] = (
    DONOR_VALIDITY_IS_ADMISSIBILITY,
    SCIENCE_WITHOUT_DONOR,
    EPOCH_FIELD_INERT,
    MAJORITY_OF_SCIENCE_SUFFICES,
    EVERYTHING_ADMISSIBLE,
    NOTHING_ADMISSIBLE,
    EMBEDDING_DECIDES,
    DONOR_RECOMPUTATION_LAUNDERS,
)

#: The axes worth profiling for inertness on this space.
ENUMERATED_AXES: tuple[str, ...] = ("embedding",)


__all__ = [
    "DONOR_FIELDS",
    "DONOR_RECOMPUTATION_LAUNDERS",
    "DONOR_VALIDITY_IS_ADMISSIBILITY",
    "EMBEDDINGS",
    "EMBEDDING_DECIDES",
    "ENUMERATED_AXES",
    "EPOCH_FIELD_INERT",
    "EVERYTHING_ADMISSIBLE",
    "FALSE_ADMISSIBILITY_THEORIES",
    "MAJORITY_OF_SCIENCE_SUFFICES",
    "NOTHING_ADMISSIBLE",
    "REFERENCE_ID",
    "SCI_FIELDS",
    "SCIENCE_WITHOUT_DONOR",
    "SHIPPED_CHECKS",
    "donor_valid",
    "donor_valid_transitions",
    "enriched_requirements",
    "finite_model_space",
    "forget",
    "forgetful_fibre",
    "ideal_enriched_product",
    "reference_admissible",
]
