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

Amendment 002 adds ``A3_decisive_absence_only``, the arm A1's measured harm points
at, and the tests for it are written the other way round. A3 destroys nothing
anywhere in this repository, and every one of those zeros is either structural or
circular, so the assertions below pin ``CANNOT_CHECK`` and pin *why*: that the one
corpus A3 can fire on derives its gold by A3's own decision rule, and that the
gate detects this and refuses the zero. The counterfactual tests show the gate can
also say ``PASS`` and ``FAIL``, and the witness test shows A3 is not literally the
corpus's gold function --- so the refusal is a judgement about coverage rather
than a tautology in either direction.
"""

from __future__ import annotations

import json
import os
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
    COORDINATE_VALUES,
    STRATUM_C,
    STRATUM_CONTRACT,
    STRATUM_D,
    STRATUM_H,
    STRATUM_S,
    HarmCorpusError,
    absence_reading_census,
    build_report,
    construction_receipts,
    gold_from_standard,
    harm_cases,
    harm_preview,
    rule_agreement_on_fully_observed,
    verify,
)
from orion.study.p3.partial_observation_probe import (
    ABSENT_VALUE,
    ARMS,
    ARM_ASYMMETRIC,
    ARM_CURRENT,
    ARM_DECISIVE,
    ARM_ORDER,
    ARM_STRICT,
    CANDIDATE_COORDINATE,
    COORDINATES,
    DECISIVENESS_RULE_MARKER,
    FREEZE_TWIN,
    INTACT_DERIVATION,
    INTACT_HARM_SYNTHETIC,
    INTACT_HELDOUT_REAL,
    INTACT_HELDOUT_SYNTHETIC,
    INTACT_ORDER,
    INTACT_RECORD_GOLD,
    INTACT_ROLE,
    INTACT_SOURCES,
    MINING_ARM_ORDER,
    PARTIALLY_OBSERVED_INTACT_ORDER,
    PROBE_DERIVATION,
    PROBE_HELDOUT_REAL,
    PROBE_HELDOUT_SYNTHETIC,
    PROBE_OF,
    SYMMETRIC_INTACT_ORDER,
    VERDICT_T5,
    FreezeViolation,
    admissible_completions,
    arm_decisive_absence_only,
    build_probe,
    construction_precondition,
    arm_disagreement,
    discriminating_coordinates,
    evaluate_gates,
    exact_agreement_where_the_arm_can_fire,
    frozen_digest,
    main,
    observed,
    one_sided_absence_census,
    overall_outcome,
    redactable_coordinates,
    run_campaign,
    score_pairs,
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


#: What ``A0_orion_current`` gets wrong on each intact corpus, in the two kinds a
#: merge guard can express. Zero on the four corpora frozen before amendment 003.
#: On ``INTACT_RECORD_GOLD`` gold survives the extraction loss, so the merge-ward
#: reading of a one-sided absence produces eight false merges on records that
#: differ and the separation-ward reading of ``modality`` produces one false split
#: on records that agree.
A0_FAILURE_CENSUS: dict[str, dict[str, int]] = {
    INTACT_DERIVATION: {"FALSE_MERGE": 0, "FALSE_SPLIT": 0},
    INTACT_HELDOUT_REAL: {"FALSE_MERGE": 0, "FALSE_SPLIT": 0},
    INTACT_HELDOUT_SYNTHETIC: {"FALSE_MERGE": 0, "FALSE_SPLIT": 0},
    INTACT_HARM_SYNTHETIC: {"FALSE_MERGE": 0, "FALSE_SPLIT": 0},
    INTACT_RECORD_GOLD: {"FALSE_MERGE": 8, "FALSE_SPLIT": 1},
}

#: A harm row with every count at zero, i.e. an arm that touched nothing.
_NO_HARM: dict[str, int] = {
    "decisions_changed": 0,
    "correct_answers_destroyed": 0,
    "wrong_answers_repaired": 0,
    "pairs_a0_answers_correctly": 0,
    "pairs_a0_answers_correctly_with_a_one_sided_absence": 0,
}


def _fabricated_corpora(
    *,
    a1: dict[str, int] | None = None,
    a3: dict[str, int] | None = None,
    gold_rule: str = "identity:adjudicated-by-people",
    a3_reproduces_gold: bool = False,
    a3_reproduces_gold_where_it_fires: bool = False,
    a3_denominator: int = 12,
) -> dict[str, object]:
    """A corpora payload with the shape ``evaluate_gates`` reads and nothing real in it.

    Every gate here reports a negative on the shipped corpora. A gate that can
    only report a negative is not a gate, so each of them is also run against a
    fabricated world in which the positive is the right answer. The fabrication
    is obvious and local; it is never fed to a claim.
    """

    a1_row = {**_NO_HARM, **(a1 or {})}
    a3_row = {
        **_NO_HARM,
        "pairs_a0_answers_correctly_with_a_one_sided_absence": a3_denominator,
        **(a3 or {}),
    }

    def corpus(kind: str) -> dict[str, object]:
        return {
            "kind": kind,
            "n_cases": 33,
            "one_sided_absence_census": {"n_pairs_with_a_one_sided_absence": 27},
            "gold_provenance": {
                "declared_rules": [gold_rule],
                "gold_derived_by_completion_invariance": DECISIVENESS_RULE_MARKER in gold_rule,
            },
            "harm_vs_current": {
                ARM_ASYMMETRIC: a1_row,
                ARM_STRICT: dict(_NO_HARM),
                ARM_DECISIVE: a3_row,
            },
            "exact_agreement_with_gold": {
                arm: {
                    "reproduces_gold_on_every_case": (
                        arm == ARM_DECISIVE and a3_reproduces_gold
                    )
                }
                for arm in ARM_ORDER
            },
            "exact_agreement_where_the_arm_can_fire": {
                arm: {
                    "n_pairs_with_a_one_sided_absence": 27,
                    "reproduces_gold_on_every_pair_it_can_fire_on": (
                        arm == ARM_DECISIVE and a3_reproduces_gold_where_it_fires
                    ),
                }
                for arm in ARM_ORDER
            },
            "mining_census": {"failures": []},
            "mining_census_a3": {"failures": []},
            "arm_disagreement": {
                arm: {"n_differing": 0}
                for arm in (ARM_CURRENT, ARM_ASYMMETRIC, ARM_STRICT)
            },
            "by_arm": {},
        }

    corpora: dict[str, object] = {corpus_id: corpus("INTACT") for corpus_id in INTACT_ORDER}
    for probe_id in PROBE_IDS:
        corpora[probe_id] = corpus("PROBE")
    return corpora


#: One fully observed projection's worth of coordinate values, so a test can
#: silence exactly one of them and know every other is stated on both sides.
_FULLY_OBSERVED: dict[str, object] = {
    "referent_ids": ("probe:referent:0",),
    "construct_ids": ("probe:construct:0",),
    "measurement_ids": ("probe:measurement:0",),
    "temporal_context_ids": ("probe:temporal:0",),
    "assumption_ids": ("probe:assumption:0",),
    "attribution_id": "probe:attribution:0",
    "discourse_relation": "probe:discourse:0",
    "polarity": Polarity.POSITIVE,
    "modality": Modality.ASSERTED,
}


def _fully_observed(**overrides: object) -> ScientificMeaningProjection:
    return _projection(**{**_FULLY_OBSERVED, **overrides})


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
            env={
                "PYTHONPATH": "src",
                "PATH": "/usr/bin:/bin",
                # The interpreter binary needs its own runtime loader path.
                # A Python installed outside a default prefix (an HPC module,
                # pyenv, some conda layouts) keeps libpython there, and
                # scrubbing this kills the child with exit 127 before Python
                # starts. Carrying it does not weaken the isolation this env
                # is for: it is the loader's path, not an import path.
                **{
                    key: value
                    for key, value in os.environ.items()
                    if key in ("LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH")
                },
            },
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
    def test_the_current_arms_false_merge_census_is_what_it_is_declared_to_be(
        self, campaign: dict[str, object], corpus_id: str
    ) -> None:
        """Zero on every corpus but the one added by amendment 003, and not zero there.

        The published finding --- ORION commits zero false merges and zero false
        splits on every P3 atlas --- is about those atlases, and the four rows of
        zeroes below are it, unchanged. ``INTACT_RECORD_GOLD`` is not one of them:
        its gold is the relation between two source records, so it stays
        determinate on a pair whose deciding coordinate the extraction dropped,
        and ``compare_meaning``'s reading of that silence is then a false merge
        rather than an over-resolution. The count is recorded here rather than
        scoped away, and the eight-to-one split is the absence-reading table
        restated.
        """

        entry = campaign["corpora"][corpus_id]["by_arm"][ARM_CURRENT]
        kinds = entry["decision_kinds"]
        expected = A0_FAILURE_CENSUS[corpus_id]
        assert kinds["FALSE_MERGE"] == expected["FALSE_MERGE"]
        assert kinds["FALSE_SPLIT"] == expected["FALSE_SPLIT"]
        assert entry["false_merge"]["outcome"] == (
            Outcome.PASS.value if not expected["FALSE_MERGE"] else Outcome.FAIL.value
        )

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
        # The finding amendment 001 reported, pinned where it is true: on the
        # corpus built for it. The gate's totals are sums over the intact corpora
        # and amendment 003 adds one, so they move; the row does not.
        row = gate["by_corpus"][INTACT_HARM_SYNTHETIC]
        assert row["pairs_where_a1_could_fire"] == 27
        assert row["decisions_changed"] == 21
        assert row["correct_answers_destroyed"] == 12
        assert gate["decisions_changed"] == 47
        assert gate["correct_answers_destroyed"] == 29
        assert gate["pairs_where_a1_could_fire"] == 53

    def test_the_harm_gate_would_report_a_pass_if_a1_left_the_corpus_alone(self) -> None:
        """The gate is not wired to fail whatever happens.

        Same code path, same denominator, an arm that changes nothing: the gate
        reads PASS. Without this, ``FAIL`` above would be consistent with a gate
        that cannot say anything else.
        """

        gates = evaluate_gates(_fabricated_corpora())
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

        Amendment 003 adds nine more, on INTACT_RECORD_GOLD, of a different kind:
        gold there survives the extraction loss, so the same merge-ward reading
        that over-resolves on the harm corpus is a false merge here, plus one
        false split from the separation-ward reading of ``modality``. Eighteen
        failures, none with a discriminating coordinate, and the finding is the
        same one twice over.
        """

        gate = campaign["gates"]["G5_MINING_YIELD"]
        part_a = gate["a_intact_failures"]
        assert part_a["n_failures"] == 18
        assert part_a["n_demanding_a_missing_coordinate"] == 18
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
        assert INTACT_HARM_SYNTHETIC in PARTIALLY_OBSERVED_INTACT_ORDER
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


