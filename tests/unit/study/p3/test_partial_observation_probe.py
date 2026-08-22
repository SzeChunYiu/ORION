"""The partial-observation probe must find the defect in the shipped atlases.

These run against the frozen artifacts, not only a fixture. The assertions that
pin ``CANNOT_CHECK`` --- the absent violation rate on the symmetric intact atlases
--- are the ones that must never quietly become ``PASS``: each of them is a place
where a zero could be mistaken for a result.

Two gates that used to be pinned at ``CANNOT_CHECK`` are pinned at ``FAIL`` since
amendment 001, and the difference between those two states is the point of this
file. ``CANNOT_CHECK`` meant the gate had no denominator: A1 could not fire on any
intact pair, and A0 could not fail on one. ``FAIL`` means the denominator exists
and the measurement came back negative. The tests below pin the denominator as
well as the outcome, precisely so that a corpus regression back to zero one-sided
absences shows up as a test failure rather than as a gate quietly returning to a
zero that looks clean.
"""

from __future__ import annotations

import json
import subprocess
import sys
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
from orion.programme.records import Outcome
from orion.study.p3.partial_observation_harm_build import (
    STRATUM_C,
    STRATUM_CONTRACT,
    STRATUM_D,
    STRATUM_H,
    STRATUM_S,
    HarmCorpusError,
    absence_reading_census,
    build_report,
    construction_receipts,
    harm_cases,
    harm_preview,
    rule_agreement_on_fully_observed,
    verify,
)
from orion.study.p3.partial_observation_probe import (
    ABSENT_VALUE,
    ARM_ASYMMETRIC,
    ARM_CURRENT,
    ARM_ORDER,
    ARM_STRICT,
    CANDIDATE_COORDINATE,
    COORDINATES,
    FREEZE_TWIN,
    INTACT_HARM_SYNTHETIC,
    INTACT_ORDER,
    INTACT_SOURCES,
    PARTIALLY_OBSERVED_INTACT_ORDER,
    PROBE_DERIVATION,
    PROBE_HELDOUT_REAL,
    PROBE_HELDOUT_SYNTHETIC,
    PROBE_OF,
    SYMMETRIC_INTACT_ORDER,
    VERDICT_T5,
    FreezeViolation,
    build_probe,
    construction_precondition,
    discriminating_coordinates,
    frozen_digest,
    main,
    observed,
    one_sided_absence_census,
    overall_outcome,
    redactable_coordinates,
    run_campaign,
    verify_against_twin,
)
from orion.study.p3_public_reference import load_jsonl

REPO_ROOT = Path(__file__).resolve().parents[4]
PROBE_IDS = (PROBE_DERIVATION, PROBE_HELDOUT_REAL, PROBE_HELDOUT_SYNTHETIC)

#: The probe corpora each parent emits. Pinned so the amendment's extra condition
#: on ``redactable_coordinates`` is shown to be a no-op rather than asserted to be.
PROBE_SIZES = {PROBE_DERIVATION: 12, PROBE_HELDOUT_REAL: 8, PROBE_HELDOUT_SYNTHETIC: 28}


@pytest.fixture(scope="module")
def campaign() -> dict[str, object]:
    payload, _probe = run_campaign(REPO_ROOT)
    return payload


@pytest.fixture(scope="module")
def shipped() -> list[dict[str, object]]:
    """The harm corpus as it ships, read through the same loader the probe uses."""

    return load_jsonl(REPO_ROOT / INTACT_SOURCES[INTACT_HARM_SYNTHETIC])


def _projection(**overrides: object) -> ScientificMeaningProjection:
    base = {
        "projection_id": "p",
        "source_id": "s",
        "source_span": "span",
        "predicate": "reports_quantity",
        "referent_ids": ("r1",),
        "polarity": Polarity.POSITIVE,
        "modality": Modality.ASSERTED,
    }
    base.update(overrides)
    return ScientificMeaningProjection(**base)  # type: ignore[arg-type]


