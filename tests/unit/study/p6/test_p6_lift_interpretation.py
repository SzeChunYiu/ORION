"""Tests for P6's certificate lift as an instance of stated primitives.

A conjunction is the easiest thing to reproduce by accident, so the tests that
matter are the ones that change the shipped rule underneath the derivation. The
first version of these passed against all three mutations, because the module
imported `reference_admissible` by value and the perturbations never reached it
-- a mutation test measuring an unperturbed object. That is pinned below.
"""

from __future__ import annotations

import json

import pytest

from orion.study.p6 import finite_model_theories as fm
from orion.study.p6 import lift_interpretation as li


@pytest.fixture(scope="module")
def baseline() -> dict:
    return li.soundness_check()


class TestSoundness:
    def test_the_derivation_reproduces_the_shipped_lift_everywhere(self, baseline: dict) -> None:
        assert baseline["disagreement_count"] == 0
        assert baseline["sound"] is True
        assert baseline["agreements"] == baseline["states"] == 1536

    def test_both_verdicts_are_present_in_the_space(self, baseline: dict) -> None:
        """A rule validated only where it refuses has been validated on one answer."""

        assert baseline["both_verdicts_present"] is True
        assert baseline["admissible_states"] == 24
        assert baseline["inadmissible_states"] == 1512


class TestItIsADerivationNotARestatement:
    @staticmethod
    def _with_rule(replacement) -> dict:
        original = fm.reference_admissible
        fm.reference_admissible = replacement
        try:
            return li.soundness_check()
        finally:
            fm.reference_admissible = original

    def test_making_a_scientific_coordinate_compensatory_breaks_it(self) -> None:
        def compensatory(point):
            donor = all(point[n] for n in fm.EMBEDDINGS[str(point["embedding"])])
            return donor and sum(1 for n in fm.SCI_FIELDS if point[n]) >= 3

        report = self._with_rule(compensatory)
        assert report["sound"] is False
        assert report["disagreement_count"] == 96

    def test_waiving_an_embeddings_donor_requirement_breaks_it(self) -> None:
        def waivable(point):
            required = fm.EMBEDDINGS[str(point["embedding"])]
            donor = all(point[n] for n in required) or all(
                point[n] for n in fm.DONOR_FIELDS if n not in required
            )
            return donor and all(point[n] for n in fm.SCI_FIELDS)

        report = self._with_rule(waivable)
        assert report["sound"] is False
        assert report["disagreement_count"] == 9

    def test_dropping_conservativity_breaks_it(self) -> None:
        """A lift that may outrun its donor is a different rule and must be seen as one."""

        def non_conservative(point):
            return all(point[n] for n in fm.SCI_FIELDS)

        report = self._with_rule(non_conservative)
        assert report["sound"] is False
        assert report["disagreement_count"] == 72

    def test_the_module_reads_the_shipped_rule_through_its_module(self) -> None:
        """Pin the import style, because by-value import made these tests vacuous.

        `from finite_model_theories import reference_admissible` binds the
        function object at import time, so rebinding the name in that module
        leaves this one calling the original. All three mutations above passed
        under it while changing nothing.
        """

        source = (
            li.__file__ and __import__("pathlib").Path(li.__file__).read_text(encoding="utf-8")
        )
        assert "_shipped.reference_admissible(point)" in source
        assert "    reference_admissible,\n" not in source


