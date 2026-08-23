"""A merge/split rate is evidence only when its denominator travels with it.

P3 reports both guards over every case in the atlas. Only 6 of 32 cases admit a
false merge, and neither comparator ever declines to merge, so the reported
``false_split_rate`` of a comparator is a structural zero.
"""

from __future__ import annotations

import pytest

from orion.knowledge.semantics import MeaningRelation
from orion.programme.guard_exercise import GuardVerdictReason, worst_outcome
from orion.programme.records import Outcome
from orion.study.p3.identity_opportunity import (
    FALSE_MERGE_GUARD_ID,
    FALSE_SPLIT_GUARD_ID,
    UNRESOLVED_CALIBRATION_GUARD_ID,
    IdentityDecisionKind,
    IdentityDecisionReceipt,
    assess_identity_guards,
    build_identity_ledger,
    classify_identity_decision,
)
from orion.study.p3_public_reference import NONMERGE_RELATIONS

COMPATIBLE = MeaningRelation.COMPATIBLE
CONTRADICTORY = MeaningRelation.CONTRADICTORY
UNRESOLVED = MeaningRelation.UNRESOLVED


def _rows(arm_id: str, pairs: list[tuple[MeaningRelation, MeaningRelation]]):
    return [(f"case-{index}", arm_id, gold, pred) for index, (gold, pred) in enumerate(pairs)]


class TestClassification:
    def test_the_taxonomy_partitions_every_meaning_relation(self) -> None:
        """A relation nobody sorted would silently leave both denominators."""

        merge = {COMPATIBLE}
        abstain = {UNRESOLVED}
        assert merge | abstain | NONMERGE_RELATIONS == set(MeaningRelation)
        assert not merge & abstain
        assert not (merge | abstain) & NONMERGE_RELATIONS

    @pytest.mark.parametrize(
        ("gold", "predicted", "expected"),
        [
            (COMPATIBLE, COMPATIBLE, IdentityDecisionKind.MERGED_CORRECTLY),
            (COMPATIBLE, CONTRADICTORY, IdentityDecisionKind.FALSE_SPLIT),
            (COMPATIBLE, UNRESOLVED, IdentityDecisionKind.ABSTAINED_ON_MERGEABLE),
            (CONTRADICTORY, COMPATIBLE, IdentityDecisionKind.FALSE_MERGE),
            (CONTRADICTORY, CONTRADICTORY, IdentityDecisionKind.SEPARATED_CORRECTLY),
            (
                MeaningRelation.DISTINCT_MEASUREMENT,
                MeaningRelation.DISTINCT_REFERENT,
                IdentityDecisionKind.SEPARATED_CORRECTLY,
            ),
            (CONTRADICTORY, UNRESOLVED, IdentityDecisionKind.ABSTAINED_ON_SEPARABLE),
            (UNRESOLVED, UNRESOLVED, IdentityDecisionKind.ABSTAINED_AS_GOLD_REQUIRES),
            (UNRESOLVED, COMPATIBLE, IdentityDecisionKind.MERGED_WHERE_GOLD_UNRESOLVED),
            (UNRESOLVED, CONTRADICTORY, IdentityDecisionKind.SEPARATED_WHERE_GOLD_UNRESOLVED),
        ],
    )
    def test_every_cell_of_the_grid_has_a_name(
        self, gold: MeaningRelation, predicted: MeaningRelation, expected: IdentityDecisionKind
    ) -> None:
        assert classify_identity_decision(gold, predicted) is expected

    def test_every_kind_is_reachable(self) -> None:
        relations = [COMPATIBLE, CONTRADICTORY, UNRESOLVED]
        produced = {
            classify_identity_decision(gold, pred) for gold in relations for pred in relations
        }
        assert produced == set(IdentityDecisionKind)

    def test_exactly_one_denominator_claims_each_kind(self) -> None:
        for kind in IdentityDecisionKind:
            memberships = [
                kind.gold_admits_false_merge,
                kind.gold_admits_false_split,
                kind.gold_admits_over_resolution,
            ]
            assert sum(memberships) == 1, kind

    def test_a_receipt_cannot_misreport_its_own_kind(self) -> None:
        with pytest.raises(ValueError, match="contradicts"):
            IdentityDecisionReceipt(
                case_id="c",
                arm_id="orion",
                gold=COMPATIBLE,
                predicted=COMPATIBLE,
                kind=IdentityDecisionKind.FALSE_MERGE,
            )


