"""Baseline stubs for GlobalPositiveCertificate.v1.

These are counterfactual decision rules. They are not authority. The
certificate scores a bundle against them once outcomes exist; until then they
return CANNOT_CHECK.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.study.global_positive.admission import admit_candidate
from orion.study.global_positive.outcomes import (
    CandidateOutcomeBundle,
    ObservationStatus,
)
from orion.study.global_positive.portfolio import FrozenPortfolio, load_portfolio
from orion.study.global_positive.schema import CandidateTerminal, load_schema

ADOPTION_BOUNDARY = "V2_ADDITIVE"


class BaselineKind(str, Enum):
    AVERAGE_SCORE = "average_score"
    REPLAY_ONLY = "replay_only"
    FRESH_ONLY_WITHOUT_SAFETY = "fresh_only_without_safety"
    P5_STAGED_ACCEPTANCE = "p5_staged_acceptance"
    NO_CHANGE_CONSERVATIVE = "no_change_conservative"
    CONTINUAL_OPTIMIZER_UNAVAILABLE = "continual_optimizer_unavailable"
    ORACLE_PARETO_CEILING = "oracle_pareto_ceiling"


@dataclass(frozen=True)
class BaselineDecision:
    kind: BaselineKind
    would_admit: bool
    terminal: CandidateTerminal
    reasons: tuple[str, ...]
    authority: str = "baseline_stub_not_authority"


def _family_delta(bundle: CandidateOutcomeBundle, dimension_id: str) -> list[float]:
    values: list[float] = []
    for family in bundle.family_outcomes:
        observed = family.observation(dimension_id)
        if observed is None or observed.delta is None:
            continue
        if observed.status is ObservationStatus.CANNOT_CHECK:
            continue
        values.append(observed.delta)
    return values


def _any_positive(bundle: CandidateOutcomeBundle, dimension_id: str) -> bool:
    return any(value > 0 for value in _family_delta(bundle, dimension_id))


def score_baseline(
    kind: BaselineKind,
    bundle: CandidateOutcomeBundle,
    *,
    freeze: FrozenPortfolio | None = None,
) -> BaselineDecision:
    freeze = freeze or load_portfolio()
    schema = load_schema()
    if any(item.unbound for item in freeze.families if item.required_for_admission):
        if not bundle.family_outcomes:
            return BaselineDecision(
                kind,
                False,
                CandidateTerminal.CANNOT_CHECK,
                ("required_family_tasks_unbound",),
            )

    if kind is BaselineKind.CONTINUAL_OPTIMIZER_UNAVAILABLE:
        return BaselineDecision(
            kind,
            False,
            CandidateTerminal.CANNOT_CHECK,
            ("official_continual_optimizer_baseline_unbound",),
        )
    if kind is BaselineKind.ORACLE_PARETO_CEILING:
        return BaselineDecision(
            kind,
            False,
            CandidateTerminal.CANNOT_CHECK,
            ("oracle_ceiling_is_analysis_only",),
        )
    if kind is BaselineKind.NO_CHANGE_CONSERVATIVE:
        return BaselineDecision(
            kind,
            False,
            CandidateTerminal.NULL_NONINFERIOR_ONLY,
            ("no_change_never_admits_a_candidate",),
        )
    if kind is BaselineKind.AVERAGE_SCORE:
        deltas: list[float] = []
        for spec in schema.dimensions:
            if spec.scope.value != "per_family":
                continue
            deltas.extend(_family_delta(bundle, spec.dimension_id))
        if not deltas:
            return BaselineDecision(
                kind, False, CandidateTerminal.CANNOT_CHECK, ("no_numeric_deltas",)
            )
        mean = sum(deltas) / len(deltas)
        would = mean > 0
        return BaselineDecision(
            kind,
            would,
            CandidateTerminal.GLOBAL_POSITIVE if would else CandidateTerminal.NULL_NONINFERIOR_ONLY,
            ("mean_delta_used_as_forbidden_authority_counterfactual",),
        )
    if kind is BaselineKind.REPLAY_ONLY:
        would = _any_positive(bundle, "correctness")
        return BaselineDecision(
            kind,
            would,
            CandidateTerminal.GLOBAL_POSITIVE if would else CandidateTerminal.NULL_NONINFERIOR_ONLY,
            ("replay_or_correctness_gain_ignores_fresh_and_safety",),
        )
    if kind is BaselineKind.FRESH_ONLY_WITHOUT_SAFETY:
        would = _any_positive(bundle, "fresh_transfer")
        return BaselineDecision(
            kind,
            would,
            CandidateTerminal.GLOBAL_POSITIVE if would else CandidateTerminal.NULL_NONINFERIOR_ONLY,
            ("fresh_gain_ignores_evaluator_integrity_and_worst_family",),
        )
    if kind is BaselineKind.P5_STAGED_ACCEPTANCE:
        # Stub: replay+fresh without cross-family Pareto or evaluator integrity.
        would = _any_positive(bundle, "correctness") and _any_positive(
            bundle, "fresh_transfer"
        )
        return BaselineDecision(
            kind,
            would,
            CandidateTerminal.GLOBAL_POSITIVE if would else CandidateTerminal.CANNOT_CHECK,
            ("p5_staged_stub_does_not_encode_cross_family_pareto",),
        )
    raise ValueError(f"unknown baseline {kind}")


def score_all_baselines(
    bundle: CandidateOutcomeBundle,
    *,
    freeze: FrozenPortfolio | None = None,
) -> tuple[BaselineDecision, ...]:
    freeze = freeze or load_portfolio()
    return tuple(score_baseline(kind, bundle, freeze=freeze) for kind in BaselineKind)


def certificate_versus_baselines(
    bundle: CandidateOutcomeBundle,
    *,
    freeze: FrozenPortfolio | None = None,
) -> dict[str, bool | str]:
    freeze = freeze or load_portfolio()
    certificate = admit_candidate(bundle, freeze=freeze)
    baselines = score_all_baselines(bundle, freeze=freeze)
    return {
        "certificate_admitted": certificate.admitted,
        "certificate_terminal": certificate.candidate_terminal.value,
        **{item.kind.value: item.would_admit for item in baselines},
    }
