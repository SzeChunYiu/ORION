"""Scoring, statistics and publication-table tests for the ORION-P1 study.

The statistical assertions are pinned to **published** reference values, not to
this repository's own output: Wilson score intervals from the standard tabulated
results (including Newcombe's 81/263 worked example) and Holm-Bonferroni
adjustments worked by hand in the docstrings below. A test that compared the
implementation with itself would pass while the statistic was wrong.
"""

from __future__ import annotations

import json

import pytest

from orion.study.p1 import statistics as stats
from orion.study.p1 import tables
from orion.study.p1.cases import (
    AdjudicationStatus,
    HiddenShiftCase,
    ProtectedGold,
    Split,
    TaskFamily,
)
from orion.study.p1.metrics import (
    NO_LABEL,
    BinaryRate,
    ControlOutcome,
    FailureMode,
    RepeatReduction,
    ScoreStatus,
    SetComparison,
    SystemRole,
    aggregate,
    blinded_case_id,
    case_score_from_record,
    case_score_to_record,
    score_case,
)
from orion.study.p1.systems import ResourceUse, SystemTrace

SUITE = "fingerprint-under-test"
REPEATS = stats.PROTOCOL_STOCHASTIC_REPEATS
CONTROL_FAMILY_ENUMS = (TaskFamily.EVIDENCE_ONLY_CONTROL, TaskFamily.EXECUTION_ONLY_CONTROL)


# --- fixtures ------------------------------------------------------------------


def make_case(
    case_id: str,
    family: TaskFamily,
    *,
    depth: int = 1,
    dependencies: tuple[str, ...] = ("dep.alpha", "dep.beta"),
    coordinates: tuple[str, ...] = ("W.search_universe", "M.measurement_model"),
    responsibility: str = "formulation",
) -> HiddenShiftCase:
    control = family in CONTROL_FAMILY_ENUMS
    return HiddenShiftCase(
        case_id=case_id,
        task_family=family,
        public_prompt="a prompt whose formulation may or may not be sufficient",
        observable_resources=("resource.one",),
        protected_gold=ProtectedGold(
            reframe_required=not control,
            responsibility_family=responsibility,
            target_coordinates=() if control else coordinates,
            dependencies_to_reopen=() if control else dependencies,
            root_success_rubric="the root question is answered under the frozen rubric",
            dependency_depth=0 if control else depth,
        ),
        budget_class="standard",
        adjudication_status=AdjudicationStatus.MECHANICAL_GOLD,
        split=Split.TEST,
    )


def perfect_trace(case: HiddenShiftCase, *, system_id: str, seed: int) -> SystemTrace:
    """A trace that matches gold exactly on every scored coordinate."""

    gold = case.protected_gold
    return SystemTrace(
        case_id=case.case_id,
        system_id=system_id,
        seed=seed,
        reframed=gold.reframe_required,
        responsibility_family=gold.responsibility_family,
        target_coordinates=gold.target_coordinates,
        reopened=gold.dependencies_to_reopen,
        root_solved=True,
        max_recursion_depth=max(gold.dependency_depth, 1 if gold.reframe_required else 0),
        resources=ResourceUse(wallclock_seconds=12.0, model_tokens=1000, tool_calls=4, search_queries=2),
    )


def null_trace(case: HiddenShiftCase, *, system_id: str, seed: int) -> SystemTrace:
    """A trace that does nothing: no reframe, no reopen, no claim, no solution."""

    return SystemTrace(
        case_id=case.case_id,
        system_id=system_id,
        seed=seed,
        reframed=False,
        root_solved=False,
        resources=ResourceUse(wallclock_seconds=3.0, model_tokens=200, tool_calls=1),
    )


def abstaining_trace(case: HiddenShiftCase, *, system_id: str, seed: int) -> SystemTrace:
    return SystemTrace(
        case_id=case.case_id,
        system_id=system_id,
        seed=seed,
        reframed=False,
        root_solved=False,
        abstained=True,
        resources=ResourceUse(wallclock_seconds=1.0, model_tokens=50),
    )


def scores_for(case, trace_factory, *, system_id, role=SystemRole.SUBJECT, repeats=REPEATS):
    return [
        score_case(
            case,
            None if trace_factory is None else trace_factory(case, system_id=system_id, seed=seed),
            system_id=system_id,
            seed=seed,
            system_role=role,
            suite_fingerprint=SUITE,
            subject_revision="rev-under-test",
        )
        for seed in range(repeats)
    ]


# --- per-case scoring: perfect and null ----------------------------------------


def test_perfect_trace_scores_one_on_every_primary_and_mechanistic_metric():
    case = make_case("P1-CASE-001", TaskFamily.HIDDEN_PARENT_DOMAIN, depth=2)
    result = aggregate(scores_for(case, perfect_trace, system_id="orion"))

    assert result.root_success == BinaryRate(1, 1, "case", RepeatReduction.MAJORITY)
    assert result.root_success.value == 1.0
    assert result.hidden_shift_success.value == 1.0
    assert result.reframe_target_accuracy.value == 1.0
    assert result.responsibility_macro_f1 == 1.0
    assert result.reopen.precision == 1.0
    assert result.reopen.recall == 1.0
    assert result.reopen.f1 == 1.0
    assert result.stale_closure_survival.value == 0.0
    assert result.invariant_violation.value == 0.0
    assert result.authority_violation.value == 0.0
    assert result.trace_fidelity.value == 1.0
    assert result.depth_adequacy.value == 1.0
    assert result.cannot_check_cases == 0


