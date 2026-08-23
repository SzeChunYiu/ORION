"""Exact fixed-proposal control study for P10 A0.

This module deliberately contains no LLM.  It asks whether the proposed P10
responsibility controller has any residual after composing already-established
structured control primitives under identical proposal and information custody.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import Iterable


class Responsibility(str, Enum):
    LOCAL_ACTION = "LOCAL_ACTION"
    NEED_EVIDENCE = "NEED_EVIDENCE"
    LOCAL_REPAIR = "LOCAL_REPAIR"
    REFRAME_REPRESENTATION = "REFRAME_REPRESENTATION"
    UNRESOLVED = "UNRESOLVED"


class ProposalKind(str, Enum):
    ACT = "ACT"
    ACQUIRE_EVIDENCE = "ACQUIRE_EVIDENCE"
    LOCAL_REPAIR = "LOCAL_REPAIR"
    REFRAME_REPRESENTATION = "REFRAME_REPRESENTATION"
    UNRESOLVED = "UNRESOLVED"


class ControllerArm(str, Enum):
    FIRST_CANDIDATE_NULL = "FIRST_CANDIDATE_NULL"
    SERIALIZED_STATE_RULE = "SERIALIZED_STATE_RULE"
    DEPENDENCY_SUPPORT_CONTROL = "DEPENDENCY_SUPPORT_CONTROL"
    SYMBOLIC_FEASIBILITY_CONTROL = "SYMBOLIC_FEASIBILITY_CONTROL"
    STRUCTURED_HISTORY_CONTROL = "STRUCTURED_HISTORY_CONTROL"
    DONOR_COMPOSED_CONTROL = "DONOR_COMPOSED_CONTROL"
    ORION_RESPONSIBILITY_CONTROL = "ORION_RESPONSIBILITY_CONTROL"


@dataclass(frozen=True)
class CandidateProposal:
    candidate_id: str
    kind: ProposalKind
    cost_units: int


@dataclass(frozen=True)
class A0Case:
    world_id: str
    surface_atom: str
    evidence_state: str
    observation_available: bool
    observation_discriminates: bool
    execution_gate: str
    narrow_fix_available: bool
    narrow_fix_restores: bool
    frame_transform_available: bool
    frame_transform_restores: bool
    compatible_failure_active: bool
    evaluator_note: str = ""

    def verify(self) -> None:
        if self.evidence_state not in {"COMPLETE", "INCOMPLETE"}:
            raise ValueError("invalid evidence state")
        if self.execution_gate not in {"PASS", "INTERFACE_BLOCK", "FRAME_BLOCK", "OTHER_BLOCK"}:
            raise ValueError("invalid execution gate")
        if self.observation_discriminates and not self.observation_available:
            raise ValueError("a discriminating observation must be available")
        if self.narrow_fix_restores and not self.narrow_fix_available:
            raise ValueError("restoring narrow fix must be available")
        if self.frame_transform_restores and not self.frame_transform_available:
            raise ValueError("restoring frame transform must be available")


@dataclass(frozen=True)
class EvaluationRecord:
    correct: bool
    unnecessary_reframe: bool
    false_closure: bool
    invalid_action: bool
    unresolved_correct: bool
    cost_units: int


def _opaque(*parts: str, length: int = 16) -> str:
    raw = "|".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:length]


def build_case(responsibility: Responsibility, *, seed: str) -> A0Case:
    """Construct one exact case without storing the responsibility label.

    Responsibility is used only by this generator to choose structural facts;
    `derive_responsibility` reconstructs the evaluator target from those facts.
    Neither the enum nor the input seed is emitted to the model payload.
    """

    common = dict(
        world_id="w" + _opaque(seed, "world"),
        surface_atom="s" + _opaque(seed, "surface"),
        observation_available=False,
        observation_discriminates=False,
        narrow_fix_available=False,
        narrow_fix_restores=False,
        frame_transform_available=False,
        frame_transform_restores=False,
        compatible_failure_active=False,
        evaluator_note="",
    )

    if responsibility is Responsibility.LOCAL_ACTION:
        case = A0Case(evidence_state="COMPLETE", execution_gate="PASS", **common)
    elif responsibility is Responsibility.NEED_EVIDENCE:
        case = A0Case(
            evidence_state="INCOMPLETE",
            execution_gate="OTHER_BLOCK",
            observation_available=True,
            observation_discriminates=True,
            **{k: v for k, v in common.items() if k not in {"observation_available", "observation_discriminates"}},
        )
    elif responsibility is Responsibility.LOCAL_REPAIR:
        case = A0Case(
            evidence_state="COMPLETE",
            execution_gate="INTERFACE_BLOCK",
            narrow_fix_available=True,
            narrow_fix_restores=True,
            **{k: v for k, v in common.items() if k not in {"narrow_fix_available", "narrow_fix_restores"}},
        )
    elif responsibility is Responsibility.REFRAME_REPRESENTATION:
        case = A0Case(
            evidence_state="COMPLETE",
            execution_gate="FRAME_BLOCK",
            frame_transform_available=True,
            frame_transform_restores=True,
            **{k: v for k, v in common.items() if k not in {"frame_transform_available", "frame_transform_restores"}},
        )
    else:
        case = A0Case(evidence_state="INCOMPLETE", execution_gate="OTHER_BLOCK", **common)
    case.verify()
    return case


def derive_responsibility(case: A0Case) -> Responsibility:
    """Evaluator-side exact responsibility derived from structural facts."""

    case.verify()
    if case.evidence_state == "INCOMPLETE":
        if case.observation_available and case.observation_discriminates:
            return Responsibility.NEED_EVIDENCE
        return Responsibility.UNRESOLVED
    if case.execution_gate == "PASS" and not case.compatible_failure_active:
        return Responsibility.LOCAL_ACTION
    if (
        case.execution_gate == "INTERFACE_BLOCK"
        and case.narrow_fix_available
        and case.narrow_fix_restores
    ):
        return Responsibility.LOCAL_REPAIR
    if (
        case.execution_gate == "FRAME_BLOCK"
        and case.frame_transform_available
        and case.frame_transform_restores
    ):
        return Responsibility.REFRAME_REPRESENTATION
    return Responsibility.UNRESOLVED


def model_payload(case: A0Case) -> dict[str, object]:
    """Return the common typed information available to all non-null arms."""

    case.verify()
    return {
        "world_id": case.world_id,
        "surface_atom": case.surface_atom,
        "evidence": ["e0", case.evidence_state],
        "observation": [case.observation_available, case.observation_discriminates],
        "execution": [case.execution_gate],
        "narrow_fix": [case.narrow_fix_available, case.narrow_fix_restores],
        "frame_transform": [case.frame_transform_available, case.frame_transform_restores],
        "history": [case.compatible_failure_active],
    }


def candidate_packet(case: A0Case, *, order_seed: str = "p10-a0-order-v1") -> tuple[CandidateProposal, ...]:
    case.verify()
    costs = {
        ProposalKind.ACT: 1,
        ProposalKind.ACQUIRE_EVIDENCE: 2,
        ProposalKind.LOCAL_REPAIR: 2,
        ProposalKind.REFRAME_REPRESENTATION: 4,
        ProposalKind.UNRESOLVED: 0,
    }
    candidates = [
        CandidateProposal(
            candidate_id="c" + _opaque(case.world_id, kind.value, "candidate"),
            kind=kind,
            cost_units=costs[kind],
        )
        for kind in ProposalKind
    ]
    return tuple(
        sorted(
            candidates,
            key=lambda candidate: _opaque(order_seed, case.world_id, candidate.candidate_id, "order"),
        )
    )


def _candidate(case: A0Case, kind: ProposalKind, *, order_seed: str) -> CandidateProposal:
    matches = [candidate for candidate in candidate_packet(case, order_seed=order_seed) if candidate.kind is kind]
    if len(matches) != 1:
        raise ValueError("fixed proposal packet must contain one candidate of each kind")
    return matches[0]


def _kind_for_responsibility(responsibility: Responsibility) -> ProposalKind:
    return {
        Responsibility.LOCAL_ACTION: ProposalKind.ACT,
        Responsibility.NEED_EVIDENCE: ProposalKind.ACQUIRE_EVIDENCE,
        Responsibility.LOCAL_REPAIR: ProposalKind.LOCAL_REPAIR,
        Responsibility.REFRAME_REPRESENTATION: ProposalKind.REFRAME_REPRESENTATION,
        Responsibility.UNRESOLVED: ProposalKind.UNRESOLVED,
    }[responsibility]


def predict(
    arm: ControllerArm,
    case: A0Case,
    *,
    order_seed: str = "p10-a0-order-v1",
) -> CandidateProposal:
    """Run a frozen controller arm over the identical typed case/candidate packet."""

    case.verify()
    if arm is ControllerArm.FIRST_CANDIDATE_NULL:
        return candidate_packet(case, order_seed=order_seed)[0]

    if arm is ControllerArm.SERIALIZED_STATE_RULE:
        if case.evidence_state == "COMPLETE" and case.execution_gate == "PASS":
            kind = ProposalKind.ACT
        else:
            kind = ProposalKind.UNRESOLVED
        return _candidate(case, kind, order_seed=order_seed)

    if arm is ControllerArm.DEPENDENCY_SUPPORT_CONTROL:
        if case.evidence_state == "INCOMPLETE":
            kind = (
                ProposalKind.ACQUIRE_EVIDENCE
                if case.observation_available and case.observation_discriminates
                else ProposalKind.UNRESOLVED
            )
        else:
            kind = ProposalKind.ACT
        return _candidate(case, kind, order_seed=order_seed)

    if arm is ControllerArm.SYMBOLIC_FEASIBILITY_CONTROL:
        if case.evidence_state != "COMPLETE":
            kind = ProposalKind.UNRESOLVED
        elif case.execution_gate == "PASS" and not case.compatible_failure_active:
            kind = ProposalKind.ACT
        elif case.execution_gate == "INTERFACE_BLOCK" and case.narrow_fix_available and case.narrow_fix_restores:
            kind = ProposalKind.LOCAL_REPAIR
        elif case.execution_gate == "FRAME_BLOCK" and case.frame_transform_available and case.frame_transform_restores:
            kind = ProposalKind.REFRAME_REPRESENTATION
        else:
            kind = ProposalKind.UNRESOLVED
        return _candidate(case, kind, order_seed=order_seed)

    if arm is ControllerArm.STRUCTURED_HISTORY_CONTROL:
        if case.compatible_failure_active:
            kind = ProposalKind.UNRESOLVED
        elif case.evidence_state == "COMPLETE" and case.execution_gate == "PASS":
            kind = ProposalKind.ACT
        else:
            kind = ProposalKind.UNRESOLVED
        return _candidate(case, kind, order_seed=order_seed)

    if arm is ControllerArm.DONOR_COMPOSED_CONTROL:
        # First apply evidence/support sufficiency; only then use symbolic
        # feasibility. This composition is intentionally donor-owned.
        if case.evidence_state == "INCOMPLETE":
            kind = (
                ProposalKind.ACQUIRE_EVIDENCE
                if case.observation_available and case.observation_discriminates
                else ProposalKind.UNRESOLVED
            )
        elif case.execution_gate == "PASS" and not case.compatible_failure_active:
            kind = ProposalKind.ACT
        elif case.execution_gate == "INTERFACE_BLOCK" and case.narrow_fix_available and case.narrow_fix_restores:
            kind = ProposalKind.LOCAL_REPAIR
        elif case.execution_gate == "FRAME_BLOCK" and case.frame_transform_available and case.frame_transform_restores:
            kind = ProposalKind.REFRAME_REPRESENTATION
        else:
            kind = ProposalKind.UNRESOLVED
        return _candidate(case, kind, order_seed=order_seed)

    if arm is ControllerArm.ORION_RESPONSIBILITY_CONTROL:
        kind = _kind_for_responsibility(derive_responsibility(case))
        return _candidate(case, kind, order_seed=order_seed)

    raise ValueError(f"unsupported controller arm: {arm}")


def evaluate_controller(case: A0Case, prediction: ProposalKind | CandidateProposal) -> EvaluationRecord:
    predicted_kind = prediction.kind if isinstance(prediction, CandidateProposal) else prediction
    gold_kind = _kind_for_responsibility(derive_responsibility(case))
    candidate = _candidate(case, predicted_kind, order_seed="evaluation-cost")
    false_closure = predicted_kind is ProposalKind.ACT and gold_kind is not ProposalKind.ACT
    unnecessary_reframe = (
        predicted_kind is ProposalKind.REFRAME_REPRESENTATION
        and gold_kind is not ProposalKind.REFRAME_REPRESENTATION
    )
    invalid_action = predicted_kind is ProposalKind.ACT and (
        case.evidence_state != "COMPLETE"
        or case.execution_gate != "PASS"
        or case.compatible_failure_active
    )
    return EvaluationRecord(
        correct=predicted_kind is gold_kind,
        unnecessary_reframe=unnecessary_reframe,
        false_closure=false_closure,
        invalid_action=invalid_action,
        unresolved_correct=(
            gold_kind is ProposalKind.UNRESOLVED and predicted_kind is ProposalKind.UNRESOLVED
        ),
        cost_units=candidate.cost_units,
    )


def _metrics(records: Iterable[EvaluationRecord], *, unresolved_total: int) -> dict[str, object]:
    rows = tuple(records)
    n = len(rows)
    unresolved_correct = sum(int(row.unresolved_correct) for row in rows)
    return {
        "sample_count": n,
        "accuracy": sum(int(row.correct) for row in rows) / n if n else None,
        "unnecessary_reframe_rate": sum(int(row.unnecessary_reframe) for row in rows) / n if n else None,
        "false_closure_rate": sum(int(row.false_closure) for row in rows) / n if n else None,
        "invalid_action_rate": sum(int(row.invalid_action) for row in rows) / n if n else None,
        "unresolved_accuracy": unresolved_correct / unresolved_total if unresolved_total else None,
        "mean_decision_cost_units": sum(row.cost_units for row in rows) / n if n else None,
    }


def run_a0(*, seed: str = "p10-a0-responsibility-control-v1", cases_per_family: int = 128) -> dict[str, object]:
    if cases_per_family <= 0:
        raise ValueError("cases_per_family must be positive")
    cases: list[A0Case] = []
    family_counts: dict[str, int] = {}
    for family_index, responsibility in enumerate(Responsibility):
        family_counts[responsibility.value] = cases_per_family
        for index in range(cases_per_family):
            # The opaque seed excludes responsibility names from visible ids.
            case_seed = _opaque(seed, str(family_index), str(index), "case", length=32)
            cases.append(build_case(responsibility, seed=case_seed))

    unresolved_total = sum(
        int(derive_responsibility(case) is Responsibility.UNRESOLVED) for case in cases
    )
    arms: dict[str, dict[str, object]] = {}
    for arm in ControllerArm:
        records = [evaluate_controller(case, predict(arm, case)) for case in cases]
        arms[arm.value] = _metrics(records, unresolved_total=unresolved_total)

    orion = arms[ControllerArm.ORION_RESPONSIBILITY_CONTROL.value]
    donor = arms[ControllerArm.DONOR_COMPOSED_CONTROL.value]
    symbolic = arms[ControllerArm.SYMBOLIC_FEASIBILITY_CONTROL.value]
    dependency = arms[ControllerArm.DEPENDENCY_SUPPORT_CONTROL.value]
    serialized = arms[ControllerArm.SERIALIZED_STATE_RULE.value]

    if serialized["accuracy"] == 1.0:
        terminal = "P10_NO_CONTROL_RESIDUAL"
    elif (
        symbolic["accuracy"] is not None
        and dependency["accuracy"] is not None
        and max(float(symbolic["accuracy"]), float(dependency["accuracy"])) >= float(orion["accuracy"]) - 0.02
        and max(float(symbolic["false_closure_rate"]), float(dependency["false_closure_rate"])) <= float(orion["false_closure_rate"])
    ):
        terminal = "P10_GRAPH_OR_SYMBOLIC_CONTROL_SUFFICIENT"
    elif (
        abs(float(donor["accuracy"]) - float(orion["accuracy"])) <= 0.02
        and float(donor["false_closure_rate"]) <= float(orion["false_closure_rate"])
        and float(donor["unnecessary_reframe_rate"]) <= float(orion["unnecessary_reframe_rate"])
    ):
        terminal = "P10_EXISTING_STRUCTURED_CONTROL_SUFFICIENT"
    elif float(orion["accuracy"]) == 1.0 and float(orion["accuracy"]) - float(donor["accuracy"]) >= 0.10:
        terminal = "P10_RESPONSIBILITY_CONTROL_INCREMENTAL_VALUE"
    else:
        terminal = "CANNOT_CHECK"

    return {
        "schema": "P10.A0ResponsibilityControlResult.v1",
        "protocol": "P10.A0ResponsibilityControlProtocol.v1",
        "seed_digest": "sha256:" + hashlib.sha256(seed.encode("utf-8")).hexdigest(),
        "cases_per_family": cases_per_family,
        "family_counts": family_counts,
        "arms": arms,
        "terminal": terminal,
        "claim_ceiling": "finite exact fixed-proposal responsibility-routing worlds only",
        "scientific_authority": "NONE_BOUNDED_DIAGNOSTIC",
        "grants_live_llm_escalation": terminal == "P10_RESPONSIBILITY_CONTROL_INCREMENTAL_VALUE",
    }


__all__ = [
    "A0Case",
    "CandidateProposal",
    "ControllerArm",
    "EvaluationRecord",
    "ProposalKind",
    "Responsibility",
    "build_case",
    "candidate_packet",
    "derive_responsibility",
    "evaluate_controller",
    "model_payload",
    "predict",
    "run_a0",
]