class TestFreezeBinding:
    def test_runner_digest_matches_the_frozen_twin(self) -> None:
        twin = json.loads((REPO_ROOT / FREEZE_TWIN).read_text(encoding="utf-8"))
        assert twin["parameters_sha256"] == frozen_digest()
        assert verify_against_twin(REPO_ROOT)["parameters_sha256"] == frozen_digest()

    def test_runner_refuses_to_execute_on_a_digest_mismatch(self, tmp_path: Path) -> None:
        twin_path = tmp_path / FREEZE_TWIN
        twin_path.parent.mkdir(parents=True, exist_ok=True)
        twin_path.write_text(json.dumps({"parameters_sha256": "0" * 64}), encoding="utf-8")
        with pytest.raises(FreezeViolation, match="do not match the frozen record"):
            verify_against_twin(tmp_path)

    def test_missing_twin_is_a_violation_not_a_silent_skip(self, tmp_path: Path) -> None:
        with pytest.raises(FreezeViolation, match="freeze twin missing"):
            verify_against_twin(tmp_path)

    def test_main_requires_argv_and_is_invocable_as_a_subprocess(self) -> None:
        with pytest.raises(TypeError):
            main()  # type: ignore[call-arg]
        completed = subprocess.run(
            [sys.executable, "-m", "orion.study.p3.partial_observation_probe", "--print-digest"],
            cwd=REPO_ROOT,
            env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            check=True,
        )
        assert completed.stdout.strip() == frozen_digest()


class TestCoordinateAlgebra:
    def test_observed_rejects_a_coordinate_that_is_not_one(self) -> None:
        with pytest.raises(KeyError):
            observed(_projection(), "not_a_coordinate")

    def test_every_coordinate_has_an_absent_value(self) -> None:
        assert set(COORDINATES) == set(ABSENT_VALUE)
        for coordinate, absent in ABSENT_VALUE.items():
            assert not observed(_projection(**{coordinate: absent}), coordinate)

    def test_a_one_sided_absence_discriminates_nothing(self) -> None:
        left = _projection(measurement_ids=("m1",))
        right = _projection(measurement_ids=("m2",))
        assert discriminating_coordinates(left, right) == ("measurement_ids",)
        silenced = replace(left, measurement_ids=())
        assert discriminating_coordinates(silenced, right) == ()

    def test_compare_meaning_merges_the_pair_it_can_no_longer_tell_apart(self) -> None:
        """The failure the study is derived from, in three lines."""

        left = _projection(measurement_ids=("m1",))
        right = _projection(measurement_ids=("m2",))
        assert compare_meaning(left, right).relation is MeaningRelation.DISTINCT_MEASUREMENT
        silenced = replace(left, measurement_ids=())
        assert compare_meaning(silenced, right).relation is MeaningRelation.COMPATIBLE


class TestConstructionPrecondition:
    def test_the_shipped_probes_have_the_declared_structure(
        self, campaign: dict[str, object]
    ) -> None:
        preconditions = campaign["construction_precondition"]
        assert isinstance(preconditions, dict)
        assert set(preconditions) == set(PROBE_IDS)
        for probe_id, entry in preconditions.items():
            assert entry["passed"], f"{probe_id}: {entry['offenders']}"
        assert preconditions[PROBE_DERIVATION]["n_probe_cases"] > 0

    def test_a_probe_silenced_on_both_sides_is_rejected(self) -> None:
        cases = load_jsonl(REPO_ROOT / INTACT_SOURCES[INTACT_ORDER[0]])
        probe = build_probe(cases, PROBE_DERIVATION)
        assert probe
        broken = replace(
            probe[0],
            right=replace(probe[0].right, **{probe[0].coordinate: ABSENT_VALUE[probe[0].coordinate]}),
        )
        report = construction_precondition([broken], require_nonempty=True)
        assert not report["passed"]
        assert not report["checks"]["C2_exactly_one_coordinate_absent_on_exactly_one_side"]

    def test_an_empty_probe_fails_c1_rather_than_passing_quietly(self) -> None:
        assert not construction_precondition([], require_nonempty=True)["passed"]


