"""The partial-observation probe must find the defect in the shipped atlases.

These run against the frozen artifacts, not only a fixture. The assertions that
pin ``CANNOT_CHECK`` --- the vacuous A1 harm gate, the unmineable intact failure
set, the absent violation rate --- are the ones that must never quietly become
``PASS``: each of them is a place where a zero could be mistaken for a result.
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
from orion.study.p3.partial_observation_probe import (
    ABSENT_VALUE,
    ARM_ASYMMETRIC,
    ARM_CURRENT,
    ARM_ORDER,
    ARM_STRICT,
    CANDIDATE_COORDINATE,
    COORDINATES,
    FREEZE_TWIN,
    INTACT_ORDER,
    INTACT_SOURCES,
    PROBE_DERIVATION,
    PROBE_HELDOUT_REAL,
    PROBE_HELDOUT_SYNTHETIC,
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
    run_campaign,
    verify_against_twin,
)
from orion.study.p3_public_reference import load_jsonl

REPO_ROOT = Path(__file__).resolve().parents[4]
PROBE_IDS = (PROBE_DERIVATION, PROBE_HELDOUT_REAL, PROBE_HELDOUT_SYNTHETIC)


@pytest.fixture(scope="module")
def campaign() -> dict[str, object]:
    payload, _probe = run_campaign(REPO_ROOT)
    return payload


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

    @pytest.mark.parametrize("corpus_id", INTACT_ORDER)
    def test_over_resolution_stays_cannot_check_on_the_intact_atlases(
        self, campaign: dict[str, object], corpus_id: str
    ) -> None:
        guard = campaign["corpora"][corpus_id]["by_arm"][ARM_CURRENT]["over_resolution"]
        assert guard["outcome"] == Outcome.CANNOT_CHECK.value
        assert guard["reason"] == "NEVER_EXERCISED"
        exercise = guard["exercises"][0]
        assert exercise["opportunities"] == 0
        # None, not 0.0: an absent rate must not be readable as a clean one.
        assert exercise["violation_rate"] is None

    @pytest.mark.parametrize("corpus_id", INTACT_ORDER)
    def test_no_intact_pair_is_partially_observed(
        self, campaign: dict[str, object], corpus_id: str
    ) -> None:
        census = campaign["corpora"][corpus_id]["one_sided_absence_census"]
        assert census["n_pairs_with_a_one_sided_absence"] == 0
        assert census["by_coordinate"] == {}

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
    def test_the_a1_harm_gate_declares_itself_vacuous(self, campaign: dict[str, object]) -> None:
        gate = campaign["gates"]["G6_HARM_A1"]
        assert gate["pairs_where_a1_could_fire"] == 0
        assert gate["vacuous"] is True
        # Zero changes out of zero opportunities is not a pass.
        assert gate["outcome"] == Outcome.CANNOT_CHECK.value

    def test_the_mining_gate_cannot_check_an_empty_failure_set(
        self, campaign: dict[str, object]
    ) -> None:
        gate = campaign["gates"]["G5_MINING_YIELD"]
        part_a = gate["a_intact_failures"]
        assert part_a["n_failures"] == 0
        assert part_a["outcome"] == Outcome.CANNOT_CHECK.value
        assert gate["outcome"] == Outcome.CANNOT_CHECK.value

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

    def test_the_strict_arm_publishes_its_cost_on_every_intact_atlas(
        self, campaign: dict[str, object]
    ) -> None:
        for corpus_id in INTACT_ORDER:
            harm = campaign["corpora"][corpus_id]["harm_vs_current"][ARM_STRICT]
            assert harm["decisions_changed"] == harm["n_cases"]
            assert harm["correct_answers_destroyed"] == harm["n_cases"]

    def test_the_candidate_arms_pass_the_probe_only_by_construction(
        self, campaign: dict[str, object]
    ) -> None:
        """Recorded so the zero is never quoted as a validation."""

        for arm in (ARM_ASYMMETRIC, ARM_STRICT):
            guard = campaign["corpora"][PROBE_DERIVATION]["by_arm"][arm]["over_resolution"]
            assert guard["outcome"] == Outcome.PASS.value
        caveats = campaign["caveats"]
        assert any("by construction" in text for text in caveats)


class TestArmsAreTotal:
    @pytest.mark.parametrize("arm", ARM_ORDER)
    def test_every_arm_decides_every_case_of_every_corpus(
        self, campaign: dict[str, object], arm: str
    ) -> None:
        for corpus_id, entry in campaign["corpora"].items():
            counts = entry["by_arm"][arm]["decision_kinds"]
            assert sum(counts.values()) == entry["n_cases"], corpus_id
