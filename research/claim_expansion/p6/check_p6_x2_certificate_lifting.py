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


# P6.V4.5's "ideal enriched donor product". It was written inline inside the
# enumeration loop as ``ideal = native_valid and all(science)`` -- the body of
# ``liftable`` copied. Hoisting it changes no value this checker prints; it moves
# the copy to where ``_independently_defined`` can see it.
def ideal_product(native_valid: bool, science: tuple[bool, ...]) -> bool:
    return native_valid and all(science)


# The donor-native verdict, before and after projection into the P6 model.
# Conservativity was asserted as ``projected_native = native_valid`` followed by
# ``if projected_native != native_valid`` -- one variable compared with itself.
# Naming both sides puts that tautology in front of the same gate as the ideal
# product, so if the theory lane ever supplies a projection that is not the
# identity the gate opens on its own.
def native_verdict(native_valid: bool, science: tuple[bool, ...]) -> bool:
    return native_valid


def projected_native(native_valid: bool, science: tuple[bool, ...]) -> bool:
    return native_valid


def _independently_defined(left, right) -> bool:
    """True when two predicates are not the same expression written twice.

    A counter that compares the two sides of a claim measures something only if
    the two sides were built independently. Both counters this checker publishes
    compare a definition against a copy of itself: ``ideal_product`` is the body
    of ``liftable`` written again, and ``projected_native`` is ``native_verdict``
    written again. Under a consistently applied theory of lifting each count is 0
    for every theory, right or wrong -- a structural zero published beside
    measured ones. ``ideal_product_mismatches`` in particular only ever moves off
    zero when one of the two copies is edited and the other is not, which makes
    it a copy-drift detector rather than the equivalence theorem P6.V4.5 cites.

    Giving either side a genuinely independent definition needs FORMAL_CORE's
    construction of the donor product and of the projection map, and is the
    theory lane's call. What is fixable here is the reporting: a comparison that
    cannot come out any other way must say so rather than emit a violation count.

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
    conservativity_checkable = _independently_defined(projected_native, native_verdict)
    ideal_product_checkable = _independently_defined(ideal_product, liftable)
    donor_conservativity_violations = 0
    ideal_product_mismatches = 0

    # Every ``(native_valid, science)`` point some assertion below actually
    # evaluates the rule at. The enumeration walks all 64; the assertions do not.
    asserted_points: set[tuple[bool, tuple[bool, ...]]] = set()

    # Full bounded state enumeration.
    for donor in DONORS:
        for native_valid in (False, True):
            for science in itertools.product((False, True), repeat=len(COORDS)):
                p6 = liftable(native_valid, science)
                ideal = ideal_product(native_valid, science)
                if ideal_product_checkable and ideal != p6:
                    ideal_product_mismatches += 1
                # Conservativity: projection does not alter the donor-native
                # verdict. Only a claim while the two sides are distinct maps;
                # as shipped they are one identity written twice, and the gate
                # says so instead of counting the difference as measured.
                projected = projected_native(native_valid, science)
                native = native_verdict(native_valid, science)
                if conservativity_checkable and projected != native:
                    donor_conservativity_violations += 1
                rows.append(
                    {
                        "donor": donor,
                        "native_valid": native_valid,
                        "science": dict(zip(COORDS, science)),
                        "liftable": p6,
                        "ideal_product": ideal,
                    }
                )

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

    checkable = conservativity_checkable and ideal_product_checkable
    cannot_check_reasons = []
    if not conservativity_checkable:
        cannot_check_reasons.append(
            "projected_native is the same expression as native_verdict, so the "
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
        "single_coordinate_separation_witnesses": len(separation_witnesses),
        "certificate_product_countermodels": len(product_countermodels),
        "full_revalidation_successes": full_revalidation_successes,
        "partial_revalidation_failures": partial_revalidation_failures,
        "ideal_product_mismatches": ideal_product_mismatches if ideal_product_checkable else None,
        "ideal_product_status": "CHECKED" if ideal_product_checkable else "CANNOT_CHECK",
        # Defect 3, reported rather than repaired: every assertion in this file
        # runs at native_valid=True. The other half of the space is enumerated
        # into the row digest and never asserted about, so a theory that drops
        # the donor certificate entirely walks through all three blocks. Adding
        # the missing assertion is the theory lane's call; naming the hole is not.
        "assertion_state_space": assertion_space,
        "assertion_covered_states": len(asserted_points),
        "assertion_covered_states_native_invalid": asserted_donor_invalid,
        "assertion_uncovered_states": assertion_space - len(asserted_points),
        "assertion_coverage_status": "COMPLETE" if assertions_reach_whole_space else "PARTIAL",
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
