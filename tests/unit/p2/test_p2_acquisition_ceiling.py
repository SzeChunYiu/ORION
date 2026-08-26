"""The threshold P2's negative was measured against was not one it could pass.

Every number here is read from the committed campaign artifacts, not restated
from prose. The model of the scorer is checked against both published arms
before it is used to bound anything, because a ceiling computed from a metric
you have not reproduced is a guess with decimals on it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.programme.attainable_margin import MarginVerdictReason, assess_attainable_margin
from orion.programme.gate_attainability import (
    GateDirection,
    GateReachReason,
    PreregisteredGate,
    assess_threshold_support,
)
from orion.programme.records import Outcome
from orion.study.p2.acquisition_ceiling import (
    ExposureAccount,
    RouteAdmissibility,
    RouteEvidence,
    TaskAcquisition,
    arm_ceiling,
    as_capability,
    classify_route,
    delta_support,
    intersection_over_union,
    matched_exposure,
)


def _gate(threshold: float, reads: str = "iou_delta") -> PreregisteredGate:
    return PreregisteredGate(
        gate_id=f"P2_V2_WIDE_BOUNDED_{reads.upper()}",
        reads=reads,
        threshold=threshold,
        direction=GateDirection.AT_LEAST,
    )

EVIDENCE = (
    Path(__file__).resolve().parents[3]
    / "papers"
    / "orion-12-open-world-scientific-discovery"
    / "evidence"
    / "external_results"
)
DIAGNOSTIC = EVIDENCE / "P2_V2_WIDE_BOUNDED_STAGE_DIAGNOSTIC_2026-08-18.json"
MATCHED = EVIDENCE / "P2_V2_WIDE_BOUNDED_MATCHED_RESULT_2026-08-18.json"

SUBMITTED = 20  # implied exactly by both arms' published avg_precision


@pytest.fixture(scope="module")
def diagnostic() -> dict:
    return json.loads(DIAGNOSTIC.read_text())


@pytest.fixture(scope="module")
def matched() -> dict:
    return json.loads(MATCHED.read_text())


def _tasks(diagnostic: dict, arm: str) -> list[TaskAcquisition]:
    """Build the arm's per-task record from the committed diagnostic.

    Raw acquisition is recorded per route for the governed arm only, so the
    lexical arm's acquisition is unmeasured and is passed as ``None`` rather
    than assumed equal to what it scored.
    """

    out = []
    for t in diagnostic["tasks"]:
        acquired = (
            sum(t["governed_raw_route_gold_hits"].values()) if arm == "governed" else None
        )
        out.append(
            TaskAcquisition(
                task_id=t["task_id"],
                gold_count=t["gt_count"],
                submitted=SUBMITTED,
                scored_hits=t[f"{arm}_hit_count"],
                acquired_gold=acquired,
            )
        )
    return out


# ---------------------------------------------------------------------------
# The model of the scorer, before it is trusted to bound anything
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("arm,key", [("governed", "wide_governed_multiroute"), ("lexical", "wide_lexical_arxiv")])
def test_iou_model_reproduces_both_published_arms(diagnostic, matched, arm, key):
    published = matched["official_metrics"][key]
    tasks = _tasks(diagnostic, arm)
    mine = sum(intersection_over_union(t.scored_hits, t.gold_count, t.submitted) for t in tasks) / len(tasks)
    assert round(mine, 6) == published["avg_iou"]
    recall = sum(t.scored_hits / t.gold_count for t in tasks) / len(tasks)
    assert round(recall, 6) == published["avg_recall"]


def test_submission_size_is_implied_by_published_precision(diagnostic, matched):
    """20 is read off the artifact, not assumed."""

    for arm, key in (("governed", "wide_governed_multiroute"), ("lexical", "wide_lexical_arxiv")):
        tasks = _tasks(diagnostic, arm)
        hits = sum(t.scored_hits for t in tasks)
        implied = (hits / len(tasks)) / matched["official_metrics"][key]["avg_precision"]
        assert round(implied) == SUBMITTED


# ---------------------------------------------------------------------------
# Acquisition, not selection, was the binding constraint
# ---------------------------------------------------------------------------


def test_acquisition_is_the_binding_constraint_not_selection(diagnostic):
    ceiling = arm_ceiling("wide_governed_multiroute", _tasks(diagnostic, "governed"))
    assert ceiling.gold_total == 229
    assert ceiling.acquired_total == 7
    assert ceiling.scored_total == 6
    assert ceiling.never_acquired == 222
    # A perfect selector recovers exactly one identifier across the whole slice.
    assert ceiling.acquired_total - ceiling.scored_total == 1
    assert ceiling.selection_headroom < 0.002


def test_ceiling_is_never_below_the_observed_score(diagnostic):
    ceiling = arm_ceiling("wide_governed_multiroute", _tasks(diagnostic, "governed"))
    assert ceiling.ceiling_iou >= ceiling.observed_iou
    assert ceiling.ceiling_recall >= ceiling.observed_recall


# ---------------------------------------------------------------------------
# The frozen threshold
# ---------------------------------------------------------------------------


def test_frozen_iou_threshold_was_unreachable_unconditionally(diagnostic, matched):
    """The programme's own gate, handed a support this module derives."""

    treatment = arm_ceiling("wide_governed_multiroute", _tasks(diagnostic, "governed"))
    control = arm_ceiling("wide_lexical_arxiv", _tasks(diagnostic, "lexical"))
    threshold = matched["frozen_positive_rule"]["iou_delta_at_least"]
    assert threshold == 0.03

    held = assess_threshold_support(_gate(threshold), support=delta_support(treatment, control))
    assert held.reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert held.blocks
    assert round(held.best_value, 6) == 0.004989
    assert round(threshold / held.best_value, 2) == 6.01

    # The strong form: concede the control every point it scored and there is
    # still no pass, so no conduct by either arm could have cleared the bar.
    conceded = assess_threshold_support(
        _gate(threshold), support=delta_support(treatment, control, concede_control=True)
    )
    assert conceded.reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert round(conceded.best_value, 6) == 0.011260
    assert round(threshold / conceded.best_value, 2) == 2.66


