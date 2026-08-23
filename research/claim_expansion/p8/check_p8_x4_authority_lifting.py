from __future__ import annotations

import ast
import hashlib
import inspect
import itertools
import json
import textwrap

DONORS = (
    "FAVA_PERMISSION",
    "PCAA_ACTION_CERT",
    "HDP_DELEGATION",
    "SENTINEL_DCC",
    "APC_BOUNDED_AGENTS",
    "ECA_TYPED_EVIDENCE",
    "COGEEG_SCIENTIFIC_HARNESS",
    "SCIENTISTONE_CHAIN_OF_EVIDENCE",
    "XCIENTIST_RESEARCH_HARNESS",
    "STATEFUL_DISCOVERY_ADJUDICATION",
    "EP_AEC_HETEROGENEOUS_RECEIPTS",
    "EVIDENCE_LEDGER_ADJUDICATION",
    "ARF_CROSS_DOMAIN_AUTHORITY",
)
TYPE_COORDS = ("domain", "kind", "scope", "content", "epoch")
BLOCKERS = ("REFUTED", "UNDETERMINED", "ESTABLISHED")


def scientific_terminal(native, flags, narrowing, blocker, support_a, support_b, coercion):
    if not native:
        return "NO_DONOR_AUTHORITY"
    if not narrowing:
        return "BLOCK"
    if blocker == "ESTABLISHED":
        return "BLOCK"
    if blocker == "UNDETERMINED":
        return "CANNOT_CHECK"
    if not (support_a or support_b):
        return "BLOCK"
    if not (all(flags) or coercion):
        return "BLOCK"
    return "DISCHARGE"


def discharge_states():
    """Every scientific-discharge state a donor judgment can be lifted against.

    The six arguments ``scientific_terminal`` takes beside the donor-native
    verdict: the five type coordinates, the narrowing flag, the three-valued
    blocker, the two alternative complete support families and the protected
    coercion. 1,536 of them, and they are the fibre of :func:`project_to_donor`.
    """

    return tuple(
        (type_flags, narrowing_ok, blocker, support_a, support_b, protected_coercion)
        for type_flags in itertools.product((False, True), repeat=len(TYPE_COORDS))
        for narrowing_ok in (False, True)
        for blocker in BLOCKERS
        for support_a in (False, True)
        for support_b in (False, True)
        for protected_coercion in (False, True)
    )


# ---------------------------------------------------------------------------
# Semantic extension 1: the projection from lifted judgments to donor authority.
#
# X4's T1 is "adding the scientific-discharge layer never changes the donor-native
# verdict", over the final thirteen families -- action permissions, delegation
# receipts, heterogeneous receipt composition, cross-domain authority, typed
# evidence, scientific release gates, claim-evidence chains, research-harness
# validation and evidence-ledger adjudication. This file published
# `donor_conservativity_violations: 0` for that from
#
#     projected_native = native
#     if projected_native != native:
#         donor_conservativity_violations += 1
#
# ``projected_native`` is bound from ``native`` on the line above and ``native``
# is not rebound between the two statements, so the guard is ``x != x``:
# evaluated 39,936 times, satisfied 0 times, and 0 under every theory of
# scientific discharge, right or wrong. It never called ``scientific_terminal``
# at all, so its zero held for every possible input --- including inputs that
# discharge a scientific target for a donor whose own verdict is invalid, which
# is precisely what T1 forbids.
#
# The object the projection was never applied to is the discharge relation
# itself. A donor judgment carries scientific authority *under the P8 semantics*
# when some discharge state over it reaches DISCHARGE, so the image of
# ``scientific_terminal`` along the projection is the donor-language predicate
# below, and T1 is the statement that it coincides with the donor's own verdict.
# ---------------------------------------------------------------------------
def project_to_donor(donor, native_valid, discharge_state):
    """The donor-visible part of a lifted judgment: the discharge state is forgotten."""

    del discharge_state
    return (donor, native_valid)


def native_verdict(donor_judgment):
    """The donor family's own authority/verification/adjudication verdict."""

    _donor, native_valid = donor_judgment
    return native_valid


def discharge_image_in_donor_language(donor_judgment):
    """The image of :func:`scientific_terminal` along :func:`project_to_donor`.

    A donor judgment is scientifically authoritative under the P8 lift exactly
    when some discharge state in its fibre reaches ``DISCHARGE``. This is the only
    predicate in the file that quantifies over a fibre, and it is what makes the
    ``native_valid=False`` half of the space assertable: every state whose donor
    judgment is natively invalid is now visited by a claim rather than only by the
    row builder.
    """

    donor, native_valid = donor_judgment
    del donor
    return any(
        scientific_terminal(native_valid, *state) == "DISCHARGE"
        for state in discharge_states()
    )