class TestDenominators:
    def test_false_merge_denominator_is_the_non_mergeable_pairs(self) -> None:
        """The frozen atlas shape: 6 of 32 cases admit a false merge."""

        ledger = build_identity_ledger(
            "atlas",
            _rows("flat", [(CONTRADICTORY, COMPATIBLE)] * 6 + [(COMPATIBLE, COMPATIBLE)] * 26),
        )
        exercise = ledger.false_merge_exercise("flat")
        assert (exercise.opportunities, exercise.violations) == (6, 6)
        assert exercise.violation_rate == 1.0

    def test_the_reported_rate_and_the_real_rate_differ_by_the_denominator(self) -> None:
        ledger = build_identity_ledger(
            "atlas",
            _rows("flat", [(CONTRADICTORY, COMPATIBLE)] * 6 + [(COMPATIBLE, COMPATIBLE)] * 26),
        )
        reported_over_all_cases = 6 / 32
        assert reported_over_all_cases == pytest.approx(0.1875)
        assert ledger.false_merge_exercise("flat").violation_rate == 1.0

    def test_an_arm_that_never_separates_has_no_false_split_denominator(self) -> None:
        ledger = build_identity_ledger(
            "atlas",
            _rows("exact", [(COMPATIBLE, COMPATIBLE)] * 26 + [(CONTRADICTORY, UNRESOLVED)] * 6),
        )
        assert ledger.separations_emitted("exact") == 0
        exercise = ledger.false_split_exercise("exact")
        assert exercise.opportunities == 0
        assert exercise.violation_rate is None

    def test_a_separating_arm_keeps_its_mergeable_denominator(self) -> None:
        ledger = build_identity_ledger(
            "atlas",
            _rows("orion", [(COMPATIBLE, COMPATIBLE)] * 26 + [(CONTRADICTORY, CONTRADICTORY)] * 6),
        )
        assert ledger.separations_emitted("orion") == 6
        exercise = ledger.false_split_exercise("orion")
        assert (exercise.opportunities, exercise.violations) == (26, 0)

    def test_unresolved_calibration_has_no_denominator_on_a_fully_adjudicated_atlas(self) -> None:
        ledger = build_identity_ledger(
            "atlas",
            _rows("orion", [(COMPATIBLE, COMPATIBLE)] * 26 + [(CONTRADICTORY, CONTRADICTORY)] * 6),
        )
        assert ledger.unresolved_calibration_exercise("orion").opportunities == 0

    def test_kind_counts_cover_the_total_taxonomy(self) -> None:
        ledger = build_identity_ledger("atlas", _rows("orion", [(COMPATIBLE, COMPATIBLE)]))
        counts = ledger.kind_counts("orion")
        assert set(counts) == {kind.value for kind in IdentityDecisionKind}
        assert counts["MERGED_CORRECTLY"] == 1

    def test_a_ledger_rejects_a_repeated_decision(self) -> None:
        with pytest.raises(ValueError, match="each case once"):
            build_identity_ledger(
                "atlas",
                [("c", "orion", COMPATIBLE, COMPATIBLE), ("c", "orion", COMPATIBLE, UNRESOLVED)],
            )

    def test_an_unknown_arm_raises_rather_than_returning_an_empty_denominator(self) -> None:
        ledger = build_identity_ledger("atlas", _rows("orion", [(COMPATIBLE, COMPATIBLE)]))
        with pytest.raises(KeyError):
            ledger.false_merge_exercise("nobody")