def test_the_recall_threshold_by_contrast_was_reachable(diagnostic, matched):
    """Not every frozen threshold on this campaign was unreachable.

    Without this the module would be a machine for excusing negatives.
    """

    treatment = arm_ceiling("wide_governed_multiroute", _tasks(diagnostic, "governed"))
    control = arm_ceiling("wide_lexical_arxiv", _tasks(diagnostic, "lexical"))
    threshold = matched["frozen_positive_rule"]["recall_delta_at_least"]
    reach = assess_threshold_support(
        _gate(threshold, "recall_delta"),
        support=delta_support(treatment, control, metric="recall"),
    )
    assert reach.reason is not GateReachReason.THRESHOLD_UNATTAINABLE
    assert reach.best_value >= threshold
    observed = matched["official_metrics"]["delta_governed_minus_lexical"]["avg_recall"]
    assert observed > threshold


def test_negative_control_a_richer_acquisition_flips_the_gate(diagnostic, matched):
    """The gate must be able to say reachable, or unattainable means nothing.

    Same threshold, same control arm, same tasks: only the treatment's measured
    acquisition changes. If this does not flip, the verdict above is not a
    measurement of the campaign but a property of the code.
    """

    control = arm_ceiling("wide_lexical_arxiv", _tasks(diagnostic, "lexical"))
    gate = _gate(matched["frozen_positive_rule"]["iou_delta_at_least"])

    thin = arm_ceiling("thin", _tasks(diagnostic, "governed"))
    assert assess_threshold_support(gate, support=delta_support(thin, control)).reason is (
        GateReachReason.THRESHOLD_UNATTAINABLE
    )

    # One high-gold task fully retrieved -- what the campaign would have needed.
    rich = arm_ceiling(
        "rich",
        [
            TaskAcquisition(
                task_id=t.task_id,
                gold_count=t.gold_count,
                submitted=t.submitted,
                scored_hits=t.scored_hits,
                acquired_gold=(t.gold_count if t.gold_count == 18 else t.acquired_gold),
            )
            for t in _tasks(diagnostic, "governed")
        ],
    )
    assert assess_threshold_support(gate, support=delta_support(rich, control)).reason is (
        GateReachReason.BOTH_OUTCOMES_REACHABLE
    )


def test_the_arm_hands_itself_to_the_programme_margin_check(diagnostic):
    """The ceiling is what attainable_margin was always missing for retrieval."""

    treatment = arm_ceiling("wide_governed_multiroute", _tasks(diagnostic, "governed"))
    capability = as_capability(treatment)
    assert capability.achieved == treatment.observed_iou
    assert capability.ceiling == treatment.ceiling_iou
    assert "never returned by any route" in capability.capability_definition

    # A control that could not reach the treatment's score confounds the contrast.
    handicapped = as_capability(
        arm_ceiling(
            "handicapped",
            [
                TaskAcquisition(
                    task_id=t.task_id,
                    gold_count=t.gold_count,
                    submitted=t.submitted,
                    scored_hits=0,
                    acquired_gold=0,
                )
                for t in _tasks(diagnostic, "governed")
            ],
        )
    )
    verdict = assess_attainable_margin("p2-confounded", winner=capability, baseline=handicapped)
    assert verdict.outcome is Outcome.CANNOT_CHECK
    assert verdict.reason is MarginVerdictReason.BASELINE_CEILING_BELOW_WINNER


def test_unmeasured_acquisition_refuses_to_produce_a_bound(diagnostic):
    """The lexical arm's raw acquisition was never recorded. That is not zero."""

    control = arm_ceiling("wide_lexical_arxiv", _tasks(diagnostic, "lexical"))
    assert control.outcome is Outcome.CANNOT_CHECK
    assert len(control.unmeasured_tasks) == 24

    with pytest.raises(ValueError, match="unmeasured"):
        delta_support(control, control)
    with pytest.raises(ValueError, match="unmeasured"):
        as_capability(control)


