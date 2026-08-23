"""The corpus that gives ``G9_HARM_A3`` a non-circular denominator, at the unit level.

The gate assertions live in ``test_partial_observation_probe.py``. What is pinned
here is the machinery that decides what gold *is* and the guards that keep it from
becoming the arm it is supposed to score.

Three things have to hold together for this corpus to be worth anything, and each
of them is a test class below.

* Gold is the relation between two **source records**, not a rule about what a
  projection's silence could have hidden. The rule is written out here rather than
  delegated to ``compare_meaning``, and it is *undefined* on anything but a fully
  stated record --- which is what makes it structurally incapable of being A3's
  criterion under another name.
* The census is balanced. Both directions of every coordinate are present, so
  which cells land in the harm denominator is fixed by ``compare_meaning``'s own
  absence reading and not by the builder's choices.
* Editing the corpus into circularity is refused. The strata on which
  record-anchored gold and A3 disagree are exactly the strata that make the
  corpus a measurement; deleting them is the failure mode this corpus exists to
  avoid, and both the builder and the probe refuse it.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from orion.knowledge.semantics import (
    MeaningRelation,
    Modality,
    Polarity,
    ScientificMeaningProjection,
    compare_meaning,
)
from orion.study.p3.partial_observation_probe import (
    ARM_DECISIVE,
    DECISIVENESS_RULE_MARKER,
    INTACT_RECORD_GOLD,
    INTACT_SOURCES,
    arm_decisive_absence_only,
    exact_agreement_where_the_arm_can_fire,
    gold_provenance,
    independent_harm_evidence,
    score_pairs,
)
from orion.study.p3.partial_observation_record_gold_build import (
    ABSENT_VALUE,
    COORDINATES,
    DERIVATION_RULE,
    RECORD_VALUES,
    STRATUM_CONTRACT,
    STRATUM_LA,
    STRATUM_LD,
    STRATUM_LU,
    STRATUM_NL,
    RecordCorpusError,
    absence_reading_census,
    absent_value_agreement,
    build_report,
    cases_bytes,
    construction_receipts,
    coordinate_balance,
    decisiveness_census,
    extraction_loss_is_the_only_difference,
    harm_preview,
    one_sided_absence_census,
    record_gold_cases,
    relation_from_records,
    rule_agreement_on_records,
    shape_invariants,
    standard_document,
    verify,
)
from orion.study.p3_public_reference import load_jsonl

REPO_ROOT = Path(__file__).resolve().parents[4]

#: The corpus's shape, pinned so a stratum cannot quietly disappear. The two
#: ``L`` strata are one case per coordinate; ``LU`` covers every coordinate that
#: has one strictly above it; ``NL`` is nine differing controls plus one agreeing
#: one.
STRATUM_SIZES = {STRATUM_LA: 9, STRATUM_LD: 9, STRATUM_LU: 8, STRATUM_NL: 10}


@pytest.fixture(scope="module")
def cases() -> list[dict[str, object]]:
    return record_gold_cases()


@pytest.fixture(scope="module")
def shipped() -> list[dict[str, object]]:
    """The corpus as it ships, read through the same loader the probe uses."""

    return load_jsonl(REPO_ROOT / INTACT_SOURCES[INTACT_RECORD_GOLD])


@pytest.fixture(scope="module")
def receipts(cases: list[dict[str, object]]) -> list[dict[str, object]]:
    return construction_receipts(cases)


def _stratum(case: dict[str, object]) -> str:
    meta = case["partial_observation_record_gold"]
    assert isinstance(meta, dict)
    return str(meta["stratum"])


def _record(**overrides: object) -> ScientificMeaningProjection:
    """A record that states all nine coordinates."""

    base: dict[str, object] = {
        "projection_id": "rec",
        "source_id": "s",
        "source_span": "span",
        "predicate": "reports_quantity",
    }
    base.update({name: values[0] for name, values in RECORD_VALUES.items()})
    base.update(overrides)
    return ScientificMeaningProjection(**base)  # type: ignore[arg-type]


class TestGoldIsAnchoredToTheRecord:
    def test_the_rule_is_undefined_on_anything_that_is_not_a_full_record(self) -> None:
        """The structural reason this gold cannot be A3's criterion.

        A rule with no branch that reads an absence has no opinion about what an
        absence could have hidden. It cannot quantify over completions because it
        refuses the input on which a completion would be needed.
        """

        left = _record()
        right = replace(_record(), measurement_ids=())
        with pytest.raises(RecordCorpusError, match="state every coordinate"):
            relation_from_records(left, right)

    @pytest.mark.parametrize("coordinate", COORDINATES)
    def test_the_rule_is_undefined_however_the_absence_arrives(
        self, coordinate: str
    ) -> None:
        left = _record()
        right = replace(_record(), **{coordinate: ABSENT_VALUE[coordinate]})
        with pytest.raises(RecordCorpusError):
            relation_from_records(left, right)
        with pytest.raises(RecordCorpusError):
            relation_from_records(right, left)

    def test_gold_does_not_move_when_the_extraction_loses_a_coordinate(self) -> None:
        """The whole construction in one assertion.

        The records determine ``DISTINCT_MEASUREMENT``. Blanking the deciding
        coordinate on one side is what ORION's extractor does, not what the
        sources do, so gold stays where it was --- and ``compare_meaning`` moves.
        """

        left = _record()
        right = _record(measurement_ids=RECORD_VALUES["measurement_ids"][1])
        assert relation_from_records(left, right) is MeaningRelation.DISTINCT_MEASUREMENT
        extracted = replace(right, measurement_ids=())
        assert compare_meaning(left, extracted).relation is MeaningRelation.COMPATIBLE
        assert relation_from_records(left, right) is MeaningRelation.DISTINCT_MEASUREMENT

    def test_the_rule_agrees_with_compare_meaning_on_every_record_pair(
        self, cases: list[dict[str, object]]
    ) -> None:
        """Written out independently, checked where both are defined.

        A rule that disagreed with ``compare_meaning`` on a pair with nothing
        missing would make the corpus measure a system ORION does not have.
        """

        agreement = rule_agreement_on_records(cases)
        assert agreement["agrees_everywhere"] is True
        assert agreement["record_pairs_compared"] == len(cases)

    def test_every_shipped_gold_is_the_relation_between_that_cases_records(
        self, receipts: list[dict[str, object]]
    ) -> None:
        for row in receipts:
            assert row["gold"] == row["gold_from_records"]

    def test_each_projection_is_its_record_minus_one_coordinate(
        self, cases: list[dict[str, object]]
    ) -> None:
        loss = extraction_loss_is_the_only_difference(cases)
        assert loss["holds_everywhere"] is True
        assert loss["n_cases"] == len(cases)

    def test_the_declared_rule_does_not_name_the_criterion_a3_decides_by(
        self, shipped: list[dict[str, object]]
    ) -> None:
        provenance = gold_provenance(shipped)
        assert provenance["declared_rules"] == [DERIVATION_RULE]
        assert provenance["n_cases_declaring_a_rule"] == len(shipped)
        assert DECISIVENESS_RULE_MARKER not in DERIVATION_RULE
        assert provenance["rules_naming_completion_invariance"] == []
        assert provenance["gold_derived_by_completion_invariance"] is False


class TestConstructionPreconditions:
    """The C1-C5 analogue: what has to be true of the corpus before any arm number
    over it means anything. Each check is separate so a failure says which one."""

    def test_c1_the_shipped_corpus_is_what_the_builder_emits(
        self, shipped: list[dict[str, object]], cases: list[dict[str, object]]
    ) -> None:
        assert cases_bytes(shipped) == cases_bytes(cases)

    def test_c2_every_case_holds_its_stratum_contract(
        self, receipts: list[dict[str, object]]
    ) -> None:
        counts: dict[str, int] = {}
        for row in receipts:
            contract = STRATUM_CONTRACT[str(row["stratum"])]
            assert (
                len(list(row["one_sided_absences"])) == contract["n_one_sided_absences"]
            ), row["case_id"]
            assert row["gold_is_determinate"] is contract["gold_is_determinate"]
            assert row["absence_is_decisive"] is contract["absence_is_decisive"]
            counts[str(row["stratum"])] = counts.get(str(row["stratum"]), 0) + 1
        assert counts == STRATUM_SIZES

    def test_c3_the_denominator_is_not_zero_and_reaches_every_coordinate(
        self, cases: list[dict[str, object]]
    ) -> None:
        census = one_sided_absence_census(cases)
        assert census["n_pairs"] == 36
        assert census["n_pairs_with_a_one_sided_absence"] == 26
        assert census["coordinates_never_one_sided"] == []
        assert set(census["by_coordinate"]) == set(COORDINATES)

    def test_c4_both_directions_of_every_coordinate_are_present(
        self, cases: list[dict[str, object]]
    ) -> None:
        """The guard against choosing cases by their effect on the gate.

        ``compare_meaning`` is right about a silence on the eight merge-ward
        coordinates when the records agree, and about ``modality`` when they
        differ. Holding both cells for every coordinate is what leaves the harm
        denominator to ``compare_meaning`` rather than to the builder.
        """

        balance = coordinate_balance(cases)
        assert balance["balanced"] is True
        assert balance["missing_cells"] == []

    def test_c5_the_absence_reading_splits_eight_to_one_as_the_freeze_declared(
        self, cases: list[dict[str, object]]
    ) -> None:
        census = absence_reading_census(cases)
        assert census["every_cell_matches_the_freeze"] is True
        assert census["counts"] == {"MERGE_WARD": 8, "SEPARATION_WARD": 1}
        assert census["by_coordinate"]["modality"]["observed_reading"] == "SEPARATION_WARD"

    def test_the_two_modules_agree_about_which_value_means_absent(self) -> None:
        agreement = absent_value_agreement()
        assert agreement["agrees"] is True
        assert agreement["mismatched"] == []
        assert set(agreement["coordinates_compared"]) == set(COORDINATES)

    def test_no_construction_level_feature_varies_with_gold(
        self, cases: list[dict[str, object]]
    ) -> None:
        """The P4 lesson applied before the fact rather than after.

        A corpus whose gold is recoverable from a case-id length or a source-span
        template measures a shortcut cue. Every shape is a singleton set.
        """

        for name, values in shape_invariants(cases).items():
            assert len(values) == 1, (name, values)

    def test_the_standard_states_the_rule_it_derives_gold_by(self) -> None:
        document = standard_document()
        assert document["derivation_rule"] == DERIVATION_RULE
        assert set(document["strata"]) == set(STRATUM_SIZES)
        assert document["coordinate_precedence"] == list(COORDINATES)


class TestTheGoldIsNotTheArmItScores:
    """The tests that would fail if the corpus were edited into circularity."""

    def test_gold_does_not_coincide_with_completion_invariance(
        self, receipts: list[dict[str, object]]
    ) -> None:
        """The extensional non-circularity claim, as a count.

        A corpus whose partially observed pairs have determinate gold exactly
        where the completions agree has a gold that *is* the completion-invariance
        criterion, whatever rule string it declares. This one has 18 pairs off
        that diagonal: determinate gold, decisive loss.
        """

        census = decisiveness_census(receipts)
        assert census["gold_coincides_with_completion_invariance"] is False
        assert census["n_partially_observed_pairs"] == 26
        assert census["n_determinate_gold_with_a_decisive_loss"] == 18
        assert census["n_determinate_gold_with_an_undecisive_loss"] == 8

    def test_a3_does_not_reproduce_gold_where_it_can_fire(
        self, shipped: list[dict[str, object]]
    ) -> None:
        """If it did, its zero harm here would follow by arithmetic.

        Computed through the probe's own scoring path rather than from the build
        report, so this is the number the gate reads.
        """

        pairs = []
        for case in shipped:
            expected = case["expected"]
            assert isinstance(expected, dict)
            left = case["left_projection"]
            right = case["right_projection"]
            assert isinstance(left, dict) and isinstance(right, dict)
            from orion.study.p3_public_reference import projection_from_dict

            pairs.append(
                (
                    str(case["case_id"]),
                    projection_from_dict(left),
                    projection_from_dict(right),
                    MeaningRelation(str(expected["meaning_relation"])),
                )
            )
        agreement = exact_agreement_where_the_arm_can_fire(score_pairs(pairs), ARM_DECISIVE)
        assert agreement["n_pairs_with_a_one_sided_absence"] == 26
        assert agreement["n_exact"] == 8
        assert agreement["reproduces_gold_on_every_pair_it_can_fire_on"] is False

    def test_the_builder_refuses_a_corpus_edited_into_circularity(
        self, cases: list[dict[str, object]]
    ) -> None:
        """Deleting the strata where gold and A3 disagree is refused.

        This is the edit that would make ``G9_HARM_A3`` look like a pass: keep the
        pairs A3 gets right, drop the ones it does not. What is left is a corpus
        whose gold is determinate exactly where the completions agree, i.e. A3's
        own criterion with a different name on it, and the builder says so.
        """

        kept = [case for case in cases if _stratum(case) in {STRATUM_LU, STRATUM_NL}]
        # What is left is circular in extension: every partially observed pair it
        # still holds has determinate gold and an undecisive loss, which is the
        # completion-invariance criterion restated.
        census = decisiveness_census(construction_receipts(kept))
        assert census["gold_coincides_with_completion_invariance"] is True
        assert census["n_determinate_gold_with_a_decisive_loss"] == 0
        # The builder refuses it. It names the earlier and more specific fault ---
        # half of every coordinate's pair has been deleted --- and either refusal
        # is the right one; what matters is that the corpus cannot be emitted.
        with pytest.raises(RecordCorpusError, match="choosing cases by their effect"):
            verify(kept, construction_receipts(kept))

    def test_the_probe_withholds_the_evidence_of_such_a_corpus(
        self, cases: list[dict[str, object]]
    ) -> None:
        """And the refusal is not only the builder's.

        The builder can be bypassed --- a corpus is a file, and a later edit need
        not go through it. The gate reads the corpus, so it has to catch the same
        edit on its own. It returns ``CANNOT_CHECK``, never a pass.
        """

        kept = [case for case in cases if _stratum(case) in {STRATUM_LU, STRATUM_NL}]
        entry = _corpus_entry(kept)
        evidence = independent_harm_evidence(entry, ARM_DECISIVE)
        assert evidence["supplies_independent_evidence"] is False
        assert (
            "GOLD_COINCIDES_WITH_THE_ARM_WHEREVER_THE_ARM_CAN_FIRE"
            in evidence["withheld_because"]
        )
        assert evidence["gold_derived_by_completion_invariance"] is False

    def test_the_unedited_corpus_does_supply_independent_evidence(
        self, shipped: list[dict[str, object]]
    ) -> None:
        evidence = independent_harm_evidence(_corpus_entry(shipped), ARM_DECISIVE)
        assert evidence["supplies_independent_evidence"] is True
        assert evidence["withheld_because"] == []
        assert evidence["harm_denominator"] == 17
        assert evidence["declared_gold_rules"] == [DERIVATION_RULE]

    def test_the_builder_refuses_a_corpus_with_no_undecisive_loss(
        self, cases: list[dict[str, object]]
    ) -> None:
        """The other direction of the same guard.

        Without ``LU`` every partially observed pair is one A3 abstains on, so A3
        and A1 make the same decision everywhere and the corpus cannot show what
        A3 was built to do. A harm number over it would be A1's.
        """

        kept = [case for case in cases if _stratum(case) != STRATUM_LU]
        with pytest.raises(RecordCorpusError, match="A3 and A1 make the same decision"):
            verify(kept, construction_receipts(kept))

    def test_the_builder_refuses_a_corpus_missing_half_of_a_coordinate(
        self, cases: list[dict[str, object]]
    ) -> None:
        """Choosing cases by their effect on the gate, caught by counting cells."""

        kept = [case for case in cases if _stratum(case) != STRATUM_LA]
        with pytest.raises(RecordCorpusError, match="choosing cases by their effect"):
            verify(kept, construction_receipts(kept))

    def test_the_builder_refuses_a_corpus_with_no_one_sided_absence(
        self, cases: list[dict[str, object]]
    ) -> None:
        controls = [case for case in cases if _stratum(case) == STRATUM_NL]
        with pytest.raises(RecordCorpusError, match="exactly as vacuous"):
            verify(controls, construction_receipts(controls))

    def test_the_builder_refuses_a_case_whose_gold_is_not_its_record_relation(
        self, cases: list[dict[str, object]]
    ) -> None:
        """Gold has to be the record's answer, not an answer beside it."""

        tampered = [dict(case) for case in cases]
        target = next(case for case in tampered if _stratum(case) == STRATUM_LA)
        expected = dict(target["expected"])  # type: ignore[arg-type]
        expected["meaning_relation"] = MeaningRelation.UNRESOLVED.value
        target["expected"] = expected
        with pytest.raises(RecordCorpusError):
            verify(tampered, construction_receipts(tampered))