class TestTheIntactAtlasesAreUnchanged:
    """A repair may only subtract. The intact side must read exactly as before."""

    @pytest.mark.parametrize("corpus_id", INTACT_ORDER)
    def test_current_arm_still_commits_no_false_merge_and_no_false_split(
        self, campaign: dict[str, object], corpus_id: str
    ) -> None:
        entry = campaign["corpora"][corpus_id]["by_arm"][ARM_CURRENT]
        kinds = entry["decision_kinds"]
        assert kinds["FALSE_MERGE"] == 0
        assert kinds["FALSE_SPLIT"] == 0
        assert entry["false_merge"]["outcome"] == Outcome.PASS.value

    @pytest.mark.parametrize("corpus_id", SYMMETRIC_INTACT_ORDER)
    def test_over_resolution_stays_cannot_check_on_the_symmetric_atlases(
        self, campaign: dict[str, object], corpus_id: str
    ) -> None:
        guard = campaign["corpora"][corpus_id]["by_arm"][ARM_CURRENT]["over_resolution"]
        assert guard["outcome"] == Outcome.CANNOT_CHECK.value
        assert guard["reason"] == "NEVER_EXERCISED"
        exercise = guard["exercises"][0]
        assert exercise["opportunities"] == 0
        # None, not 0.0: an absent rate must not be readable as a clean one.
        assert exercise["violation_rate"] is None

    @pytest.mark.parametrize("corpus_id", SYMMETRIC_INTACT_ORDER)
    def test_no_pair_of_the_2026_08_21_atlases_is_partially_observed(
        self, campaign: dict[str, object], corpus_id: str
    ) -> None:
        census = campaign["corpora"][corpus_id]["one_sided_absence_census"]
        assert census["n_pairs_with_a_one_sided_absence"] == 0
        assert census["by_coordinate"] == {}

    @pytest.mark.parametrize("corpus_id", SYMMETRIC_INTACT_ORDER)
    def test_the_2026_08_21_atlases_are_still_probe_parents(self, corpus_id: str) -> None:
        assert corpus_id in PROBE_OF

    @pytest.mark.parametrize("probe_id", PROBE_IDS)
    def test_the_extra_redactability_condition_is_a_no_op_on_them(
        self, campaign: dict[str, object], probe_id: str
    ) -> None:
        """Amendment 001 refuses to redact a parent that already has an absence.

        Every parent of these three has none, so the probes must be exactly the
        size they were before the condition existed. A shrunken probe would mean
        the condition is silently deleting evidence.
        """

        assert campaign["corpora"][probe_id]["n_cases"] == PROBE_SIZES[probe_id]

    def test_a_parent_with_a_one_sided_absence_is_not_redactable(self) -> None:
        left = _projection(measurement_ids=("m1",), attribution_id="a")
        right = _projection(measurement_ids=("m2",), attribution_id="a")
        assert redactable_coordinates(
            left, right, MeaningRelation.DISTINCT_MEASUREMENT
        ) == ("measurement_ids",)
        asymmetric = replace(right, attribution_id="")
        assert (
            redactable_coordinates(left, asymmetric, MeaningRelation.DISTINCT_MEASUREMENT) == ()
        )

    def test_the_census_would_count_a_partially_observed_pair(self) -> None:
        left = _projection(measurement_ids=("m1",))
        right = _projection()
        census = one_sided_absence_census([("c", left, right, MeaningRelation.COMPATIBLE)])
        assert census["n_pairs_with_a_one_sided_absence"] == 1
        assert census["by_coordinate"] == {"measurement_ids": 1}