# --------------------------------------------------------------------------
# Amendment 002: the decisiveness-aware arm
# --------------------------------------------------------------------------


def _richer_completions(coordinate: str, mirror: object) -> tuple[object, ...]:
    """More values than the arm's two witnesses, for the completeness check."""

    absent = ABSENT_VALUE[coordinate]
    if isinstance(absent, tuple):
        assert isinstance(mirror, tuple)
        return (mirror, ("z:1",), ("z:2",), mirror + ("z:3",), ("z:1", "z:2"))
    if isinstance(absent, (Polarity, Modality)):
        return tuple(value for value in type(absent) if value is not absent)
    return (mirror, "z:1", "z:2")


class TestTheDecisiveArmDecidesOnDecisiveness:
    """``A3_decisive_absence_only`` abstains on the absence that moves the answer.

    A1's twelve destroyed answers are a design defect: it abstains on the
    *presence* of an absence. These pin that the new arm abstains on the thing
    that matters instead, on pairs written here rather than on a corpus, so the
    behaviour is checked against the rule and not against a gold file.
    """

    def test_it_answers_where_a_higher_coordinate_already_decides(self) -> None:
        left = _fully_observed(measurement_ids=ABSENT_VALUE["measurement_ids"])
        right = _fully_observed(referent_ids=("probe:referent:1",))
        assert arm_decisive_absence_only(left, right) is MeaningRelation.DISTINCT_REFERENT
        # A1 throws that answer away purely because something is missing.
        assert ARMS[ARM_ASYMMETRIC](left, right) is MeaningRelation.UNRESOLVED
        assert ARMS[ARM_CURRENT](left, right) is MeaningRelation.DISTINCT_REFERENT

    def test_it_abstains_where_the_absence_is_what_the_answer_turns_on(self) -> None:
        left = _fully_observed(measurement_ids=ABSENT_VALUE["measurement_ids"])
        right = _fully_observed()
        assert arm_decisive_absence_only(left, right) is MeaningRelation.UNRESOLVED
        # and the current rule does not: it reads the silence as agreement.
        assert ARMS[ARM_CURRENT](left, right) is MeaningRelation.COMPATIBLE

    def test_it_is_the_current_rule_exactly_when_nothing_is_one_sided(self) -> None:
        left = _fully_observed()
        right = _fully_observed(construct_ids=("probe:construct:9",))
        assert arm_decisive_absence_only(left, right) is compare_meaning(left, right).relation
        both_silent = (
            _fully_observed(assumption_ids=()),
            _fully_observed(assumption_ids=()),
        )
        assert (
            arm_decisive_absence_only(*both_silent)
            is compare_meaning(*both_silent).relation
        )

    @pytest.mark.parametrize("coordinate", COORDINATES)
    def test_two_witnesses_enumerate_every_relation_a_richer_table_reaches(
        self, coordinate: str
    ) -> None:
        """The arm's completion set is complete, not a sample.

        Every branch of ``compare_meaning`` tests an absent coordinate only for
        equality with the mirror value, so two witnesses --- agree, differ ---
        reach every relation any larger set of admissible values reaches. If that
        stopped being true the arm would be abstaining or answering on the
        strength of which values someone happened to list, which is the failure
        mode the whole circularity section is about.
        """

        for other in (_fully_observed(), _fully_observed(referent_ids=("probe:referent:1",))):
            left = _fully_observed(**{coordinate: ABSENT_VALUE[coordinate]})
            mirror = getattr(other, coordinate)
            witnessed = {
                compare_meaning(one, two).relation
                for one, two in admissible_completions(left, other)
            }
            richer = {
                compare_meaning(replace(left, **{coordinate: value}), other).relation
                for value in _richer_completions(coordinate, mirror)
            }
            assert witnessed == richer, (coordinate, witnessed, richer)


