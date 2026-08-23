"""Amendment 004: the identifiability ceiling under partial observation.

``G9_HARM_A3`` fails on nine destroyed correct answers. The question amendment
004 settles is whether nine is a defect of ``A3_decisive_absence_only`` --- the
kind of thing a fifth arm would repair --- or the price of the evidence. It is
the price, and these tests are what makes that a measurement rather than an
argument.

The load-bearing assertions are the ones that could go the other way:

* the canonicalisation strips only what gold does not read, and the tests exhibit
  a pair it must *not* collapse for each thing it does collapse;
* every arm on record is constant on every orbit, so the canonicalisation is not
  quietly discarding something an arm actually uses;
* the witness is two *legal cases of the shipped corpus* with identical
  projections and different gold, accepted by the builder's own validators;
* the numbers reproduce on held-out draws, which is the guard against a bound
  reverse-engineered from the nine cases it was derived after seeing;
* the rule that does beat nine is exhibited, measured, and shown to buy it by
  surrendering the whole benefit ``A3`` exists for.
"""

from __future__ import annotations

import json
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
from orion.programme.guard_exercise import assess_guard
from orion.programme.records import Outcome
from orion.study.p3.identity_opportunity import build_identity_ledger
from orion.study.p3.partial_observation_probe import (
    ABSENT_VALUE,
    ARM_ASYMMETRIC,
    ARM_CURRENT,
    ARM_DECISIVE,
    ARM_ORDER,
    ARM_STRICT,
    ARMS,
    CANONICAL_BOOKKEEPING_FIELDS,
    CANONICAL_ROLE_FIELDS,
    CLOSED_VOCABULARY_FIELDS,
    COORDINATES,
    FREEZE_TWIN,
    INTACT_ORDER,
    INTACT_RECORD_GOLD,
    INTACT_SOURCES,
    OPEN_VOCABULARY_FIELDS,
    PROBE_OF,
    AMENDMENT_004_TWIN,
    PROBE_GOLD_DERIVATION_RULE,
    build_probe,
    canonical_pair_form,
    canonicalisation_field_census,
    frozen_digest,
    identifiability_ceiling,
    projection_orbits,
    redactable_coordinates,
    run_campaign,
)
from orion.study.p3.partial_observation_record_gold_build import (
    DEFAULT_DRAW,
    DEFAULT_DRAW_LABEL,
    FRESH_DRAW_VALUE_PREFIX,
    RECORD_VALUES,
    STRATUM_CONTRACT,
    STRATUM_LA,
    STRATUM_LD,
    RecordCorpusError,
    RecordDraw,
    cases_bytes,
    construction_receipts,
    fresh_draw,
    held_out_corpus,
    record_gold_cases,
    relation_from_records,
    standard_bytes,
    undecidability_witness_cases,
)
from orion.study.p3_public_reference import (
    NONMERGE_RELATIONS,
    load_jsonl,
    projection_from_dict,
    validate_case,
)

REPO_ROOT = Path(__file__).resolve().parents[4]

#: Seeds the held-out draws are taken at. Fixed here rather than drawn so the
#: suite is deterministic, and more than one so a reproduction is not a
#: coincidence of a single draw.
HELD_OUT_SEEDS: tuple[int, ...] = (7, 11, 23, 41, 101)

#: What amendment 004 asserts about the shipped corpus. Kept as one block so a
#: drift in any of them is a single obvious failure rather than four.
COMMITTED_CEILING: dict[str, int] = {
    "n_pairs": 36,
    "n_orbits": 27,
    "n_undecidable_orbits": 9,
    "n_pairs_in_an_undecidable_orbit": 18,
    "n_pairs_no_candidate_visible_rule_can_answer_correctly": 9,
    "max_exact_agreement_reachable_by_a_candidate_visible_rule": 27,
    "n_orbits_forcing_a_false_merge_a_false_split_or_an_abstention": 9,
    "harm_floor_for_an_arm_that_commits_no_false_merge_and_no_false_split": 9,
}


def _projection(side: str, **coordinates: object) -> ScientificMeaningProjection:
    values: dict[str, object] = {
        "projection_id": f"ceil:{side}",
        "source_id": f"ceil-source-{side}",
        "source_span": f"ceil.txt#{side}",
        "predicate": "reports_quantity",
        "referent_ids": ("ceil:referent:0",),
        "construct_ids": ("ceil:construct:0",),
        "measurement_ids": ("ceil:measurement:0",),
        "temporal_context_ids": ("ceil:temporal:0",),
        "attribution_id": "ceil:attribution:0",
        "discourse_relation": "ceil:discourse:0",
        "assumption_ids": ("ceil:assumption:0",),
        "polarity": Polarity.POSITIVE,
        "modality": Modality.ASSERTED,
    }
    values.update(coordinates)
    return ScientificMeaningProjection(**values)  # type: ignore[arg-type]


def _pairs(cases: list[dict[str, object]]) -> list[tuple[str, object, object, MeaningRelation]]:
    rows = []
    for case in cases:
        expected = case["expected"]
        assert isinstance(expected, dict)
        rows.append(
            (
                str(case["case_id"]),
                projection_from_dict(case["left_projection"]),
                projection_from_dict(case["right_projection"]),
                MeaningRelation(str(expected["meaning_relation"])),
            )
        )
    return rows


def _harm(cases: list[dict[str, object]], arm) -> tuple[int, int]:
    """``(correct answers destroyed, wrong answers repaired)`` against ``A0``."""

    destroyed = repaired = 0
    for _case_id, left, right, gold in _pairs(cases):
        current = compare_meaning(left, right).relation
        predicted = arm(left, right)
        if current is gold and predicted is not gold:
            destroyed += 1
        if current is not gold and predicted is gold:
            repaired += 1
    return destroyed, repaired


