from __future__ import annotations

from orion.study.global_positive.baselines import (
    BaselineKind,
    score_all_baselines,
    score_baseline,
)
from orion.study.global_positive.outcomes import CandidateOutcomeBundle, ObservationStatus
from orion.study.global_positive.schema import CandidateTerminal

from orion.study.global_positive.known_answer import complete_bundle, known_answer_freeze


def test_published_unbound_portfolio_makes_empty_baselines_cannot_check() -> None:
    empty = CandidateOutcomeBundle(
        candidate_id="none",
        candidate_digest="b" * 64,
        family_outcomes=(),
        evaluator_integrity=ObservationStatus.CANNOT_CHECK,
        failure_classes=(),
    )
    decision = score_baseline(BaselineKind.AVERAGE_SCORE, empty)
    assert decision.would_admit is False
    assert decision.terminal is CandidateTerminal.CANNOT_CHECK
    assert decision.authority == "baseline_stub_not_authority"


def test_continual_optimizer_and_oracle_remain_cannot_check() -> None:
    freeze = known_answer_freeze()
    bundle = complete_bundle()
    continual = score_baseline(
        BaselineKind.CONTINUAL_OPTIMIZER_UNAVAILABLE, bundle, freeze=freeze
    )
    oracle = score_baseline(BaselineKind.ORACLE_PARETO_CEILING, bundle, freeze=freeze)
    assert continual.terminal is CandidateTerminal.CANNOT_CHECK
    assert oracle.terminal is CandidateTerminal.CANNOT_CHECK
    assert not continual.would_admit
    assert not oracle.would_admit


def test_no_change_conservative_never_admits() -> None:
    freeze = known_answer_freeze()
    decision = score_baseline(
        BaselineKind.NO_CHANGE_CONSERVATIVE, complete_bundle(), freeze=freeze
    )
    assert decision.would_admit is False
    assert decision.terminal is CandidateTerminal.NULL_NONINFERIOR_ONLY


def test_all_baseline_stubs_are_scorable_once_outcomes_exist() -> None:
    freeze = known_answer_freeze()
    results = score_all_baselines(complete_bundle(), freeze=freeze)
    assert {item.kind for item in results} == set(BaselineKind)
    by_kind = {item.kind: item for item in results}
    assert by_kind[BaselineKind.AVERAGE_SCORE].would_admit
    assert by_kind[BaselineKind.REPLAY_ONLY].would_admit
    assert by_kind[BaselineKind.FRESH_ONLY_WITHOUT_SAFETY].would_admit
    assert by_kind[BaselineKind.P5_STAGED_ACCEPTANCE].would_admit