class TestTheChannelOpens:
    @pytest.mark.parametrize("probe_id", PROBE_IDS)
    def test_the_guard_now_has_a_denominator_and_fails(
        self, campaign: dict[str, object], probe_id: str
    ) -> None:
        guard = campaign["corpora"][probe_id]["by_arm"][ARM_CURRENT]["over_resolution"]
        exercise = guard["exercises"][0]
        assert exercise["opportunities"] > 0
        assert exercise["violations"] == exercise["opportunities"]
        assert exercise["violation_rate"] == 1.0
        assert guard["outcome"] == Outcome.FAIL.value
        assert guard["reason"] == "VIOLATED"

    def test_the_derivation_probe_comes_from_real_adjudicated_cases(
        self, campaign: dict[str, object]
    ) -> None:
        entry = campaign["corpora"][PROBE_DERIVATION]
        assert entry["n_cases"] == 12
        assert entry["redacted_coordinates"] == ["polarity"]
        assert entry["parent_gold_relations"] == ["CONTRADICTORY"]

    def test_under_parent_gold_the_same_decisions_are_false_merges(
        self, campaign: dict[str, object]
    ) -> None:
        guard = campaign["corpora"][PROBE_DERIVATION]["parent_gold_scoring"][ARM_CURRENT][
            "false_merge"
        ]
        assert guard["outcome"] == Outcome.FAIL.value
        assert guard["exercises"][0]["violation_rate"] == 1.0