def arm_shared_observed_frame(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> MeaningRelation:
    """The candidate that beats ``A3``'s harm, stated before it was measured.

    The record standard decides a relation by reading the coordinates in
    precedence order and taking the first on which the two records differ. A
    coordinate stated on one side only is not evidence of a difference and not
    evidence of an agreement; it is not evidence. So restrict both projections to
    the coordinates observed on *both* sides and apply the precedence order to
    that frame. Where a higher-precedence coordinate survives on both sides and
    separates, it decides --- which is the ``LU`` stratum, and the reason this is
    not ``A1``. Where nothing that survives separates, the pair is compatible on
    everything the extraction preserved.

    What separates it from ``A0`` is one branch: ``compare_meaning`` reads a
    one-sided ``modality`` absence as a distinct value and separates, and this
    rule drops the coordinate instead. On ``INTACT_RECORD_GOLD`` those are the
    only two decisions it moves.

    It is a function of the two projections and it imports nothing from any
    corpus builder, so it is a legitimate candidate arm. It is not registered as
    one: :class:`TestTheRuleThatBeatsTheHarmSurrendersTheBenefit` measures what it
    pays.
    """

    trimmed_left, trimmed_right = left, right
    for coordinate in COORDINATES:
        observed_left = getattr(left, coordinate) != ABSENT_VALUE[coordinate]
        observed_right = getattr(right, coordinate) != ABSENT_VALUE[coordinate]
        if observed_left != observed_right or not observed_left:
            blank = {coordinate: ABSENT_VALUE[coordinate]}
            trimmed_left = replace(trimmed_left, **blank)
            trimmed_right = replace(trimmed_right, **blank)
    return compare_meaning(trimmed_left, trimmed_right).relation


def _differing_case(
    cases: list[dict[str, object]], coordinate: str
) -> dict[str, object]:
    """The ``LD`` case of the shipped corpus for one coordinate."""

    for case in cases:
        meta = case["partial_observation_record_gold"]
        assert isinstance(meta, dict)
        if str(meta["stratum"]) == STRATUM_LD and meta["lost_coordinate"] == coordinate:
            return case
    raise AssertionError(f"no {STRATUM_LD} case for {coordinate}")


def _orbit_form(cases: list[dict[str, object]], coordinate: str) -> str:
    """The canonical form of the undecidable orbit for one coordinate."""

    case = _differing_case(cases, coordinate)
    return canonical_pair_form(
        projection_from_dict(case["left_projection"]),
        projection_from_dict(case["right_projection"]),
    )


@pytest.fixture(scope="module")
def shipped_cases() -> list[dict[str, object]]:
    return load_jsonl(REPO_ROOT / INTACT_SOURCES[INTACT_RECORD_GOLD])


@pytest.fixture(scope="module")
def campaign() -> dict[str, object]:
    payload, _probe = run_campaign(REPO_ROOT)
    return payload


class TestTheCanonicalisationStripsOnlyWhatGoldDoesNotRead:
    """Each thing it collapses, with a pair it must not collapse beside it."""

    def test_it_accounts_for_every_field_a_projection_has(self) -> None:
        """A field it neither reads nor names as bookkeeping would overstate the ceiling.

        Two pairs differing only in an ignored field would be reported as the
        same evidence, and the orbit count --- and so the floor --- would come out
        too high. The split is computed against the dataclass, so a field added
        to ``ScientificMeaningProjection`` fails this until someone places it.
        """

        census = canonicalisation_field_census()
        assert census["uncovered"] == []
        assert census["named_but_not_a_projection_field"] == []
        assert census["covers_every_field"] is True
        assert set(census["projection_fields"]) == (
            set(CANONICAL_BOOKKEEPING_FIELDS)
            | set(OPEN_VOCABULARY_FIELDS)
            | set(CLOSED_VOCABULARY_FIELDS)
            | set(CANONICAL_ROLE_FIELDS)
        )

    def test_argument_roles_are_canonicalised_and_not_dropped(self) -> None:
        """No rule reads them; that is not a licence to treat them as absent."""

        plain = (_projection("l"), _projection("r"))
        with_roles = (
            replace(plain[0], argument_roles=(("agent", "ceil:referent:0"),)),
            plain[1],
        )
        assert canonical_pair_form(*with_roles) != canonical_pair_form(*plain)

    def test_bookkeeping_is_not_part_of_the_evidence(self) -> None:
        left, right = _projection("l"), _projection("r")
        renamed_left = replace(
            left,
            projection_id="somewhere:else:l",
            source_id="a-different-source",
            source_span="other.txt#l",
        )
        assert set(CANONICAL_BOOKKEEPING_FIELDS) == {
            "projection_id",
            "source_id",
            "source_span",
        }
        assert canonical_pair_form(renamed_left, right) == canonical_pair_form(left, right)

    def test_a_relation_is_symmetric_so_orientation_is_not_evidence(self) -> None:
        left = _projection("l", referent_ids=("ceil:referent:1",))
        right = _projection("r")
        assert compare_meaning(left, right).relation is compare_meaning(right, left).relation
        assert canonical_pair_form(left, right) == canonical_pair_form(right, left)

    def test_a_consistent_renaming_of_ids_is_invisible_to_every_rule(self) -> None:
        """And is therefore invisible to the canonical form, for the same reason."""

        left = _projection("l", construct_ids=("ceil:construct:1",))
        right = _projection("r")
        renaming = {
            "construct_ids": ("renamed:construct:0",),
            "referent_ids": ("renamed:referent:0",),
        }
        moved_left = replace(left, referent_ids=renaming["referent_ids"])
        moved_right = replace(
            right,
            referent_ids=renaming["referent_ids"],
            construct_ids=renaming["construct_ids"],
        )
        moved_left = replace(moved_left, construct_ids=("renamed:construct:1",))
        for arm in ARM_ORDER:
            assert ARMS[arm](moved_left, moved_right) is ARMS[arm](left, right)
        assert canonical_pair_form(moved_left, moved_right) == canonical_pair_form(left, right)

    def test_an_inconsistent_renaming_is_a_different_pair(self) -> None:
        """The check that the canonicalisation is not collapsing everything."""

        left, right = _projection("l"), _projection("r")
        one_side_only = replace(left, referent_ids=("ceil:referent:9",))
        assert compare_meaning(one_side_only, right).relation is not (
            compare_meaning(left, right).relation
        )
        assert canonical_pair_form(one_side_only, right) != canonical_pair_form(left, right)

    def test_an_absent_value_never_canonicalises_onto_a_stated_one(self) -> None:
        """The one collapse that would destroy the study if it happened."""

        stated = _projection("l"), _projection("r")
        for coordinate in COORDINATES:
            silenced = (
                replace(stated[0], **{coordinate: ABSENT_VALUE[coordinate]}),
                stated[1],
            )
            assert canonical_pair_form(*silenced) != canonical_pair_form(*stated), coordinate

    def test_the_closed_vocabularies_are_relabelled_only_when_asked(self) -> None:
        """And the default is the one amendment 004 measures with."""

        assert CLOSED_VOCABULARY_FIELDS == ("polarity", "modality")
        assert "polarity" not in OPEN_VOCABULARY_FIELDS
        positive = (_projection("l"), _projection("r", polarity=ABSENT_VALUE["polarity"]))
        negated = (
            _projection("l", polarity=Polarity.NEGATED),
            _projection("r", polarity=ABSENT_VALUE["polarity"]),
        )
        assert canonical_pair_form(
            *positive, relabel_closed_vocabularies=False
        ) != canonical_pair_form(*negated, relabel_closed_vocabularies=False)
        assert canonical_pair_form(*positive) == canonical_pair_form(*negated)


class TestTheWitnessIsTwoLegalCasesWithOneSetOfProjections:
    """The bound in its sharpest form: no swap, no renaming, nothing to argue.

    ``undecidability_witness_cases`` builds an ``LA`` case and an ``LD`` case
    whose extraction loss falls on the same side, which the record standard
    leaves free and the derivation rule does not read. ``LD``'s surviving record
    keeps the base value and ``LA``'s records both hold it, so the projections
    come out identical.
    """

    @pytest.mark.parametrize("coordinate", COORDINATES)
    def test_the_projections_are_identical_and_the_gold_is_not(
        self, coordinate: str
    ) -> None:
        agreeing, differing = undecidability_witness_cases(coordinate)

        def evidence(case: dict[str, object]) -> dict[str, object]:
            out: dict[str, object] = {}
            for side in ("left_projection", "right_projection"):
                payload = case[side]
                assert isinstance(payload, dict)
                out[side] = {
                    key: value
                    for key, value in payload.items()
                    if key not in {"projection_id", "source_span"}
                }
            return out

        assert evidence(agreeing) == evidence(differing)
        assert agreeing["case_id"] != differing["case_id"]

        agreeing_gold = MeaningRelation(str(agreeing["expected"]["meaning_relation"]))
        differing_gold = MeaningRelation(str(differing["expected"]["meaning_relation"]))
        assert agreeing_gold is MeaningRelation.COMPATIBLE
        assert differing_gold in NONMERGE_RELATIONS

    @pytest.mark.parametrize("coordinate", COORDINATES)
    def test_their_canonical_forms_are_equal_without_any_relabelling(
        self, coordinate: str
    ) -> None:
        agreeing, differing = undecidability_witness_cases(coordinate)
        pairs = [
            (
                projection_from_dict(case["left_projection"]),
                projection_from_dict(case["right_projection"]),
            )
            for case in (agreeing, differing)
        ]
        assert canonical_pair_form(
            *pairs[0], relabel_closed_vocabularies=False
        ) == canonical_pair_form(*pairs[1], relabel_closed_vocabularies=False)

    @pytest.mark.parametrize("coordinate", COORDINATES)
    def test_the_builders_own_validators_accept_both(self, coordinate: str) -> None:
        """A constructed witness is only worth anything if it is a legal case."""

        cases = list(undecidability_witness_cases(coordinate))
        for case in cases:
            validate_case(case)
        for receipt in construction_receipts(cases):
            contract = STRATUM_CONTRACT[str(receipt["stratum"])]
            assert len(list(receipt["one_sided_absences"])) == contract["n_one_sided_absences"]
            assert bool(receipt["gold_is_determinate"]) is contract["gold_is_determinate"]
            assert bool(receipt["absence_is_decisive"]) is contract["absence_is_decisive"]
            assert receipt["gold"] == receipt["gold_from_records"]

    @pytest.mark.parametrize("coordinate", COORDINATES)
    def test_every_arm_answers_the_two_the_same_way(self, coordinate: str) -> None:
        """Which is the whole point: one of the two answers is necessarily wrong.

        Not only the four arms on record. Any function of the two projections
        gives these two cases one answer, because they *are* one pair of
        projections; the arms are checked because they are the functions this
        study has, and because a difference would mean an arm is reading the case
        id.
        """

        cases = undecidability_witness_cases(coordinate)
        answers = []
        golds = []
        for case in cases:
            left = projection_from_dict(case["left_projection"])
            right = projection_from_dict(case["right_projection"])
            answers.append({arm: ARMS[arm](left, right) for arm in ARM_ORDER})
            golds.append(MeaningRelation(str(case["expected"]["meaning_relation"])))
        assert answers[0] == answers[1]
        assert golds[0] is not golds[1]
        for arm, answer in answers[0].items():
            # At most one of the two, for every arm: one answer, two golds.
            assert sum(1 for gold in golds if answer is gold) <= 1, arm

    def test_the_records_behind_them_do_differ(self) -> None:
        """The relation is determinate at the source; only the extraction is not."""

        agreeing, differing = undecidability_witness_cases("polarity")
        for case in (agreeing, differing):
            meta = case["partial_observation_record_gold"]
            assert isinstance(meta, dict)
            left = projection_from_dict(meta["left_record"])
            right = projection_from_dict(meta["right_record"])
            assert relation_from_records(left, right) is MeaningRelation(
                str(case["expected"]["meaning_relation"])
            )
        agreeing_meta = agreeing["partial_observation_record_gold"]
        differing_meta = differing["partial_observation_record_gold"]
        assert isinstance(agreeing_meta, dict) and isinstance(differing_meta, dict)
        assert agreeing_meta["records_differ_on"] is None
        assert differing_meta["records_differ_on"] == "polarity"

    def test_it_refuses_a_coordinate_that_is_not_one(self) -> None:
        with pytest.raises(KeyError):
            undecidability_witness_cases("observation_status")


class TestTheCommittedCorpusCarriesTheSameConflict:
    """The shipped 36 cases, without constructing anything."""

    def test_the_ceiling_is_what_amendment_004_states(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        ceiling = identifiability_ceiling(_pairs(shipped_cases))
        for field, value in COMMITTED_CEILING.items():
            assert ceiling[field] == value, field

    def test_a0_already_reaches_the_ceiling_and_no_other_arm_does(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        """"A better rule" is not available here, and this is the number that says so."""

        ceiling = identifiability_ceiling(_pairs(shipped_cases))
        assert ceiling["arms_at_the_ceiling"] == [ARM_CURRENT]
        assert ceiling["exact_agreement_by_arm"] == {
            ARM_CURRENT: 27,
            ARM_ASYMMETRIC: 10,
            ARM_STRICT: 10,
            ARM_DECISIVE: 18,
        }

    def test_there_is_one_undecidable_orbit_per_identity_coordinate(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        """Not a cluster of near-misses on one coordinate: the whole census."""

        stratum_of = {}
        lost_of = {}
        for case in shipped_cases:
            meta = case["partial_observation_record_gold"]
            assert isinstance(meta, dict)
            stratum_of[str(case["case_id"])] = str(meta["stratum"])
            lost_of[str(case["case_id"])] = meta["lost_coordinate"]

        ceiling = identifiability_ceiling(_pairs(shipped_cases))
        coordinates = set()
        for orbit in ceiling["undecidable_orbits"]:
            case_ids = list(orbit["case_ids"])
            assert len(case_ids) == 2
            assert sorted(stratum_of[case_id] for case_id in case_ids) == [
                STRATUM_LA,
                STRATUM_LD,
            ]
            lost = {lost_of[case_id] for case_id in case_ids}
            assert len(lost) == 1
            coordinates |= lost
            assert MeaningRelation.COMPATIBLE.value in orbit["golds"]
            assert orbit["forces_a_false_merge_a_false_split_or_an_abstention"] is True
            assert len(orbit["a0_is_correct_on"]) == 1
        assert coordinates == set(COORDINATES)

    def test_without_relabelling_the_poles_eight_of_the_nine_still_collapse(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        """Which one needs the extra step, and that only one does.

        The shipped corpus alternates which side each loss falls on, so ``LA``
        and ``LD`` state the surviving value on opposite sides. For the seven
        opaque coordinates and for ``modality`` a swap is enough; for
        ``polarity`` the two cases state opposite poles, so collapsing them needs
        the closed-vocabulary relabelling of section 2.1 of the amendment. That
        step is not load-bearing --- ``undecidability_witness_cases`` reaches the
        same conflict for ``polarity`` with no relabelling and no swap --- and
        this pins exactly how much of the count depends on it.
        """

        strict = identifiability_ceiling(
            _pairs(shipped_cases), relabel_closed_vocabularies=False
        )
        assert strict["n_undecidable_orbits"] == 8
        assert (
            strict["harm_floor_for_an_arm_that_commits_no_false_merge_and_no_false_split"] == 8
        )
        lost_of = {}
        for case in shipped_cases:
            meta = case["partial_observation_record_gold"]
            assert isinstance(meta, dict)
            lost_of[str(case["case_id"])] = meta["lost_coordinate"]
        reached = {
            lost_of[case_id]
            for orbit in strict["undecidable_orbits"]
            for case_id in orbit["case_ids"]
        }
        assert set(COORDINATES) - reached == {"polarity"}

    def test_the_lu_and_nl_strata_are_not_in_an_undecidable_orbit(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        """Which is why the floor is 9 and not the whole harm denominator of 17.

        On the eight ``LU`` pairs a coordinate that survives on both sides already
        decides, so the loss could not have changed the answer and no rule is
        forced to abstain there. ``A1`` abstains anyway and pays 17; ``A3`` does
        not and pays 9. The eight-pair difference between them is exactly the
        stratum the bound leaves free.
        """

        stratum_of = {}
        for case in shipped_cases:
            meta = case["partial_observation_record_gold"]
            assert isinstance(meta, dict)
            stratum_of[str(case["case_id"])] = str(meta["stratum"])
        ceiling = identifiability_ceiling(_pairs(shipped_cases))
        in_an_orbit = {
            case_id for orbit in ceiling["undecidable_orbits"] for case_id in orbit["case_ids"]
        }
        assert {stratum_of[case_id] for case_id in in_an_orbit} == {STRATUM_LA, STRATUM_LD}
        assert _harm(shipped_cases, ARMS[ARM_ASYMMETRIC])[0] - _harm(
            shipped_cases, ARMS[ARM_DECISIVE]
        )[0] == 8

    def test_every_arm_is_constant_on_every_orbit(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        """The check that the canonicalisation is not stripping something an arm reads.

        If it were, some arm would answer two members of one orbit differently
        and the bound would not apply to it. This is the assertion that keeps the
        canonicalisation honest, and it is measured rather than declared.
        """

        ceiling = identifiability_ceiling(_pairs(shipped_cases))
        assert ceiling["every_arm_is_constant_on_every_orbit"] is True
        assert ceiling["arm_is_constant_on_every_orbit"] == {arm: True for arm in ARM_ORDER}

    def test_the_trilemma_exhausts_the_relation_type(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        """Three options and no fourth, which is what makes the floor a floor.

        ``MeaningRelation`` is ``COMPATIBLE``, ``UNRESOLVED`` and the five
        ``NONMERGE_RELATIONS``. On an orbit carrying ``COMPATIBLE`` and a
        separation, the first is a false merge, the five are false splits and the
        last destroys ``A0``'s one correct answer. If the type grew a value that
        was none of those three, the argument would have a hole and this test
        would find it.
        """

        assert set(MeaningRelation) == (
            {MeaningRelation.COMPATIBLE, MeaningRelation.UNRESOLVED} | set(NONMERGE_RELATIONS)
        )
        ceiling = identifiability_ceiling(_pairs(shipped_cases))
        for orbit in ceiling["undecidable_orbits"]:
            golds = {MeaningRelation(value) for value in orbit["golds"]}
            assert MeaningRelation.COMPATIBLE in golds
            assert golds & set(NONMERGE_RELATIONS)
            assert MeaningRelation.UNRESOLVED not in golds
            assert len(orbit["a0_is_correct_on"]) == 1

    def test_a3s_measured_harm_is_exactly_the_floor(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        ceiling = identifiability_ceiling(_pairs(shipped_cases))
        destroyed, repaired = _harm(shipped_cases, ARMS[ARM_DECISIVE])
        assert destroyed == 9
        assert repaired == 0
        assert destroyed == (
            ceiling["harm_floor_for_an_arm_that_commits_no_false_merge_and_no_false_split"]
        )

    def test_a1_pays_more_than_the_floor_so_the_floor_is_not_trivial(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        """A bound every arm meets would say nothing about A3."""

        assert _harm(shipped_cases, ARMS[ARM_ASYMMETRIC])[0] == 17
        assert _harm(shipped_cases, ARMS[ARM_STRICT])[0] == 17

    def test_no_other_corpus_has_an_undecidable_orbit(
        self, campaign: dict[str, object]
    ) -> None:
        """Which is why G9 could not be measured before amendment 003."""

        corpora = campaign["corpora"]
        for corpus_id, entry in corpora.items():
            expected = 9 if corpus_id == INTACT_RECORD_GOLD else 0
            assert entry["identifiability_ceiling"]["n_undecidable_orbits"] == expected, (
                corpus_id
            )

    def test_removing_the_conflicting_strata_removes_the_floor(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        """The floor is read off the cases, not quoted, and it moves with them.

        This is the same edit that makes the corpus circular and returns ``G9``
        to ``CANNOT_CHECK``. Here it is the other face of the same fact: the
        strata on which gold and ``A3`` disagree are exactly the strata on which
        gold is not a function of the projections.
        """

        kept = []
        for case in shipped_cases:
            meta = case["partial_observation_record_gold"]
            assert isinstance(meta, dict)
            if str(meta["stratum"]) not in {STRATUM_LA, STRATUM_LD}:
                kept.append(case)
        ceiling = identifiability_ceiling(_pairs(kept))
        assert ceiling["n_undecidable_orbits"] == 0
        assert (
            ceiling["harm_floor_for_an_arm_that_commits_no_false_merge_and_no_false_split"] == 0
        )
        assert _harm(kept, ARMS[ARM_DECISIVE]) == (0, 0)


class TestHeldOutDraws:
    """Re-measured on cases nobody had in front of them when the bound was stated."""

    def test_the_default_draw_is_the_corpus_that_ships(self) -> None:
        """A parameterised builder that changed its own output would be a rewrite."""

        assert DEFAULT_DRAW.label == DEFAULT_DRAW_LABEL
        assert DEFAULT_DRAW.record_values is RECORD_VALUES
        directory = REPO_ROOT / "research/p3-partial-observation-record-gold-v1"
        assert cases_bytes(record_gold_cases()) == (directory / "cases.jsonl").read_bytes()
        assert standard_bytes() == (
            directory / "PARTIAL_OBSERVATION_RECORD_STANDARD.json"
        ).read_bytes()

    @pytest.mark.parametrize("seed", HELD_OUT_SEEDS)
    def test_a_held_out_draw_shares_no_value_with_the_frozen_table(self, seed: int) -> None:
        """Held out means held out: no id string of the shipped corpus survives."""

        draw = fresh_draw(seed)
        for coordinate in COORDINATES:
            drawn = set(draw.record_values[coordinate])
            if coordinate in CLOSED_VOCABULARY_FIELDS:
                # Closed vocabularies have finitely many values, so a redraw can
                # only permute or re-pick within them; what must not repeat is
                # the absent value.
                assert ABSENT_VALUE[coordinate] not in drawn
                continue
            assert not drawn & set(RECORD_VALUES[coordinate])
            for value in drawn:
                token = value[0] if isinstance(value, tuple) else value
                assert token.startswith(FRESH_DRAW_VALUE_PREFIX)

    def test_a_draw_is_reproducible_from_its_seed_and_two_seeds_differ(self) -> None:
        assert fresh_draw(7).record_values == fresh_draw(7).record_values
        assert fresh_draw(7).lost_side == fresh_draw(7).lost_side
        assert fresh_draw(7).record_values != fresh_draw(11).record_values

    @pytest.mark.parametrize("seed", HELD_OUT_SEEDS)
    def test_every_number_of_the_bound_reproduces(self, seed: int) -> None:
        """``held_out_corpus`` runs the builder's own ``verify`` before returning."""

        cases = held_out_corpus(seed)
        assert len(cases) == 36
        ceiling = identifiability_ceiling(_pairs(cases))
        assert ceiling["n_undecidable_orbits"] == 9
        assert ceiling["max_exact_agreement_reachable_by_a_candidate_visible_rule"] == 27
        assert ceiling["arms_at_the_ceiling"] == [ARM_CURRENT]
        assert ceiling["every_arm_is_constant_on_every_orbit"] is True
        assert (
            ceiling["harm_floor_for_an_arm_that_commits_no_false_merge_and_no_false_split"] == 9
        )

    @pytest.mark.parametrize("seed", HELD_OUT_SEEDS)
    def test_the_arms_cost_the_same_on_a_held_out_draw(self, seed: int) -> None:
        cases = held_out_corpus(seed)
        assert _harm(cases, ARMS[ARM_DECISIVE]) == (9, 0)
        assert _harm(cases, ARMS[ARM_ASYMMETRIC]) == (17, 0)

    @pytest.mark.parametrize("seed", HELD_OUT_SEEDS)
    def test_a_held_out_draw_is_never_written(self, seed: int) -> None:
        """The corpus directory holds one corpus, and it is the frozen draw's."""

        held_out_corpus(seed)
        directory = REPO_ROOT / "research/p3-partial-observation-record-gold-v1"
        assert cases_bytes(record_gold_cases()) == (directory / "cases.jsonl").read_bytes()
        assert not any(
            path.name.startswith(FRESH_DRAW_VALUE_PREFIX) for path in directory.iterdir()
        )

    def test_a_draw_that_states_an_absent_value_on_a_record_is_refused(self) -> None:
        """A record that states nothing is not a record gold can be read off."""

        broken = dict(fresh_draw(7).record_values)
        broken["polarity"] = (Polarity.UNKNOWN, Polarity.NEGATED)
        with pytest.raises(RecordCorpusError, match="absent value"):
            RecordDraw(
                label="broken", record_values=broken, lost_side=fresh_draw(7).lost_side
            )

    def test_a_draw_missing_a_loss_side_is_refused(self) -> None:
        drawn = fresh_draw(7)
        sides = {key: value for key, value in drawn.lost_side.items()}
        del sides[(STRATUM_LA, "modality")]
        with pytest.raises(RecordCorpusError, match="no loss side"):
            RecordDraw(label="broken", record_values=drawn.record_values, lost_side=sides)


class TestTheRuleThatBeatsTheHarmSurrendersTheBenefit:
    """The (a) branch, measured rather than asserted not to exist.

    ``arm_shared_observed_frame`` is a real candidate: a function of the two
    projections, importing nothing from any corpus builder, stated over the
    record standard's precedence order. It destroys one correct answer instead of
    nine. It pays for that by answering a determinate relation on every probe
    case, where the frozen probe gold is ``UNRESOLVED``.
    """

    def test_it_does_beat_a3_on_harm(self, shipped_cases: list[dict[str, object]]) -> None:
        assert _harm(shipped_cases, arm_shared_observed_frame) == (1, 1)
        assert _harm(shipped_cases, ARMS[ARM_DECISIVE]) == (9, 0)

    def test_and_it_is_not_a0(self, shipped_cases: list[dict[str, object]]) -> None:
        """Otherwise the comparison would be with the system under test wearing a hat.

        It is not ``A0``, and it is barely not ``A0``: the two decisions it moves
        are the ``modality`` orbit, where ``compare_meaning`` reads the one-sided
        absence as a distinct value and this rule drops the coordinate. That is
        the whole of the difference, and it is why the harm it saves and the
        benefit it forfeits are two faces of one branch.
        """

        moved = []
        for case in shipped_cases:
            meta = case["partial_observation_record_gold"]
            assert isinstance(meta, dict)
            left = projection_from_dict(case["left_projection"])
            right = projection_from_dict(case["right_projection"])
            if arm_shared_observed_frame(left, right) is not (
                compare_meaning(left, right).relation
            ):
                moved.append(meta["lost_coordinate"])
        assert moved == ["modality", "modality"]

    @pytest.mark.parametrize("corpus_id", sorted(PROBE_OF))
    def test_it_over_resolves_every_probe_case(self, corpus_id: str) -> None:
        probe_id = PROBE_OF[corpus_id]
        probe = build_probe(load_jsonl(REPO_ROOT / INTACT_SOURCES[corpus_id]), probe_id)
        assert probe
        ledger = build_identity_ledger(
            probe_id,
            [
                (
                    case.case_id,
                    "shared_observed_frame",
                    case.gold,
                    arm_shared_observed_frame(case.left, case.right),
                )
                for case in probe
            ],
        )
        exercise = ledger.unresolved_calibration_exercise("shared_observed_frame")
        assessment = assess_guard(exercise)
        assert exercise.opportunities == len(probe)
        assert exercise.violations == len(probe)
        assert exercise.violation_rate == 1.0
        assert assessment.outcome is Outcome.FAIL

    @pytest.mark.parametrize("corpus_id", sorted(PROBE_OF))
    def test_a3_still_scores_zero_on_the_same_probe(self, corpus_id: str) -> None:
        """The comparison G10 makes, run against the candidate on the same cases."""

        probe_id = PROBE_OF[corpus_id]
        probe = build_probe(load_jsonl(REPO_ROOT / INTACT_SOURCES[corpus_id]), probe_id)
        ledger = build_identity_ledger(
            probe_id,
            [
                (case.case_id, ARM_DECISIVE, case.gold, ARMS[ARM_DECISIVE](case.left, case.right))
                for case in probe
            ],
        )
        assert ledger.unresolved_calibration_exercise(ARM_DECISIVE).violations == 0

    @pytest.mark.parametrize("seed", HELD_OUT_SEEDS)
    def test_the_trade_off_reproduces_on_a_held_out_draw(self, seed: int) -> None:
        """Both halves of it: the harm it saves and the abstention it forfeits."""

        cases = held_out_corpus(seed)
        assert _harm(cases, arm_shared_observed_frame) == (1, 1)
        determinate = [
            case_id
            for case_id, left, right, _gold in _pairs(cases)
            if arm_shared_observed_frame(left, right) is not MeaningRelation.UNRESOLVED
        ]
        assert len(determinate) == len(cases)

    def test_the_trade_off_is_the_bound_restated(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        """Every unit of harm below the floor is bought with an over-resolution.

        On each undecidable orbit the candidate answers ``COMPATIBLE``, which is
        the false-merge horn of the trilemma; the harm it saves is the harm the
        floor says an abstaining rule must pay.
        """

        orbits = projection_orbits(_pairs(shipped_cases))
        pairs = {case_id: (left, right) for case_id, left, right, _ in _pairs(shipped_cases)}
        ceiling = identifiability_ceiling(_pairs(shipped_cases))
        for orbit in ceiling["undecidable_orbits"]:
            answers = {
                arm_shared_observed_frame(*pairs[case_id]) for case_id in orbit["case_ids"]
            }
            assert answers == {MeaningRelation.COMPATIBLE}
        assert len(orbits) == 27


class TestTheFreezesOwnProbeGoldSaysAbstainOnEveryUndecidableOrbit:
    """The bridge from "no false merge and no false split" to "keeps A3's benefit".

    The floor is stated over the failure kinds: a rule that commits neither a
    false merge nor a false split on ``INTACT_RECORD_GOLD`` must abstain on the
    nine orbits and pays nine. Tying that to ``G10_BENEFIT_A3`` needs one more
    step, because ``G10`` is measured on the three probe corpora and *those* have
    no canonical form in common with this one --- the atlases they are redacted
    from populate different coordinates.

    The step is that the freeze's probe-gold rule is corpus-independent. Every
    ``LD`` case's *record* pair is a legal probe parent under
    ``redactable_coordinates``, and redacting its deciding coordinate --- the
    freeze's own construction, section 4.2 --- yields a probe case whose
    projections are the orbit, with gold ``UNRESOLVED`` by
    ``PROBE_GOLD_DERIVATION_RULE``. So the freeze already says abstention is
    right on these pairs. Whether the shipped probe corpora happen to contain
    one is a fact about which atlases exist, not about the rule, and this class
    keeps the two apart instead of letting the stronger claim borrow the weaker
    one's evidence.
    """

    @pytest.mark.parametrize("coordinate", COORDINATES)
    def test_the_differing_records_are_a_legal_probe_parent(
        self, coordinate: str, shipped_cases: list[dict[str, object]]
    ) -> None:
        case = _differing_case(shipped_cases, coordinate)
        meta = case["partial_observation_record_gold"]
        assert isinstance(meta, dict)
        left = projection_from_dict(meta["left_record"])
        right = projection_from_dict(meta["right_record"])
        gold = MeaningRelation(str(case["expected"]["meaning_relation"]))
        assert gold in NONMERGE_RELATIONS
        assert redactable_coordinates(left, right, gold) == (coordinate,)

    @pytest.mark.parametrize("coordinate", COORDINATES)
    def test_redacting_it_lands_on_the_orbit_with_gold_unresolved(
        self, coordinate: str, shipped_cases: list[dict[str, object]]
    ) -> None:
        case = _differing_case(shipped_cases, coordinate)
        meta = case["partial_observation_record_gold"]
        assert isinstance(meta, dict)
        parent = {
            "case_id": f"{case['case_id']}|records",
            "left_projection": meta["left_record"],
            "right_projection": meta["right_record"],
            "expected": case["expected"],
        }
        probe = build_probe([parent], "PROBE_FROM_THE_RECORD_PAIR")
        assert probe
        orbit = _orbit_form(shipped_cases, coordinate)
        landed = [
            item
            for item in probe
            if canonical_pair_form(item.left, item.right) == orbit
        ]
        assert landed, coordinate
        for item in landed:
            assert item.gold is MeaningRelation.UNRESOLVED
        assert PROBE_GOLD_DERIVATION_RULE.endswith("probe-gold-is-unresolved-after-redaction")

    def test_the_shipped_probes_do_not_contain_these_orbits(
        self, shipped_cases: list[dict[str, object]]
    ) -> None:
        """Stated so the stronger claim is not read off the weaker evidence.

        ``G10`` as measured cannot force abstention on these orbits, because the
        three probe corpora reach only ``polarity``, ``measurement_ids`` and
        ``temporal_context_ids`` and their atlases populate the other coordinates
        differently. The freeze's rule forces it; the shipped sample does not.
        """

        orbits = set(projection_orbits(_pairs(shipped_cases)))
        for corpus_id, probe_id in PROBE_OF.items():
            probe = build_probe(load_jsonl(REPO_ROOT / INTACT_SOURCES[corpus_id]), probe_id)
            forms = {canonical_pair_form(item.left, item.right) for item in probe}
            assert not forms & orbits, probe_id


class TestTheGateCarriesTheFloor:
    def test_g9_still_fails_with_the_same_counts(self, campaign: dict[str, object]) -> None:
        """A floor is not a licence to pass, and the gate is unchanged where it counts."""

        gate = campaign["gates"]["G9_HARM_A3"]
        assert gate["outcome"] == Outcome.FAIL.value
        assert gate["correct_answers_destroyed"] == 9
        assert gate["decisions_changed"] == 27
        assert gate["wrong_answers_repaired"] == 9

    def test_and_now_says_the_nine_is_a_floor(self, campaign: dict[str, object]) -> None:
        gate = campaign["gates"]["G9_HARM_A3"]
        assert gate["harm_floor_for_any_candidate_visible_rule"] == 9
        assert gate["a3_harm_is_at_the_floor"] is True
        assert gate["by_corpus"][INTACT_RECORD_GOLD]["harm_floor"] == 9
        assert gate["by_corpus"][INTACT_RECORD_GOLD]["undecidable_orbits"] == 9
        for corpus_id in INTACT_ORDER:
            if corpus_id == INTACT_RECORD_GOLD:
                continue
            assert gate["by_corpus"][corpus_id]["harm_floor"] == 0

    def test_the_threshold_and_the_subject_did_not_move(self) -> None:
        from orion.study.p3.partial_observation_probe import GATES

        spec = GATES["G9_HARM_A3"]
        assert spec["statement"].startswith("A3_decisive_absence_only")
        assert spec["blocking"] is True
        assert spec["amendment_004"]["threshold_unchanged"] is True
        assert spec["amendment_004"]["statement_unchanged"] is True
        assert spec["amendment_004"]["arms_added"] == []
        assert spec["amendment_004"]["corpora_added"] == []
        assert ARM_ORDER == (ARM_CURRENT, ARM_ASYMMETRIC, ARM_STRICT, ARM_DECISIVE)

    def test_a_corpus_payload_without_a_ceiling_reports_an_unknown_floor(self) -> None:
        """Not a crash, and not a zero either: a zero would read as "no floor"."""

        from orion.study.p3.partial_observation_probe import evaluate_gates

        payload, _probe = run_campaign(REPO_ROOT)
        stripped = {
            corpus_id: {
                key: value
                for key, value in entry.items()
                if key != "identifiability_ceiling"
            }
            for corpus_id, entry in payload["corpora"].items()
        }
        gates = evaluate_gates(stripped)
        assert gates["G9_HARM_A3"]["outcome"] == Outcome.FAIL.value
        assert gates["G9_HARM_A3"]["harm_floor_for_any_candidate_visible_rule"] is None
        assert gates["G9_HARM_A3"]["a3_harm_is_at_the_floor"] is False
        assert gates["G9_HARM_A3"]["by_corpus"][INTACT_RECORD_GOLD]["harm_floor"] is None

    def test_the_campaign_is_still_a_failure_overall(
        self, campaign: dict[str, object]
    ) -> None:
        assert campaign["overall_outcome"] == Outcome.FAIL.value


class TestAmendmentFourBindsToItsOwnRecord:
    def test_the_runner_binds_to_the_amendment_in_force(self) -> None:
        assert FREEZE_TWIN == AMENDMENT_004_TWIN
        twin = json.loads((REPO_ROOT / FREEZE_TWIN).read_text(encoding="utf-8"))
        assert twin["parameters_sha256"] == frozen_digest()
        assert twin["added_arm"] is None
        assert twin["added_corpus"] is None
        assert twin["threshold_changes"] == []
        assert twin["gate_subject_changes"] == []
        assert twin["gate_outcome_changes"] == []

    def test_the_earlier_records_are_left_alone(self) -> None:
        from orion.study.p3.partial_observation_probe import (
            AMENDMENT_002_TWIN,
            AMENDMENT_003_TWIN,
            AMENDMENT_TWIN,
            ORIGINAL_FREEZE_TWIN,
        )

        recorded = {
            ORIGINAL_FREEZE_TWIN: (
                "28d3e289d3dddddaef142e5756b77a825829836f1eadb900b80e49f985f73691"
            ),
            AMENDMENT_TWIN: (
                "d4e97dcfc8a35d97656ec5eee60efc249a8e24dc682dd153c029fd9450b59ac8"
            ),
            AMENDMENT_002_TWIN: (
                "9292414c63a50f0f31ad832b45a891a1eaf90584751f90f10362d941ad36c28e"
            ),
            AMENDMENT_003_TWIN: (
                "a1057b6fe0d1d6fbe1f95c8e2202abe2936c913309aa549036a89a878a4d9b34"
            ),
        }
        for path, digest in recorded.items():
            twin = json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))
            assert twin["parameters_sha256"] == digest
        assert frozen_digest() not in set(recorded.values())

    def test_the_amendment_declares_what_it_serves_and_what_it_leaves_alone(self) -> None:
        twin = json.loads((REPO_ROOT / AMENDMENT_004_TWIN).read_text(encoding="utf-8"))
        assert twin["gate_served"] == "G9_HARM_A3"
        assert twin["gates_not_touched"] == [
            "G5_MINING_YIELD",
            "G6_HARM_A1",
            "G7_COST_A2",
            "G8_NOVELTY",
            "G10_BENEFIT_A3",
        ]
        for prior in twin["amends"]["prior_amendments"]:
            assert prior["left_byte_identical"] is True
        assert twin["amends"]["amended_document_left_byte_identical"] is True