class TestWhatTheCorpusMeasures:
    def test_the_harm_preview_reports_the_number_it_hands_the_gate(
        self, receipts: list[dict[str, object]]
    ) -> None:
        preview = harm_preview(receipts)
        assert preview["pairs_with_a_one_sided_absence"] == 26
        assert preview["harm_denominator"] == 17
        assert preview["a3_correct_answers_destroyed"] == 9
        assert preview["a1_correct_answers_destroyed"] == 17
        assert preview["pairs_a1_destroys_and_a3_spares"] == 8

    def test_a3_destroys_exactly_the_decisive_losses_a0_answers_correctly(
        self, receipts: list[dict[str, object]]
    ) -> None:
        """The count is not a property of the cases, and this is why.

        A3 abstains on every decisive one-sided absence. So the pairs it destroys
        are exactly the pairs that are decisive, determinate and answered
        correctly by A0 --- no more, no fewer. Nothing about the corpus could make
        that set smaller except removing its members.
        """

        destroyed = {str(row["case_id"]) for row in receipts if row["a3_destroys_a_correct_answer"]}
        necessary = {
            str(row["case_id"])
            for row in receipts
            if row["absence_is_decisive"]
            and row["gold_is_determinate"]
            and row["a0_reproduces_gold"]
        }
        assert destroyed == necessary
        assert len(destroyed) == 9

    def test_the_nine_are_the_eight_merge_ward_coordinates_plus_modality(
        self, receipts: list[dict[str, object]]
    ) -> None:
        """Which cells they are is fixed by compare_meaning, not by the builder."""

        destroyed = [row for row in receipts if row["a3_destroys_a_correct_answer"]]
        by_stratum: dict[str, set[str]] = {}
        for row in destroyed:
            by_stratum.setdefault(str(row["stratum"]), set()).add(str(row["lost_coordinate"]))
        assert by_stratum[STRATUM_LA] == set(COORDINATES) - {"modality"}
        assert by_stratum[STRATUM_LD] == {"modality"}

    def test_a3_spares_the_undecisive_losses_a1_destroys(
        self, receipts: list[dict[str, object]]
    ) -> None:
        """The benefit A3 was built for, measured on gold neither arm wrote."""

        spared = [
            row
            for row in receipts
            if row["a1_destroys_a_correct_answer"] and not row["a3_destroys_a_correct_answer"]
        ]
        assert len(spared) == 8
        assert {str(row["stratum"]) for row in spared} == {STRATUM_LU}
        for row in spared:
            assert row["a3_reproduces_gold"] is True

    def test_a3_repairs_nothing_here_and_the_report_says_so(
        self, receipts: list[dict[str, object]]
    ) -> None:
        """Abstention cannot equal a determinate gold, so there is nothing to repair.

        Every partially observed pair of this corpus has determinate gold, and A3
        answers ``UNRESOLVED`` wherever it differs from A0. So A3's repair count
        here is zero by construction, and quoting the nine repairs it scores on
        the circular corpus as if they carried over would be reading a number off
        the corpus that cannot score it.
        """

        assert all(bool(row["gold_is_determinate"]) for row in receipts)
        repaired = [
            row
            for row in receipts
            if not row["a0_reproduces_gold"] and row["a3_reproduces_gold"]
        ]
        assert repaired == []

    def test_the_arm_is_imported_rather_than_reimplemented(
        self, cases: list[dict[str, object]]
    ) -> None:
        """Scoring an arm against a copy of itself would be a second circularity.

        The receipts call the probe's ``arm_decisive_absence_only``. Gold is
        computed here; the arm is not.
        """

        from orion.study.p3_public_reference import projection_from_dict

        for case, row in zip(cases, construction_receipts(cases)):
            left = projection_from_dict(case["left_projection"])
            right = projection_from_dict(case["right_projection"])
            assert row["a3_decisive_absence_only"] == arm_decisive_absence_only(left, right).value

    def test_the_build_report_carries_its_external_validity_sentence(
        self, cases: list[dict[str, object]]
    ) -> None:
        report = build_report(cases)
        assert "synthetic" in report["external_validity"]
        assert "not an accuracy benchmark" in report["not_an_accuracy_benchmark"].lower()
        assert report["gate_served"] == "G9_HARM_A3"


