"""Section 6 -- the frozen criterion evaluator.

No check anywhere in this module consults the system under test about whether it
succeeded. A criterion with no implemented check returns CANNOT_CHECK, never a
pass and never a zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .identity import CheckableCriterion, CriterionCheck
from .packet import FrozenLiveResearchPacket
from .tasks import FrozenTaskBinding, ProtectedTargetGold
from .trace import EvidenceUseReport, RawTrialTrace, classify_evidence_use


class CriterionStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class CriterionResult:
    criterion_id: str
    check: CriterionCheck
    status: CriterionStatus
    detail: str = ""
    observed: int | None = None


@dataclass(frozen=True)
class TaskOutcomeInput:
    """Everything the frozen evaluator reads. None of it is a self-report."""

    task_id: str
    trace: RawTrialTrace
    answer_text: str
    cited_ids: tuple[str, ...]
    residual_ids: tuple[str, ...] = ()
    orion_resource_units: float | None = None
    baseline_resource_units: float | None = None


def evaluate_task(
    packet: FrozenLiveResearchPacket,
    outcome: TaskOutcomeInput,
) -> tuple[CriterionResult, ...]:
    """Run every frozen criterion for one task. Every criterion returns a result.

    There is no early exit and no exclusion: an uncheckable criterion produces
    CANNOT_CHECK rather than being skipped, because "could not check" and
    "checked and passed" are different facts and a suite that drops the first
    reports the second.
    """

    binding = packet.binding(outcome.task_id)
    if binding is None:
        raise ValueError(f"unknown task for this packet: {outcome.task_id}")
    report = classify_evidence_use(outcome.trace, cited_ids=outcome.cited_ids)
    gold = binding.gold
    results: list[CriterionResult] = []
    for criterion in binding.criteria:
        results.append(_evaluate_criterion(criterion, packet, binding, outcome, report, gold))
    return tuple(results)


def _evaluate_criterion(
    criterion: CheckableCriterion,
    packet: FrozenLiveResearchPacket,
    binding: FrozenTaskBinding,
    outcome: TaskOutcomeInput,
    report: EvidenceUseReport,
    gold: ProtectedTargetGold | None,
) -> CriterionResult:
    check = criterion.check
    if check is CriterionCheck.EVERY_CITATION_IN_RAW_TRACE:
        ungrounded = report.cited_but_unretrieved
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if not ungrounded else CriterionStatus.FAIL,
            "" if not ungrounded else f"ungrounded citations: {list(ungrounded)}",
            observed=len(ungrounded),
        )
    if check is CriterionCheck.DISTINCT_ROUTE_FAMILIES:
        observed = len(outcome.trace.productive_route_kinds)
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if observed >= criterion.threshold else CriterionStatus.FAIL,
            f"{observed} productive route families, {criterion.threshold} required",
            observed=observed,
        )
    if check is CriterionCheck.INDEPENDENT_CORROBORATION:
        observed = sum(
            1
            for item_id in outcome.trace.item_ids
            if len({backend for _, backend in outcome.trace.routes_for(item_id)}) > 1
        )
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if observed >= criterion.threshold else CriterionStatus.FAIL,
            f"{observed} items captured by distinct backends",
            observed=observed,
        )
    if check is CriterionCheck.RETRIEVAL_FULLY_CLASSIFIED:
        classified = {item for item, _ in report.classes}
        unclassified = [item for item in outcome.trace.item_ids if item not in classified]
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if not unclassified else CriterionStatus.FAIL,
            "" if not unclassified else f"unclassified retrieval: {unclassified}",
            observed=len(unclassified),
        )
    if check is CriterionCheck.PROTECTED_GOLD_TOKENS_RECOVERED:
        if gold is None:
            return CriterionResult(
                criterion.criterion_id,
                check,
                CriterionStatus.CANNOT_CHECK,
                "no protected gold is bound for this task",
            )
        missing = [item for item in gold.required_answer_tokens if item not in outcome.answer_text]
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if not missing else CriterionStatus.FAIL,
            # The tokens themselves are never echoed: a failure detail that
            # printed the answer key would leak the gold into the run record.
            f"{len(missing)} of {len(gold.required_answer_tokens)} gold tokens absent",
            observed=len(missing),
        )
    if check is CriterionCheck.PROTECTED_GOLD_ANCHOR_CITED:
        if gold is None:
            return CriterionResult(
                criterion.criterion_id,
                check,
                CriterionStatus.CANNOT_CHECK,
                "no protected gold is bound for this task",
            )
        cited = gold.anchor_source_id in outcome.cited_ids
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if cited else CriterionStatus.FAIL,
            "anchor cited" if cited else "protected anchor absent from cited evidence",
            observed=int(cited),
        )
    if check is CriterionCheck.NON_RECOVERY_DECLARES_RESIDUAL:
        if gold is None:
            return CriterionResult(
                criterion.criterion_id,
                check,
                CriterionStatus.CANNOT_CHECK,
                "recovery cannot be judged without bound ground truth",
            )
        recovered = all(item in outcome.answer_text for item in gold.required_answer_tokens)
        ok = recovered or bool(outcome.residual_ids)
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if ok else CriterionStatus.FAIL,
            "" if ok else "target not recovered and no residual declared",
            observed=len(outcome.residual_ids),
        )
    if check is CriterionCheck.RESOURCE_WITHIN_MATCHED_LIMIT:
        if outcome.orion_resource_units is None or outcome.baseline_resource_units is None:
            return CriterionResult(
                criterion.criterion_id,
                check,
                CriterionStatus.CANNOT_CHECK,
                "resource use for one or both arms was not observed",
            )
        ceiling = min(
            packet.limits.budget_units,
            outcome.baseline_resource_units * packet.limits.max_orion_to_baseline_ratio,
        )
        within = outcome.orion_resource_units <= ceiling
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if within else CriterionStatus.FAIL,
            f"{outcome.orion_resource_units} units against a ceiling of {ceiling}",
        )
    # Unreachable while CriterionCheck and this dispatch stay in step; kept so a
    # new member surfaces as CANNOT_CHECK rather than as a silent pass.
    return CriterionResult(  # pragma: no cover - defensive
        criterion.criterion_id,
        check,
        CriterionStatus.CANNOT_CHECK,
        f"no frozen check is implemented for {check.value}",
    )