class TestTheRevalidationModelIsDerived:
    """155 restorations and 1,055 strict-subset failures, from the same primitive."""

    def test_both_published_counts_are_reproduced(self) -> None:
        report = li.derive_revalidation()
        assert report["full_restorations"] == 155
        assert report["proper_subset_failures"] == 1055
        assert report["derived"] is True

    def test_no_full_repair_fails_and_no_proper_subset_succeeds(self) -> None:
        """Soundness and minimality, stated as the absence of counterexamples."""

        report = li.derive_revalidation()
        assert report["soundness_counterexamples"] == []
        assert report["minimality_counterexamples"] == []

    @staticmethod
    def _with_primitive(replacement) -> dict:
        original = li._admissible_from_coordinates
        li._admissible_from_coordinates = replacement
        try:
            return li.derive_revalidation()
        finally:
            li._admissible_from_coordinates = original

    @pytest.mark.parametrize(
        ("label", "rule", "expected_partial"),
        [
            ("one coordinate compensatory", lambda c: sum(c) >= len(c) - 1, 655),
            ("majority suffices", lambda c: sum(c) > len(c) // 2, 255),
            ("always admissible", lambda c: True, 0),
        ],
    )
    def test_weakening_the_primitive_moves_the_discriminating_count(
        self, label: str, rule, expected_partial: int
    ) -> None:
        report = self._with_primitive(rule)
        assert report["proper_subset_failures"] == expected_partial, label
        assert report["derived"] is False

    def test_the_full_restoration_count_is_a_weak_witness_and_says_so(self) -> None:
        """155 survives every perturbation, so it discriminates nothing.

        A full repair sets every coordinate true and therefore satisfies any
        monotone rule. Reporting it beside the 1,055 without saying which one
        carries the claim would overstate what the pair establishes.
        """

        for rule in (lambda c: sum(c) >= len(c) - 1, lambda c: sum(c) > len(c) // 2, lambda c: True):
            assert self._with_primitive(rule)["full_restorations"] == 155

        report = li.derive_revalidation()
        assert "discriminates between very few" in report["full_restorations_are_a_weak_witness"]


class TestTheDerivationIsTiedToTheShippedEnumeration:
    """Matching two integers is weak; being accepted by the shipped block is not."""

    def test_the_constants_come_from_the_shipped_enumeration(self) -> None:
        from orion.study.p6 import lift_theories

        assert li.REVALIDATION_DONORS is lift_theories.DONOR_FAMILIES
        assert li.REVALIDATION_COORDS is lift_theories.LIFT_COORDINATES

    def test_the_shipped_revalidation_block_accepts_the_derived_rule(self) -> None:
        assert li.shipped_block_accepts_the_derivation() is True

    @pytest.mark.parametrize(
        "mutation",
        [
            pytest.param(lambda c: all(c[1:]), id="one-coordinate-compensatory"),
            pytest.param(lambda c: sum(c) * 2 > len(c), id="majority-suffices"),
            pytest.param(lambda c: True, id="always-admissible"),
        ],
    )
    def test_the_shipped_block_rejects_a_weakened_primitive(self, mutation) -> None:
        original = li._admissible_from_coordinates
        try:
            li._admissible_from_coordinates = mutation
            assert li.shipped_block_accepts_the_derivation() is False
        finally:
            li._admissible_from_coordinates = original

    def test_the_shipped_block_is_blind_to_conservativity_and_that_is_recorded(
        self,
    ) -> None:
        # Not a defect in the derivation -- a limit of the block, which pins
        # native_valid true everywhere it asserts. Pinned so the report's
        # blindspot note cannot become stale without a test failing.
        assert li.shipped_block_sees_conservativity() is False
        report = li.derive_revalidation()
        assert report["shipped_block_sees_conservativity"] is False
        assert "no falsifier for conservativity" in report["shipped_block_blindspot"]


class TestTheReport:
    def test_the_report_carries_both_derivations_and_is_sound(self) -> None:
        report = li.build_report(date="2026-08-22")
        assert report["sound"] is True
        assert report["both_verdicts_present"] is True
        assert report["revalidation"]["derived"] is True
        assert report["record"] == "P6_LIFT_INTERPRETATION"
        assert report["schema_version"] == li.SCHEMA_VERSION

    def test_the_date_is_supplied_not_read_from_the_clock(self) -> None:
        # A content-bound artifact that changes on every regeneration cannot be
        # compared against the one that was reviewed.
        assert li.build_report(date="1999-01-01")["date"] == "1999-01-01"

    def test_the_cli_writes_the_artifact_and_reports_success(self, tmp_path) -> None:
        out = tmp_path / "nested" / "report.json"
        assert li.main(["--date", "2026-08-22", "--output", str(out)]) == 0
        written = json.loads(out.read_text(encoding="utf-8"))
        assert written["revalidation"]["full_restorations"] == 155
        assert written["revalidation"]["proper_subset_failures"] == 1055

    def test_the_cli_fails_when_the_derivation_does_not_reproduce_the_counts(
        self,
    ) -> None:
        original = li._admissible_from_coordinates
        try:
            li._admissible_from_coordinates = lambda c: sum(c) * 2 > len(c)
            assert li.main(["--date", "2026-08-22"]) == 3
        finally:
            li._admissible_from_coordinates = original
