"""Independent scoring for prospective Self-ORION V3 revision decisions.

Decision correctness is evaluated against the protected suite, never against a
policy's own trace.  Post-revision fresh-transfer/harm evidence is a separate
record family bound to the exact policy decision digest.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from orion.study.p5.revision_level_v3_freeze import validate_protected_suite
from orion.study.p5.revision_level_v3_policies import RevisionPolicyDecision
from orion.transfer.v2.canonical import content_digest


@dataclass(frozen=True)
class RevisionDecisionCaseScore:
    case_id: str
    selected_revision_class: str
    gold_revision_class: str
    correct: bool
    false_broad_revision: bool
    correct_unresolved: bool
    diagnostic_actions: int
    diagnostic_cost: float


@dataclass(frozen=True)
class RevisionDecisionScoreReport:
    policy_id: str
    total_cases: int
    correct_revision_count: int
    incorrect_revision_count: int
    revision_accuracy: float
    false_broad_revision_count: int
    false_broad_revision_rate: float
    correct_unresolved_count: int
    correct_unresolved_denominator: int
    total_diagnostic_actions: int
    total_diagnostic_cost: float
    analysis_only: bool
    eligible_for_superiority_claim: bool
    case_scores: tuple[RevisionDecisionCaseScore, ...]


@dataclass(frozen=True)
class RevisionExecutionOutcome:
    policy_id: str
    case_id: str
    decision_digest: str
    fresh_transfer_applicable: bool
    fresh_transfer_success: bool
    harmful_regression: bool
    preservation_satisfied: bool
    evaluator_or_authority_violation: bool
    digest: str

    @classmethod
    def build(
        cls,
        *,
        policy_id: str,
        case_id: str,
        decision_digest: str,
        fresh_transfer_applicable: bool,
        fresh_transfer_success: bool,
        harmful_regression: bool,
        preservation_satisfied: bool,
        evaluator_or_authority_violation: bool,
    ) -> "RevisionExecutionOutcome":
        payload = {
            "version": "SelfOrionV3RevisionExecutionOutcome.v1",
            "policy_id": str(policy_id),
            "case_id": str(case_id),
            "decision_digest": str(decision_digest),
            "fresh_transfer_applicable": bool(fresh_transfer_applicable),
            "fresh_transfer_success": bool(fresh_transfer_success),
            "harmful_regression": bool(harmful_regression),
            "preservation_satisfied": bool(preservation_satisfied),
            "evaluator_or_authority_violation": bool(evaluator_or_authority_violation),
            "grants_scientific_authority": False,
        }
        result = cls(
            policy_id=payload["policy_id"],
            case_id=payload["case_id"],
            decision_digest=payload["decision_digest"],
            fresh_transfer_applicable=payload["fresh_transfer_applicable"],
            fresh_transfer_success=payload["fresh_transfer_success"],
            harmful_regression=payload["harmful_regression"],
            preservation_satisfied=payload["preservation_satisfied"],
            evaluator_or_authority_violation=payload["evaluator_or_authority_violation"],
            digest=content_digest(payload),
        )
        result.verify()
        return result

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "SelfOrionV3RevisionExecutionOutcome.v1",
            "policy_id": self.policy_id,
            "case_id": self.case_id,
            "decision_digest": self.decision_digest,
            "fresh_transfer_applicable": self.fresh_transfer_applicable,
            "fresh_transfer_success": self.fresh_transfer_success,
            "harmful_regression": self.harmful_regression,
            "preservation_satisfied": self.preservation_satisfied,
            "evaluator_or_authority_violation": self.evaluator_or_authority_violation,
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        if not self.policy_id or not self.case_id or not self.decision_digest:
            raise ValueError("execution outcome identities are required")
        if self.fresh_transfer_success and not self.fresh_transfer_applicable:
            raise ValueError("fresh transfer success requires applicable fresh-transfer evaluation")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("execution outcome digest mismatch")


@dataclass(frozen=True)
class RevisionExecutionScoreReport:
    policy_id: str
    outcome_count: int
    fresh_transfer_denominator: int
    fresh_transfer_success_count: int
    fresh_transfer_success_rate: float | None
    harmful_regression_count: int
    preservation_violation_count: int
    authority_violation_count: int


def _case_index(suite: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    return {str(case["case_id"]): case for case in suite["cases"]}  # type: ignore[index]


def _decision_index(decisions: Sequence[RevisionPolicyDecision]) -> dict[str, RevisionPolicyDecision]:
    result: dict[str, RevisionPolicyDecision] = {}
    for decision in decisions:
        decision.verify()
        if decision.case_id in result:
            raise ValueError(f"decision set contains duplicate case: {decision.case_id}")
        result[decision.case_id] = decision
    return result


def _diagnostic_cost(case: Mapping[str, object], decision: RevisionPolicyDecision) -> float:
    raw_actions = case.get("allowed_diagnostics")
    if not isinstance(raw_actions, list):
        raise ValueError("protected case allowed_diagnostics must be an array")
    costs = {
        str(action["action_id"]): float(action["cost"])
        for action in raw_actions
        if isinstance(action, Mapping)
    }
    unknown = set(decision.diagnostic_actions) - set(costs)
    if unknown:
        raise ValueError(f"decision uses unavailable diagnostic: {sorted(unknown)}")
    spent = sum(costs[action] for action in decision.diagnostic_actions)
    budget = float(case.get("diagnostic_budget", 0.0))
    if spent > budget + 1e-12:
        raise ValueError("decision exceeds protected case diagnostic budget")
    return spent


def score_revision_decisions(
    protected_suite: Mapping[str, object],
    decisions: Sequence[RevisionPolicyDecision],
) -> RevisionDecisionScoreReport:
    validate_protected_suite(protected_suite)
    cases = _case_index(protected_suite)
    by_case = _decision_index(decisions)
    if set(by_case) != set(cases):
        raise ValueError("decision set must match protected suite case set exactly")
    policy_ids = {decision.policy_id for decision in decisions}
    if len(policy_ids) != 1:
        raise ValueError("one score report may contain only one policy identity")
    policy_id = next(iter(policy_ids))
    analysis_flags = {decision.analysis_only for decision in decisions}
    if len(analysis_flags) != 1:
        raise ValueError("mixed analysis-only and ordinary decisions are not score-comparable")
    analysis_only = next(iter(analysis_flags))

    invasiveness = protected_suite.get("revision_invasiveness")
    if not isinstance(invasiveness, Mapping):
        raise ValueError("protected suite missing revision invasiveness map")

    rows: list[RevisionDecisionCaseScore] = []
    correct = broad = correct_unresolved = unresolved_denom = total_actions = 0
    total_cost = 0.0
    for case_id in sorted(cases):
        case = cases[case_id]
        decision = by_case[case_id]
        selected = decision.selected_revision_class
        gold = str(case["protected_gold_revision_class"])
        selected_rank = invasiveness.get(selected)
        gold_rank = invasiveness.get(gold)
        if selected_rank is None:
            raise ValueError(f"selected revision class lacks invasiveness binding: {selected}")
        if gold_rank is None:
            raise ValueError(f"gold revision class lacks invasiveness binding: {gold}")
        is_correct = selected == gold
        is_broad = selected not in {"UNRESOLVED", "NO_REVISION"} and int(selected_rank) > int(gold_rank)
        is_correct_unresolved = gold == "UNRESOLVED" and selected == "UNRESOLVED"
        unresolved_denom += int(gold == "UNRESOLVED")
        correct += int(is_correct)
        broad += int(is_broad)
        correct_unresolved += int(is_correct_unresolved)
        total_actions += len(decision.diagnostic_actions)
        cost = _diagnostic_cost(case, decision)
        total_cost += cost
        rows.append(
            RevisionDecisionCaseScore(
                case_id=case_id,
                selected_revision_class=selected,
                gold_revision_class=gold,
                correct=is_correct,
                false_broad_revision=is_broad,
                correct_unresolved=is_correct_unresolved,
                diagnostic_actions=len(decision.diagnostic_actions),
                diagnostic_cost=cost,
            )
        )
    total = len(rows)
    return RevisionDecisionScoreReport(
        policy_id=policy_id,
        total_cases=total,
        correct_revision_count=correct,
        incorrect_revision_count=total - correct,
        revision_accuracy=correct / total,
        false_broad_revision_count=broad,
        false_broad_revision_rate=broad / total,
        correct_unresolved_count=correct_unresolved,
        correct_unresolved_denominator=unresolved_denom,
        total_diagnostic_actions=total_actions,
        total_diagnostic_cost=total_cost,
        analysis_only=analysis_only,
        eligible_for_superiority_claim=not analysis_only,
        case_scores=tuple(rows),
    )


def score_revision_execution_outcomes(
    decisions: Sequence[RevisionPolicyDecision],
    outcomes: Sequence[RevisionExecutionOutcome],
) -> RevisionExecutionScoreReport:
    by_case = _decision_index(decisions)
    if not outcomes:
        raise ValueError("at least one execution outcome is required")
    seen: set[str] = set()
    policy_ids: set[str] = set()
    fresh_denom = fresh_success = harm = preservation = authority = 0
    for outcome in outcomes:
        outcome.verify()
        if outcome.case_id in seen:
            raise ValueError(f"duplicate execution outcome case: {outcome.case_id}")
        seen.add(outcome.case_id)
        policy_ids.add(outcome.policy_id)
        decision = by_case.get(outcome.case_id)
        if decision is None:
            raise ValueError(f"execution outcome has no matching decision: {outcome.case_id}")
        if decision.policy_id != outcome.policy_id:
            raise ValueError("execution outcome policy identity mismatch")
        if decision.digest != outcome.decision_digest:
            raise ValueError("execution outcome decision digest mismatch")
        fresh_denom += int(outcome.fresh_transfer_applicable)
        fresh_success += int(outcome.fresh_transfer_applicable and outcome.fresh_transfer_success)
        harm += int(outcome.harmful_regression)
        preservation += int(not outcome.preservation_satisfied)
        authority += int(outcome.evaluator_or_authority_violation)
    if len(policy_ids) != 1:
        raise ValueError("one execution score report may contain only one policy")
    return RevisionExecutionScoreReport(
        policy_id=next(iter(policy_ids)),
        outcome_count=len(outcomes),
        fresh_transfer_denominator=fresh_denom,
        fresh_transfer_success_count=fresh_success,
        fresh_transfer_success_rate=None if fresh_denom == 0 else fresh_success / fresh_denom,
        harmful_regression_count=harm,
        preservation_violation_count=preservation,
        authority_violation_count=authority,
    )


__all__ = [
    "RevisionDecisionCaseScore",
    "RevisionDecisionScoreReport",
    "RevisionExecutionOutcome",
    "RevisionExecutionScoreReport",
    "score_revision_decisions",
    "score_revision_execution_outcomes",
]