class TestTheDecisiveArmIsNotTheHarmCorpusGoldFunction:
    """The circularity is about one corpus's coverage, not about A3 being gold.

    If A3 and ``gold_from_standard`` were the same function, ``G9_HARM_A3``
    reporting ``CANNOT_CHECK`` would be a tautology rather than a finding about
    the evidence available. They are not the same function, and this exhibits a
    pair on which they disagree.
    """

    def test_they_disagree_on_a_pair_outside_the_corpus_vocabulary(self) -> None:
        base = {name: values[0] for name, values in COORDINATE_VALUES.items()}
        silent = _projection(**{**base, "referent_ids": ABSENT_VALUE["referent_ids"]})
        stated = _projection(**{**base, "referent_ids": ("outside:the:frozen:vocabulary",)})

        # gold_from_standard completes the silence only from its own table, and
        # every value in that table differs from what the other side states, so
        # it calls the pair determinate.
        assert gold_from_standard(silent, stated) is MeaningRelation.DISTINCT_REFERENT
        # A3 completes it from the pair, so "the silence hid an agreement" is one
        # of the worlds it has to rule out, and it cannot.
        assert arm_decisive_absence_only(silent, stated) is MeaningRelation.UNRESOLVED

    def test_a3_answers_a_pair_the_corpus_rule_refuses_to_answer(self) -> None:
        """Different domains, not only different values.

        ``gold_from_standard`` is defined on at most one one-sided absence and
        raises otherwise; A3 takes the product.
        """

        left = _fully_observed(
            measurement_ids=ABSENT_VALUE["measurement_ids"],
            attribution_id=ABSENT_VALUE["attribution_id"],
        )
        right = _fully_observed(referent_ids=("probe:referent:1",))
        with pytest.raises(ValueError, match="at most one one-sided absence"):
            gold_from_standard(left, right)
        assert arm_decisive_absence_only(left, right) is MeaningRelation.DISTINCT_REFERENT
        assert len(list(admissible_completions(left, right))) == 4

    def test_the_runner_does_not_import_the_corpus_builder(self) -> None:
        """The arm cannot be reading the corpus's rule, because it cannot see it.

        The dependency runs the other way: the builder imports the probe's
        absent-value table and checks it against its own. Checked over the parsed
        imports rather than over the text, because the module's prose names the
        builder repeatedly and a substring check would pass or fail on prose.
        """

        import ast

        tree = ast.parse(
            (REPO_ROOT / "src/orion/study/p3/partial_observation_probe.py").read_text(
                encoding="utf-8"
            )
        )
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
                imported.update(f"{node.module or ''}.{alias.name}" for alias in node.names)
        assert not any("partial_observation_harm_build" in name for name in imported), imported


