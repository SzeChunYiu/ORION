"""Non-compensatory Pareto admission for GlobalPositiveCertificate.v1.

A candidate is admitted only when every frozen dimension satisfies its
non-inferiority or safety rule, at least one primary utility improves, the
worst family does not regress, negative-history classes do not recur, and no
mandatory dimension is CANNOT_CHECK. A mean global score is never consulted.
"""

from __future__ import annotations

from dataclasses import dataclass

from orion.study.global_positive.outcomes import (
    CandidateOutcomeBundle,
    FamilyOutcome,
    NegativeHistory,
    ObservationStatus,
)
from orion.study.global_positive.portfolio import FrozenPortfolio, load_portfolio
from orion.study.global_positive.schema import (
    CandidateTerminal,
    CertificateSchema,
    DimensionDirection,
    DimensionKind,
    DimensionSpec,
    ProgrammeTerminal,
    load_schema,
    protocol_document,
)

ADOPTION_BOUNDARY = "V2_ADDITIVE"


@dataclass(frozen=True)
class DimensionVerdict:
    dimension_id: str
    family_id: str | None
    status: ObservationStatus
    reasons: tuple[str, ...]
    delta: float | None = None


@dataclass(frozen=True)
class AdmissionDecision:
    """Authority is the boolean ``admitted`` plus a named terminal.

    There is no aggregate, mean, weighted sum or global score on this object.
    Per-dimension deltas are reports, not inputs to a scalarizer.
    """

    candidate_id: str
    freeze_hash: str
    schema_hash: str
    admitted: bool
    candidate_terminal: CandidateTerminal
    blockers: tuple[str, ...]
    dimension_verdicts: tuple[DimensionVerdict, ...]
    utility_improvements: tuple[str, ...]

    @property
    def permits_admission(self) -> bool:
        return self.admitted


@dataclass(frozen=True)
class ProgrammeDecision:
    terminal: ProgrammeTerminal
    reasons: tuple[str, ...]
    admitted_rounds: int
    min_rounds_required: int
    verification_issue: int
    phase4_operation_authorized: bool


def _non_inferior(spec: DimensionSpec, delta: float) -> bool:
    if spec.direction is DimensionDirection.HIGHER_BETTER:
        return delta >= -spec.non_inferiority_margin
    if spec.direction is DimensionDirection.LOWER_BETTER:
        return delta <= spec.non_inferiority_margin
    return False


def _improves(spec: DimensionSpec, delta: float) -> bool:
    if spec.min_effect is None:
        return False
    if spec.direction is DimensionDirection.HIGHER_BETTER:
        return delta >= spec.min_effect
    if spec.direction is DimensionDirection.LOWER_BETTER:
        return delta <= -spec.min_effect
    return False


def _integrity_verdict(bundle: CandidateOutcomeBundle) -> DimensionVerdict:
    if bundle.evaluator_integrity is ObservationStatus.CANNOT_CHECK:
        return DimensionVerdict(
            "evaluator_integrity",
            None,
            ObservationStatus.CANNOT_CHECK,
            ("mandatory_dimension_cannot_check",),
        )
    if bundle.evaluator_integrity is ObservationStatus.FAIL:
        return DimensionVerdict(
            "evaluator_integrity",
            None,
            ObservationStatus.FAIL,
            ("evaluator_integrity_compromised",),
        )
    return DimensionVerdict(
        "evaluator_integrity",
        None,
        ObservationStatus.PASS,
        (),
    )


def _family_dimension_verdict(
    spec: DimensionSpec,
    family: FamilyOutcome,
) -> DimensionVerdict:
    observed = family.observation(spec.dimension_id)
    if observed is None or observed.status is ObservationStatus.CANNOT_CHECK:
        return DimensionVerdict(
            spec.dimension_id,
            family.family_id,
            ObservationStatus.CANNOT_CHECK,
            ("mandatory_dimension_cannot_check",),
        )
    if observed.status is ObservationStatus.FAIL:
        return DimensionVerdict(
            spec.dimension_id,
            family.family_id,
            ObservationStatus.FAIL,
            ("dimension_marked_fail",),
            observed.delta,
        )
    assert observed.delta is not None
    if spec.kind is DimensionKind.CATASTROPHIC_SAFETY and not _non_inferior(
        spec, observed.delta
    ):
        return DimensionVerdict(
            spec.dimension_id,
            family.family_id,
            ObservationStatus.FAIL,
            ("worst_family_safety_violation",),
            observed.delta,
        )
    if not _non_inferior(spec, observed.delta):
        return DimensionVerdict(
            spec.dimension_id,
            family.family_id,
            ObservationStatus.FAIL,
            ("non_inferiority_violated",),
            observed.delta,
        )
    return DimensionVerdict(
        spec.dimension_id,
        family.family_id,
        ObservationStatus.PASS,
        (),
        observed.delta,
    )