class TestGatesRefuseToLaunder:
    def test_the_a1_harm_gate_has_a_denominator_and_reports_a_harm(
        self, campaign: dict[str, object]
    ) -> None:
        """The gate that used to be vacuous now measures something.

        Both halves matter. A zero denominator would put the gate back where it
        started, reporting ``CANNOT_CHECK``; that is the regression the first two
        assertions catch. The rest pins the measurement itself: A1 abstains on
        every pair with a one-sided absence, so on the twelve whose answer is
        determined by a coordinate stated on *both* sides it destroys an answer
        A0 already had right.
        """

        gate = campaign["gates"]["G6_HARM_A1"]
        assert gate["pairs_where_a1_could_fire"] > 0
        assert gate["vacuous"] is False
        assert gate["outcome"] == Outcome.FAIL.value
        assert gate["decisions_changed"] == 21
        assert gate["correct_answers_destroyed"] == 12
        assert gate["pairs_where_a1_could_fire"] == 27

    def test_the_harm_gate_would_report_a_pass_if_a1_left_the_corpus_alone(self) -> None:
        """The gate is not wired to fail whatever happens.

        Same code path, same denominator, an arm that changes nothing: the gate
        reads PASS. Without this, ``FAIL`` above would be consistent with a gate
        that cannot say anything else.
        """

        from orion.study.p3.partial_observation_probe import evaluate_gates

        corpora = {
            corpus_id: {
                "one_sided_absence_census": {"n_pairs_with_a_one_sided_absence": 27},
                "harm_vs_current": {
                    ARM_ASYMMETRIC: {"decisions_changed": 0, "correct_answers_destroyed": 0},
                    ARM_STRICT: {"decisions_changed": 0, "correct_answers_destroyed": 0},
                },
                "mining_census": {"failures": []},
                "by_arm": {},
            }
            for corpus_id in INTACT_ORDER
        }
        for probe_id in PROBE_IDS:
            corpora[probe_id] = {"by_arm": {}, "mining_census": {"failures": []}}
        gates = evaluate_gates(corpora)
        assert gates["G6_HARM_A1"]["outcome"] == Outcome.PASS.value
        assert gates["G6_HARM_A1"]["vacuous"] is False

    def test_the_a1_harm_is_confined_to_the_corpus_built_for_it(
        self, campaign: dict[str, object]
    ) -> None:
        by_corpus = campaign["gates"]["G6_HARM_A1"]["by_corpus"]
        for corpus_id in SYMMETRIC_INTACT_ORDER:
            assert by_corpus[corpus_id]["pairs_where_a1_could_fire"] == 0
            assert by_corpus[corpus_id]["decisions_changed"] == 0
        assert by_corpus[INTACT_HARM_SYNTHETIC]["correct_answers_destroyed"] == 12

    def test_the_mining_gate_now_has_intact_failures_and_reports_them(
        self, campaign: dict[str, object]
    ) -> None:
        """Part (a)'s empty yield was incidental, not structural.

        All three arms can err only by abstaining, and abstention where gold is
        determinate is not one of the four failure kinds, so the only possible
        intact failure was one A0 itself commits --- and A0 answers every
        symmetric intact pair correctly. A partially observed intact pair breaks
        both halves at once: A0 over-resolves nine of them, and none of the nine
        has a discriminating coordinate, because what is missing is a third value
        on an existing axis rather than an axis. FAIL is that finding, not a
        contradiction of it.
        """

        gate = campaign["gates"]["G5_MINING_YIELD"]
        part_a = gate["a_intact_failures"]
        assert part_a["n_failures"] == 9
        assert part_a["n_demanding_a_missing_coordinate"] == 9
        assert part_a["outcome"] == Outcome.FAIL.value
        assert gate["outcome"] == Outcome.FAIL.value
        # and it did not license the "no new coordinate" verdict, which needs PASS
        assert "mining" not in campaign["verdicts"]

    @pytest.mark.parametrize("corpus_id", SYMMETRIC_INTACT_ORDER)
    def test_the_symmetric_atlases_still_contribute_no_minable_failure(
        self, campaign: dict[str, object], corpus_id: str
    ) -> None:
        assert campaign["corpora"][corpus_id]["mining_census"]["n_failures"] == 0

    def test_every_probe_over_resolution_lacks_a_discriminating_coordinate(
        self, campaign: dict[str, object]
    ) -> None:
        part_b = campaign["gates"]["G5_MINING_YIELD"]["b_probe_over_resolutions"]
        assert part_b["n_over_resolutions"] == 48
        assert part_b["n_explained_by_an_existing_coordinate"] == 0

    def test_novelty_fails_by_construction_and_t5_is_not_discharged(
        self, campaign: dict[str, object]
    ) -> None:
        assert campaign["gates"]["G8_NOVELTY"]["outcome"] == Outcome.FAIL.value
        assert campaign["verdicts"]["t5"] == VERDICT_T5
        assert CANDIDATE_COORDINATE["is_a_new_identity_axis"] is False

    def test_the_campaign_is_a_failure_overall(self, campaign: dict[str, object]) -> None:
        assert campaign["overall_outcome"] == Outcome.FAIL.value
        assert overall_outcome(campaign["gates"]) is Outcome.FAIL

    def test_the_strict_arm_publishes_its_cost_on_every_symmetric_atlas(
        self, campaign: dict[str, object]
    ) -> None:
        """Every pair of those three has *some* coordinate absent on both sides.

        A2 abstains on an absence of either kind, so it abstains on all of them,
        and every gold there is determinate, so every abstention destroys an
        answer. The number is the cost of treating two silences as non-agreement.
        """

        for corpus_id in SYMMETRIC_INTACT_ORDER:
            harm = campaign["corpora"][corpus_id]["harm_vs_current"][ARM_STRICT]
            assert harm["decisions_changed"] == harm["n_cases"]
            assert harm["correct_answers_destroyed"] == harm["n_cases"]

    def test_the_strict_arm_costs_less_where_some_gold_is_unresolved(
        self, campaign: dict[str, object]
    ) -> None:
        """The 33-case corpus is the first on which A2's cost is a fraction.

        Its ``C_FULLY_OBSERVED`` pairs give A2 nothing to abstain over, and its
        gold-``UNRESOLVED`` pairs make an abstention correct. Both are checks that
        the harm accounting distinguishes "changed" from "destroyed" rather than
        counting every move as damage.
        """

        harm = campaign["corpora"][INTACT_HARM_SYNTHETIC]["harm_vs_current"][ARM_STRICT]
        assert harm["n_cases"] == 33
        assert harm["decisions_changed"] == 21
        assert harm["correct_answers_destroyed"] == 12

    def test_the_candidate_arms_pass_the_probe_only_by_construction(
        self, campaign: dict[str, object]
    ) -> None:
        """Recorded so the zero is never quoted as a validation."""

        for arm in (ARM_ASYMMETRIC, ARM_STRICT):
            guard = campaign["corpora"][PROBE_DERIVATION]["by_arm"][arm]["over_resolution"]
            assert guard["outcome"] == Outcome.PASS.value
        caveats = campaign["caveats"]
        assert any("by construction" in text for text in caveats)


