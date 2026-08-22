from __future__ import annotations

import ast
import hashlib
import inspect
import itertools
import json
import textwrap

DONORS = ("POE", "PCE", "PCAA", "WORKFLOW_SIGNATURE", "CERTIFIED_PURITY")
COORDS = (
    "claim_content_binding",
    "measurement_semantics",
    "evidence_semantics",
    "inferential_obligation",
    "scientific_epoch",
)


def liftable(native_valid: bool, science: tuple[bool, ...]) -> bool:
    return native_valid and all(science)


# ---------------------------------------------------------------------------
# Semantic extension 1: the projection from lifted states to donor certificates.
#
# T1 of P6_X2_CERTIFICATE_LIFTING_THEOREMS_V1.md is "projection from the lifted
# semantics to the donor certificate never changes the donor-native validity
# verdict". This file used to apply the projection to the donor *atom* and
# compare the result with the atom -- ``projected_native = native_valid``
# followed by ``if projected_native != native_valid``. That is the projection's
# definition, not a theorem, and it is 0 for every theory of lifting.
#
# The object the map was never applied to is the lift predicate itself. A
# donor certificate is certified *by the lifted semantics* when some scientific
# extension over it lifts, so the image of ``liftable`` along the projection is
# the donor-language predicate below, and conservativity is the statement that
# it coincides with the donor's own verdict. Both directions carry content:
# left to right the lift never manufactures donor validity it was not given,
# right to left it never silently withdraws a donor verdict the donor theory
# issues. Neither direction can be stated without the projection, which is why
# the check that named T1 had nothing to say.
# ---------------------------------------------------------------------------
def project_to_donor(
    donor: str, native_valid: bool, science: tuple[bool, ...]
) -> tuple[str, bool]:
    """The donor-visible part of a lifted state: the scientific extension is forgotten."""

    del science
    return (donor, native_valid)


def native_verdict(donor_certificate: tuple[str, bool]) -> bool:
    """``DonorValid``: the donor family's own validator, run on the projected certificate."""

    _donor, native_valid = donor_certificate
    return native_valid


def lift_image_in_donor_language(donor_certificate: tuple[str, bool]) -> bool:
    """The image of ``liftable`` along :func:`project_to_donor`.

    The donor certificate is certified by the lifted semantics exactly when some
    scientific extension in its fibre lifts. This is the only predicate in the
    file that quantifies over a fibre, and it is what makes the ``native_valid``
    half of the space assertable: every state with an invalid donor certificate
    is now visited by a claim, not only by the row builder.
    """

    donor, native_valid = donor_certificate
    del donor
    return any(
        liftable(native_valid, science)
        for science in itertools.product((False, True), repeat=len(COORDS))
    )


# ---------------------------------------------------------------------------
# Semantic extension 2: the enriched donor product.
#
# T5 asks whether "a donor product enriched with the exact same scientific
# coordinates and lifting predicate is extensionally equivalent to P6 lifting".
# Read as "the ideal product *is* the lifting predicate" the comparison restates
# one expression and cannot fail; read as "the ideal product is a second copy of
# it" the counter detects copy drift and is not about donor products.
#
# There is a third construction and it is the one the theorem names. The
# enriched donor product is the donor theory whose required-field set has been
# enlarged by the five scientific coordinates, validated by the donor's own
# native validator. It mentions the scientific coordinates -- "the exact same
# scientific coordinates" -- and it never mentions ``liftable``, so substituting
# a different theory of lifting does not co-mutate it. The repository's own
# independent finite-model verifier already derives its ideal product this way
# (``all(s[k] for k in req | set(SCI))``); the primary did not.
# ---------------------------------------------------------------------------
#: The donor theory's required-field set, enriched by the scientific coordinates.
ENRICHED_REQUIREMENTS = ("native_validity",) + COORDS


def donor_native_validator(
    required: tuple[str, ...], fields: dict[str, bool]
) -> bool:
    """A donor family's native validator: every required certificate field holds."""

    return all(fields[name] for name in required)


def ideal_product(native_valid: bool, science: tuple[bool, ...]) -> bool:
    """``DonorValid`` of the donor theory enriched by the five scientific coordinates."""

    return donor_native_validator(
        ENRICHED_REQUIREMENTS,
        {"native_validity": native_valid, **dict(zip(COORDS, science))},
    )