def test_a_trace_cannot_score_gold_it_never_acquired():
    with pytest.raises(ValueError, match="never acquired"):
        TaskAcquisition(task_id="t", gold_count=5, submitted=20, scored_hits=3, acquired_gold=1)


def test_acquisition_beyond_the_submission_size_is_not_headroom():
    t = TaskAcquisition(task_id="t", gold_count=40, submitted=20, scored_hits=2, acquired_gold=30)
    assert t.attainable_hits == 20


# ---------------------------------------------------------------------------
# Why the ceiling was low: two of three routes could not emit a scoring identifier
# ---------------------------------------------------------------------------


def test_route_admissibility_is_earned_by_emitting_the_scheme():
    assert classify_route(
        RouteEvidence(route_id="arxiv", scheme="arxiv", records_returned=20, records_carrying_scheme=20)
    ) is RouteAdmissibility.ADMISSIBLE
    assert classify_route(
        RouteEvidence(route_id="openaire", scheme="arxiv", records_returned=20, records_carrying_scheme=0)
    ) is RouteAdmissibility.INADMISSIBLE
    # An empty result convicts the query, not the backend.
    assert classify_route(
        RouteEvidence(route_id="dblp", scheme="arxiv", records_returned=0, records_carrying_scheme=0)
    ) is RouteAdmissibility.UNPROBED
    assert classify_route(
        RouteEvidence(
            route_id="s2", scheme="arxiv", records_returned=9, records_carrying_scheme=0, probed=False
        )
    ) is RouteAdmissibility.UNPROBED


def test_matched_request_counts_hid_a_threefold_exposure_gap(diagnostic):
    """The P2 case: the counts matched and the scoring opportunity did not.

    Route admissibility is taken from the diagnostic's own per-route gold tally
    and the runner's ``no_arxiv_identifier_in_response`` note: arXiv returned 7
    gold identifiers across the slice, OpenAIRE and DBLP returned 0 between them
    while returning records on every OK response.
    """

    agg = diagnostic["aggregate"]
    assert agg["governed_arxiv_raw_gold_hits"] == 7
    assert agg["governed_openaire_raw_gold_hits"] == 0
    assert agg["governed_dblp_raw_gold_hits"] == 0
    assert "zero scorer-gold arXiv identifiers" in agg["note"]

    admissibility = {
        "arxiv": RouteAdmissibility.ADMISSIBLE,
        "openaire": RouteAdmissibility.INADMISSIBLE,
        "dblp": RouteAdmissibility.INADMISSIBLE,
    }
    governed = ExposureAccount(
        arm_id="wide_governed_multiroute",
        scheme="arxiv",
        requests_by_route={"arxiv": 1, "openaire": 1, "dblp": 1},
        admissibility=admissibility,
    )
    lexical = ExposureAccount(
        arm_id="wide_lexical_arxiv",
        scheme="arxiv",
        requests_by_route={"arxiv": 3},
        admissibility=admissibility,
    )

    assert governed.total_requests == lexical.total_requests == 3
    assert governed.admissible_requests == 1
    assert lexical.admissible_requests == 3
    assert governed.scoring_eligible_fraction == pytest.approx(1 / 3)
    assert lexical.scoring_eligible_fraction == 1.0
    assert matched_exposure(governed, lexical) is Outcome.FAIL


def test_negative_control_matched_exposure_can_also_say_pass():
    """A predicate that can only return FAIL is the failure this module names."""

    admissibility = {"arxiv": RouteAdmissibility.ADMISSIBLE, "openaire": RouteAdmissibility.ADMISSIBLE}
    a = ExposureAccount("a", "arxiv", {"arxiv": 2, "openaire": 1}, admissibility)
    b = ExposureAccount("b", "arxiv", {"arxiv": 3}, admissibility)
    assert matched_exposure(a, b) is Outcome.PASS


def test_unprobed_spend_blocks_a_matched_exposure_claim():
    admissibility = {"arxiv": RouteAdmissibility.ADMISSIBLE, "mystery": RouteAdmissibility.UNPROBED}
    a = ExposureAccount("a", "arxiv", {"arxiv": 2, "mystery": 1}, admissibility)
    b = ExposureAccount("b", "arxiv", {"arxiv": 3}, admissibility)
    assert matched_exposure(a, b) is Outcome.CANNOT_CHECK


def test_arms_scored_against_different_schemes_cannot_be_compared():
    a = ExposureAccount("a", "arxiv", {"arxiv": 3}, {"arxiv": RouteAdmissibility.ADMISSIBLE})
    b = ExposureAccount("b", "doi", {"arxiv": 3}, {"arxiv": RouteAdmissibility.ADMISSIBLE})
    with pytest.raises(ValueError, match="different schemes"):
        matched_exposure(a, b)