class TestTheDecisivenessGateRefusesTheZeroItCannotEarn:
    def test_a3_destroys_nine_correct_answers_on_gold_it_did_not_write(
        self, campaign: dict[str, object]
    ) -> None:
        """Amendment 003's measurement, and the reason G9 is no longer a refusal.

        Under amendment 002 this read 0 destroyed and 9 repaired, and the gate
        refused to call either a result because the only corpus A3 could fire on
        derived its gold by A3's own criterion. INTACT_RECORD_GOLD derives its
        gold from source records instead, and over it A3 destroys.
        """

        gate = campaign["gates"]["G9_HARM_A3"]
        assert gate["correct_answers_destroyed"] == 9
        assert gate["decisions_changed"] == 27
        assert gate["wrong_answers_repaired"] == 9
        assert gate["by_corpus"][INTACT_RECORD_GOLD]["correct_answers_destroyed"] == 9
        assert gate["by_corpus"][INTACT_HARM_SYNTHETIC]["correct_answers_destroyed"] == 0

    def test_the_gate_fails_and_the_failure_rests_on_independent_gold(
        self, campaign: dict[str, object]
    ) -> None:
        """A FAIL is only worth having if the corpus that produced it counts.

        The gate reports the harm count before it reads the evidence block, so a
        destroyed answer on a circular corpus would fail it too. This pins that
        the destruction is on the corpus whose gold is *not* derived by A3's
        criterion, which is what makes the FAIL a finding rather than an artefact.
        """

        gate = campaign["gates"]["G9_HARM_A3"]
        assert gate["outcome"] == Outcome.FAIL.value
        assert gate["corpora_supplying_independent_evidence"] == [INTACT_RECORD_GOLD]
        assert gate["corpora_where_a3_destroyed_a_correct_answer"] == [INTACT_RECORD_GOLD]
        assert gate[
            "corpora_where_a3_destroyed_a_correct_answer_on_independent_gold"
        ] == [INTACT_RECORD_GOLD]
        assert gate["vacuous_or_circular"] is False

    def test_the_harm_corpus_is_withheld_for_naming_a3s_own_criterion(
        self, campaign: dict[str, object]
    ) -> None:
        """The circularity is detected from the corpus, not hard-coded here.

        This is the assertion that fails if A3's number is ever read off its own
        definition: the corpus declares the derivation rule, the runner matches
        the marker, and the evidence is withheld on that basis.
        """

        evidence = campaign["gates"]["G9_HARM_A3"]["by_corpus"][INTACT_HARM_SYNTHETIC][
            "evidence"
        ]
        assert evidence["supplies_independent_evidence"] is False
        assert "GOLD_DERIVED_BY_THE_CRITERION_THE_ARM_DECIDES_BY" in evidence["withheld_because"]
        assert evidence["gold_derived_by_completion_invariance"] is True
        assert any(
            DECISIVENESS_RULE_MARKER in rule for rule in evidence["declared_gold_rules"]
        )
        assert evidence["harm_denominator"] == 18

    def test_a3_reproduces_that_corpus_gold_on_every_case(
        self, campaign: dict[str, object]
    ) -> None:
        """33 of 33, which is the definition restated and not a score.

        Pinned so the number exists on the record and so the reason the gate
        withholds it is checkable rather than asserted.
        """

        agreement = campaign["corpora"][INTACT_HARM_SYNTHETIC]["exact_agreement_with_gold"][
            ARM_DECISIVE
        ]
        assert agreement["n_cases"] == 33
        assert agreement["n_exact"] == 33
        assert agreement["reproduces_gold_on_every_case"] is True

    @pytest.mark.parametrize("corpus_id", SYMMETRIC_INTACT_ORDER)
    def test_the_symmetric_atlases_give_a3_nothing_to_fire_on(
        self, campaign: dict[str, object], corpus_id: str
    ) -> None:
        """The same structural zero G6 carried before amendment 001."""

        row = campaign["gates"]["G9_HARM_A3"]["by_corpus"][corpus_id]
        assert row["pairs_where_a3_could_fire"] == 0
        assert row["decisions_changed"] == 0
        assert row["evidence"]["harm_denominator"] == 0
        assert "NO_HARM_DENOMINATOR" in row["evidence"]["withheld_because"]

    def test_the_gate_would_pass_on_a_corpus_that_could_have_failed_it(self) -> None:
        gates = evaluate_gates(_fabricated_corpora())
        assert gates["G9_HARM_A3"]["outcome"] == Outcome.PASS.value
        assert gates["G9_HARM_A3"]["corpora_supplying_independent_evidence"] == sorted(
            INTACT_ORDER
        )

    def test_the_gate_fails_when_the_arm_destroys_an_answer(self) -> None:
        gates = evaluate_gates(
            _fabricated_corpora(a3={"decisions_changed": 3, "correct_answers_destroyed": 1})
        )
        assert gates["G9_HARM_A3"]["outcome"] == Outcome.FAIL.value
        assert gates["G9_HARM_A3"]["correct_answers_destroyed"] == len(INTACT_ORDER)

    def test_the_gate_refuses_a_pass_when_gold_agrees_with_the_arm_wherever_it_fires(
        self,
    ) -> None:
        """The extensional circularity check added by amendment 003.

        Everything that produced ``PASS`` above is held fixed --- innocent
        derivation rule, real denominator, no whole-corpus perfect score --- and
        the corpus's gold is made to agree with A3 on every pair A3 can fire on.
        That is the same circularity reached by construction instead of by
        declaration, and the gate declines to certify. It is the assertion that
        fails if INTACT_RECORD_GOLD is ever edited into a corpus A3 gets right.
        """

        gates = evaluate_gates(_fabricated_corpora(a3_reproduces_gold_where_it_fires=True))
        assert gates["G9_HARM_A3"]["outcome"] == Outcome.CANNOT_CHECK.value
        assert gates["G9_HARM_A3"]["corpora_supplying_independent_evidence"] == []

    def test_the_gate_refuses_a_pass_when_the_gold_rule_names_a3s_criterion(self) -> None:
        """Same zero, same denominator, a gold rule derived by A3's own criterion.

        This is the non-circularity test proper. Everything that produced ``PASS``
        two tests up is held fixed except the corpus's declared derivation rule,
        and the gate declines to certify.
        """

        gates = evaluate_gates(
            _fabricated_corpora(
                gold_rule="identity:observed-coordinate-precedence-with-completion-invariance"
            )
        )
        assert gates["G9_HARM_A3"]["outcome"] == Outcome.CANNOT_CHECK.value
        assert gates["G9_HARM_A3"]["corpora_supplying_independent_evidence"] == []

    def test_the_gate_refuses_a_pass_when_the_arm_reproduces_gold_everywhere(self) -> None:
        """A perfect score makes zero harm arithmetic rather than a comparison."""

        gates = evaluate_gates(_fabricated_corpora(a3_reproduces_gold=True))
        assert gates["G9_HARM_A3"]["outcome"] == Outcome.CANNOT_CHECK.value

    def test_the_gate_refuses_a_pass_without_a_harm_denominator(self) -> None:
        gates = evaluate_gates(_fabricated_corpora(a3_denominator=0))
        assert gates["G9_HARM_A3"]["outcome"] == Outcome.CANNOT_CHECK.value


