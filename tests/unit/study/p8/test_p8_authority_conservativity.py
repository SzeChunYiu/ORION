"""P8's donor-conservativity count, before and after it could produce a number.

All three claim-expansion checkers published ``donor_conservativity_violations: 0``
for T1 and ``ideal_product_mismatches: 0`` for T9/T10 from guards whose two
operands could not differ. The pre-repair shapes are kept here as fixtures rather
than as prose, so the detector that says they are gone is pinned against source
that has them.

The decisive test is :meth:`TestTheNegativeControl.test_the_control_fires`: a
theory that discharges a scientific target for a donor whose own verdict is
invalid, run through the shipped file end to end. It is what separates a repaired
guard from a differently-worded dead one.
"""

from __future__ import annotations

import inspect

import pytest

from orion.study.p8 import authority_conservativity as conservativity

LABELS = ("X2", "X3", "X4")

#: Donor families per pass, and therefore the number of natively invalid donor
#: judgments a conservativity violation is counted at.
DONOR_COUNT = {"X2": 6, "X3": 10, "X4": 13}

#: The guards as shipped, transcribed from the three files at
#: ``research/claim_expansion/p8`` before 2026-08-22. Both are dead: the first
#: compares a name against the name it was just assigned from, the second compares
#: a deterministic call against the same call written again.
PRE_REPAIR_GUARDS = '''
def main():
    donor_conservativity_violations = 0
    ideal_product_mismatches = 0
    for native in (False, True):
        terminal = scientific_terminal(native, flags)
        ideal = scientific_terminal(native, flags)
        if terminal != ideal:
            ideal_product_mismatches += 1
        projected_native = native
        if projected_native != native:
            donor_conservativity_violations += 1
'''


@pytest.fixture(scope="module", params=LABELS)
def label(request) -> str:
    return request.param


@pytest.fixture(scope="module")
def capacity(label) -> dict:
    return conservativity.donor_conservativity_capacity(label)


class TestTheGuardThatCouldNotFire:
    """The defect, stated mechanically and kept as a regression."""

    def test_the_detector_finds_both_shipped_shapes(self, tmp_path) -> None:
        scratch = tmp_path / "pre_repair_guards.py"
        scratch.write_text(PRE_REPAIR_GUARDS, encoding="utf-8")

        assert conservativity.identity_guards(scratch) == (
            "main: projected_native != native",
            "main: terminal != ideal",
        )

    def test_a_rebound_name_is_not_reported(self, tmp_path) -> None:
        """The detector has to be able to stay silent, or its silence says nothing.

        ``first = point`` inside a loop that rebinds ``point`` is a real
        comparison, and so are two identical calls with a mutation between them.
        Neither is an identity guard and neither is reported.
        """

        scratch = tmp_path / "real_comparisons.py"
        scratch.write_text(
            "def read(points, allocator):\n"
            "    first = None\n"
            "    for point in points:\n"
            "        if first is None:\n"
            "            first = point\n"
            "        if point == first:\n"
            "            continue\n"
            "    before = state(allocator)\n"
            "    allocator.record()\n"
            "    after = state(allocator)\n"
            "    if after != before:\n"
            "        raise AssertionError\n",
            encoding="utf-8",
        )

        assert conservativity.identity_guards(scratch) == ()

    def test_no_identity_guard_remains_in_any_of_the_three_checkers(self, label) -> None:
        assert conservativity.identity_guards(conservativity.CHECKERS[label]) == ()

    def test_the_repaired_operands_are_not_the_same_binding(self, label) -> None:
        """The AST independence gate, checked from the outside as well as inside.

        ``discharge_image_in_donor_language`` quantifies over the fibre of the
        projection and ``native_verdict`` reads one field of the projected
        judgment; ``ideal_product`` walks the decentralized product's gate table
        and ``scientific_terminal`` is the shared calculus. No pair is the other
        written twice, which is what makes each comparison capable of failing.
        """

        module = conservativity.checker_module(label, "_independence")

        assert module._independently_defined(
            module.discharge_image_in_donor_language, module.native_verdict
        )
        assert module._independently_defined(module.ideal_product, module.scientific_terminal)
        assert not module._independently_defined(module.native_verdict, module.native_verdict)


