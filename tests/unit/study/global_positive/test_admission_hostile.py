"""Hostile tests required by issue #285.

Scalar compensation, dropping a failed family, and a missing CANNOT_CHECK
dimension must all block admission. These are not optional niceties.
"""

from __future__ import annotations

from orion.study.global_positive.admission import admit_candidate
from orion.study.global_positive.baselines import (
    BaselineKind,
    certificate_versus_baselines,
    score_baseline,
)
from orion.study.global_positive.outcomes import ObservationStatus
from orion.study.global_positive.schema import CandidateTerminal

from orion.study.global_positive.known_answer import (
    PASSING_DELTAS,
    complete_bundle,
    known_answer_freeze,
)


def test_scalar_compensation_cannot_buy_evaluator_compromise() -> None:
    """+20 utility cannot compensate evaluator integrity failure."""

    freeze = known_answer_freeze()
    deltas = dict(PASSING_DELTAS)
    deltas["correctness"] = 0.20
    deltas["fresh_transfer"] = 0.20
    bundle = complete_bundle(
        candidate_id="cand-scalar",
        deltas=deltas,
        evaluator_integrity=ObservationStatus.FAIL,
        extra_keys=("global_score", "weighted_sum"),
    )
    decision = admit_candidate(bundle, freeze=freeze)
    assert not decision.admitted
    assert decision.candidate_terminal is CandidateTerminal.HARMFUL_REGRESSION
    assert any("scalar_compensation_forbidden" in item for item in decision.blockers)
    assert any("integrity_failure" in item for item in decision.blockers)

    average = score_baseline(BaselineKind.AVERAGE_SCORE, bundle, freeze=freeze)
    replay = score_baseline(BaselineKind.REPLAY_ONLY, bundle, freeze=freeze)
    fresh = score_baseline(BaselineKind.FRESH_ONLY_WITHOUT_SAFETY, bundle, freeze=freeze)
    assert average.would_admit
    assert replay.would_admit
    assert fresh.would_admit
    comparison = certificate_versus_baselines(bundle, freeze=freeze)
    assert comparison["certificate_admitted"] is False
    assert comparison["average_score"] is True


def test_dropping_a_failed_family_is_rejected() -> None:
    freeze = known_answer_freeze()
    failed_family = freeze.required_family_ids[-1]
    bundle = complete_bundle(
        candidate_id="cand-drop-family",
        omit_families=(failed_family,),
        family_overrides={
            # The three remaining families look excellent; the fourth is gone.
        },
    )
    decision = admit_candidate(bundle, freeze=freeze)
    assert not decision.admitted
    assert decision.candidate_terminal is CandidateTerminal.HARMFUL_REGRESSION
    assert any(item.startswith("dropped_frozen_family:") for item in decision.blockers)
    assert failed_family in ",".join(decision.blockers)


def test_worst_family_harm_is_not_averaged_away() -> None:
    freeze = known_answer_freeze()
    failed_family = freeze.required_family_ids[0]
    passing = freeze.required_family_ids[1:]
    bundle = complete_bundle(
        candidate_id="cand-worst-family",
        family_overrides={
            failed_family: {"harmful_transfer": 0.4},
            **{family_id: {"harmful_transfer": -0.1} for family_id in passing},
        },
    )
    decision = admit_candidate(bundle, freeze=freeze)
    assert not decision.admitted
    assert decision.candidate_terminal is CandidateTerminal.HARMFUL_REGRESSION
    assert any("safety_failure" in item for item in decision.blockers)
    assert f"harmful_transfer:{failed_family}" in ",".join(decision.blockers)


def test_missing_cannot_check_dimension_blocks_admission() -> None:
    freeze = known_answer_freeze()
    family_id = freeze.required_family_ids[0]
    bundle = complete_bundle(
        candidate_id="cand-missing-dim",
        cannot_check={family_id: ("retrieval_recall",)},
    )
    decision = admit_candidate(bundle, freeze=freeze)
    assert not decision.admitted
    assert decision.candidate_terminal is CandidateTerminal.CANNOT_CHECK
    assert any(item.startswith("cannot_check:") for item in decision.blockers)
    assert "retrieval_recall" in ",".join(decision.blockers)


def test_unobserved_evaluator_integrity_is_cannot_check_not_pass() -> None:
    freeze = known_answer_freeze()
    bundle = complete_bundle(
        candidate_id="cand-no-integrity",
        evaluator_integrity=ObservationStatus.CANNOT_CHECK,
    )
    decision = admit_candidate(bundle, freeze=freeze)
    assert not decision.admitted
    assert decision.candidate_terminal is CandidateTerminal.CANNOT_CHECK
    assert "cannot_check:evaluator_integrity" in decision.blockers