class TestTheBenefitGateSeparatesNothing:
    def test_a3_keeps_abstaining_where_the_probe_gold_says_it_should(
        self, campaign: dict[str, object]
    ) -> None:
        gate = campaign["gates"]["G10_BENEFIT_A3"]
        assert gate["outcome"] == Outcome.PASS.value
        for probe_id in PROBE_IDS:
            rates = gate["by_probe"][probe_id]["violation_rate_by_arm"]
            assert rates[ARM_DECISIVE] == 0.0
            assert rates[ARM_CURRENT] == 1.0

    def test_and_that_zero_is_shared_with_the_arms_it_is_meant_to_beat(
        self, campaign: dict[str, object]
    ) -> None:
        """Probe gold is UNRESOLVED on all 48, so abstaining scores perfectly.

        Recorded so A3's probe number is never quoted as a superiority over A1.
        """

        gate = campaign["gates"]["G10_BENEFIT_A3"]
        for probe_id in PROBE_IDS:
            rates = gate["by_probe"][probe_id]["violation_rate_by_arm"]
            assert rates[ARM_ASYMMETRIC] == 0.0
            assert rates[ARM_STRICT] == 0.0
            assert gate["by_probe"][probe_id]["disagreement_with_a1"]["n_differing"] == 0

    def test_the_separation_is_now_visible_on_gold_neither_arm_wrote(
        self, campaign: dict[str, object]
    ) -> None:
        """Under amendment 002 the second list was empty. It is not now.

        The first list is every corpus on which A1 and A3 make different
        decisions; the second is the subset whose gold is not A3's own criterion,
        by declaration or in effect. INTACT_RECORD_GOLD is in both, and on it A3
        is right on all 8 pairs where they part.
        """

        gate = campaign["gates"]["G10_BENEFIT_A3"]
        assert gate["corpora_separating_a3_from_a1"] == [
            INTACT_HARM_SYNTHETIC,
            INTACT_RECORD_GOLD,
        ]
        assert gate[
            "corpora_separating_a3_from_a1_on_gold_not_derived_by_the_criterion_a3_uses"
        ] == [INTACT_RECORD_GOLD]
        row = gate["separation_from_a1_on_independent_gold"][INTACT_RECORD_GOLD]
        assert row["n_differing"] == 8
        assert row["n_differing_where_this_arm_is_right"] == 8
        assert row["n_differing_where_the_other_arm_is_right"] == 0

    def test_where_they_do_differ_a3_is_the_one_that_is_right(
        self, campaign: dict[str, object]
    ) -> None:
        """Reported for completeness, and reported as circular.

        The twelve pairs A1 destroys are exactly the ones A3 spares, and that is
        an identity on this corpus rather than a comparison: the corpus's gold
        calls them determinate by the criterion A3 decides by.
        """

        row = campaign["corpora"][INTACT_HARM_SYNTHETIC]["arm_disagreement"][ARM_ASYMMETRIC]
        assert row["n_differing"] == 12
        assert row["n_differing_where_this_arm_is_right"] == 12
        assert row["n_differing_where_the_other_arm_is_right"] == 0
        # exactly the twelve G6 records A1 as destroying, and no others: on the
        # nine decisive-absence pairs and the six incomparable ones both arms
        # abstain, so the only place they part is the stratum whose gold this
        # corpus derives by A3's own criterion.
        assert campaign["gates"]["G6_HARM_A1"]["by_corpus"][INTACT_HARM_SYNTHETIC][
            "correct_answers_destroyed"
        ] == row["n_differing"]