def _independently_defined(left, right) -> bool:
    """True when two predicates are not the same expression written twice.

    A counter that compares the two sides of a claim measures something only if
    the two sides were built independently. Both counters this checker publishes
    used to compare a definition against a copy of itself: ``ideal_product`` was
    the body of ``liftable`` written again, and ``projected_native`` was
    ``native_verdict`` written again. Under a consistently applied theory of
    lifting each count was 0 for every theory, right or wrong -- a structural
    zero published beside measured ones.

    Both sides now have their own construction and this gate is what keeps them
    apart: :func:`lift_image_in_donor_language` quantifies over the fibre of the
    projection and :func:`ideal_product` runs the donor validator over an
    enriched requirement set, so neither can be produced by copying the rule it
    is compared against. The gate stays because the repair is only as durable as
    the distinction: if a later edit collapses either pair back into one
    expression, the counter reports CANNOT_CHECK rather than a clean zero.

    Bodies are compared as parsed statements with a leading docstring dropped, so
    prose written about a definition is never mistaken for a second definition.
    When the source cannot be recovered at all -- a rule substituted at runtime,
    say -- independence is not established, and the answer is False so the
    checker reports CANNOT_CHECK instead of crediting an unverified pass.
    """

    def body(function):
        try:
            statements = ast.parse(textwrap.dedent(inspect.getsource(function))).body[0].body
        except Exception:
            return None
        if (
            statements
            and isinstance(statements[0], ast.Expr)
            and isinstance(statements[0].value, ast.Constant)
            and isinstance(statements[0].value.value, str)
        ):
            statements = statements[1:]
        return "\n".join(ast.dump(node) for node in statements)

    left_body = body(left)
    right_body = body(right)
    if left_body is None or right_body is None:
        return False
    return left_body != right_body


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main() -> None:
    rows = []
    conservativity_checkable = _independently_defined(
        lift_image_in_donor_language, native_verdict
    )
    ideal_product_checkable = _independently_defined(ideal_product, liftable)
    donor_conservativity_violations = 0
    ideal_product_mismatches = 0

    # Every ``(native_valid, science)`` point some assertion below actually
    # evaluates the rule at. The enumeration walks all 64; before the projection
    # was a primitive, the assertions walked 32 of them.
    asserted_points: set[tuple[bool, tuple[bool, ...]]] = set()

    # Full bounded state enumeration.
    for donor in DONORS:
        for native_valid in (False, True):
            for science in itertools.product((False, True), repeat=len(COORDS)):
                p6 = liftable(native_valid, science)
                ideal = ideal_product(native_valid, science)
                if ideal_product_checkable and ideal != p6:
                    ideal_product_mismatches += 1
                rows.append(
                    {
                        "donor": donor,
                        "native_valid": native_valid,
                        "science": dict(zip(COORDS, science)),
                        "liftable": p6,
                        "ideal_product": ideal,
                    }
                )

    # T1 --- donor conservativity, over the donor-visible states rather than over
    # the lifted ones. ``lift_image_in_donor_language`` quantifies over each
    # fibre of the projection, so this block evaluates ``liftable`` at every
    # ``(native_valid, science)`` state including the 32 with an invalid donor
    # certificate, which no other block in this file reaches.
    donor_conservativity_states = 0
    for donor in DONORS:
        for native_valid in (False, True):
            fibre = tuple(itertools.product((False, True), repeat=len(COORDS)))
            # Every state in the fibre projects onto the same donor certificate,
            # which is what makes the image a donor-language predicate.
            certificate = project_to_donor(donor, native_valid, fibre[0])
            assert all(
                project_to_donor(donor, native_valid, science) == certificate
                for science in fibre
            )
            image = lift_image_in_donor_language(certificate)
            native = native_verdict(certificate)
            donor_conservativity_states += 1
            for science in fibre:
                asserted_points.add((native_valid, science))
            if conservativity_checkable and image != native:
                donor_conservativity_violations += 1

    # Minimal one-coordinate separation witnesses.
    separation_witnesses = []
    full = (True,) * len(COORDS)
    for donor in DONORS:
        assert liftable(True, full)
        asserted_points.add((True, full))
        for idx, coord in enumerate(COORDS):
            broken = list(full)
            broken[idx] = False
            broken = tuple(broken)
            assert not liftable(True, broken)
            asserted_points.add((True, broken))
            separation_witnesses.append({"donor": donor, "coordinate": coord})

    # A product of all donor-native valid certificates cannot infer missing science coordinates.
    product_countermodels = []
    for science in itertools.product((False, True), repeat=len(COORDS)):
        if all(science):
            continue
        assert not liftable(True, science)
        asserted_points.add((True, science))
        product_countermodels.append(dict(zip(COORDS, science)))

    # Exact selective revalidation.
    full_revalidation_successes = 0
    partial_revalidation_failures = 0
    for donor in DONORS:
        for r in range(1, len(COORDS) + 1):
            for changed in itertools.combinations(range(len(COORDS)), r):
                damaged = [True] * len(COORDS)
                for idx in changed:
                    damaged[idx] = False
                assert not liftable(True, tuple(damaged))
                asserted_points.add((True, tuple(damaged)))

                fully_repaired = damaged[:]
                for idx in changed:
                    fully_repaired[idx] = True
                assert liftable(True, tuple(fully_repaired))
                asserted_points.add((True, tuple(fully_repaired)))
                full_revalidation_successes += 1

                changed_set = set(changed)
                for k in range(0, len(changed)):
                    for repaired in itertools.combinations(changed, k):
                        partial = damaged[:]
                        for idx in repaired:
                            partial[idx] = True
                        if set(repaired) != changed_set:
                            assert not liftable(True, tuple(partial))
                            asserted_points.add((True, tuple(partial)))
                            partial_revalidation_failures += 1

    # The donor axis is a pure loop multiplier, so the assertion blocks range over
    # one copy of the 64-point ``(native_valid, science)`` space, not over 320.
    assertion_space = 2 * 2 ** len(COORDS)
    asserted_donor_invalid = sum(1 for native_valid, _ in asserted_points if not native_valid)
    assertions_reach_whole_space = len(asserted_points) == assertion_space

    # The donor axis, reported rather than left for a reader to notice. ``liftable``
    # does not take the donor family as an argument, so the loops that range over
    # ``DONORS`` repeat every quantity below them five times over. That is a
    # structural fact about the rule's signature, not a comparison that could come
    # out either way, so it is read off the signature instead of counted.
    donor_read_by_rule = "donor" in inspect.signature(liftable).parameters
    donor_multiplier = 1 if donor_read_by_rule else len(DONORS)

    checkable = conservativity_checkable and ideal_product_checkable
    cannot_check_reasons = []
    if not conservativity_checkable:
        cannot_check_reasons.append(
            "lift_image_in_donor_language is the same expression as native_verdict, so the "
            "conservativity comparison restates one definition and cannot refute any theory"
        )
    if not ideal_product_checkable:
        cannot_check_reasons.append(
            "ideal_product is the same expression as liftable, so the equivalence "
            "comparison restates one definition and cannot refute any theory"
        )
    if not assertions_reach_whole_space:
        cannot_check_reasons.append(
            f"the assertion blocks evaluate the rule at {len(asserted_points)} of the "
            f"{assertion_space} (native_valid, science) states and at "
            f"{asserted_donor_invalid} of the {assertion_space // 2} with native_valid=False, "
            "so no assertion here can refute a theory that ignores the donor certificate"
        )

    result = {
        "schema": "P6.X2.CertificateLiftingResult.v1",
        "donor_families": list(DONORS),
        "science_coordinates": list(COORDS),
        "state_evaluations": len(rows),
        "donor_conservativity_violations": (
            donor_conservativity_violations if conservativity_checkable else None
        ),
        "donor_conservativity_status": "CHECKED" if conservativity_checkable else "CANNOT_CHECK",
        "donor_conservativity_states": donor_conservativity_states,
        "donor_conservativity_distinct_states": donor_conservativity_states // donor_multiplier,
        "single_coordinate_separation_witnesses": len(separation_witnesses),
        "certificate_product_countermodels": len(product_countermodels),
        "full_revalidation_successes": full_revalidation_successes,
        "partial_revalidation_failures": partial_revalidation_failures,
        "ideal_product_mismatches": ideal_product_mismatches if ideal_product_checkable else None,
        "ideal_product_status": "CHECKED" if ideal_product_checkable else "CANNOT_CHECK",
        # Assertion coverage. It read PARTIAL --- 32 of 64 states, 0 of the 32
        # with native_valid=False --- for as long as every assertion here ran at
        # native_valid=True, which is why a theory that drops the donor
        # certificate walked through the whole file. It is COMPLETE now, and not
        # because a "nothing lifts without a donor" assertion was bolted on: the
        # conservativity block quantifies over each fibre of the projection, so
        # the missing half of the space is visited by T1 itself.
        "assertion_state_space": assertion_space,
        "assertion_covered_states": len(asserted_points),
        "assertion_covered_states_native_invalid": asserted_donor_invalid,
        "assertion_uncovered_states": assertion_space - len(asserted_points),
        "assertion_coverage_status": "COMPLETE" if assertions_reach_whole_space else "PARTIAL",
        # An axis no verdict depends on multiplies every count enumerated inside
        # it. Published so the headline numbers carry their own multiplicity
        # rather than reading as that many distinct facts.
        "donor_axis": {
            "values": len(DONORS),
            "read_by_liftable": donor_read_by_rule,
            "multiplier": donor_multiplier,
            "distinct_state_evaluations": len(rows) // donor_multiplier,
            "distinct_separation_witnesses": len(separation_witnesses) // donor_multiplier,
            "distinct_product_countermodels": len(product_countermodels),
            "distinct_full_revalidation_successes": (
                full_revalidation_successes // donor_multiplier
            ),
            "distinct_partial_revalidation_failures": (
                partial_revalidation_failures // donor_multiplier
            ),
        },
        "cannot_check_reasons": cannot_check_reasons,
        "canonical_rows_sha256": hashlib.sha256(canonical(rows).encode()).hexdigest(),
        # Three-valued on purpose. Both counters are None when they could not be
        # checked, and `not None` is True, so a two-valued terminal would read an
        # unchecked counter as a clean one -- the exact substitution this repair
        # exists to stop. An unexercised check blocks the terminal as a violation
        # would, and so does an assertion panel that never visits half its space.
        "terminal": (
            "CANNOT_CHECK"
            if not (checkable and assertions_reach_whole_space)
            else "PASS"
            if not (donor_conservativity_violations or ideal_product_mismatches)
            and len(separation_witnesses) == 25
            and len(product_countermodels) == 31
            and full_revalidation_successes == 155
            and partial_revalidation_failures == 1055
            else "FAIL"
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