class TestAssessIdentityGuards:
    def _frozen_atlas_ledger(self):
        """The v1.1 confirmatory shape: 26 mergeable, 6 contradictory."""

        rows = []
        rows += _rows("orion", [(COMPATIBLE, COMPATIBLE)] * 26 + [(CONTRADICTORY, CONTRADICTORY)] * 6)
        rows += _rows(
            "exact_coordinate_conservative",
            [(COMPATIBLE, COMPATIBLE)] * 26 + [(CONTRADICTORY, UNRESOLVED)] * 6,
        )
        return build_identity_ledger("public-reference-v1.1-confirmatory", rows)

    def test_the_false_split_comparison_blocks_on_an_incapable_comparator(self) -> None:
        merge, split, calibration = assess_identity_guards(
            self._frozen_atlas_ledger(),
            candidate="orion",
            comparator="exact_coordinate_conservative",
        )
        assert merge.guard_id == FALSE_MERGE_GUARD_ID
        assert merge.outcome is Outcome.PASS
        assert split.guard_id == FALSE_SPLIT_GUARD_ID
        assert split.outcome is Outcome.CANNOT_CHECK
        assert split.reason is GuardVerdictReason.COMPARATOR_NEVER_EXERCISED
        assert calibration.guard_id == UNRESOLVED_CALIBRATION_GUARD_ID
        assert calibration.outcome is Outcome.CANNOT_CHECK

    def test_the_candidates_own_false_merge_guard_holds_on_a_real_denominator(self) -> None:
        merge, _, _ = assess_identity_guards(
            self._frozen_atlas_ledger(),
            candidate="orion",
            comparator="exact_coordinate_conservative",
        )
        exercise = merge.exercises[0]
        assert (exercise.opportunities, exercise.violations) == (6, 0)

    def test_the_roll_up_blocks(self) -> None:
        assessments = assess_identity_guards(
            self._frozen_atlas_ledger(),
            candidate="orion",
            comparator="exact_coordinate_conservative",
        )
        assert worst_outcome(assessments) is Outcome.CANNOT_CHECK

    def test_a_comparator_that_can_split_yields_a_real_comparison(self) -> None:
        rows = []
        rows += _rows(
            "orion", [(COMPATIBLE, COMPATIBLE)] * 26 + [(CONTRADICTORY, CONTRADICTORY)] * 6
        )
        rows += _rows(
            "eager_splitter",
            [(COMPATIBLE, CONTRADICTORY)] * 13
            + [(COMPATIBLE, COMPATIBLE)] * 13
            + [(CONTRADICTORY, CONTRADICTORY)] * 6,
        )
        ledger = build_identity_ledger("atlas", rows)
        _, split, _ = assess_identity_guards(
            ledger, candidate="orion", comparator="eager_splitter"
        )
        assert split.outcome is Outcome.PASS
        assert split.reason is GuardVerdictReason.HELD_UNDER_EXERCISE
        assert split.exercises[1].violation_rate == pytest.approx(0.5)

    def test_an_arm_cannot_be_its_own_comparator(self) -> None:
        with pytest.raises(ValueError, match="own comparator"):
            assess_identity_guards(
                self._frozen_atlas_ledger(), candidate="orion", comparator="orion"
            )

    def test_json_report_carries_every_denominator(self) -> None:
        payload = self._frozen_atlas_ledger().as_json()
        orion = payload["by_arm"]["orion"]
        assert orion["separations_emitted"] == 6
        assert orion["false_merge_exercise"]["opportunities"] == 6
        assert orion["false_split_exercise"]["opportunities"] == 26
        comparator = payload["by_arm"]["exact_coordinate_conservative"]
        assert comparator["false_split_exercise"]["opportunities"] == 0