class TestAmendmentTwoMovedNoPublishedNumber:
    def test_the_a1_harm_finding_still_reproduces(self, campaign: dict[str, object]) -> None:
        """27 / 21 / 12 on the corpus it is a finding about, unchanged.

        The finding G6 reports is why A3 exists. Adding A3 must not disturb it,
        and neither may adding a corpus. Amendment 003 adds one, so the gate's
        totals are larger; the row the finding lives in is byte-identical, and
        that is where it is pinned.
        """

        gate = campaign["gates"]["G6_HARM_A1"]
        assert gate["outcome"] == Outcome.FAIL.value
        row = gate["by_corpus"][INTACT_HARM_SYNTHETIC]
        assert row["pairs_where_a1_could_fire"] == 27
        assert row["decisions_changed"] == 21
        assert row["correct_answers_destroyed"] == 12

    def test_g6_still_names_a1_and_was_not_repointed(self) -> None:
        """A failing gate may not be repaired by changing its subject."""

        from orion.study.p3.partial_observation_probe import GATES

        assert GATES["G6_HARM_A1"]["statement"].startswith("A1_observedness_asymmetric")
        assert ARM_DECISIVE not in GATES["G6_HARM_A1"]["statement"]
        assert GATES["G9_HARM_A3"]["statement"].startswith("A3_decisive_absence_only")
        assert GATES["G6_HARM_A1"]["blocking"] is True

    def test_the_new_arm_contributes_no_minable_failure_anywhere(
        self, campaign: dict[str, object]
    ) -> None:
        """And the mining gate says so in a field rather than by omission."""

        for corpus_id in (*INTACT_ORDER, *PROBE_IDS):
            assert campaign["corpora"][corpus_id]["mining_census_a3"]["n_failures"] == 0
        reported = campaign["gates"]["G5_MINING_YIELD"]["c_arm_added_by_amendment_002"]
        assert reported["arm_id"] == ARM_DECISIVE
        assert reported["n_failures"] == 0
        assert reported["counted_towards_the_outcome"] is False

    def test_the_mining_census_is_scoped_to_the_arms_it_was_frozen_over(
        self, campaign: dict[str, object]
    ) -> None:
        gate = campaign["gates"]["G5_MINING_YIELD"]
        assert gate["census_arms"] == list(MINING_ARM_ORDER)
        assert ARM_DECISIVE not in gate["census_arms"]
        assert gate["a_intact_failures"]["n_failures"] == 18
        assert gate["b_probe_over_resolutions"]["n_over_resolutions"] == 48
        assert gate["outcome"] == Outcome.FAIL.value

    def test_the_strict_arm_cost_is_unchanged(self, campaign: dict[str, object]) -> None:
        harm = campaign["gates"]["G7_COST_A2"]["by_corpus"][INTACT_HARM_SYNTHETIC]
        assert harm["decisions_changed"] == 21
        assert harm["correct_answers_destroyed"] == 12

    def test_the_campaign_is_still_a_failure_and_t5_is_still_not_discharged(
        self, campaign: dict[str, object]
    ) -> None:
        assert campaign["overall_outcome"] == Outcome.FAIL.value
        assert campaign["verdicts"]["t5"] == VERDICT_T5


