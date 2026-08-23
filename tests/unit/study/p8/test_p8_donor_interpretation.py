"""Tests for P8's donor model as an instance of the proved calculus.

The whole risk here is that an "interpretation" is really a transcription: if
the derived terminal reimplements X4's if-chain, agreement is guaranteed and
derives nothing. So the central test is not that the two agree -- it is that
they stop agreeing when X4's semantics is changed underneath.
"""

from __future__ import annotations

import pytest

from orion.study.p8 import donor_interpretation as di
from orion.study.p8.authority_terminals import x4_module


@pytest.fixture(scope="module")
def baseline() -> dict:
    return di.soundness_check()


class TestSoundness:
    def test_the_calculus_reproduces_x4_on_every_distinct_state(self, baseline: dict) -> None:
        assert baseline["disagreement_count"] == 0
        assert baseline["sound"] is True
        assert baseline["agreements"] == baseline["distinct_states"]

    def test_the_instance_count_is_the_honest_one(self, baseline: dict) -> None:
        """3,072 distinct states, not 39,936 -- the donor axis is a replication factor."""

        assert baseline["distinct_states"] == 3072
        assert baseline["total_enumerated_points"] == 39936
        assert baseline["donor_replication"] == 13

    def test_every_terminal_is_actually_reached(self, baseline: dict) -> None:
        """An interpretation validated only on one outcome derives one outcome."""

        assert baseline["every_terminal_reached"] is True
        covered = baseline["terminals_covered"]
        assert set(covered) == {"BLOCK", "CANNOT_CHECK", "DISCHARGE", "NO_DONOR_AUTHORITY"}
        assert all(count > 0 for count in covered.values())


class TestItIsADerivationNotATranscription:
    """Change X4 underneath; the derivation must notice."""

    @staticmethod
    def _with_terminal(replacement):
        module = x4_module()
        original = module.scientific_terminal
        module.scientific_terminal = replacement
        try:
            return di.soundness_check()
        finally:
            module.scientific_terminal = original

    def test_removing_the_support_requirement_breaks_soundness(self) -> None:
        def no_support(native, flags, narrowing, blocker, support_a, support_b, coercion):
            if not native:
                return "NO_DONOR_AUTHORITY"
            if not narrowing:
                return "BLOCK"
            if blocker == "ESTABLISHED":
                return "BLOCK"
            if blocker == "UNDETERMINED":
                return "CANNOT_CHECK"
            if not (all(flags) or coercion):
                return "BLOCK"
            return "DISCHARGE"

        report = self._with_terminal(no_support)
        assert report["sound"] is False
        assert report["disagreement_count"] > 0

    def test_weakening_an_established_blocker_breaks_soundness(self) -> None:
        def weak(native, flags, narrowing, blocker, support_a, support_b, coercion):
            if not native:
                return "NO_DONOR_AUTHORITY"
            if not narrowing:
                return "BLOCK"
            if blocker in ("ESTABLISHED", "UNDETERMINED"):
                return "CANNOT_CHECK"
            if not (support_a or support_b):
                return "BLOCK"
            if not (all(flags) or coercion):
                return "BLOCK"
            return "DISCHARGE"

        report = self._with_terminal(weak)
        assert report["sound"] is False

    def test_letting_coercion_override_narrowing_breaks_soundness(self) -> None:
        module = x4_module()
        original = module.scientific_terminal

        def coercion_wins(native, flags, narrowing, blocker, support_a, support_b, coercion):
            if not native:
                return "NO_DONOR_AUTHORITY"
            if coercion:
                return "DISCHARGE"
            return original(native, flags, narrowing, blocker, support_a, support_b, coercion)

        report = self._with_terminal(coercion_wins)
        assert report["sound"] is False


class TestTheReportCountsHonestly:
    def test_disagreements_are_counted_in_full_not_capped(self) -> None:
        """The examples list is truncated; the count must not be.

        The first version derived the agreement count from the truncated example
        list, so any number of disagreements above twenty was reported as twenty
        -- a cap presented as a measurement.
        """

        def no_support(native, flags, narrowing, blocker, support_a, support_b, coercion):
            if not native:
                return "NO_DONOR_AUTHORITY"
            if not narrowing:
                return "BLOCK"
            if blocker == "ESTABLISHED":
                return "BLOCK"
            if blocker == "UNDETERMINED":
                return "CANNOT_CHECK"
            if not (all(flags) or coercion):
                return "BLOCK"
            return "DISCHARGE"

        report = TestItIsADerivationNotATranscription._with_terminal(no_support)
        assert report["disagreement_count"] == 33
        assert len(report["disagreement_examples"]) == 20
        assert report["examples_truncated"] is True
        assert report["agreements"] == report["distinct_states"] - 33