class TestTheNegativeControl:
    """A control that does not fire is not evidence that a guard works."""

    def test_the_control_fires(self, capacity, label) -> None:
        """``discharges_without_donor_authority`` moves the count off zero.

        One violation per donor family, because it is the natively invalid
        judgment of each family that acquires scientific authority it was never
        given. The theory is held consistently across both sides of both counters,
        so the ideal-product tie reports 0 and the conservativity count is the only
        quantity in the artifact that moves.
        """

        assert capacity["violations_under_the_theory_held_consistently"] == DONOR_COUNT[label]
        assert capacity["ideal_mismatches_under_the_theory_held_consistently"] == 0
        assert capacity["terminal_under_the_theory"] == "FAIL"

    def test_no_assertion_in_the_file_can_see_the_same_theory(self, capacity) -> None:
        """Which is what makes the count load-bearing rather than redundant.

        Every assertion in all three files evaluates the rule at
        ``native_valid=True``, where this theory agrees with the shipped calculus
        exactly. All eight assertion-derived counts are unchanged under it.
        """

        assert capacity["assertion_counts_unchanged_under_the_theory"] == tuple(
            sorted(conservativity.ASSERTION_COUNTS)
        )

    def test_the_unmutated_checker_still_reports_its_real_value(self, capacity) -> None:
        assert capacity["status"] == "CHECKED"
        assert capacity["violations"] == 0
        assert capacity["distinct_donor_judgments"] == 2

    def test_collapsing_the_two_sides_reports_cannot_check_not_a_clean_zero(
        self, capacity
    ) -> None:
        """The durability gate: the repair is only as good as the distinction it made."""

        assert capacity["collapsed_status"] == "CANNOT_CHECK"
        assert capacity["collapsed_violations"] is None
        assert capacity["collapsed_terminal"] == "CANNOT_CHECK"


class TestWhatTheCountNowMeasures:
    def test_the_claim_panel_reaches_the_whole_discharge_space(self, label) -> None:
        """And reaches it through T1 itself, not through a bolted-on assertion.

        Before the projection was a primitive, the assertion blocks visited 17 of
        3,072 states in X2 and 16 in X3 and X4, and none of the 1,536 with
        ``native_valid=False``, which is why a theory that discharges without
        donor authority walked through the whole file. The conservativity block quantifies over each fibre, so the
        missing half is visited by the claim that is about it.
        """

        shipped = conservativity.shipped_result(label)

        assert shipped["assertion_state_space"] == 3072
        assert shipped["assertion_covered_states"] == 3072
        assert shipped["assertion_covered_states_native_invalid"] == 1536
        assert shipped["assertion_coverage_status"] == "COMPLETE"

    def test_the_donor_axis_is_a_replication_factor_over_two_decided_judgments(
        self, label
    ) -> None:
        """``scientific_terminal`` takes seven arguments and donor is not one.

        So the block visits one judgment per donor family per native verdict and
        decides two distinct things, however many families are registered.
        """

        shipped = conservativity.shipped_result(label)

        assert shipped["donor_conservativity_states"] == 2 * DONOR_COUNT[label]
        assert shipped["donor_conservativity_distinct_states"] == 2

    def test_the_image_is_the_only_predicate_quantifying_over_a_fibre(self, label) -> None:
        """The projection is what carries the claim; nothing else in the file has it."""

        module = conservativity.checker_module(label, "_fibre")
        fibre = module.discharge_states()

        assert len(fibre) == 1536
        for native in (False, True):
            judgment = module.project_to_donor(module.DONORS[0], native, fibre[0])
            assert all(
                module.project_to_donor(module.DONORS[0], native, state) == judgment
                for state in fibre
            )
            assert module.discharge_image_in_donor_language(judgment) is native
            assert module.native_verdict(judgment) is native

    def test_the_ideal_product_never_mentions_the_rule_it_is_compared_against(
        self, label
    ) -> None:
        """T9/T10's product is a third construction, not the calculus or a copy of it.

        If it named ``scientific_terminal`` it would co-mutate with every theory
        substituted for the calculus and the tie could not fail; the separately
        owned gate table is what keeps it able to.
        """

        module = conservativity.checker_module(label, "_product")
        product = inspect.getsource(module.ideal_product)
        gates = inspect.getsource(module.decentralized_gate_report)

        assert "scientific_terminal" not in product
        assert "scientific_terminal" not in gates
        assert len(module.DECENTRALIZED_GATES) == 6
        assert dict(module.DECENTRALIZED_GATES)["native_authority"] == "NO_DONOR_AUTHORITY"