def test_null_trace_scores_zero_and_leaves_every_stale_closure_alive():
    case = make_case("P1-CASE-002", TaskFamily.HIDDEN_REPRESENTATION, depth=2)
    result = aggregate(scores_for(case, null_trace, system_id="inert"))

    assert result.root_success.value == 0.0
    assert result.hidden_shift_success.value == 0.0
    assert result.reframe_target_accuracy.value == 0.0
    assert result.responsibility_macro_f1 == 0.0
    assert result.reopen.precision == 0.0
    assert result.reopen.recall == 0.0
    assert result.reopen.f1 == 0.0
    # Every gold dependency was required and none was reopened.
    assert result.stale_closure_survival.value == 1.0
    assert result.depth_adequacy.value == 0.0
    # A trace that claims nothing makes no *inconsistent* claim: fidelity is an
    # internal-consistency metric, deliberately not a success metric.
    assert result.trace_fidelity.value == 1.0


def test_null_trace_names_no_responsibility_family_and_is_not_a_label():
    case = make_case("P1-CASE-003", TaskFamily.HIDDEN_DECOMPOSITION)
    score = score_case(case, null_trace(case, system_id="inert", seed=0), system_id="inert", seed=0)

    assert score.responsibility_predicted == NO_LABEL
    assert score.responsibility_correct is False
    assert score.failure_mode is FailureMode.MISSED_REFRAME


# --- the abstention rule -------------------------------------------------------


def test_abstention_on_a_control_is_not_a_correct_non_reframe():
    """An abstention is its own outcome and never a pass on a negative control."""

    case = make_case("P1-CASE-010", TaskFamily.EVIDENCE_ONLY_CONTROL)
    score = score_case(case, abstaining_trace(case, system_id="shy", seed=0), system_id="shy", seed=0)

    assert score.control_outcome is ControlOutcome.ABSTAINED
    assert score.control_outcome is not ControlOutcome.CORRECT_RESTRAINT
    assert score.root_success is False
    assert score.failure_mode is FailureMode.ABSTENTION


def test_an_always_abstaining_system_earns_no_restraint_credit():
    case = make_case("P1-CASE-011", TaskFamily.EXECUTION_ONLY_CONTROL)
    result = aggregate(scores_for(case, abstaining_trace, system_id="shy"))

    assert result.control_abstention.value == 1.0
    assert result.control_correct_restraint.value == 0.0
    assert result.unnecessary_reframe.value == 0.0
    assert result.root_success.value == 0.0
    # The three control outcomes partition the cases: nothing is double counted
    # and nothing is silently dropped.
    total = (
        result.unnecessary_reframe.successes
        + result.control_abstention.successes
        + result.control_correct_restraint.successes
    )
    assert total == result.unnecessary_reframe.n == 1


def test_genuine_restraint_is_distinguished_from_abstention():
    case = make_case("P1-CASE-012", TaskFamily.EVIDENCE_ONLY_CONTROL)
    result = aggregate(scores_for(case, perfect_trace, system_id="orion"))

    assert result.control_correct_restraint.value == 1.0
    assert result.control_abstention.value == 0.0
    assert result.unnecessary_reframe.value == 0.0


def test_reframing_a_control_is_an_unnecessary_reframe():
    case = make_case("P1-CASE-013", TaskFamily.EXECUTION_ONLY_CONTROL)

    def eager(target, *, system_id, seed):
        return SystemTrace(
            case_id=target.case_id,
            system_id=system_id,
            seed=seed,
            reframed=True,
            responsibility_family="formulation",
            target_coordinates=("W.search_universe",),
            max_recursion_depth=1,
        )

    result = aggregate(scores_for(case, eager, system_id="eager"))
    assert result.unnecessary_reframe.value == 1.0
    assert result.control_correct_restraint.value == 0.0


def test_split_repeats_on_a_control_resolve_to_the_worst_outcome():
    """A 2/2/1 panel of repeats can never be rounded up into restraint."""

    case = make_case("P1-CASE-014", TaskFamily.EVIDENCE_ONLY_CONTROL)

    def mixed(target, *, system_id, seed):
        if seed < 2:
            return SystemTrace(
                case_id=target.case_id,
                system_id=system_id,
                seed=seed,
                reframed=True,
                responsibility_family="formulation",
                target_coordinates=("W.search_universe",),
                max_recursion_depth=1,
            )
        if seed < 4:
            return abstaining_trace(target, system_id=system_id, seed=seed)
        return perfect_trace(target, system_id=system_id, seed=seed)

    result = aggregate(scores_for(case, mixed, system_id="unstable"))
    assert result.unnecessary_reframe.value == 1.0
    assert result.control_correct_restraint.value == 0.0


# --- the CANNOT_CHECK rule -----------------------------------------------------


def test_a_case_with_no_trace_is_cannot_check_not_a_failure():
    case = make_case("P1-CASE-020", TaskFamily.HIDDEN_MEASUREMENT)
    score = score_case(
        case,
        None,
        system_id="uncredentialed",
        seed=0,
        cannot_check_reason="no live provider credential",
    )

    assert score.status is ScoreStatus.CANNOT_CHECK
    assert score.root_success is None
    assert score.reopen is None
    assert score.trace_fidelity is None
    assert score.failure_mode is FailureMode.CANNOT_CHECK
    assert "credential" in score.cannot_check_reason


def test_cannot_check_never_aggregates_as_zero():
    """The decisive rule: a missing trace leaves the denominator, it does not fail."""

    solved = make_case("P1-CASE-021", TaskFamily.HIDDEN_PARENT_DOMAIN)
    missing = make_case("P1-CASE-022", TaskFamily.HIDDEN_PARENT_DOMAIN)
    scores = scores_for(solved, perfect_trace, system_id="partial") + scores_for(
        missing, None, system_id="partial"
    )

    result = aggregate(scores)

    assert result.root_success.value == 1.0, "a CANNOT_CHECK case must not drag the rate to 0.5"
    assert result.root_success.n == 1
    assert result.n_cases_total == 2
    assert result.n_cases_scored == 1
    assert result.cannot_check_case_ids == ("P1-CASE-022",)


