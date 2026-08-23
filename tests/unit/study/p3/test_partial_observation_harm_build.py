"""The corpus that gives ``G6_HARM_A1`` a denominator, checked at the unit level.

The gate assertions live in ``test_partial_observation_probe.py``. What is pinned
here is the machinery that decides what gold *is*: a rule written out so that gold
is not defined by the system under test, and a completion enumeration that makes
"the answer does not depend on the absent coordinate" a decided question rather
than a claimed one. If either of those quietly starts guessing, the harm number
built on top of them means nothing.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from orion.knowledge.semantics import (
    MeaningRelation,
    Modality,
    Polarity,
    ScientificMeaningProjection,
    compare_meaning,
)
from orion.study.p3.partial_observation_harm_build import (
    ABSENT_VALUE,
    COORDINATE_VALUES,
    COORDINATES,
    HarmCorpusError,
    absent_value_agreement,
    admissible_completions,
    build_report,
    cases_bytes,
    construction_receipts,
    gold_from_standard,
    harm_cases,
    observed,
    one_sided_absences,
    relation_from_observed,
    shape_invariants,
    standard_document,
    verify,
)


def _full(**overrides: object) -> ScientificMeaningProjection:
    """A projection that states all nine coordinates."""

    base: dict[str, object] = {
        "projection_id": "p",
        "source_id": "s",
        "source_span": "span",
        "predicate": "reports_quantity",
    }
    base.update({name: values[0] for name, values in COORDINATE_VALUES.items()})
    base.update(overrides)
    return ScientificMeaningProjection(**base)  # type: ignore[arg-type]


class TestTheRuleRefusesToGuess:
    def test_it_is_undefined_on_a_partially_observed_pair(self) -> None:
        left = _full()
        right = replace(_full(), measurement_ids=())
        with pytest.raises(ValueError, match="fully observed"):
            relation_from_observed(left, right)

    def test_it_reads_the_coordinates_in_precedence_order(self) -> None:
        left = _full()
        # a difference at referent outranks one at measurement
        right = _full(
            referent_ids=COORDINATE_VALUES["referent_ids"][1],
            measurement_ids=COORDINATE_VALUES["measurement_ids"][1],
        )
        assert relation_from_observed(left, right) is MeaningRelation.DISTINCT_REFERENT

    def test_it_agrees_with_compare_meaning_where_both_are_defined(self) -> None:
        left = _full()
        for coordinate in COORDINATES:
            right = _full(**{coordinate: COORDINATE_VALUES[coordinate][1]})
            assert relation_from_observed(left, right) is compare_meaning(left, right).relation


class TestGoldFromCompletionInvariance:
    def test_an_absence_the_answer_turns_on_leaves_the_pair_unresolved(self) -> None:
        left = _full()
        right = replace(_full(), measurement_ids=())
        assert one_sided_absences(left, right) == ("measurement_ids",)
        assert gold_from_standard(left, right) is MeaningRelation.UNRESOLVED
        # and this is exactly where compare_meaning merges instead
        assert compare_meaning(left, right).relation is MeaningRelation.COMPATIBLE

    def test_an_absence_below_the_deciding_coordinate_leaves_gold_determinate(self) -> None:
        left = _full(referent_ids=COORDINATE_VALUES["referent_ids"][1])
        right = replace(_full(), attribution_id="")
        assert one_sided_absences(left, right) == ("attribution_id",)
        assert gold_from_standard(left, right) is MeaningRelation.DISTINCT_REFERENT
        relations = {
            relation_from_observed(completed_left, completed_right)
            for _value, completed_left, completed_right in admissible_completions(left, right)
        }
        assert relations == {MeaningRelation.DISTINCT_REFERENT}

    def test_incomparable_predicates_dominate_the_absence(self) -> None:
        left = _full()
        right = replace(_full(predicate="reports_observed_state"), modality=Modality.UNKNOWN)
        assert gold_from_standard(left, right) is MeaningRelation.UNRESOLVED
        assert compare_meaning(left, right).relation is MeaningRelation.UNRESOLVED

    def test_two_one_sided_absences_are_refused_rather_than_completed(self) -> None:
        left = _full()
        right = replace(_full(), measurement_ids=(), attribution_id="")
        with pytest.raises(ValueError, match="at most one one-sided absence"):
            list(admissible_completions(left, right))

    def test_every_coordinate_has_a_value_that_can_differ_from_the_mirror(self) -> None:
        """Otherwise a completion set could be a singleton for the wrong reason."""

        for coordinate in COORDINATES:
            values = COORDINATE_VALUES[coordinate]
            assert len(set(values)) >= 2
            assert ABSENT_VALUE[coordinate] not in values


class TestTheCorpusItself:
    def test_the_build_is_deterministic(self) -> None:
        assert cases_bytes(harm_cases()) == cases_bytes(harm_cases())

    def test_the_shipped_verification_passes(self) -> None:
        cases = harm_cases()
        verify(cases, construction_receipts(cases))

    def test_construction_level_shapes_are_constant(self) -> None:
        for name, values in shape_invariants(harm_cases()).items():
            assert len(values) == 1, f"{name} varies across cases: {values}"

    def test_the_report_carries_its_own_external_validity_bound(self) -> None:
        report = build_report(harm_cases())
        assert "synthetic" in report["external_validity"]
        assert "not an accuracy benchmark" in report["not_an_accuracy_benchmark"].lower()
        assert report["synthetic_case_count"] == report["built_n"]

    def test_the_standard_states_the_rule_it_derives_gold_by(self) -> None:
        standard = standard_document()
        assert standard["coordinate_precedence"] == list(COORDINATES)
        assert set(standard["admissible_values"]) == set(COORDINATES)
        assert "UNRESOLVED" in str(standard["derivation_rule_statement"])


class TestTheTwoModulesAgreeAboutAbsence:
    def test_the_absent_value_tables_match_the_probe(self) -> None:
        agreement = absent_value_agreement()
        assert agreement["agrees"] is True
        assert agreement["mismatched"] == []

    def test_a_drifted_table_is_caught_rather_than_measured(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Two modules disagreeing about "absent" would measure two things.

        The disagreement would then surface as a gate number rather than as an
        error, which is exactly the substitution this lane exists to prevent, so
        the build refuses instead.
        """

        from orion.study.p3 import partial_observation_probe

        monkeypatch.setitem(
            partial_observation_probe.ABSENT_VALUE, "polarity", Polarity.NEGATED
        )
        assert absent_value_agreement()["mismatched"] == ["polarity"]
        cases = harm_cases()
        with pytest.raises(HarmCorpusError, match="disagree about which value means"):
            verify(cases, construction_receipts(cases))

    def test_observed_rejects_a_coordinate_that_is_not_one(self) -> None:
        with pytest.raises(KeyError):
            observed(_full(), "not_a_coordinate")
