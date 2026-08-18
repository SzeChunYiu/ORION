"""Matched policy/mechanism comparators for the prospective Self-ORION V3 study.

These policies output proposals only.  They never see protected gold (except the
analysis-only oracle ceiling), never score themselves, and never gain adoption or
scientific authority.  ``FULL_T7`` deliberately calls the merged higher-order
responsibility/revision/control machinery rather than merely using its name.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from orion.self_orion.epistemic_control import (
    EpistemicControlStatus,
    compose_epistemic_control,
)
from orion.self_orion.revision_gate import assess_revision_gate
from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.epistemic_computation import (
    assess_computation_action,
    build_computation_action,
    select_epistemic_computation,
)
from orion.transfer.v2.epistemic_responsibility import (
    ResponsibilityStatus,
    assess_responsibility,
    build_responsibility_hypothesis,
)
from orion.transfer.v2.higher_order_epistemic_mechanics import (
    assess_mechanic,
    build_mechanic,
)
from orion.transfer.v2.interface_adequacy import (
    InterfaceCheckState,
    assess_interface_adequacy,
    build_interface_check,
)


class FeedbackMode(str, Enum):
    NORMAL = "NORMAL"
    PERMUTED = "PERMUTED"
    NONE = "NONE"
    CONTRADICTORY = "CONTRADICTORY"
    RANDOM = "RANDOM"


class PolicyKind(str, Enum):
    NO_REVISION = "NO_REVISION"
    DIRECT_SELF_EDIT = "DIRECT_SELF_EDIT"
    M_OPEN_ONLY = "M_OPEN_ONLY"
    WORLD_MODEL_REVISION = "WORLD_MODEL_REVISION"
    REPRESENTATION_REGIME_ONLY = "REPRESENTATION_REGIME_ONLY"
    GENERIC_CAUSAL_DIAGNOSIS = "GENERIC_CAUSAL_DIAGNOSIS"
    FULL_T7 = "FULL_T7"
    RANDOM_DIAGNOSTIC = "RANDOM_DIAGNOSTIC"
    ALWAYS_UNRESOLVED = "ALWAYS_UNRESOLVED"
    ORACLE_CEILING = "ORACLE_CEILING"


@dataclass(frozen=True)
class ProtectedFeedbackOracle:
    """Host-side diagnostic feedback adapter.

    Candidate policies receive only the ``observe`` callback semantics.  The
    protected mapping belongs to evaluator/host custody in confirmatory use.
    """

    case_id: str
    outcome_by_action: Mapping[str, str]
    mode: FeedbackMode = FeedbackMode.NORMAL
    alternate_outcomes: Mapping[str, str] | None = None

    def observe(self, action_id: str) -> str:
        if action_id not in self.outcome_by_action:
            raise ValueError(f"diagnostic unavailable in protected feedback oracle: {action_id}")
        actual = str(self.outcome_by_action[action_id])
        alternate = None if self.alternate_outcomes is None else self.alternate_outcomes.get(action_id)
        if self.mode is FeedbackMode.NORMAL:
            return actual
        if self.mode is FeedbackMode.NONE:
            return "NO_FEEDBACK"
        if self.mode in {FeedbackMode.PERMUTED, FeedbackMode.CONTRADICTORY}:
            if alternate is None:
                return "CONTRADICTORY_FEEDBACK"
            return str(alternate)
        if self.mode is FeedbackMode.RANDOM:
            candidates = sorted({actual, *( () if alternate is None else (str(alternate),) )})
            if not candidates:
                return "NO_FEEDBACK"
            digest = hashlib.sha256(f"{self.case_id}:{action_id}".encode("utf-8")).digest()
            return candidates[digest[0] % len(candidates)]
        raise ValueError(f"unsupported feedback mode: {self.mode}")


@dataclass(frozen=True)
class RevisionPolicyDecision:
    policy_id: str
    case_id: str
    diagnostic_actions: tuple[str, ...]
    observed_feedback: tuple[tuple[str, str], ...]
    selected_revision_class: str
    trace: tuple[str, ...]
    analysis_only: bool
    excluded_from_superiority_claim: bool
    digest: str

    @classmethod
    def build(
        cls,
        *,
        policy_id: str,
        case_id: str,
        diagnostic_actions: Sequence[str],
        observed_feedback: Sequence[tuple[str, str]],
        selected_revision_class: str,
        trace: Sequence[str],
        analysis_only: bool = False,
        excluded_from_superiority_claim: bool = False,
    ) -> "RevisionPolicyDecision":
        action_tuple = tuple(map(str, diagnostic_actions))
        feedback_tuple = tuple((str(action), str(outcome)) for action, outcome in observed_feedback)
        trace_tuple = tuple(map(str, trace))
        payload = {
            "version": "SelfOrionV3RevisionPolicyDecision.v1",
            "policy_id": str(policy_id),
            "case_id": str(case_id),
            "diagnostic_actions": list(action_tuple),
            "observed_feedback": [list(row) for row in feedback_tuple],
            "selected_revision_class": str(selected_revision_class),
            "trace": list(trace_tuple),
            "analysis_only": bool(analysis_only),
            "excluded_from_superiority_claim": bool(excluded_from_superiority_claim),
            "grants_scientific_authority": False,
            "grants_revision_authority": False,
            "grants_adoption_authority": False,
            "grants_promotion_authority": False,
        }
        decision = cls(
            policy_id=payload["policy_id"],
            case_id=payload["case_id"],
            diagnostic_actions=action_tuple,
            observed_feedback=feedback_tuple,
            selected_revision_class=payload["selected_revision_class"],
            trace=trace_tuple,
            analysis_only=payload["analysis_only"],
            excluded_from_superiority_claim=payload["excluded_from_superiority_claim"],
            digest=content_digest(payload),
        )
        decision.verify()
        return decision

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    @property
    def grants_revision_authority(self) -> bool:
        return False

    @property
    def grants_adoption_authority(self) -> bool:
        return False

    @property
    def grants_promotion_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "SelfOrionV3RevisionPolicyDecision.v1",
            "policy_id": self.policy_id,
            "case_id": self.case_id,
            "diagnostic_actions": list(self.diagnostic_actions),
            "observed_feedback": [list(row) for row in self.observed_feedback],
            "selected_revision_class": self.selected_revision_class,
            "trace": list(self.trace),
            "analysis_only": self.analysis_only,
            "excluded_from_superiority_claim": self.excluded_from_superiority_claim,
            "grants_scientific_authority": False,
            "grants_revision_authority": False,
            "grants_adoption_authority": False,
            "grants_promotion_authority": False,
        }

    def verify(self) -> None:
        if not self.policy_id or not self.case_id or not self.selected_revision_class:
            raise ValueError("policy/case/revision identities are required")
        if len(self.diagnostic_actions) != len(set(self.diagnostic_actions)):
            raise ValueError("policy cannot execute one diagnostic twice in the bounded V3 session")
        if tuple(action for action, _ in self.observed_feedback) != self.diagnostic_actions:
            raise ValueError("observed feedback must bind exactly to diagnostic action order")
        if self.analysis_only and not self.excluded_from_superiority_claim:
            raise ValueError("analysis-only policy must be excluded from superiority claims")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("revision policy decision digest mismatch")


def _diagnostic_catalog(case: Mapping[str, Any]) -> dict[str, float]:
    raw = case.get("allowed_diagnostics", [])
    if not isinstance(raw, list):
        raise ValueError("allowed_diagnostics must be an array")
    result: dict[str, float] = {}
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("diagnostic entry must be an object")
        action_id = str(item.get("action_id", ""))
        if not action_id or action_id in result:
            raise ValueError("diagnostic identities must be nonempty and unique")
        cost = float(item.get("cost", -1))
        if cost < 0:
            raise ValueError("diagnostic cost must be non-negative")
        result[action_id] = cost
    return result


def _choose_discriminator(case: Mapping[str, Any]) -> str | None:
    actions = _diagnostic_catalog(case)
    budget = float(case.get("diagnostic_budget", 0.0))
    hypotheses = case.get("hypotheses")
    if not isinstance(hypotheses, Mapping):
        raise ValueError("hypotheses must be an object")
    candidates: list[tuple[int, float, str]] = []
    for action_id, cost in actions.items():
        if cost > budget:
            continue
        signatures = {
            tuple(sorted(map(str, (prediction.get(action_id, []) if isinstance(prediction, Mapping) else []))))
            for prediction in hypotheses.values()
        }
        candidates.append((len(signatures), -cost, action_id))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    best_partition = candidates[0][0]
    if best_partition <= 1:
        # Still allowed: a non-identifying probe can establish that ambiguity is real.
        affordable = sorted((cost, action_id) for action_id, cost in actions.items() if cost <= budget)
        return None if not affordable else affordable[0][1]
    top = [row for row in candidates if row[0] == best_partition]
    top.sort(key=lambda row: (-row[1], row[2]))  # lower cost, then stable id
    return top[0][2]


def _survivors(case: Mapping[str, Any], action_id: str, outcome: str) -> tuple[str, ...]:
    hypotheses = case.get("hypotheses")
    if not isinstance(hypotheses, Mapping):
        raise ValueError("hypotheses must be an object")
    survivors: list[str] = []
    for label, raw_prediction in hypotheses.items():
        if not isinstance(raw_prediction, Mapping):
            continue
        allowed = tuple(map(str, raw_prediction.get(action_id, ())))
        if outcome in allowed:
            survivors.append(str(label))
    return tuple(sorted(survivors))


def _simple_decision(
    kind: PolicyKind,
    case: Mapping[str, Any],
    selected: str,
    *,
    trace: Sequence[str],
    actions: Sequence[str] = (),
    feedback: Sequence[tuple[str, str]] = (),
    analysis_only: bool = False,
) -> RevisionPolicyDecision:
    return RevisionPolicyDecision.build(
        policy_id=kind.value,
        case_id=str(case["case_id"]),
        diagnostic_actions=actions,
        observed_feedback=feedback,
        selected_revision_class=selected,
        trace=trace,
        analysis_only=analysis_only,
        excluded_from_superiority_claim=analysis_only,
    )


def _run_diagnosis(kind: PolicyKind, case: Mapping[str, Any], oracle: ProtectedFeedbackOracle) -> RevisionPolicyDecision:
    action_id = _choose_discriminator(case)
    if action_id is None:
        return _simple_decision(kind, case, "UNRESOLVED", trace=("NO_AFFORDABLE_DIAGNOSTIC",))
    outcome = oracle.observe(action_id)
    survivors = _survivors(case, action_id, outcome)
    selected = survivors[0] if len(survivors) == 1 else "UNRESOLVED"
    return _simple_decision(
        kind,
        case,
        selected,
        trace=("GENERIC_CAUSAL_DIAGNOSIS", f"SURVIVORS:{','.join(survivors)}"),
        actions=(action_id,),
        feedback=((action_id, outcome),),
    )


def _write_coordinate(label: str, invasiveness: Mapping[str, Any]) -> str:
    return f"revision/{int(invasiveness.get(label, 999))}/{label.lower()}"


def _run_full_t7(case: Mapping[str, Any], oracle: ProtectedFeedbackOracle) -> RevisionPolicyDecision:
    action_id = _choose_discriminator(case)
    if action_id is None:
        return _simple_decision(PolicyKind.FULL_T7, case, "UNRESOLVED", trace=("T7:NO_AFFORDABLE_DIAGNOSTIC",))
    outcome = oracle.observe(action_id)
    claim_id = f"P5.V3:{case['case_id']}"
    hypotheses_raw = case.get("hypotheses")
    if not isinstance(hypotheses_raw, Mapping):
        raise ValueError("hypotheses must be an object")
    responsibility_hypotheses = tuple(
        build_responsibility_hypothesis(
            hypothesis_id=str(label),
            claim_id=claim_id,
            expected_observations={
                str(discriminator_id): tuple(map(str, outcomes))
                for discriminator_id, outcomes in prediction.items()
            },
            support_evidence_ids=(f"candidate-hypothesis:{label}",),
        )
        for label, prediction in sorted(hypotheses_raw.items())
        if isinstance(prediction, Mapping)
    )
    responsibility = assess_responsibility(
        responsibility_hypotheses,
        observed_outcomes={action_id: outcome},
    )
    if responsibility.status is not ResponsibilityStatus.IDENTIFIED:
        return _simple_decision(
            PolicyKind.FULL_T7,
            case,
            "UNRESOLVED",
            trace=("T7:RESPONSIBILITY_NOT_IDENTIFIED", responsibility.status.value),
            actions=(action_id,),
            feedback=((action_id, outcome),),
        )

    interface = assess_interface_adequacy(
        (
            build_interface_check(
                check_id="registered-benchmark-interface",
                scope="benchmark/candidate-interface",
                state=InterfaceCheckState.PASS,
                evidence_ids=(f"candidate-packet:{case['case_id']}",),
                required=True,
            ),
        )
    )
    invasiveness = case.get("revision_invasiveness", {})
    if not isinstance(invasiveness, Mapping):
        raise ValueError("revision_invasiveness must be an object")
    labels = tuple(map(str, case.get("competing_revision_classes", ())))
    mechanics = tuple(
        build_mechanic(
            mechanic_id=f"v3:{label}",
            claim_id=claim_id,
            kind=label,
            write_coordinates=(_write_coordinate(label, invasiveness),),
            preservation_obligations=tuple(map(str, case.get("preservation_obligations", ()))),
        )
        for label in labels
    )
    assessments = tuple(assess_mechanic(mechanic, obligation_states={}) for mechanic in mechanics)
    bindings = {label: (f"v3:{label}",) for label in labels}
    revision = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=assessments,
        responsibility_bindings=bindings,
    )
    idle = build_computation_action(
        action_id="v3-local-stop",
        claim_id=claim_id,
        kind="LOCAL_STOP_SENTINEL",
        expected_decision_value=0.0,
        cost=0.0,
    )
    idle_assessment = assess_computation_action(idle, requirement_states={})
    computation = select_epistemic_computation((idle,), (idle_assessment,))
    control = compose_epistemic_control(revision=revision, computation=computation)
    if control.status is EpistemicControlStatus.REVISION_CANDIDATE and control.selected_revision_mechanic_id:
        prefix = "v3:"
        selected = (
            control.selected_revision_mechanic_id[len(prefix):]
            if control.selected_revision_mechanic_id.startswith(prefix)
            else control.selected_revision_mechanic_id
        )
    else:
        selected = "UNRESOLVED"
    return _simple_decision(
        PolicyKind.FULL_T7,
        case,
        selected,
        trace=(
            "T7:RESPONSIBILITY_GATE",
            f"RESPONSIBILITY:{responsibility.status.value}",
            f"REVISION_GATE:{revision.status.value}",
            f"CONTROL:{control.status.value}",
        ),
        actions=(action_id,),
        feedback=((action_id, outcome),),
    )


def run_revision_policy(
    policy: PolicyKind | str,
    case: Mapping[str, Any],
    feedback_oracle: ProtectedFeedbackOracle,
    *,
    protected_gold_revision_class: str | None = None,
) -> RevisionPolicyDecision:
    kind = policy if isinstance(policy, PolicyKind) else PolicyKind(policy)
    if str(case.get("case_id", "")) != feedback_oracle.case_id:
        raise ValueError("feedback oracle case identity mismatch")
    if kind is not PolicyKind.ORACLE_CEILING and protected_gold_revision_class is not None:
        raise ValueError("protected gold may only be supplied to the analysis-only oracle ceiling")

    if kind is PolicyKind.ORACLE_CEILING:
        if protected_gold_revision_class is None:
            raise ValueError("oracle ceiling requires protected gold")
        return _simple_decision(
            kind,
            case,
            str(protected_gold_revision_class),
            trace=("PROTECTED_ORACLE_CEILING",),
            analysis_only=True,
        )
    if kind is PolicyKind.NO_REVISION:
        return _simple_decision(kind, case, "NO_REVISION", trace=("FIXED_NO_REVISION_CONTROL",))
    if kind is PolicyKind.DIRECT_SELF_EDIT:
        return _simple_decision(kind, case, "BROAD_SELF_EDIT", trace=("DIRECT_BROAD_SELF_EDIT_CONTROL",))
    if kind is PolicyKind.M_OPEN_ONLY:
        return _simple_decision(kind, case, "MODEL_CLASS_EXPANSION", trace=("M_OPEN_ONLY", "MECHANISM_COMPARATOR"))
    if kind is PolicyKind.WORLD_MODEL_REVISION:
        return _simple_decision(kind, case, "WITHIN_CLASS_MODEL_REPAIR", trace=("WORLD_MODEL_REVISION", "MECHANISM_COMPARATOR"))
    if kind is PolicyKind.REPRESENTATION_REGIME_ONLY:
        return _simple_decision(kind, case, "REPRESENTATION_REGIME_REPAIR", trace=("REPRESENTATION_REGIME_ONLY", "MECHANISM_COMPARATOR"))
    if kind is PolicyKind.ALWAYS_UNRESOLVED:
        return _simple_decision(kind, case, "UNRESOLVED", trace=("BROKEN_SHUT_CONTROL",))
    if kind is PolicyKind.GENERIC_CAUSAL_DIAGNOSIS:
        return _run_diagnosis(kind, case, feedback_oracle)
    if kind is PolicyKind.FULL_T7:
        return _run_full_t7(case, feedback_oracle)
    if kind is PolicyKind.RANDOM_DIAGNOSTIC:
        actions = _diagnostic_catalog(case)
        budget = float(case.get("diagnostic_budget", 0.0))
        affordable = sorted(action for action, cost in actions.items() if cost <= budget)
        if not affordable:
            return _simple_decision(kind, case, "UNRESOLVED", trace=("RANDOM_NO_AFFORDABLE_DIAGNOSTIC",))
        digest = hashlib.sha256(str(case["case_id"]).encode("utf-8")).digest()
        action = affordable[digest[0] % len(affordable)]
        outcome = feedback_oracle.observe(action)
        survivors = _survivors(case, action, outcome)
        selected = survivors[0] if len(survivors) == 1 else "UNRESOLVED"
        return _simple_decision(
            kind,
            case,
            selected,
            trace=("DETERMINISTIC_RANDOM_DIAGNOSTIC_CONTROL",),
            actions=(action,),
            feedback=((action, outcome),),
        )
    raise ValueError(f"unsupported V3 policy: {kind}")


__all__ = [
    "FeedbackMode",
    "PolicyKind",
    "ProtectedFeedbackOracle",
    "RevisionPolicyDecision",
    "run_revision_policy",
]