def test_partially_missing_repeats_are_cannot_check_not_a_smaller_sample():
    case = make_case("P1-CASE-023", TaskFamily.HIDDEN_DECOMPOSITION)
    partial = scores_for(case, perfect_trace, system_id="flaky", repeats=REPEATS - 2)

    result = aggregate(partial)

    assert result.cannot_check_case_ids == ("P1-CASE-023",)
    assert result.root_success.n == 0
    assert result.root_success.value is None, "an empty denominator is CANNOT_CHECK, never 0.0"
    assert result.repeat_coverage_ok is False


def test_an_empty_rate_reports_none_rather_than_zero():
    assert BinaryRate(0, 0).value is None
    assert BinaryRate(0, 3).value == 0.0
    with pytest.raises(ValueError):
        stats.wilson_interval(0, 0)


# --- mechanistic metrics -------------------------------------------------------


def test_reopen_set_comparison_counts_precision_recall_and_stale_closures():
    case = make_case("P1-CASE-030", TaskFamily.HIDDEN_DECOMPOSITION, dependencies=("a", "b", "c"))

    def partial_reopen(target, *, system_id, seed):
        trace = perfect_trace(target, system_id=system_id, seed=seed)
        return SystemTrace(
            case_id=trace.case_id,
            system_id=trace.system_id,
            seed=trace.seed,
            reframed=True,
            responsibility_family=trace.responsibility_family,
            target_coordinates=trace.target_coordinates,
            reopened=("a", "b", "z"),
            root_solved=True,
            max_recursion_depth=trace.max_recursion_depth,
        )

    score = score_case(case, partial_reopen(case, system_id="orion", seed=0), system_id="orion", seed=0)

    assert score.reopen == SetComparison(true_positives=2, false_positives=1, false_negatives=1)
    assert score.reopen.precision == pytest.approx(2 / 3)
    assert score.reopen.recall == pytest.approx(2 / 3)
    assert score.reopen.f1 == pytest.approx(2 / 3)
    assert score.stale_closures == 1
    assert score.failure_mode is FailureMode.INCOMPLETE_REOPEN

    result = aggregate(scores_for(case, partial_reopen, system_id="orion"))
    assert result.stale_closure_survival.successes == REPEATS
    assert result.stale_closure_survival.n == REPEATS * 3
    assert result.stale_closure_survival.value == pytest.approx(1 / 3)


def test_empty_versus_empty_reopen_is_not_applicable_rather_than_perfect():
    empty = SetComparison()
    assert empty.applicable is False
    assert empty.precision is None
    assert empty.recall is None
    assert empty.f1 is None


def test_responsibility_macro_f1_averages_over_the_observed_label_universe():
    """Two classes, one perfectly predicted and one never predicted.

    Gold: two `formulation` cases and two `measurement` cases. The system labels
    everything `formulation`.
      formulation: tp=2, fp=2, fn=0 -> P=0.5, R=1.0, F1=2/3
      measurement: tp=0, fp=0, fn=2 -> P=0.0, R=0.0, F1=0.0
      macro = (2/3 + 0)/2 = 1/3
    """

    scores = []
    for index, responsibility in enumerate(("formulation", "formulation", "measurement", "measurement")):
        case = make_case(f"P1-CASE-04{index}", TaskFamily.HIDDEN_PARENT_DOMAIN, responsibility=responsibility)
        for seed in range(REPEATS):
            trace = perfect_trace(case, system_id="mono", seed=seed)
            scores.append(
                score_case(
                    case,
                    SystemTrace(
                        case_id=trace.case_id,
                        system_id="mono",
                        seed=seed,
                        reframed=True,
                        responsibility_family="formulation",
                        target_coordinates=trace.target_coordinates,
                        reopened=trace.reopened,
                        root_solved=True,
                        max_recursion_depth=trace.max_recursion_depth,
                    ),
                    system_id="mono",
                    seed=seed,
                )
            )

    result = aggregate(scores)
    assert result.responsibility_labels == ("formulation", "measurement")
    assert result.responsibility_macro_f1 == pytest.approx(1 / 3)


def test_a_reframe_naming_no_target_is_an_attribution_failure_not_a_bookkeeping_one():
    """An untyped system reframing without naming a cause is reporting honestly.

    Trace fidelity is an internal-consistency audit: it asks whether a trace
    contradicts itself. A system that reframes and names no responsibility is
    not contradicting itself — it has no typed attribution mechanism, which is
    exactly the property the untyped baselines and the generic-retry ablation
    exist to test. Scoring it as TRACE_INFIDELITY reported an attribution
    failure as bookkeeping, and because integrity outranks performance in the
    precedence order, it masked those systems' defining property behind a
    housekeeping label.

    Claiming a reframe while recording no recursion depth remains a genuine
    contradiction: the trace asserts an act it also says never ran.
    """

    from orion.study.p1.metrics import _trace_fidelity_faults

    def trace(*, coords, family, depth):
        return SystemTrace(
            case_id="p1-c101",
            system_id="tree_search_iterative_research",
            seed=0,
            reframed=True,
            responsibility_family=family,
            target_coordinates=coords,
            max_recursion_depth=depth,
        )

    untyped = trace(coords=(), family="", depth=2)
    faults = _trace_fidelity_faults(untyped)
    assert "reframe_without_target_coordinates" not in faults
    assert "reframe_without_responsibility_family" not in faults

    contradictory = trace(coords=("W.REPRESENTATIONS",), family="SEARCH", depth=0)
    assert "reframe_without_recursion_depth" in _trace_fidelity_faults(contradictory)