def _corpus_entry(cases: list[dict[str, object]]) -> dict[str, object]:
    """The corpus payload shape ``independent_harm_evidence`` reads, from cases.

    Built through the probe's own scoring so that the test exercises the path the
    gate takes rather than a description of it.
    """

    from orion.study.p3.partial_observation_probe import (
        exact_agreement_with_gold,
        harm_against_current,
    )
    from orion.study.p3_public_reference import projection_from_dict

    pairs = []
    for case in cases:
        expected = case["expected"]
        assert isinstance(expected, dict)
        pairs.append(
            (
                str(case["case_id"]),
                projection_from_dict(case["left_projection"]),
                projection_from_dict(case["right_projection"]),
                MeaningRelation(str(expected["meaning_relation"])),
            )
        )
    scored = score_pairs(pairs)
    return {
        "gold_provenance": gold_provenance(cases),
        "harm_vs_current": {ARM_DECISIVE: harm_against_current(scored, ARM_DECISIVE)},
        "exact_agreement_with_gold": {
            ARM_DECISIVE: exact_agreement_with_gold(scored, ARM_DECISIVE)
        },
        "exact_agreement_where_the_arm_can_fire": {
            ARM_DECISIVE: exact_agreement_where_the_arm_can_fire(scored, ARM_DECISIVE)
        },
    }


class TestTheCoordinateTablesAreRealisable:
    """Small algebraic facts the census depends on."""

    def test_every_record_value_is_distinct_from_the_absent_value(self) -> None:
        for name, values in RECORD_VALUES.items():
            assert len(set(values)) == len(values)
            for value in values:
                assert value != ABSENT_VALUE[name]

    def test_polarity_and_modality_records_never_state_unknown(self) -> None:
        assert Polarity.UNKNOWN not in RECORD_VALUES["polarity"]
        assert Modality.UNKNOWN not in RECORD_VALUES["modality"]