class TestTheHarmDenominatorExists:
    """The corpus that turned G6 from a structural zero into a measurement.

    Every assertion here is a regression guard on the denominator rather than on
    the outcome. If the corpus loses its one-sided absences the gate goes back to
    ``CANNOT_CHECK`` --- an outcome that reads as clean --- so the denominator has
    to be pinned separately from the harm number.
    """

    def test_the_shipped_corpus_is_what_the_builder_emits(
        self, shipped: list[dict[str, object]]
    ) -> None:
        assert build_report(shipped)["cases_hash"] == build_report(harm_cases())["cases_hash"]

    def test_the_corpus_is_registered_as_intact_and_not_as_a_probe_parent(self) -> None:
        assert INTACT_HARM_SYNTHETIC in INTACT_ORDER
        assert INTACT_HARM_SYNTHETIC in INTACT_SOURCES
        assert PARTIALLY_OBSERVED_INTACT_ORDER == (INTACT_HARM_SYNTHETIC,)
        # Redacting a pair that already has a one-sided absence would give a probe
        # case with two, which C2 rejects and which would abort the campaign.
        assert INTACT_HARM_SYNTHETIC not in PROBE_OF

    def test_the_denominator_is_not_zero_and_reaches_every_coordinate(
        self, campaign: dict[str, object]
    ) -> None:
        census = campaign["corpora"][INTACT_HARM_SYNTHETIC]["one_sided_absence_census"]
        assert census["n_pairs"] == 33
        assert census["n_pairs_with_a_one_sided_absence"] == 27
        assert set(census["by_coordinate"]) == set(COORDINATES)

    def test_every_case_holds_its_stratum_contract(
        self, shipped: list[dict[str, object]]
    ) -> None:
        counts: dict[str, int] = {}
        for row in construction_receipts(shipped):
            contract = STRATUM_CONTRACT[str(row["stratum"])]
            assert len(list(row["one_sided_absences"])) == contract["n_one_sided_absences"]
            assert row["gold_is_determinate"] is contract["gold_is_determinate"]
            assert (
                row["compare_meaning_reproduces_gold"]
                is contract["compare_meaning_reproduces_gold"]
            )
            counts[str(row["stratum"])] = counts.get(str(row["stratum"]), 0) + 1
        assert counts == {STRATUM_H: 12, STRATUM_D: 9, STRATUM_S: 6, STRATUM_C: 6}

    def test_gold_is_not_defined_by_the_system_under_test(
        self, shipped: list[dict[str, object]]
    ) -> None:
        """The derivation rule is written out, and checked where both are defined.

        It must agree with ``compare_meaning`` on every fully observed pair --- a
        rule that did not would make the corpus measure a system ORION does not
        have --- and it must disagree on the partially observed pairs of the D
        stratum, which is the finding.
        """

        agreement = rule_agreement_on_fully_observed(shipped)
        assert agreement["agrees_everywhere"] is True
        assert agreement["completed_pairs_compared"] > 0
        disagreeing = [
            row
            for row in construction_receipts(shipped)
            if not row["compare_meaning_reproduces_gold"]
        ]
        assert {str(row["stratum"]) for row in disagreeing} == {STRATUM_D}

    def test_the_absence_reading_splits_eight_to_one_as_the_freeze_declared(
        self, shipped: list[dict[str, object]]
    ) -> None:
        census = absence_reading_census(shipped)
        assert census["every_cell_matches_the_freeze"] is True
        assert census["counts"] == {"MERGE_WARD": 8, "SEPARATION_WARD": 1}
        assert census["by_coordinate"]["modality"]["observed_reading"] == "SEPARATION_WARD"

    def test_the_builder_refuses_a_corpus_with_no_one_sided_absence(
        self, shipped: list[dict[str, object]]
    ) -> None:
        controls = [case for case in shipped if _stratum(case) == STRATUM_C]
        with pytest.raises(HarmCorpusError, match="exactly as vacuous"):
            verify(controls, construction_receipts(controls))

    def test_the_builder_refuses_a_corpus_that_could_not_show_a_harm(
        self, shipped: list[dict[str, object]]
    ) -> None:
        no_harm = [case for case in shipped if _stratum(case) != STRATUM_H]
        with pytest.raises(HarmCorpusError, match="destroy a correct answer"):
            verify(no_harm, construction_receipts(no_harm))

    def test_the_builder_refuses_a_corpus_where_every_firing_is_a_change(
        self, shipped: list[dict[str, object]]
    ) -> None:
        always = [case for case in shipped if _stratum(case) in {STRATUM_H, STRATUM_C}]
        with pytest.raises(HarmCorpusError, match="unfalsifiable"):
            verify(always, construction_receipts(always))

    def test_the_harm_preview_and_the_gate_agree(
        self, shipped: list[dict[str, object]], campaign: dict[str, object]
    ) -> None:
        preview = harm_preview(construction_receipts(shipped))
        gate = campaign["gates"]["G6_HARM_A1"]["by_corpus"][INTACT_HARM_SYNTHETIC]
        assert preview["pairs_where_it_could_fire"] == gate["pairs_where_a1_could_fire"]
        assert preview["decisions_it_would_change"] == gate["decisions_changed"]
        assert preview["correct_answers_it_would_destroy"] == gate["correct_answers_destroyed"]

    def test_the_over_resolution_guard_is_exercised_on_an_intact_corpus(
        self, campaign: dict[str, object]
    ) -> None:
        """The first intact corpus on which this guard has a denominator at all."""

        guard = campaign["corpora"][INTACT_HARM_SYNTHETIC]["by_arm"][ARM_CURRENT][
            "over_resolution"
        ]
        exercise = guard["exercises"][0]
        assert exercise["opportunities"] == 15
        assert exercise["violations"] == 9
        assert guard["outcome"] == Outcome.FAIL.value

    def test_the_false_merge_guard_still_reports_zero_opportunities_on_the_probes(
        self, campaign: dict[str, object]
    ) -> None:
        """An honest zero denominator is left honest.

        The amendment creates a denominator where one can legitimately exist. It
        does not create one here, and this pins that it did not: no probe case has
        a non-merge gold, so the false-merge guard has nothing to be exercised on
        and says so.
        """

        for probe_id in PROBE_IDS:
            guard = campaign["corpora"][probe_id]["by_arm"][ARM_CURRENT]["false_merge"]
            assert guard["outcome"] == Outcome.CANNOT_CHECK.value
            assert guard["exercises"][0]["opportunities"] == 0


def _stratum(case: dict[str, object]) -> str:
    meta = case["partial_observation"]
    assert isinstance(meta, dict)
    return str(meta["stratum"])


class TestArmsAreTotal:
    @pytest.mark.parametrize("arm", ARM_ORDER)
    def test_every_arm_decides_every_case_of_every_corpus(
        self, campaign: dict[str, object], arm: str
    ) -> None:
        for corpus_id, entry in campaign["corpora"].items():
            counts = entry["by_arm"][arm]["decision_kinds"]
            assert sum(counts.values()) == entry["n_cases"], corpus_id