def test_violations_use_any_reduction_so_one_bad_repeat_marks_the_case():
    case = make_case("P1-CASE-051", TaskFamily.HIDDEN_PARENT_DOMAIN)

    def occasionally_illegal(target, *, system_id, seed):
        trace = perfect_trace(target, system_id=system_id, seed=seed)
        if seed != 0:
            return trace
        return SystemTrace(
            case_id=trace.case_id,
            system_id=system_id,
            seed=seed,
            reframed=True,
            responsibility_family=trace.responsibility_family,
            target_coordinates=trace.target_coordinates,
            reopened=trace.reopened,
            root_solved=True,
            authority_violations=("wrote outside the authorized boundary",),
            max_recursion_depth=trace.max_recursion_depth,
        )

    result = aggregate(scores_for(case, occasionally_illegal, system_id="orion"))
    assert result.authority_violation.reduction is RepeatReduction.ANY
    assert result.authority_violation.value == 1.0
    assert result.root_success.value == 1.0, "the majority of repeats still solved the root"


def test_trace_fidelity_is_bucketed_by_gold_dependency_depth():
    shallow = make_case("P1-CASE-060", TaskFamily.HIDDEN_PARENT_DOMAIN, depth=1)
    deep = make_case("P1-CASE-061", TaskFamily.HIDDEN_PARENT_DOMAIN, depth=4)
    result = aggregate(
        scores_for(shallow, perfect_trace, system_id="orion") + scores_for(deep, perfect_trace, system_id="orion")
    )

    assert [depth for depth, _ in result.trace_fidelity_by_depth] == [1, 4]
    assert all(rate.value == 1.0 for _, rate in result.trace_fidelity_by_depth)


def test_resource_metrics_are_per_trial_means():
    case = make_case("P1-CASE-070", TaskFamily.HIDDEN_REPRESENTATION)
    result = aggregate(scores_for(case, perfect_trace, system_id="orion"))

    assert result.resources.trials == REPEATS
    assert result.resources.wallclock_seconds_mean == pytest.approx(12.0)
    assert result.resources.model_tokens_mean == pytest.approx(1000.0)
    assert result.resources.tool_calls_mean == pytest.approx(4.0)


# --- record round-trip ---------------------------------------------------------


def test_case_score_survives_the_archive_round_trip():
    case = make_case("P1-CASE-080", TaskFamily.HIDDEN_DECOMPOSITION)
    score = score_case(
        case,
        perfect_trace(case, system_id="orion", seed=3),
        system_id="orion",
        seed=3,
        system_role=SystemRole.SUBJECT,
        suite_fingerprint=SUITE,
        subject_revision="rev-under-test",
    )
    restored = case_score_from_record(json.loads(json.dumps(case_score_to_record(score))))
    assert restored == score


def test_a_record_from_an_unknown_schema_is_refused():
    with pytest.raises(ValueError, match="unsupported record schema"):
        case_score_from_record({"schema_version": "something.else.v9"})


def test_blinded_case_ids_are_deterministic_and_do_not_echo_the_raw_id():
    first = blinded_case_id("P1-CASE-090", suite_fingerprint=SUITE)
    assert first == blinded_case_id("P1-CASE-090", suite_fingerprint=SUITE)
    assert first != blinded_case_id("P1-CASE-090", suite_fingerprint="other-suite")
    assert "P1-CASE-090" not in first


# --- Wilson intervals against published values ---------------------------------


@pytest.mark.parametrize(
    ("successes", "n", "low", "high"),
    [
        # Standard tabulated Wilson score intervals at 95%.
        (0, 10, 0.0000, 0.2775),
        (5, 10, 0.2366, 0.7634),
        (7, 10, 0.3968, 0.8922),
        (10, 10, 0.7225, 1.0000),
        (1, 20, 0.0089, 0.2361),
        # Newcombe (1998) worked example: 81 of 263.
        (81, 263, 0.2553, 0.3662),
    ],
)
def test_wilson_interval_matches_published_values(successes, n, low, high):
    interval = stats.wilson_interval(successes, n)
    assert interval.point == pytest.approx(successes / n)
    assert interval.low == pytest.approx(low, abs=5e-5)
    assert interval.high == pytest.approx(high, abs=5e-5)


def test_wilson_interval_satisfies_its_algebraic_identities():
    """Checks independent of the arithmetic used to produce the tabulated values."""

    half = stats.wilson_interval(5, 10)
    assert half.point == 0.5
    # At p = 0.5 the Wilson interval is exactly symmetric about 0.5.
    assert (half.low + half.high) / 2 == pytest.approx(0.5, abs=1e-12)

    none_of_ten = stats.wilson_interval(0, 10)
    all_of_ten = stats.wilson_interval(10, 10)
    assert round(none_of_ten.low, 10) == 0.0
    assert round(all_of_ten.high, 10) == 1.0
    # 0/n and n/n are reflections of one another.
    assert all_of_ten.low == pytest.approx(1.0 - none_of_ten.high, abs=1e-12)


def test_wilson_interval_rejects_impossible_inputs():
    with pytest.raises(ValueError):
        stats.wilson_interval(-1, 10)
    with pytest.raises(ValueError):
        stats.wilson_interval(11, 10)
    with pytest.raises(ValueError):
        stats.wilson_interval(1, 10, confidence=1.0)


def test_normal_quantile_matches_the_published_975th_percentile():
    assert stats.normal_quantile(0.975) == pytest.approx(1.959964, abs=5e-7)
    assert stats.normal_quantile(0.995) == pytest.approx(2.575829, abs=5e-7)


# --- paired bootstrap ----------------------------------------------------------

SUBJECT_UNITS = [1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0]
COMPARATOR_UNITS = [0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0]


def test_paired_bootstrap_is_deterministic_under_a_fixed_seed():
    first = stats.paired_bootstrap_difference(SUBJECT_UNITS, COMPARATOR_UNITS, resamples=2000, seed=11)
    again = stats.paired_bootstrap_difference(SUBJECT_UNITS, COMPARATOR_UNITS, resamples=2000, seed=11)
    other = stats.paired_bootstrap_difference(SUBJECT_UNITS, COMPARATOR_UNITS, resamples=2000, seed=12)

    assert (first.point, first.low, first.high) == (again.point, again.low, again.high)
    assert first.two_sided_p == again.two_sided_p
    assert first.seed == 11
    assert first.resamples == 2000
    # The point estimate is a property of the data, not of the resampling seed.
    assert other.point == first.point