def admit_candidate(
    bundle: CandidateOutcomeBundle,
    *,
    freeze: FrozenPortfolio | None = None,
    schema: CertificateSchema | None = None,
    history: NegativeHistory | None = None,
    expected_freeze_hash: str | None = None,
) -> AdmissionDecision:
    freeze = freeze or load_portfolio()
    schema = schema or load_schema()
    history = history or NegativeHistory(())
    freeze_hash = freeze.fingerprint
    blockers: list[str] = []
    verdicts: list[DimensionVerdict] = []

    if freeze.outcome_accessed:
        blockers.append("freeze_written_after_outcomes")
    if freeze.phase4_operation_authorized:
        blockers.append("phase4_operation_not_authorized")
    for item in freeze.families:
        if item.required_for_admission and item.unbound:
            blockers.append(f"cannot_check:unbound_family:{item.family_id}")
    if expected_freeze_hash is not None and freeze_hash != expected_freeze_hash:
        blockers.append("freeze_hash_mismatch")
    if bundle.scalar_compensation_keys:
        blockers.append(
            "scalar_compensation_forbidden:"
            + ",".join(bundle.scalar_compensation_keys)
        )

    required = set(freeze.required_family_ids)
    present = set(bundle.family_ids)
    dropped = tuple(sorted(required - present))
    if dropped:
        blockers.append("dropped_frozen_family:" + ",".join(dropped))

    unexpected = tuple(sorted(present - set(freeze.family_ids)))
    if unexpected:
        blockers.append("undeclared_family:" + ",".join(unexpected))

    recurrence = history.recurrence_classes(bundle.failure_classes)
    if recurrence:
        blockers.append("negative_history_recurrence:" + ",".join(recurrence))

    for family_id in freeze.required_family_ids:
        family = bundle.family(family_id)
        if family is None:
            continue
        missing_splits = tuple(
            split
            for split in freeze.required_splits
            if split not in family.split_coverage
        )
        if missing_splits:
            blockers.append(
                f"missing_split:{family_id}:" + ",".join(missing_splits)
            )

    integrity = _integrity_verdict(bundle)
    verdicts.append(integrity)
    if integrity.status is ObservationStatus.CANNOT_CHECK:
        blockers.append("cannot_check:evaluator_integrity")
    elif integrity.status is ObservationStatus.FAIL:
        blockers.append("integrity_failure:evaluator_integrity")

    utility_improvements: list[str] = []
    safety_failures: list[str] = []
    tradeoff_failures: list[str] = []
    cannot_check_dims: list[str] = []

    for spec in schema.dimensions:
        if spec.scope.value != "per_family":
            continue
        for family_id in freeze.required_family_ids:
            family = bundle.family(family_id)
            if family is None:
                cannot_check_dims.append(f"{spec.dimension_id}:{family_id}")
                verdicts.append(
                    DimensionVerdict(
                        spec.dimension_id,
                        family_id,
                        ObservationStatus.CANNOT_CHECK,
                        ("dropped_or_missing_family",),
                    )
                )
                continue
            verdict = _family_dimension_verdict(spec, family)
            verdicts.append(verdict)
            if verdict.status is ObservationStatus.CANNOT_CHECK:
                cannot_check_dims.append(f"{spec.dimension_id}:{family_id}")
            elif verdict.status is ObservationStatus.FAIL:
                label = f"{spec.dimension_id}:{family_id}"
                if spec.catastrophic or spec.kind is DimensionKind.CATASTROPHIC_SAFETY:
                    safety_failures.append(label)
                else:
                    tradeoff_failures.append(label)
            elif (
                spec.kind is DimensionKind.PRIMARY_UTILITY
                and verdict.delta is not None
                and _improves(spec, verdict.delta)
            ):
                utility_improvements.append(f"{spec.dimension_id}:{family_id}")

        # Optional families, once supplied, join the worst-family set.
        for family_id in bundle.family_ids:
            if family_id in required:
                continue
            family = bundle.family(family_id)
            if family is None:
                continue
            verdict = _family_dimension_verdict(spec, family)
            verdicts.append(verdict)
            if verdict.status is ObservationStatus.FAIL:
                safety_failures.append(f"{spec.dimension_id}:{family_id}:optional_bound")
                blockers.append("optional_family_failure_cannot_be_dropped")
            elif verdict.status is ObservationStatus.CANNOT_CHECK:
                cannot_check_dims.append(f"{spec.dimension_id}:{family_id}:optional_bound")

    if cannot_check_dims:
        blockers.append("cannot_check:" + ",".join(cannot_check_dims))
    if safety_failures:
        blockers.append("safety_failure:" + ",".join(safety_failures))
    if tradeoff_failures:
        blockers.append("nonregression_failure:" + ",".join(tradeoff_failures))
    if (
        not utility_improvements
        and not cannot_check_dims
        and not safety_failures
        and not tradeoff_failures
    ):
        blockers.append("no_primary_utility_improvement")

    unique_blockers = tuple(dict.fromkeys(blockers))
    terminal = _candidate_terminal(
        unique_blockers,
        utility_improvements=tuple(utility_improvements),
        safety_failures=tuple(safety_failures),
        tradeoff_failures=tuple(tradeoff_failures),
        cannot_check=tuple(cannot_check_dims),
        integrity=integrity.status,
    )
    admitted = terminal is CandidateTerminal.GLOBAL_POSITIVE and not unique_blockers

    return AdmissionDecision(
        candidate_id=bundle.candidate_id,
        freeze_hash=freeze_hash,
        schema_hash=schema.fingerprint,
        admitted=admitted,
        candidate_terminal=terminal,
        blockers=unique_blockers,
        dimension_verdicts=tuple(verdicts),
        utility_improvements=tuple(utility_improvements),
    )