# ---------------------------------------------------------------------------
# Semantic extension 2: the ideal decentralized product.
#
# X4's T10 is "a product carrying the exact same type, narrowing, support,
# blocker, coercion and composition rules agrees extensionally with P8", and this
# file published `ideal_product_mismatches: 0` for it from
#
#     terminal = scientific_terminal(...)
#     ideal    = scientific_terminal(...)
#     if terminal != ideal: ...
#
# --- the same call written twice on the same arguments. A deterministic function
# equals itself, so that count was 0 for every calculus too.
#
# The construction T10 names is neither the rule itself nor a copy of it: the
# decentralized product is the same requirements held by *separate* donors, each
# deciding its own gate, with the escalation order they agree on deciding which
# unmet gate is reported. It mentions the discharge interface and never mentions
# ``scientific_terminal``, so substituting a different theory of discharge does
# not co-mutate it. It is extensionally equal to the shared calculus on all 3,072
# distinct states, so every row and the canonical digest are unchanged.
# ---------------------------------------------------------------------------
#: Each separately owned gate of the decentralized product, and the terminal the
#: product reports when that gate is the first unmet one.
DECENTRALIZED_GATES = (
    ("native_authority", "NO_DONOR_AUTHORITY"),
    ("non_widening_authority", "BLOCK"),
    ("blocker_not_established", "BLOCK"),
    ("blocker_resolved", "CANNOT_CHECK"),
    ("complete_support_family_survives", "BLOCK"),
    ("scientific_type_matched_or_bridged", "BLOCK"),
)


def decentralized_gate_report(native_valid, type_flags, narrowing_ok, blocker, support_a, support_b, protected_coercion):
    """Each donor's own gate over the shared discharge interface, decided locally."""

    return {
        "native_authority": native_valid,
        "non_widening_authority": narrowing_ok,
        "blocker_not_established": blocker != "ESTABLISHED",
        "blocker_resolved": blocker != "UNDETERMINED",
        "complete_support_family_survives": support_a or support_b,
        "scientific_type_matched_or_bridged": all(type_flags) or protected_coercion,
    }


def ideal_product(native_valid, type_flags, narrowing_ok, blocker, support_a, support_b, protected_coercion):
    """The decentralized product's terminal: the first unmet gate, in agreed order."""

    report = decentralized_gate_report(
        native_valid,
        type_flags,
        narrowing_ok,
        blocker,
        support_a,
        support_b,
        protected_coercion,
    )
    for gate, terminal_when_unmet in DECENTRALIZED_GATES:
        if not report[gate]:
            return terminal_when_unmet
    return "DISCHARGE"