def test_paired_bootstrap_interval_contains_its_point_estimate():
    result = stats.paired_bootstrap_difference(SUBJECT_UNITS, COMPARATOR_UNITS, resamples=2000, seed=11)
    # mean(subject) = 0.8, mean(comparator) = 0.3 -> difference 0.5, by hand.
    assert result.point == pytest.approx(0.5)
    assert result.contains(result.point)
    assert result.low <= result.point <= result.high
    assert result.n == 10


def test_paired_bootstrap_uses_the_pairing():
    """Identical values on every unit give a zero difference with a zero-width interval."""

    result = stats.paired_bootstrap_difference(SUBJECT_UNITS, SUBJECT_UNITS, resamples=500, seed=5)
    assert result.point == 0.0
    assert result.low == 0.0
    assert result.high == 0.0
    assert result.two_sided_p == 1.0


def test_paired_bootstrap_p_value_never_reports_a_fabricated_zero():
    result = stats.paired_bootstrap_difference(SUBJECT_UNITS, COMPARATOR_UNITS, resamples=1000, seed=3)
    assert result.p_floor == pytest.approx(1 / 1000)
    assert result.two_sided_p >= result.p_floor


def test_paired_bootstrap_refuses_unmatched_or_empty_samples():
    with pytest.raises(ValueError):
        stats.paired_bootstrap_difference([1.0, 0.0], [1.0], seed=1)
    with pytest.raises(ValueError):
        stats.paired_bootstrap_difference([], [], seed=1)


# --- Holm correction -----------------------------------------------------------


def test_holm_correction_orders_and_adjusts_by_hand_worked_values():
    """p = (0.01, 0.04, 0.03), m = 3.

    Ascending: 0.01, 0.03, 0.04.
      rank 0: 3 * 0.01 = 0.03
      rank 1: max(0.03, 2 * 0.03 = 0.06) = 0.06
      rank 2: max(0.06, 1 * 0.04 = 0.04) = 0.06   <- monotonicity binds here
    Returned in the caller's order: (0.03, 0.06, 0.06).
    """

    entries = stats.holm_correction([0.01, 0.04, 0.03], labels=["a", "b", "c"])

    assert [entry.label for entry in entries] == ["a", "b", "c"]
    assert [entry.adjusted_p for entry in entries] == pytest.approx([0.03, 0.06, 0.06])
    assert [entry.rank for entry in entries] == [1, 3, 2]
    assert [entry.rejected for entry in entries] == [True, False, False]


def test_holm_correction_second_hand_worked_family():
    """p = (0.005, 0.011, 0.02, 0.04), m = 4 -> (0.02, 0.033, 0.04, 0.04)."""

    entries = stats.holm_correction([0.005, 0.011, 0.02, 0.04])
    assert [entry.adjusted_p for entry in entries] == pytest.approx([0.02, 0.033, 0.04, 0.04])
    assert [entry.rejected for entry in entries] == [True, True, True, True]


def test_holm_correction_is_monotone_and_capped():
    entries = stats.holm_correction([0.5, 0.6, 0.7])
    assert [entry.adjusted_p for entry in entries] == pytest.approx([1.0, 1.0, 1.0])
    assert not any(entry.rejected for entry in entries)
    assert stats.holm_correction([]) == ()


def test_holm_correction_rejects_impossible_p_values():
    with pytest.raises(ValueError):
        stats.holm_correction([0.1, 1.5])
    with pytest.raises(ValueError):
        stats.holm_correction([0.1], labels=["a", "b"])


# --- hypothesis verdicts against the frozen margins ----------------------------


def difference(point, low, high, *, n=40, p=0.01):
    return stats.BootstrapDifference(
        point=point,
        low=low,
        high=high,
        confidence=0.95,
        resamples=stats.PROTOCOL_RESAMPLES,
        n=n,
        seed=1,
        two_sided_p=p,
        p_floor=1 / stats.PROTOCOL_RESAMPLES,
    )


def test_h1_is_not_supported_when_the_interval_crosses_the_frozen_margin():
    """Positive difference, but the 95% interval straddles +0.05."""

    verdict = stats.assess_hypothesis(
        hypothesis_id="P1.H1",
        direction=stats.HypothesisDirection.SUPERIORITY,
        margin=stats.H1_SUPERIORITY_MARGIN,
        difference=difference(0.08, 0.01, 0.15),
    )
    assert verdict.verdict is stats.HypothesisVerdict.NOT_SUPPORTED


def test_h1_is_supported_only_when_the_whole_interval_clears_the_margin():
    supported = stats.assess_hypothesis(
        hypothesis_id="P1.H1",
        direction=stats.HypothesisDirection.SUPERIORITY,
        margin=stats.H1_SUPERIORITY_MARGIN,
        difference=difference(0.20, 0.12, 0.28),
    )
    assert supported.verdict is stats.HypothesisVerdict.SUPPORTED

    touching = stats.assess_hypothesis(
        hypothesis_id="P1.H1",
        direction=stats.HypothesisDirection.SUPERIORITY,
        margin=stats.H1_SUPERIORITY_MARGIN,
        difference=difference(0.20, stats.H1_SUPERIORITY_MARGIN, 0.28),
    )
    assert touching.verdict is stats.HypothesisVerdict.NOT_SUPPORTED, "an interval touching the margin is not support"


