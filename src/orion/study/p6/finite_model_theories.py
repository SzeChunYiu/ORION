"""P6's 1,536-state finite-model checker, and the terminal it computes from itself.

``research/claim_expansion/p6/check_p6_x_finite_models.py`` is the artifact the
superiority ledger names as P6-U-T1's current authority, and
``P6_X_FINITE_MODEL_RESULT_V1.json`` records ``"terminal": "PASS"``. That
terminal is::

    "terminal": "PASS" if not (t1_violations or t3_violations or t4_violations)
                and len(t2_pairs) == 96 and len(t5_countermodels) == 96 else "FAIL"

Three violation counters and two case counts, and four of the five cannot be
non-zero for any wrong theory of scientific admissibility:

* ``t4`` compares ``scientific_admissible`` to ``ideal_product``, whose bodies
  are the same characters. Edit one copy and it fires; edit the theory --- which
  is what P6.V4.5's "identical scientific fields/rules" means --- and it cannot.
  It detects copy drift, which is worth having and is not an equivalence theorem.
* ``t1`` compares ``donor_valid(s, emb)`` to the same expression recomputed
  through ``forget``, which preserves every donor field verbatim.
* ``t2`` and ``t5`` append their 96s unconditionally, so given the script
  terminates both counts are 96 whatever the rule is. ``t5``'s own assertion,
  ``assert donor_valid(changed, emb)``, is about the donor side alone.

``t3`` is the exception and is registered as such: it compares two genuinely
different functions, and it is the one published counter that a wrong theory can
move.

The assertions inside the ``t2`` loop do have refutation capacity --- the shipped
script dies on them for six of the seven theories registered here --- so what is
vacuous is what the JSON publishes, not the whole file. This module registers
those theories, transcribes each reported quantity as a predicate over a supplied
rule, and profiles the ``embedding`` axis, because the 96s are 4 distinct
scientific separations repeated over 24 donor-visible states.

The failure class is recorded under
``research/failures/2026-08-unfalsifiable-check-zero-refutation-capacity/``.
"""

from __future__ import annotations

import itertools

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


def _accepts_t1_conservativity(rule: Rule) -> bool:
    """The shipped ``t1_violations == 0`` counter, replayed.

    ``forget`` returns ``tuple((f, state[f]) for f in DONOR_FIELDS)``, so the
    right-hand side re-reads the same values the left-hand side read. The rule
    under test never enters the comparison.
    """

    del rule
    violations = 0
    for point in finite_model_space():
        forgotten = dict((name, point[name]) for name in DONOR_FIELDS)
        recomputed = all(forgotten[name] for name in EMBEDDINGS[str(point["embedding"])])
        if donor_valid(point) != recomputed:
            violations += 1
    return violations == 0


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


def _accepts_t4_ideal_product(rule: Rule) -> bool:
    """The shipped ``t4_violations == 0`` counter, replayed.

    ``ideal_product``'s body is ``scientific_admissible``'s body, character for
    character, so the ideal is the rule.
    """

    ideal = rule
    return not any(ideal(point) != rule(point) for point in finite_model_space())


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


def _accepts_t5_countermodels(rule: Rule) -> bool:
    """The shipped ``t5_countermodels`` block, replayed (96 countermodels).

    The assertion attached to this quantity is ``assert donor_valid(changed, emb)``
    --- the donor transition stays valid while the scientific certificate revokes
    --- and it is about the donor side alone, so no theory of scientific
    admissibility can falsify it. The block does sit inside the ``t2`` loop, so a
    rule that breaks ``t2`` never reaches it; what is measured here is the
    marginal capacity ``t5`` adds, and it is none.
    """

    del rule
    for base in _donor_valid_bases():
        for field in SCI_FIELDS:
            if not donor_valid({**dict(base), field: False}):
                return False
    return True


SHIPPED_CHECKS: tuple[MechanizedCheck, ...] = (
    MechanizedCheck(
        check_id="t1_violations",
        asserts="donor-visible forgetting preserves donor validity on all 1,536 states",
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
        asserts="an ideal enriched donor product agrees with P6 on all 1,536 states",
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
        check_id="t5_countermodels",
        asserts=(
            "the donor transition stays valid across each of the 96 scientific revocations"
        ),
        accepts=_accepts_t5_countermodels,
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

#: The wrong theories of scientific admissibility a reviewer would want rejected.
FALSE_ADMISSIBILITY_THEORIES: tuple[FalseTheory, ...] = (
    DONOR_VALIDITY_IS_ADMISSIBILITY,
    SCIENCE_WITHOUT_DONOR,
    EPOCH_FIELD_INERT,
    MAJORITY_OF_SCIENCE_SUFFICES,
    EVERYTHING_ADMISSIBLE,
    NOTHING_ADMISSIBLE,
    EMBEDDING_DECIDES,
)

#: The axes worth profiling for inertness on this space.
ENUMERATED_AXES: tuple[str, ...] = ("embedding",)


__all__ = [
    "DONOR_FIELDS",
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
    "finite_model_space",
    "reference_admissible",
]
