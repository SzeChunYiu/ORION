"""Tests for P6's certificate lift as an instance of stated primitives.

A conjunction is the easiest thing to reproduce by accident, so the tests that
matter are the ones that change the shipped rule underneath the derivation. The
first version of these passed against all three mutations, because the module
imported `reference_admissible` by value and the perturbations never reached it
-- a mutation test measuring an unperturbed object. That is pinned below.
"""

from __future__ import annotations

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