def test_a_cannot_check_unit_blocks_any_verdict():
    verdict = stats.assess_hypothesis(
        hypothesis_id="P1.H1",
        direction=stats.HypothesisDirection.SUPERIORITY,
        margin=stats.H1_SUPERIORITY_MARGIN,
        difference=difference(0.20, 0.12, 0.28),
        cannot_check_units=1,
    )
    assert verdict.verdict is stats.HypothesisVerdict.CANNOT_CHECK

    absent = stats.assess_hypothesis(
        hypothesis_id="P1.H1",
        direction=stats.HypothesisDirection.SUPERIORITY,
        margin=stats.H1_SUPERIORITY_MARGIN,
        difference=None,
    )
    assert absent.verdict is stats.HypothesisVerdict.CANNOT_CHECK


def test_underpowered_requires_a_caller_declared_prospective_n():
    inconclusive = difference(0.08, 0.01, 0.15, n=12)

    assert (
        stats.assess_hypothesis(
            hypothesis_id="P1.H1",
            direction=stats.HypothesisDirection.SUPERIORITY,
            margin=stats.H1_SUPERIORITY_MARGIN,
            difference=inconclusive,
        ).verdict
        is stats.HypothesisVerdict.NOT_SUPPORTED
    )
    assert (
        stats.assess_hypothesis(
            hypothesis_id="P1.H1",
            direction=stats.HypothesisDirection.SUPERIORITY,
            margin=stats.H1_SUPERIORITY_MARGIN,
            difference=inconclusive,
            min_units=40,
        ).verdict
        is stats.HypothesisVerdict.UNDERPOWERED
    )


def test_h2_non_inferiority_needs_both_control_abstention_rates():
    within_margin = difference(0.0, -0.01, 0.015)

    blind = stats.assess_hypothesis(
        hypothesis_id="P1.H2",
        direction=stats.HypothesisDirection.NON_INFERIORITY,
        margin=stats.H2_NON_INFERIORITY_MARGIN,
        difference=within_margin,
    )
    assert blind.verdict is stats.HypothesisVerdict.CANNOT_CHECK

    equivalent = stats.assess_hypothesis(
        hypothesis_id="P1.H2",
        direction=stats.HypothesisDirection.NON_INFERIORITY,
        margin=stats.H2_NON_INFERIORITY_MARGIN,
        difference=within_margin,
        subject_abstention_rate=0.02,
        comparator_abstention_rate=0.02,
    )
    assert equivalent.verdict is stats.HypothesisVerdict.EQUIVALENT


def test_h2_cannot_be_won_by_abstaining_on_the_controls():
    """A low unnecessary-reframe rate bought with abstentions is not restraint."""

    verdict = stats.assess_hypothesis(
        hypothesis_id="P1.H2",
        direction=stats.HypothesisDirection.NON_INFERIORITY,
        margin=stats.H2_NON_INFERIORITY_MARGIN,
        difference=difference(-0.30, -0.40, -0.20),
        subject_abstention_rate=0.60,
        comparator_abstention_rate=0.05,
    )
    assert verdict.verdict is stats.HypothesisVerdict.CANNOT_CHECK
    assert "confounded by abstention" in verdict.rationale


def test_h2_is_not_supported_when_the_upper_bound_reaches_the_margin():
    verdict = stats.assess_hypothesis(
        hypothesis_id="P1.H2",
        direction=stats.HypothesisDirection.NON_INFERIORITY,
        margin=stats.H2_NON_INFERIORITY_MARGIN,
        difference=difference(0.01, -0.02, 0.06),
        subject_abstention_rate=0.0,
        comparator_abstention_rate=0.0,
    )
    assert verdict.verdict is stats.HypothesisVerdict.NOT_SUPPORTED


def test_cohens_h_is_zero_for_equal_proportions_and_signed_otherwise():
    assert stats.cohens_h(0.5, 0.5) == 0.0
    assert stats.cohens_h(0.6, 0.4) > 0.0
    assert stats.cohens_h(0.4, 0.6) < 0.0


# --- publication tables from archived records ----------------------------------


def build_archive(tmp_path):
    """A small but complete archive: subject, two baselines, one ablation."""

    suite = [
        make_case("P1-CASE-100", TaskFamily.HIDDEN_PARENT_DOMAIN, depth=1),
        make_case("P1-CASE-101", TaskFamily.HIDDEN_REPRESENTATION, depth=2),
        make_case("P1-CASE-102", TaskFamily.HIDDEN_DECOMPOSITION, depth=2),
        make_case("P1-CASE-103", TaskFamily.HIDDEN_MEASUREMENT, depth=3),
        make_case("P1-CASE-104", TaskFamily.EVIDENCE_ONLY_CONTROL),
        make_case("P1-CASE-105", TaskFamily.EXECUTION_ONLY_CONTROL),
    ]

    def strong(target, *, system_id, seed):
        return perfect_trace(target, system_id=system_id, seed=seed)

    def weak(target, *, system_id, seed):
        if target.task_family is TaskFamily.HIDDEN_PARENT_DOMAIN:
            return perfect_trace(target, system_id=system_id, seed=seed)
        return null_trace(target, system_id=system_id, seed=seed)

    plan = [
        ("orion_full", SystemRole.SUBJECT, strong),
        ("static_react_tool_workflow", SystemRole.BASELINE, weak),
        ("tree_search_iterative_research", SystemRole.BASELINE, null_trace),
        ("orion_without_explicit_W", SystemRole.ABLATION, null_trace),
    ]

    records = []
    for system_id, role, factory in plan:
        for case in suite:
            for score in scores_for(case, factory, system_id=system_id, role=role):
                records.append(case_score_to_record(score))

    archive = tmp_path / "raw"
    archive.mkdir()
    (archive / "records.jsonl").write_text("\n".join(json.dumps(record) for record in records) + "\n")
    return archive, suite


