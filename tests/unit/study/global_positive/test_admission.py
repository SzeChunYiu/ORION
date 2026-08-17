from __future__ import annotations

from orion.study.global_positive.admission import admit_candidate, programme_terminal
from orion.study.global_positive.known_answer import (
    complete_bundle,
    harmful_history,
    known_answer_freeze,
)
from orion.study.global_positive.schema import CandidateTerminal, ProgrammeTerminal


def test_complete_noninferior_vector_with_utility_gain_is_admitted() -> None:
    freeze = known_answer_freeze()
    decision = admit_candidate(complete_bundle(), freeze=freeze)
    assert decision.admitted
    assert decision.candidate_terminal is CandidateTerminal.GLOBAL_POSITIVE
    assert decision.blockers == ()
    assert decision.utility_improvements
    assert decision.freeze_hash == freeze.fingerprint


def test_published_unbound_freeze_blocks_even_with_synthetic_numbers() -> None:
    decision = admit_candidate(complete_bundle())
    assert not decision.admitted
    assert decision.candidate_terminal is CandidateTerminal.CANNOT_CHECK
    assert any(item.startswith("cannot_check:unbound_family:") for item in decision.blockers)


def test_noninferior_without_utility_gain_is_null() -> None:
    freeze = known_answer_freeze()
    bundle = complete_bundle(deltas={
        "abstention_correctness": 0.0,
        "correctness": 0.0,
        "cost": 0.0,
        "false_authority": 0.0,
        "fresh_transfer": 0.0,
        "harmful_transfer": 0.0,
        "obstruction_safety": 0.0,
        "retrieval_recall": 0.0,
    })
    decision = admit_candidate(bundle, freeze=freeze)
    assert not decision.admitted
    assert decision.candidate_terminal is CandidateTerminal.NULL_NONINFERIOR_ONLY


def test_cost_regression_with_utility_gain_is_local_tradeoff() -> None:
    freeze = known_answer_freeze()
    bundle = complete_bundle(deltas={
        "abstention_correctness": 0.0,
        "correctness": 0.05,
        "cost": 0.5,
        "false_authority": 0.0,
        "fresh_transfer": 0.03,
        "harmful_transfer": 0.0,
        "obstruction_safety": 0.0,
        "retrieval_recall": 0.0,
    })
    decision = admit_candidate(bundle, freeze=freeze)
    assert not decision.admitted
    assert decision.candidate_terminal is CandidateTerminal.LOCAL_POSITIVE_WITH_TRADEOFF


def test_negative_history_recurrence_blocks() -> None:
    freeze = known_answer_freeze()
    bundle = complete_bundle(failure_classes=("replay_overfit_harmful_transfer",))
    decision = admit_candidate(
        bundle,
        freeze=freeze,
        history=harmful_history("replay_overfit_harmful_transfer"),
    )
    assert not decision.admitted
    assert decision.candidate_terminal is CandidateTerminal.HARMFUL_REGRESSION
    assert any("negative_history_recurrence" in item for item in decision.blockers)


def test_retuned_freeze_hash_does_not_match_expected() -> None:
    freeze = known_answer_freeze()
    decision = admit_candidate(
        complete_bundle(),
        freeze=freeze,
        expected_freeze_hash="0" * 64,
    )
    assert not decision.admitted
    assert "freeze_hash_mismatch" in decision.blockers


def test_one_round_cannot_close_global_positive_supported() -> None:
    decision = programme_terminal(
        admitted_round_count=1,
        baseline_beaten=True,
        verification_receipt=True,
    )
    assert decision.terminal is ProgrammeTerminal.CANNOT_CHECK
    assert "insufficient_prospective_rounds" in decision.reasons
    assert decision.min_rounds_required == 2
