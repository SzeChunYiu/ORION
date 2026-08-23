from __future__ import annotations

import ast
import hashlib
import inspect
import itertools
import json
import textwrap

DONORS = (
    "PLANNING_REFINEMENT",
    "CEGAR_REFINEMENT",
    "BIDIRECTIONAL_MIGRATION",
    "WORLD_MODEL_REPLAN",
    "TERMINAL_COMMITMENT",
)
COORDS = (
    "obligations_total",
    "obligations_unambiguous",
    "frontier_resolved",
    "objective_semantics_preserved",
    "closure_epoch_current",
)


def carries(native_valid: bool, closure: tuple[bool, ...]) -> bool:
    return native_valid and all(closure)


def compose(c1: bool, c2: bool, bridge_match: bool) -> bool:
    return c1 and c2 and bridge_match


# ---------------------------------------------------------------------------
# Semantic extension 1: the projection from carried states to donor transforms.
#
# P7.V4.7 publishes "zero donor-conservativity violations". The claim behind that
# count is that absorbing a donor transform never changes its native verdict. This
# file used to state it on the donor *atom*:
#
#     projected_native = native_valid
#     if projected_native != native_valid:
#         donor_conservativity_violations += 1
#
# ``projected_native`` is bound from ``native_valid`` on the line above and
# ``native_valid`` is not rebound between the two statements, so the guard is
# ``x != x``. It was evaluated 320 times and satisfied 0 times, and it is 0 for
# every theory of closure carrying, right or wrong: replacing ``carries`` with
# ``lambda native_valid, closure: all(closure)`` --- closure carried by a donor
# transform whose own verdict is invalid, which is the violation the count names
# --- ran the whole file to completion and still printed 0.
#
# The object the projection was never applied to is the carrying predicate itself.
# A donor transform is closure-carrying *under the P7 semantics* when some closure
# vector over it carries, so the image of ``carries`` along the projection is the
# donor-language predicate below, and conservativity is the statement that it
# coincides with the transform's own native verdict. Both directions carry
# content: left to right the semantics never manufactures a native verdict it was
# not given, right to left it never silently withdraws one the donor theory
# issues. Neither direction is statable without the projection, which is why the
# count that named the claim had nothing to say.
# ---------------------------------------------------------------------------
def project_to_donor(
    donor: str, native_valid: bool, closure: tuple[bool, ...]
) -> tuple[str, bool]:
    """The donor-visible part of a carried state: the closure vector is forgotten."""

    del closure
    return (donor, native_valid)


def native_verdict(donor_transform: tuple[str, bool]) -> bool:
    """The donor family's own validator, run on the projected transform."""

    _donor, native_valid = donor_transform
    return native_valid


def carry_image_in_donor_language(donor_transform: tuple[str, bool]) -> bool:
    """The image of :func:`carries` along :func:`project_to_donor`.

    A donor transform is closure-carrying under the P7 semantics exactly when some
    closure vector in its fibre carries. This is the only predicate in the file
    that quantifies over a fibre, and it is what makes the ``native_valid=False``
    half of the space assertable: every state whose donor transform is natively
    invalid is now visited by a claim rather than only by the row builder.
    """

    donor, native_valid = donor_transform
    del donor
    return any(
        carries(native_valid, closure)
        for closure in itertools.product((False, True), repeat=len(COORDS))
    )


# ---------------------------------------------------------------------------
# Semantic extension 2: the ideal donor product.
#
# The ownership boundary P7's README states is "an ideal donor product carrying
# the exact same scientific closure fields and bridge rules ties P7
# extensionally". Read as "the ideal product *is* the carrying predicate" the
# comparison restates one expression and cannot fail; read as "the ideal product
# is a second copy of it" the counter detects copy drift and is not about donor
# products. The construction the boundary names is the third one: the donor theory
# whose required-field set has been enlarged by the five closure coordinates,
# validated by the donor's own native validator. It mentions the closure
# coordinates and never mentions ``carries``, so substituting a different theory
# of carrying does not co-mutate it.
#
# It is extensionally equal to the ``native_valid and all(closure)`` this file
# published before, so every row and the canonical digest are unchanged.
# ---------------------------------------------------------------------------
#: The donor theory's required-field set, enriched by the five closure coordinates.
ENRICHED_REQUIREMENTS = ("native_validity",) + COORDS


def donor_native_validator(required: tuple[str, ...], fields: dict[str, bool]) -> bool:
    """A donor family's native validator: every required transform field holds."""

    return all(fields[name] for name in required)


def ideal_product(native_valid: bool, closure: tuple[bool, ...]) -> bool:
    """The donor theory enriched by the five closure coordinates, natively validated."""

    return donor_native_validator(
        ENRICHED_REQUIREMENTS,
        {"native_validity": native_valid, **dict(zip(COORDS, closure))},
    )