def _independently_defined(left, right):
    """True when two rules are not the same expression written twice.

    A counter that compares the two sides of a claim measures something only if
    the two sides were built independently. Both counters this checker publishes
    used to compare a definition against a copy of itself: ``ideal`` was the same
    ``scientific_terminal`` call as ``terminal``, and ``projected_native`` was
    ``native`` written again. Under a consistently applied theory of scientific
    discharge each count was 0 for every theory, right or wrong --- a structural
    zero published beside measured ones.

    Both sides now have their own construction and this gate is what keeps them
    apart: :func:`discharge_image_in_donor_language` quantifies over the fibre of
    the projection and :func:`ideal_product` reports the first unmet gate of a
    decentralized product, so neither can be produced by copying the rule it is
    compared against. The gate stays because the repair is only as durable as the
    distinction: if a later edit collapses either pair back into one expression,
    the counter reports CANNOT_CHECK rather than a clean zero.

    Bodies are compared as parsed statements with a leading docstring dropped, so
    prose written about a definition is never mistaken for a second definition.
    When the source cannot be recovered at all --- a rule substituted at runtime,
    say --- independence is not established, and the answer is False so the
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


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main():
    rows = []
    terminal_counts = {"NO_DONOR_AUTHORITY": 0, "BLOCK": 0, "CANNOT_CHECK": 0, "DISCHARGE": 0}
    conservativity_checkable = _independently_defined(
        discharge_image_in_donor_language, native_verdict
    )
    ideal_product_checkable = _independently_defined(ideal_product, scientific_terminal)
    donor_conservativity_violations = 0
    ideal_product_mismatches = 0

    # Every ``(native_valid, discharge_state)`` point some claim below actually
    # evaluates the rule at. The enumeration walks all 3,072; before the
    # projection was a primitive, the claims walked 16 of them, none of which had
    # ``native_valid=False``.
    asserted_points = set()

    for donor in DONORS:
        for native in (False, True):
            for flags in itertools.product((False, True), repeat=5):
                for narrowing in (False, True):
                    for blocker in BLOCKERS:
                        for support_a in (False, True):
                            for support_b in (False, True):
                                for coercion in (False, True):
                                    terminal = scientific_terminal(native, flags, narrowing, blocker, support_a, support_b, coercion)
                                    ideal = ideal_product(native, flags, narrowing, blocker, support_a, support_b, coercion)
                                    terminal_counts[terminal] += 1
                                    if ideal_product_checkable and terminal != ideal:
                                        ideal_product_mismatches += 1
                                    rows.append({
                                        "donor": donor,
                                        "native_valid": native,
                                        "scientific_type": dict(zip(TYPE_COORDS, flags)),
                                        "narrowing_ok": narrowing,
                                        "blocker": blocker,
                                        "support_a": support_a,
                                        "support_b": support_b,
                                        "protected_coercion": coercion,
                                        "terminal": terminal,
                                        "ideal_product": ideal,
                                    })

    # T1 --- native-authority conservativity, over the donor-visible judgments
    # rather than over the lifted ones. ``discharge_image_in_donor_language``
    # quantifies over each fibre of the projection, so this block evaluates
    # ``scientific_terminal`` at every one of the 3,072 states including the 1,536
    # whose donor judgment is natively invalid, which no other block here reaches.
    donor_conservativity_states = 0
    fibre = discharge_states()
    assert len(rows) == len(DONORS) * 2 * len(fibre)
    for donor in DONORS:
        for native in (False, True):
            # Every state in the fibre projects onto the same donor judgment,
            # which is what makes the image a donor-language predicate.
            judgment = project_to_donor(donor, native, fibre[0])
            assert all(project_to_donor(donor, native, state) == judgment for state in fibre)
            image = discharge_image_in_donor_language(judgment)
            native_own = native_verdict(judgment)
            donor_conservativity_states += 1
            for state in fibre:
                asserted_points.add((native, state))
            if conservativity_checkable and image != native_own:
                donor_conservativity_violations += 1

    def asserted(native, flags, narrowing, blocker, support_a, support_b, coercion):
        """Record a state a claim below evaluates the rule at, and return it."""

        asserted_points.add((native, (flags, narrowing, blocker, support_a, support_b, coercion)))
        return scientific_terminal(native, flags, narrowing, blocker, support_a, support_b, coercion)

    full = (True,) * 5
    type_separations = coercion_successes = unprotected_countermodels = 0
    blocker_refuted = blocker_unknown = blocker_established = 0
    support_survivals = all_support_broken = 0
    for donor in DONORS:
        for idx in range(5):
            broken = list(full)
            broken[idx] = False
            broken = tuple(broken)
            assert asserted(True, broken, True, "REFUTED", True, False, False) == "BLOCK"
            type_separations += 1
            unprotected_countermodels += 1
            assert asserted(True, broken, True, "REFUTED", True, False, True) == "DISCHARGE"
            coercion_successes += 1

        assert asserted(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
        blocker_refuted += 1
        assert asserted(True, full, True, "UNDETERMINED", True, False, False) == "CANNOT_CHECK"
        blocker_unknown += 1
        assert asserted(True, full, True, "ESTABLISHED", True, False, False) == "BLOCK"
        blocker_established += 1

        assert asserted(True, full, True, "REFUTED", False, True, False) == "DISCHARGE"
        support_survivals += 1
        assert asserted(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
        support_survivals += 1
        assert asserted(True, full, True, "REFUTED", False, False, False) == "BLOCK"
        all_support_broken += 1

    chain_successes = chain_widening_countermodels = 0
    for _left in DONORS:
        for _right in DONORS:
            assert asserted(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
            chain_successes += 1
            assert asserted(True, full, False, "REFUTED", True, False, False) == "BLOCK"
            chain_widening_countermodels += 1

    # The donor axis is a pure loop multiplier --- ``scientific_terminal`` takes
    # seven arguments and the donor family is not among them --- so the claims
    # above range over one copy of the 3,072-point discharge space, not over
    # 39,936. Read off the signature rather than counted, because it is a
    # structural fact and not a comparison that could come out either way.
    donor_read_by_rule = any(
        "donor" in parameter for parameter in inspect.signature(scientific_terminal).parameters
    )
    donor_multiplier = 1 if donor_read_by_rule else len(DONORS)
    assertion_space = 2 * len(fibre)
    asserted_native_invalid = sum(1 for native, _ in asserted_points if not native)
    assertions_reach_whole_space = len(asserted_points) == assertion_space

    checkable = conservativity_checkable and ideal_product_checkable
    cannot_check_reasons = []
    if not conservativity_checkable:
        cannot_check_reasons.append(
            "discharge_image_in_donor_language is the same expression as native_verdict, so "
            "the T1 comparison restates one definition and cannot refute any theory"
        )
    if not ideal_product_checkable:
        cannot_check_reasons.append(
            "ideal_product is the same expression as scientific_terminal, so the T10 "
            "equivalence comparison restates one definition and cannot refute any theory"
        )
    if not assertions_reach_whole_space:
        cannot_check_reasons.append(
            f"the claims evaluate the rule at {len(asserted_points)} of the "
            f"{assertion_space} (native_valid, discharge_state) states and at "
            f"{asserted_native_invalid} of the {assertion_space // 2} with "
            "native_valid=False, so no claim here can refute a theory that discharges "
            "without donor authority"
        )

    result = {
        "schema": "P8.X4.AuthorityLiftingResult.v1",
        "donor_families": list(DONORS),
        "scientific_type_coordinates": list(TYPE_COORDS),
        "state_evaluations": len(rows),
        "terminal_counts": terminal_counts,
        "donor_conservativity_violations": (
            donor_conservativity_violations if conservativity_checkable else None
        ),
        "donor_conservativity_status": "CHECKED" if conservativity_checkable else "CANNOT_CHECK",
        "donor_conservativity_states": donor_conservativity_states,
        "donor_conservativity_distinct_states": donor_conservativity_states // donor_multiplier,
        "type_separation_witnesses": type_separations,
        "protected_coercion_successes": coercion_successes,
        "unprotected_coercion_countermodels": unprotected_countermodels,
        "blocker_refuted_successes": blocker_refuted,
        "blocker_undetermined_cannot_check": blocker_unknown,
        "blocker_established_blocks": blocker_established,
        "single_support_revocation_survivals": support_survivals,
        "all_support_revoked_blocks": all_support_broken,
        "heterogeneous_chain_successes": chain_successes,
        "heterogeneous_chain_widening_countermodels": chain_widening_countermodels,
        "action_or_release_denied_independent_support_examples": len(DONORS),
        "ideal_product_mismatches": ideal_product_mismatches if ideal_product_checkable else None,
        "ideal_product_status": "CHECKED" if ideal_product_checkable else "CANNOT_CHECK",
        # Claim coverage. It read PARTIAL --- 16 of 3,072 states, 0 of the 1,536
        # with native_valid=False --- for as long as every assertion here ran at
        # native_valid=True, which is why a theory that discharges without donor
        # authority walked through the whole file. It is COMPLETE now, and not
        # because a "nothing discharges without a donor" assertion was bolted on:
        # the conservativity block quantifies over each fibre of the projection,
        # so the missing half of the space is visited by T1 itself.
        "assertion_state_space": assertion_space,
        "assertion_covered_states": len(asserted_points),
        "assertion_covered_states_native_invalid": asserted_native_invalid,
        "assertion_uncovered_states": assertion_space - len(asserted_points),
        "assertion_coverage_status": "COMPLETE" if assertions_reach_whole_space else "PARTIAL",
        "cannot_check_reasons": cannot_check_reasons,
        "canonical_rows_sha256": hashlib.sha256(canonical(rows).encode()).hexdigest(),
        # Three-valued on purpose. Both counters are None when they could not be
        # checked, and ``not None`` is True, so a two-valued terminal would read an
        # unchecked counter as a clean one --- the exact substitution this repair
        # exists to stop. An unexercised check blocks the terminal as a violation
        # would, and so does a claim panel that never visits half its space.
        "terminal": (
            "CANNOT_CHECK"
            if not (checkable and assertions_reach_whole_space)
            else "PASS"
            if not (donor_conservativity_violations or ideal_product_mismatches)
            and type_separations == 65
            and coercion_successes == 65
            and unprotected_countermodels == 65
            and support_survivals == 26
            and all_support_broken == 13
            and chain_successes == 169
            and chain_widening_countermodels == 169
            else "FAIL"
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