def test_tables_are_built_from_archived_records_only(tmp_path):
    archive, suite = build_archive(tmp_path)
    t2, t3 = tables.generate(archive, tmp_path / "out", resamples=400, bootstrap_seed=7)

    assert t2["status"] in {tables.STATUS_OK, tables.STATUS_PARTIAL}
    assert t2["provenance"]["suite_fingerprints"] == [SUITE]
    assert t2["provenance"]["bootstrap_seed"] == 7
    assert t2["provenance"]["bootstrap_resamples"] == 400

    # The comparator is the strongest BASELINE, never an ablation.
    assert t2["comparator"]["system_id"] == "static_react_tool_workflow"

    overall = {
        row["system_id"]: row
        for row in t2["rows"]
        if row["scope"] == tables.SCOPE_ALL
    }
    assert overall["orion_full"]["rate"]["value"] == 1.0
    assert overall["orion_full"]["rate"]["interval"]["low"] > 0.5
    # One of six cases solved by the strongest baseline.
    assert overall["static_react_tool_workflow"]["rate"]["value"] == pytest.approx(1 / 6)

    subject_difference = overall["orion_full"]["difference_vs_comparator"]
    assert subject_difference["comparator_system_id"] == "static_react_tool_workflow"
    assert subject_difference["difference"]["point"] == pytest.approx(5 / 6)
    assert subject_difference["assessment"]["hypothesis_id"] == "P1.H1"

    assert t3["status"] == tables.STATUS_OK
    assert any(row["failure_mode"] == FailureMode.MISSED_REFRAME.value for row in t3["rows"])
    assert any(row["failure_mode"] == FailureMode.NONE.value for row in t3["rows"])

    for name in (tables.TABLE_T2, tables.TABLE_T3):
        for suffix in (".json", ".md"):
            assert (tmp_path / "out" / f"{name}{suffix}").exists()

    # No raw case id reaches a published table, and cases are named by pseudonym.
    published = "".join(
        (tmp_path / "out" / f"{name}{suffix}").read_text()
        for name in (tables.TABLE_T2, tables.TABLE_T3)
        for suffix in (".json", ".md")
    )
    for case in suite:
        assert case.case_id not in published, f"{case.case_id} leaked into a published table"
    blinded = {blinded_case_id(case.case_id, suite_fingerprint=SUITE) for case in suite}
    assert blinded & set(json.dumps(t3["rows"]).split('"')), "the taxonomy must name representative cases by pseudonym"


def test_seed_mean_diagnostic_recovers_resolution_the_frozen_reduction_discards(tmp_path):
    """Two systems that differ per seed but reduce to the same case-level rate.

    `steady` solves every repeat; `mostly` solves 4 of 5. Majority reduction
    scores both cases solved, so the frozen difference is exactly 0.0 — the
    diagnostic must still show the real 0.2 per-seed gap.
    """

    case = make_case("P1-CASE-110", TaskFamily.HIDDEN_PARENT_DOMAIN)

    def mostly(target, *, system_id, seed):
        if seed == 0:
            return null_trace(target, system_id=system_id, seed=seed)
        return perfect_trace(target, system_id=system_id, seed=seed)

    records = [
        case_score_to_record(score)
        for score in scores_for(case, perfect_trace, system_id="steady", role=SystemRole.SUBJECT)
        + scores_for(case, mostly, system_id="wobbly", role=SystemRole.BASELINE)
    ]
    archive = tmp_path / "raw"
    archive.mkdir()
    (archive / "records.jsonl").write_text("\n".join(json.dumps(record) for record in records) + "\n")

    t2, _ = tables.generate(archive, tmp_path / "out", resamples=400, bootstrap_seed=7)
    row = next(r for r in t2["rows"] if r["scope"] == tables.SCOPE_ALL and r["system_id"] == "steady")
    block = row["difference_vs_comparator"]

    assert block["difference"]["point"] == 0.0, "majority reduction collapses the gap, as the frozen unit requires"
    assert block["seed_mean_difference"]["point"] == pytest.approx(0.2)
    # The diagnostic must cover exactly the units of the difference it accompanies.
    assert block["seed_mean_difference"]["n"] == block["difference"]["n"] == block["matched_units"]


def test_seed_mean_diagnostic_covers_the_same_units_in_every_scope(tmp_path):
    archive, _ = build_archive(tmp_path)
    t2, _ = tables.generate(archive, tmp_path / "out", resamples=200, bootstrap_seed=7)

    compared = [row for row in t2["rows"] if row["difference_vs_comparator"] is not None]
    assert compared, "the fixture must produce at least one compared row"
    for row in compared:
        block = row["difference_vs_comparator"]
        if block["difference"] is None:
            continue
        assert block["seed_mean_difference"] is not None, f"{row['system_id']}/{row['scope']} lost its diagnostic"
        assert block["seed_mean_difference"]["n"] == block["difference"]["n"]


def test_tables_are_regenerated_identically_from_the_same_archive(tmp_path):
    archive, _ = build_archive(tmp_path)
    first, _ = tables.generate(archive, tmp_path / "a", resamples=400, bootstrap_seed=7)
    second, _ = tables.generate(archive, tmp_path / "b", resamples=400, bootstrap_seed=7)

    def numbers(table):
        return json.dumps({key: value for key, value in table.items() if key != "provenance"}, sort_keys=True)

    assert numbers(first) == numbers(second)


def test_an_absent_archive_is_cannot_check_with_a_distinct_exit_code(tmp_path):
    code = tables.main(["--archive", str(tmp_path / "missing"), "--out", str(tmp_path / "out")])
    assert code == tables.EXIT_CANNOT_CHECK
    assert code not in {tables.EXIT_OK, 1}

    payload = json.loads((tmp_path / "out" / f"{tables.TABLE_T2}.json").read_text())
    assert payload["status"] == tables.STATUS_CANNOT_CHECK
    assert payload["rows"] == []
    assert "no records" in payload["reason"]