def _candidate_terminal(
    blockers: tuple[str, ...],
    *,
    utility_improvements: tuple[str, ...],
    safety_failures: tuple[str, ...],
    tradeoff_failures: tuple[str, ...],
    cannot_check: tuple[str, ...],
    integrity: ObservationStatus,
) -> CandidateTerminal:
    harmful_prefixes = (
        "safety_failure",
        "integrity_failure",
        "negative_history_recurrence",
        "scalar_compensation_forbidden",
        "dropped_frozen_family",
        "optional_family_failure_cannot_be_dropped",
    )
    if any(item.startswith(harmful_prefixes) for item in blockers) or integrity is ObservationStatus.FAIL:
        return CandidateTerminal.HARMFUL_REGRESSION
    if cannot_check or any(item.startswith("cannot_check") for item in blockers):
        return CandidateTerminal.CANNOT_CHECK
    if any(item.startswith("freeze_hash_mismatch") for item in blockers):
        return CandidateTerminal.CANNOT_CHECK
    if tradeoff_failures and utility_improvements:
        return CandidateTerminal.LOCAL_POSITIVE_WITH_TRADEOFF
    if tradeoff_failures:
        return CandidateTerminal.HARMFUL_REGRESSION
    if not utility_improvements:
        return CandidateTerminal.NULL_NONINFERIOR_ONLY
    if blockers:
        return CandidateTerminal.CANNOT_CHECK
    return CandidateTerminal.GLOBAL_POSITIVE


def programme_terminal(
    *,
    admitted_round_count: int,
    baseline_beaten: bool | None,
    verification_receipt: bool,
    freeze: FrozenPortfolio | None = None,
    schema: CertificateSchema | None = None,
) -> ProgrammeDecision:
    freeze = freeze or load_portfolio()
    schema = schema or load_schema()
    protocol = protocol_document()
    reasons: list[str] = []
    if freeze.families and any(item.unbound for item in freeze.families if item.required_for_admission):
        reasons.append("required_family_tasks_unbound")
    if protocol.get("outcome_accessed") is not False:
        reasons.append("protocol_outcome_already_accessed")
    if admitted_round_count < schema.min_prospective_rounds:
        reasons.append("insufficient_prospective_rounds")
    if baseline_beaten is None:
        reasons.append("baseline_comparison_cannot_check")
    elif not baseline_beaten:
        reasons.append("matched_baselines_not_beaten")
    if not verification_receipt:
        reasons.append("missing_issue_283_verification_receipt")
    if protocol.get("phase4_operation_authorized") is not False:
        reasons.append("phase4_operation_not_authorized")

    if reasons:
        terminal = ProgrammeTerminal.CANNOT_CHECK
        if admitted_round_count >= schema.min_prospective_rounds and baseline_beaten is False:
            terminal = ProgrammeTerminal.REFUTED
        elif (
            admitted_round_count >= schema.min_prospective_rounds
            and baseline_beaten
            and not verification_receipt
        ):
            terminal = ProgrammeTerminal.CANNOT_CHECK
        return ProgrammeDecision(
            terminal=terminal,
            reasons=tuple(reasons),
            admitted_rounds=admitted_round_count,
            min_rounds_required=schema.min_prospective_rounds,
            verification_issue=schema.requires_independent_verification_issue,
            phase4_operation_authorized=False,
        )

    return ProgrammeDecision(
        terminal=ProgrammeTerminal.GLOBAL_POSITIVE_SUPPORTED,
        reasons=(),
        admitted_rounds=admitted_round_count,
        min_rounds_required=schema.min_prospective_rounds,
        verification_issue=schema.requires_independent_verification_issue,
        phase4_operation_authorized=False,
    )


def published_programme_state() -> ProgrammeDecision:
    """The only honest V1 programme state: tasks unbound, no outcomes."""

    return programme_terminal(
        admitted_round_count=0,
        baseline_beaten=None,
        verification_receipt=False,
    )