class TestAmendmentThreeGivesTheDecisivenessGateADenominator:
    """The corpus that turned G9 from a refusal into a measurement.

    Every assertion here is a regression guard on the *denominator* and on its
    independence, not on the outcome. A corpus that quietly lost its one-sided
    absences, or whose gold quietly drifted into A3's criterion, would put the
    gate back to ``CANNOT_CHECK`` --- an outcome that reads as clean --- so the
    things that make the FAIL worth having are pinned separately from the FAIL.
    """

    def test_the_corpus_is_registered_as_intact_with_a_declared_role(self) -> None:
        assert INTACT_RECORD_GOLD in INTACT_ORDER
        assert INTACT_RECORD_GOLD in INTACT_SOURCES
        assert INTACT_RECORD_GOLD in PARTIALLY_OBSERVED_INTACT_ORDER
        assert INTACT_ROLE[INTACT_RECORD_GOLD] == (
            "HARM_MEASUREMENT_ON_GOLD_ANCHORED_OUTSIDE_THE_PROJECTIONS"
        )
        # It has one-sided absences of its own, so redacting one of its pairs
        # would give a probe case with two, which C2 rejects.
        assert INTACT_RECORD_GOLD not in PROBE_OF

    def test_every_intact_corpus_declares_a_role_and_the_old_ones_keep_theirs(
        self, campaign: dict[str, object]
    ) -> None:
        sources = campaign["sources"]
        assert set(sources) == set(INTACT_ORDER)
        for corpus_id in SYMMETRIC_INTACT_ORDER:
            assert sources[corpus_id]["role"] == "HARM_AND_PROBE_PARENT"
        assert sources[INTACT_HARM_SYNTHETIC]["role"] == "HARM_MEASUREMENT_ONLY"
        assert sources[INTACT_RECORD_GOLD]["n_cases"] == 36

    def test_the_denominator_is_not_zero_and_reaches_every_coordinate(
        self, campaign: dict[str, object]
    ) -> None:
        census = campaign["corpora"][INTACT_RECORD_GOLD]["one_sided_absence_census"]
        assert census["n_pairs"] == 36
        assert census["n_pairs_with_a_one_sided_absence"] == 26
        assert set(census["by_coordinate"]) == set(COORDINATES)
        row = campaign["gates"]["G9_HARM_A3"]["by_corpus"][INTACT_RECORD_GOLD]
        assert row["pairs_where_a3_could_fire"] == 26
        assert row["evidence"]["harm_denominator"] == 17

    def test_its_gold_is_not_derived_by_the_criterion_a3_decides_by(
        self, campaign: dict[str, object]
    ) -> None:
        """Both the nominal check and the extensional one, on the shipped corpus."""

        provenance = campaign["corpora"][INTACT_RECORD_GOLD]["gold_provenance"]
        assert provenance["declared_rules"] == ["identity:frozen-source-record-relation"]
        assert provenance["gold_derived_by_completion_invariance"] is False
        assert provenance["rules_naming_completion_invariance"] == []
        assert provenance["n_cases_declaring_a_rule"] == 36
        evidence = campaign["gates"]["G9_HARM_A3"]["by_corpus"][INTACT_RECORD_GOLD][
            "evidence"
        ]
        assert evidence["arm_reproduces_gold_on_every_pair_it_can_fire_on"] is False
        assert evidence["arm_reproduces_gold_on_every_case"] is False
        assert evidence["supplies_independent_evidence"] is True
        assert evidence["withheld_because"] == []

    def test_the_circular_corpus_is_still_withheld_and_now_for_a_third_reason(
        self, campaign: dict[str, object]
    ) -> None:
        """Adding an independent corpus must not soften the check on the other one."""

        evidence = campaign["gates"]["G9_HARM_A3"]["by_corpus"][INTACT_HARM_SYNTHETIC][
            "evidence"
        ]
        assert evidence["supplies_independent_evidence"] is False
        assert evidence["withheld_because"] == [
            "GOLD_DERIVED_BY_THE_CRITERION_THE_ARM_DECIDES_BY",
            "GOLD_COINCIDES_WITH_THE_ARM_WHEREVER_THE_ARM_CAN_FIRE",
            "ARM_REPRODUCES_GOLD_ON_EVERY_CASE",
        ]

    @pytest.mark.parametrize("corpus_id", SYMMETRIC_INTACT_ORDER)
    def test_the_extensional_check_does_not_fire_vacuously(
        self, campaign: dict[str, object], corpus_id: str
    ) -> None:
        """A corpus with no partially observed pair is not "circular" for having none.

        It is withheld for having no denominator, which is a different and honest
        reason. A vacuous truth reported as a circularity would be the same
        substitution one layer up.
        """

        evidence = campaign["gates"]["G9_HARM_A3"]["by_corpus"][corpus_id]["evidence"]
        assert evidence["n_pairs_the_arm_can_fire_on"] == 0
        assert evidence["arm_reproduces_gold_on_every_pair_it_can_fire_on"] is False
        assert "NO_HARM_DENOMINATOR" in evidence["withheld_because"]
        assert (
            "GOLD_COINCIDES_WITH_THE_ARM_WHEREVER_THE_ARM_CAN_FIRE"
            not in evidence["withheld_because"]
        )

    def test_a3_is_strictly_better_than_a1_here_and_still_not_safe(
        self, campaign: dict[str, object]
    ) -> None:
        """The two numbers that have to be read together.

        A3 spares the eight pairs whose absence could not have changed the answer,
        which A1 destroys. It still destroys the nine whose absence could have.
        The first is the benefit A3 was built for; the second is why G9 fails.
        """

        a1 = campaign["gates"]["G6_HARM_A1"]["by_corpus"][INTACT_RECORD_GOLD]
        a3 = campaign["gates"]["G9_HARM_A3"]["by_corpus"][INTACT_RECORD_GOLD]
        assert a1["pairs_a0_answers_correctly_with_a_one_sided_absence"] == 17
        assert a3["pairs_a0_answers_correctly_with_a_one_sided_absence"] == 17
        assert a1["correct_answers_destroyed"] == 17
        assert a3["correct_answers_destroyed"] == 9
        assert a3["wrong_answers_repaired"] == 0

    def test_editing_the_corpus_into_circularity_cannot_produce_a_pass(
        self, shipped_record_gold: list[dict[str, object]]
    ) -> None:
        """The load-bearing guard, run on the corpus as it actually ships.

        The edit that would make G9 look clean is to delete the strata where the
        record-anchored gold and A3 disagree, keeping only the pairs A3 gets
        right. The gate reads the file, not the builder, so it has to catch that
        on its own: the surviving corpus is withheld for coinciding with A3
        wherever A3 can fire, the gate finds no corpus supplying independent
        evidence, and it returns ``CANNOT_CHECK`` rather than ``PASS``.
        """

        kept = [
            case
            for case in shipped_record_gold
            if str(_record_gold_stratum(case)).startswith(("LU_", "NL_"))
        ]
        assert 0 < len(kept) < len(shipped_record_gold)
        corpora = _fabricated_corpora()
        corpora[INTACT_RECORD_GOLD] = _record_gold_entry(kept)
        gates = evaluate_gates(corpora)
        evidence = gates["G9_HARM_A3"]["by_corpus"][INTACT_RECORD_GOLD]["evidence"]
        assert (
            "GOLD_COINCIDES_WITH_THE_ARM_WHEREVER_THE_ARM_CAN_FIRE"
            in evidence["withheld_because"]
        )
        assert INTACT_RECORD_GOLD not in gates["G9_HARM_A3"][
            "corpora_supplying_independent_evidence"
        ]
        assert (
            INTACT_RECORD_GOLD
            not in gates["G10_BENEFIT_A3"][
                "corpora_separating_a3_from_a1_on_gold_not_derived_by_the_criterion_a3_uses"
            ]
        )

    def test_the_earlier_freeze_records_still_carry_their_own_digests(self) -> None:
        """Each amendment is a separate record; the ones it amends are untouched.

        Amendment 004 adds a fifth record and repoints ``FREEZE_TWIN`` at it. The
        four digests below are the ones this test has always pinned plus
        amendment 003's, and the runner binds to whichever amendment is in force
        --- currently 004, which adds no arm, no corpus and no gate.
        """

        from orion.study.p3.partial_observation_probe import (
            AMENDMENT_002_TWIN,
            AMENDMENT_003_TWIN,
            AMENDMENT_004_TWIN,
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
        assert FREEZE_TWIN == AMENDMENT_004_TWIN
        assert frozen_digest() not in set(recorded.values())


@pytest.fixture(scope="module")
def shipped_record_gold() -> list[dict[str, object]]:
    return load_jsonl(REPO_ROOT / INTACT_SOURCES[INTACT_RECORD_GOLD])


def _record_gold_stratum(case: dict[str, object]) -> str:
    meta = case["partial_observation_record_gold"]
    assert isinstance(meta, dict)
    return str(meta["stratum"])


def _record_gold_entry(cases: list[dict[str, object]]) -> dict[str, object]:
    """One corpus payload of the shape ``evaluate_gates`` reads, scored for real."""

    from orion.study.p3.partial_observation_probe import (
        exact_agreement_with_gold,
        gold_provenance,
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
        "kind": "INTACT",
        "n_cases": len(pairs),
        "one_sided_absence_census": one_sided_absence_census(pairs),
        "gold_provenance": gold_provenance(cases),
        "harm_vs_current": {
            arm: harm_against_current(scored, arm)
            for arm in (ARM_ASYMMETRIC, ARM_STRICT, ARM_DECISIVE)
        },
        "exact_agreement_with_gold": {
            arm: exact_agreement_with_gold(scored, arm) for arm in ARM_ORDER
        },
        "exact_agreement_where_the_arm_can_fire": {
            arm: exact_agreement_where_the_arm_can_fire(scored, arm) for arm in ARM_ORDER
        },
        "mining_census": {"failures": []},
        "mining_census_a3": {"failures": []},
        "arm_disagreement": {
            arm: arm_disagreement(scored, ARM_DECISIVE, arm)
            for arm in (ARM_CURRENT, ARM_ASYMMETRIC, ARM_STRICT)
        },
        "by_arm": {},
    }