def test_an_archive_spanning_two_suite_revisions_is_refused(tmp_path):
    archive, _ = build_archive(tmp_path)
    records = [json.loads(line) for line in (archive / "records.jsonl").read_text().splitlines()]
    records[0]["suite_fingerprint"] = "a-different-frozen-suite"
    (archive / "records.jsonl").write_text("\n".join(json.dumps(record) for record in records) + "\n")

    t2, t3 = tables.generate(archive, tmp_path / "out", resamples=200, bootstrap_seed=7)
    assert t2["status"] == tables.STATUS_CANNOT_CHECK
    assert t3["status"] == tables.STATUS_CANNOT_CHECK
    assert "suite fingerprints" in t2["reason"]


def test_an_archive_missing_stochastic_repeats_is_refused(tmp_path):
    archive, _ = build_archive(tmp_path)
    lines = (archive / "records.jsonl").read_text().splitlines()
    (archive / "records.jsonl").write_text("\n".join(lines[1:]) + "\n")

    t2, _ = tables.generate(archive, tmp_path / "out", resamples=200, bootstrap_seed=7)
    assert t2["status"] == tables.STATUS_CANNOT_CHECK
    assert "stochastic repeats" in t2["reason"]


def test_exact_archive_design_rejects_zero_of_five_and_missing_dimensions(tmp_path):
    archive, _ = build_archive(tmp_path)
    records = [json.loads(line) for line in (archive / "records.jsonl").read_text().splitlines()]
    systems = sorted({row["system_id"] for row in records})
    cases = sorted({row["case_id"] for row in records})
    seeds = sorted({row["seed"] for row in records})
    design = {
        "schema_version": "orion.p1.archive-design.v1",
        "suite_fingerprint": records[0]["suite_fingerprint"],
        "subject_revision": records[0]["subject_revision"],
        "system_ids": systems,
        "case_ids": cases,
        "seeds": seeds,
        "expected_record_count": len(systems) * len(cases) * len(seeds),
    }
    design_path = tmp_path / "design.json"
    design_path.write_text(json.dumps(design))

    variants = {
        "missing-cell": [
            row for row in records
            if not (row["system_id"] == systems[0] and row["case_id"] == cases[0])
        ],
        "missing-system": [row for row in records if row["system_id"] != systems[0]],
        "missing-case": [row for row in records if row["case_id"] != cases[0]],
    }
    for name, changed in variants.items():
        changed_path = tmp_path / name
        changed_path.mkdir()
        (changed_path / "records.jsonl").write_text(
            "\n".join(json.dumps(row) for row in changed) + "\n"
        )
        t2, _ = tables.generate(
            changed_path,
            tmp_path / f"out-{name}",
            resamples=20,
            bootstrap_seed=7,
            design_manifest=design_path,
        )
        assert t2["status"] == tables.STATUS_CANNOT_CHECK, name
        assert "expected" in t2["reason"], name


def test_exact_archive_design_rejects_duplicate_seed_replacing_required_seed(tmp_path):
    archive, _ = build_archive(tmp_path)
    records = [json.loads(line) for line in (archive / "records.jsonl").read_text().splitlines()]
    systems = sorted({row["system_id"] for row in records})
    cases = sorted({row["case_id"] for row in records})
    seeds = sorted({row["seed"] for row in records})
    design = {
        "schema_version": "orion.p1.archive-design.v1",
        "suite_fingerprint": records[0]["suite_fingerprint"],
        "subject_revision": records[0]["subject_revision"],
        "system_ids": systems,
        "case_ids": cases,
        "seeds": seeds,
        "expected_record_count": len(records),
    }
    design_path = tmp_path / "design.json"
    design_path.write_text(json.dumps(design))
    target = next(
        row for row in records
        if row["system_id"] == systems[0] and row["case_id"] == cases[0] and row["seed"] == seeds[-1]
    )
    target["seed"] = seeds[0]
    (archive / "records.jsonl").write_text("\n".join(json.dumps(row) for row in records) + "\n")

    t2, _ = tables.generate(
        archive,
        tmp_path / "out-duplicate-seed",
        resamples=20,
        bootstrap_seed=7,
        design_manifest=design_path,
    )
    assert t2["status"] == tables.STATUS_CANNOT_CHECK
    assert "non-unique" in t2["reason"]


def test_exact_archive_design_rejects_unexpected_system_and_case(tmp_path):
    archive, _ = build_archive(tmp_path)
    records = [json.loads(line) for line in (archive / "records.jsonl").read_text().splitlines()]
    systems = sorted({row["system_id"] for row in records})
    cases = sorted({row["case_id"] for row in records})
    seeds = sorted({row["seed"] for row in records})
    design = {
        "schema_version": "orion.p1.archive-design.v1",
        "suite_fingerprint": records[0]["suite_fingerprint"],
        "subject_revision": records[0]["subject_revision"],
        "system_ids": systems,
        "case_ids": cases,
        "seeds": seeds,
        "expected_record_count": len(records),
    }
    design_path = tmp_path / "design.json"
    design_path.write_text(json.dumps(design))
    records[0]["system_id"] = "unexpected-system"
    records[1]["case_id"] = "unexpected-case"
    (archive / "records.jsonl").write_text("\n".join(json.dumps(row) for row in records) + "\n")

    t2, _ = tables.generate(
        archive,
        tmp_path / "out-unexpected-identities",
        resamples=20,
        bootstrap_seed=7,
        design_manifest=design_path,
    )
    assert t2["status"] == tables.STATUS_CANNOT_CHECK
    assert "unexpected systems" in t2["reason"]
    assert "unexpected cases" in t2["reason"]


def test_a_malformed_record_is_refused_rather_than_skipped(tmp_path):
    archive = tmp_path / "raw"
    archive.mkdir()
    (archive / "records.jsonl").write_text("{not json}\n")

    assert tables.main(["--archive", str(archive), "--out", str(tmp_path / "out")]) == tables.EXIT_ERROR
