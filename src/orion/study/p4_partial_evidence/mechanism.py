"""Defeater-directed protected acquisition. Planner output cannot authorize."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Mapping, Sequence

from orion.kernel.hard_gates import (
    HardGateContract,
    HardGateObservation,
    HardGateRequirement,
    HardGateState,
    evaluate_hard_gates,
)
from orion.transfer.defeaters import Defeater
from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p4 import (
    EvidenceCustody,
    P4PlanStatus,
    ProtectedEvidenceAction,
    plan_protected_evidence,
)

GATE_IDS = (
    "EXACT_CONTENT_BINDING",
    "SOURCE_OWNERSHIP",
    "SEMANTIC_SUPPORT",
    "CHECKER_INDEPENDENCE",
    "CHECKER_DISCRIMINATION",
    "BEHAVIORAL_INFLUENCE",
    "EVALUATOR_CHRONOLOGY_INTEGRITY",
    "SEARCH_CONTAMINATION_CLEAR",
    "PROTECTED_ACCESS_CLEAR",
)

DEFEATER_GATE = {
    "source_ownership": "SOURCE_OWNERSHIP",
    "source_specific_support": "SEMANTIC_SUPPORT",
    "behavioral_influence": "BEHAVIORAL_INFLUENCE",
    "checker_independence": "CHECKER_INDEPENDENCE",
    "evaluator_custody": "EVALUATOR_CHRONOLOGY_INTEGRITY",
    "source_conflict": "SOURCE_OWNERSHIP",
    "missing_evidence": "SEMANTIC_SUPPORT",
}

Executor = Callable[[str, "PartialEvidenceCase"], Mapping[str, str]]


class CustodyClass(str, Enum):
    PROTECTED_EVALUATOR = "PROTECTED_EVALUATOR"
    INDEPENDENT_HOST = "INDEPENDENT_HOST"
    UNPROTECTED = "UNPROTECTED"
    SELF_AUTHORED = "SELF_AUTHORED"
    CANDIDATE = "CANDIDATE"


class AuthorityTerminal(str, Enum):
    AUTHORIZE = "AUTHORIZE"
    BLOCK = "BLOCK"
    CANNOT_CHECK = "CANNOT_CHECK"


class FrozenRegistryError(ValueError):
    """Candidate-controlled mutation of the frozen action registry is refused."""


_PROTECTED = frozenset({CustodyClass.PROTECTED_EVALUATOR, CustodyClass.INDEPENDENT_HOST})
_CUSTODY_TO_EVIDENCE = {
    CustodyClass.PROTECTED_EVALUATOR: EvidenceCustody.PROTECTED_EVALUATOR,
    CustodyClass.INDEPENDENT_HOST: EvidenceCustody.INDEPENDENT_HOST,
    CustodyClass.UNPROTECTED: EvidenceCustody.CANDIDATE,
    CustodyClass.SELF_AUTHORED: EvidenceCustody.SELF,
    CustodyClass.CANDIDATE: EvidenceCustody.CANDIDATE,
}


@dataclass(frozen=True)
class UnresolvedDefeater:
    defeater_id: str
    severity: float
    critical: bool
    required_custody: CustodyClass


@dataclass(frozen=True)
class ActionSpec:
    action_id: str
    addresses: frozenset[str]
    success_probability: float
    cost: float
    custody: CustodyClass
    source_digest: str

    def payload(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "addresses": sorted(self.addresses),
            "success_probability": self.success_probability,
            "cost": self.cost,
            "custody": self.custody.value,
            "source_digest": self.source_digest,
        }


def _spec_from_mapping(raw: Mapping[str, Any]) -> ActionSpec:
    return ActionSpec(
        action_id=str(raw["action_id"]),
        addresses=frozenset(str(item) for item in raw["addresses"]),
        success_probability=float(raw["success_probability"]),
        cost=float(raw["cost"]),
        custody=CustodyClass(str(raw["custody"])),
        source_digest=str(raw["source_digest"]),
    )


@dataclass(frozen=True)
class FrozenActionRegistry:
    actions: tuple[ActionSpec, ...]
    digest: str

    @classmethod
    def from_specs(cls, specs: Sequence[Mapping[str, Any]]) -> FrozenActionRegistry:
        actions = tuple(_spec_from_mapping(item) for item in specs)
        digest = content_digest({"actions": [item.payload() for item in actions]})
        return cls(actions=actions, digest=digest)

    def add(self, spec: Mapping[str, Any]) -> None:
        raise FrozenRegistryError("candidate cannot add actions to a frozen registry")

    def replace_actions(self, specs: Sequence[Mapping[str, Any]]) -> None:
        raise FrozenRegistryError("candidate cannot replace a frozen action registry")

    def by_id(self, action_id: str) -> ActionSpec | None:
        for action in self.actions:
            if action.action_id == action_id:
                return action
        return None


@dataclass(frozen=True)
class PartialEvidenceCase:
    case_id: str
    family: str
    unresolved: tuple[UnresolvedDefeater, ...]
    observations: Mapping[str, str]


@dataclass(frozen=True)
class AcquisitionReceipt:
    selected_action_id: str | None
    rejected_alternatives: tuple[str, ...]
    cost: float | None
    targeted_defeater: str | None
    custody_class: str | None
    reason: str
    planner_status: str
    planner_authority_terminal: str
    authority_terminal: AuthorityTerminal
    unresolved_critical_defeater_ids: tuple[str, ...]
    new_evidence_digest: str | None
    receipt_digest: str

    def __post_init__(self) -> None:
        if self.planner_authority_terminal != "NONE":
            raise ValueError("planner output cannot authorize")


def _can_discharge(defeater: UnresolvedDefeater, action: ActionSpec) -> bool:
    if defeater.defeater_id not in action.addresses:
        return False
    if defeater.required_custody in _PROTECTED:
        return action.custody in _PROTECTED
    return True


def _admissible(case: PartialEvidenceCase, registry: FrozenActionRegistry) -> tuple[ActionSpec, ...]:
    unresolved = {item.defeater_id: item for item in case.unresolved}
    selected: list[ActionSpec] = []
    for action in registry.actions:
        if action.custody not in _PROTECTED:
            continue
        if not any(_can_discharge(unresolved[did], action) for did in action.addresses if did in unresolved):
            continue
        selected.append(action)
    return tuple(selected)


def _authority_contract() -> HardGateContract:
    return HardGateContract(
        contract_id="P4.partial-evidence-acquisition.production-gates.v2",
        requirements=tuple(
            HardGateRequirement(gate_id, gate_id.replace("_", " ").lower())
            for gate_id in GATE_IDS
        ),
        frozen_at_round=0,
    )


def _evaluate_authority(case: PartialEvidenceCase, observations: Mapping[str, str]) -> AuthorityTerminal:
    contract = _authority_contract()
    gate_observations = []
    for gate_id in GATE_IDS:
        raw = observations.get(gate_id, HardGateState.CANNOT_CHECK.value)
        state = HardGateState(raw)
        gate_observations.append(
            HardGateObservation(
                gate_id=gate_id,
                subject_id=case.case_id,
                state=state,
                contract_fingerprint=contract.fingerprint,
                evidence_ids=(f"partial-evidence:{case.case_id}:{gate_id.lower()}",),
                detail=state.value,
            )
        )
    report = evaluate_hard_gates(
        contract, gate_observations, subject_id=case.case_id, round_index=1
    )
    if report.state is HardGateState.PASS:
        return AuthorityTerminal.AUTHORIZE
    if report.state is HardGateState.FAIL:
        return AuthorityTerminal.BLOCK
    return AuthorityTerminal.CANNOT_CHECK


def _remaining_critical(
    case: PartialEvidenceCase,
    action: ActionSpec | None,
    observations: Mapping[str, str],
) -> tuple[str, ...]:
    remaining: list[str] = []
    for defeater in case.unresolved:
        if not defeater.critical:
            continue
        discharged = (
            action is not None
            and _can_discharge(defeater, action)
            and observations.get(DEFEATER_GATE.get(defeater.defeater_id, ""), "") == "PASS"
        )
        if not discharged:
            remaining.append(defeater.defeater_id)
    return tuple(remaining)


def acquire_and_reevaluate(
    case: PartialEvidenceCase,
    registry: FrozenActionRegistry,
    *,
    executor: Executor,
    forced_action_id: str | None = None,
    candidate_registry_patch: Mapping[str, Any] | None = None,
) -> AcquisitionReceipt:
    if candidate_registry_patch is not None:
        raise FrozenRegistryError("candidate cannot patch the frozen action registry")

    admissible = _admissible(case, registry)
    defeaters = tuple(
        Defeater(item.defeater_id, item.severity, unresolved=True) for item in case.unresolved
    )
    protected_actions = tuple(
        ProtectedEvidenceAction(
            action_id=item.action_id,
            addresses=item.addresses,
            success_probability=item.success_probability,
            cost=item.cost,
            custody=_CUSTODY_TO_EVIDENCE[item.custody],
            source_digest=item.source_digest,
        )
        for item in admissible
    )
    plan = plan_protected_evidence(defeaters, protected_actions)
    selected_id = forced_action_id if forced_action_id is not None else plan.selected_action_id
    selected = registry.by_id(selected_id) if selected_id else None
    rejected = tuple(
        item.action_id for item in registry.actions if item.action_id != selected_id
    )

    observations = dict(case.observations)
    new_digest: str | None = None
    executed: ActionSpec | None = None
    if selected is not None and (forced_action_id is not None or plan.status is P4PlanStatus.GATHER_EVIDENCE):
        updates = dict(executor(selected.action_id, case))
        legal: dict[str, str] = {}
        for key, value in updates.items():
            if key in case.observations and key not in {
                DEFEATER_GATE.get(defeater.defeater_id)
                for defeater in case.unresolved
                if _can_discharge(defeater, selected)
            }:
                legal[key] = value
                continue
            gate_owners = [
                defeater
                for defeater in case.unresolved
                if DEFEATER_GATE.get(defeater.defeater_id) == key
            ]
            if gate_owners and not any(_can_discharge(item, selected) for item in gate_owners):
                continue
            if not gate_owners and not any(_can_discharge(item, selected) for item in case.unresolved):
                continue
            legal[key] = value
        observations.update(legal)
        new_digest = content_digest({"action_id": selected.action_id, "observations": observations})
        executed = selected

    remaining = _remaining_critical(case, executed, observations)
    terminal = _evaluate_authority(case, observations)
    if remaining and terminal is AuthorityTerminal.AUTHORIZE:
        terminal = AuthorityTerminal.CANNOT_CHECK
    if remaining and selected is None:
        terminal = AuthorityTerminal.CANNOT_CHECK

    targeted = None
    if selected is not None:
        for defeater in case.unresolved:
            if defeater.critical and defeater.defeater_id in selected.addresses:
                targeted = defeater.defeater_id
                break
        if targeted is None and selected.addresses:
            targeted = sorted(selected.addresses)[0]

    unsigned = {
        "selected_action_id": selected.action_id if selected is not None else None,
        "rejected_alternatives": list(rejected),
        "cost": selected.cost if selected is not None else None,
        "targeted_defeater": targeted,
        "custody_class": selected.custody.value if selected is not None else None,
        "reason": plan.reason_code,
        "planner_status": plan.status.value,
        "planner_authority_terminal": "NONE",
        "authority_terminal": terminal.value,
        "unresolved_critical_defeater_ids": list(remaining),
        "new_evidence_digest": new_digest,
    }
    return AcquisitionReceipt(
        selected_action_id=unsigned["selected_action_id"],
        rejected_alternatives=rejected,
        cost=unsigned["cost"],
        targeted_defeater=targeted,
        custody_class=unsigned["custody_class"],
        reason=plan.reason_code,
        planner_status=plan.status.value,
        planner_authority_terminal="NONE",
        authority_terminal=terminal,
        unresolved_critical_defeater_ids=remaining,
        new_evidence_digest=new_digest,
        receipt_digest=content_digest(unsigned),
    )