def _independently_defined(left, right) -> bool:
    """True when two predicates are not the same expression written twice.

    A counter that compares the two sides of a claim measures something only if the
    two sides were built independently. Both counters this checker publishes used
    to compare a definition against a copy of itself: ``ideal`` was the body of
    ``carries`` written again, and ``projected_native`` was ``native_valid``
    written again. Under a consistently applied theory of carrying each count was 0
    for every theory, right or wrong --- a structural zero published beside
    measured ones.

    Both sides now have their own construction and this gate is what keeps them
    apart: :func:`carry_image_in_donor_language` quantifies over the fibre of the
    projection and :func:`ideal_product` runs the donor validator over an enriched
    requirement set, so neither can be produced by copying the rule it is compared
    against. The gate stays because the repair is only as durable as the
    distinction: if a later edit collapses either pair back into one expression,
    the counter reports CANNOT_CHECK rather than a clean zero.

    Bodies are compared as parsed statements with a leading docstring dropped, so
    prose written about a definition is never mistaken for a second definition.
    When the source cannot be recovered at all --- a rule substituted at runtime,
    say --- independence is not established, and the answer is False so the checker
    reports CANNOT_CHECK instead of crediting an unverified pass.
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
        carry_image_in_donor_language, native_verdict
    )
    ideal_product_checkable = _independently_defined(ideal_product, carries)
    donor_conservativity_violations = 0
    ideal_product_mismatches = 0

    # Every ``(native_valid, closure)`` point some assertion below actually
    # evaluates the rule at. The enumeration walks all 64; before the projection
    # was a primitive, the assertions walked 32 of them.
    asserted_points: set[tuple[bool, tuple[bool, ...]]] = set()

    for donor in DONORS:
        for native_valid in (False, True):
            for closure in itertools.product((False, True), repeat=len(COORDS)):
                verdict = carries(native_valid, closure)
                ideal = ideal_product(native_valid, closure)
                if ideal_product_checkable and verdict != ideal:
                    ideal_product_mismatches += 1
                rows.append({
                    "donor": donor,
                    "native_valid": native_valid,
                    "closure": dict(zip(COORDS, closure)),
                    "carries": verdict,
                    "ideal_product": ideal,
                })

    # Donor conservativity, over the donor-visible transforms rather than over the
    # carried states. ``carry_image_in_donor_language`` quantifies over each fibre
    # of the projection, so this block evaluates ``carries`` at every
    # ``(native_valid, closure)`` state including the 32 whose donor transform is
    # natively invalid, which no other block in this file reaches.
    donor_conservativity_states = 0
    for donor in DONORS:
        for native_valid in (False, True):
            fibre = tuple(itertools.product((False, True), repeat=len(COORDS)))
            # Every state in the fibre projects onto the same donor transform,
            # which is what makes the image a donor-language predicate.
            transform = project_to_donor(donor, native_valid, fibre[0])
            assert all(
                project_to_donor(donor, native_valid, closure) == transform
                for closure in fibre
            )
            image = carry_image_in_donor_language(transform)
            native = native_verdict(transform)
            donor_conservativity_states += 1
            for closure in fibre:
                asserted_points.add((native_valid, closure))
            if conservativity_checkable and image != native:
                donor_conservativity_violations += 1

    separation_witnesses = 0
    full = (True,) * len(COORDS)
    for donor in DONORS:
        assert carries(True, full)
        asserted_points.add((True, full))
        for idx in range(len(COORDS)):
            broken = list(full)
            broken[idx] = False
            assert not carries(True, tuple(broken))
            asserted_points.add((True, tuple(broken)))
            separation_witnesses += 1

    product_countermodels = 0
    for closure in itertools.product((False, True), repeat=len(COORDS)):
        if all(closure):
            continue
        assert not carries(True, closure)
        asserted_points.add((True, closure))
        product_countermodels += 1

    full_refinement_successes = 0
    partial_refinement_failures = 0
    for donor in DONORS:
        for r in range(1, len(COORDS) + 1):
            for changed in itertools.combinations(range(len(COORDS)), r):
                damaged = [True] * len(COORDS)
                for idx in changed:
                    damaged[idx] = False
                assert not carries(True, tuple(damaged))
                asserted_points.add((True, tuple(damaged)))
                for k in range(0, len(changed)):
                    for repaired in itertools.combinations(changed, k):
                        partial = damaged[:]
                        for idx in repaired:
                            partial[idx] = True
                        assert not carries(True, tuple(partial))
                        asserted_points.add((True, tuple(partial)))
                        partial_refinement_failures += 1
                repaired = damaged[:]
                for idx in changed:
                    repaired[idx] = True
                assert carries(True, tuple(repaired))
                asserted_points.add((True, tuple(repaired)))
                full_refinement_successes += 1

    composition_successes = 0
    composition_bridge_countermodels = 0
    for d1 in DONORS:
        for d2 in DONORS:
            c1 = carries(True, full)
            c2 = carries(True, full)
            assert compose(c1, c2, True)
            composition_successes += 1
            assert not compose(c1, c2, False)
            composition_bridge_countermodels += 1

    # The donor axis is a pure loop multiplier, so the assertion blocks range over
    # one copy of the 64-point ``(native_valid, closure)`` space, not over 320.
    assertion_space = 2 * 2 ** len(COORDS)
    asserted_donor_invalid = sum(1 for native_valid, _ in asserted_points if not native_valid)
    assertions_reach_whole_space = len(asserted_points) == assertion_space

    # The donor axis, reported rather than left for a reader to notice. Neither
    # ``carries`` nor ``compose`` takes the donor family as an argument, so the
    # loops that range over ``DONORS`` repeat every quantity below them five times
    # over, and the ordered-pair loop repeats its two counts twenty-five times.
    # That is a structural fact about the rules' signatures, not a comparison that
    # could come out either way, so it is read off the signatures instead of
    # counted. ``project_to_donor`` does take a donor and does carry it into the
    # transform it returns, but neither predicate applied to that transform reads
    # it, which is why the conservativity block visits 10 transforms and decides 2.
    verdict_rules = {"carries": carries, "compose": compose}
    donor_reading_rules = tuple(
        sorted(
            name
            for name, rule in verdict_rules.items()
            if any("donor" in parameter for parameter in inspect.signature(rule).parameters)
        )
    )
    donor_multiplier = 1 if donor_reading_rules else len(DONORS)
    donor_pair_multiplier = donor_multiplier**2

    checkable = conservativity_checkable and ideal_product_checkable
    cannot_check_reasons = []
    if not conservativity_checkable:
        cannot_check_reasons.append(
            "carry_image_in_donor_language is the same expression as native_verdict, so "
            "the conservativity comparison restates one definition and cannot refute any "
            "theory"
        )
    if not ideal_product_checkable:
        cannot_check_reasons.append(
            "ideal_product is the same expression as carries, so the equivalence "
            "comparison restates one definition and cannot refute any theory"
        )
    if not assertions_reach_whole_space:
        cannot_check_reasons.append(
            f"the assertion blocks evaluate the rule at {len(asserted_points)} of the "
            f"{assertion_space} (native_valid, closure) states and at "
            f"{asserted_donor_invalid} of the {assertion_space // 2} with "
            "native_valid=False, so no assertion here can refute a theory that ignores "
            "the donor transform's own verdict"
        )

    result = {
        "schema": "P7.X2.ClosureCarryingResult.v1",
        "donor_families": list(DONORS),
        "closure_coordinates": list(COORDS),
        "state_evaluations": len(rows),
        "donor_conservativity_violations": (
            donor_conservativity_violations if conservativity_checkable else None
        ),
        "donor_conservativity_status": "CHECKED" if conservativity_checkable else "CANNOT_CHECK",
        "donor_conservativity_states": donor_conservativity_states,
        "donor_conservativity_distinct_states": donor_conservativity_states // donor_multiplier,
        "single_coordinate_separation_witnesses": separation_witnesses,
        "donor_product_nonclosure_countermodels": product_countermodels,
        "full_closure_refinement_successes": full_refinement_successes,
        "partial_closure_refinement_failures": partial_refinement_failures,
        "composition_successes": composition_successes,
        "composition_bridge_countermodels": composition_bridge_countermodels,
        "ideal_product_mismatches": ideal_product_mismatches if ideal_product_checkable else None,
        "ideal_product_status": "CHECKED" if ideal_product_checkable else "CANNOT_CHECK",
        # Assertion coverage. It read PARTIAL --- 32 of 64 states, 0 of the 32 with
        # native_valid=False --- for as long as every assertion here ran at
        # native_valid=True, which is why a theory that drops the donor transform's
        # own verdict walked through the whole file. It is COMPLETE now, and not
        # because a "nothing carries without a valid donor" assertion was bolted on:
        # the conservativity block quantifies over each fibre of the projection, so
        # the missing half of the space is visited by that claim itself.
        "assertion_state_space": assertion_space,
        "assertion_covered_states": len(asserted_points),
        "assertion_covered_states_native_invalid": asserted_donor_invalid,
        "assertion_uncovered_states": assertion_space - len(asserted_points),
        "assertion_coverage_status": "COMPLETE" if assertions_reach_whole_space else "PARTIAL",
        # An axis no verdict depends on multiplies every count enumerated inside it.
        # Published so the headline numbers carry their own multiplicity rather than
        # reading as that many distinct facts.
        "donor_axis": {
            "values": len(DONORS),
            "read_by_carries_or_compose": bool(donor_reading_rules),
            "verdict_rules_taking_a_donor_argument": list(donor_reading_rules),
            "multiplier": donor_multiplier,
            "pair_multiplier": donor_pair_multiplier,
            "distinct_state_evaluations": len(rows) // donor_multiplier,
            "distinct_separation_witnesses": separation_witnesses // donor_multiplier,
            "distinct_product_countermodels": product_countermodels,
            "distinct_full_refinement_successes": full_refinement_successes // donor_multiplier,
            "distinct_partial_refinement_failures": (
                partial_refinement_failures // donor_multiplier
            ),
            "distinct_composition_successes": composition_successes // donor_pair_multiplier,
            "distinct_composition_bridge_countermodels": (
                composition_bridge_countermodels // donor_pair_multiplier
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
            and separation_witnesses == 25
            and product_countermodels == 31
            and full_refinement_successes == 155
            and partial_refinement_failures == 1055
            and composition_successes == 25
            and composition_bridge_countermodels == 25
            else "FAIL"
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
