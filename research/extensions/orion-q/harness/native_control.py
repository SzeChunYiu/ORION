from __future__ import annotations

from typing import Mapping, Sequence

from orion.self_orion.epistemic_control import compose_epistemic_control
from orion.self_orion.revision_gate import assess_revision_gate
from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.epistemic_computation import (
    ComputationActionState,
    assess_computation_action,
    build_computation_action,
    select_epistemic_computation,
)
from orion.transfer.v2.epistemic_responsibility import (
    assess_responsibility,
    build_responsibility_hypothesis,
)
from orion.transfer.v2.higher_order_epistemic_mechanics import (
    ObligationState,
    assess_mechanic,
    build_mechanic,
)
from orion.transfer.v2.interface_adequacy import (
    InterfaceCheckState,
    assess_interface_adequacy,
    build_interface_check,
)

from .model import NativeDecisionReceipt, ResearchState


def _phase(manifest: Mapping[str, object], phase_id: str) -> Mapping[str, object]:
    phases = manifest.get("phases")
    if not isinstance(phases, Mapping) or phase_id not in phases:
        raise ValueError(f"unknown harness phase: {phase_id}")
    phase = phases[phase_id]
    if not isinstance(phase, Mapping):
        raise ValueError("phase must be an object")
    return phase


def _build_responsibility(state: ResearchState, phase: Mapping[str, object]):
    rows = phase.get("responsibility_hypotheses", ())
    hypotheses = tuple(
        build_responsibility_hypothesis(
            hypothesis_id=str(row["hypothesis_id"]),
            claim_id=state.claim_id,
            expected_observations={
                str(k): tuple(map(str, v)) for k, v in row["expected_observations"].items()
            },
            support_evidence_ids=tuple(map(str, row.get("support_evidence_ids", ()))),
            defeater_evidence_ids=tuple(map(str, row.get("defeater_evidence_ids", ()))),
        )
        for row in rows
    )
    return hypotheses, assess_responsibility(
        hypotheses,
        observed_outcomes=state.observation_map,
    )


def _build_interface(phase: Mapping[str, object]):
    rows = phase.get("interface_checks", ())
    checks = tuple(
        build_interface_check(
            check_id=str(row["check_id"]),
            scope=str(row["scope"]),
            state=InterfaceCheckState(str(row["state"])),
            evidence_ids=tuple(map(str, row.get("evidence_ids", ()))),
            required=bool(row.get("required", True)),
        )
        for row in rows
    )
    return assess_interface_adequacy(checks)


def _build_mechanics(state: ResearchState, phase: Mapping[str, object]):
    rows = phase.get("revision_mechanics", ())
    mechanics = tuple(
        build_mechanic(
            mechanic_id=str(row["mechanic_id"]),
            claim_id=state.claim_id,
            kind=str(row.get("kind", "GENERIC")),
            read_coordinates=tuple(map(str, row.get("read_coordinates", ()))),
            write_coordinates=tuple(map(str, row.get("write_coordinates", ()))),
            preconditions=tuple(map(str, row.get("preconditions", ()))),
            hard_requirements=tuple(map(str, row.get("hard_requirements", ()))),
            preservation_obligations=tuple(
                map(str, row.get("preservation_obligations", ()))
            ),
            required_authorities=tuple(map(str, row.get("required_authorities", ()))),
            cost=float(row.get("cost", 0.0)),
        )
        for row in rows
    )
    states = {
        str(k): ObligationState(str(v))
        for k, v in phase.get("mechanic_obligation_states", {}).items()
    }
    granted = tuple(map(str, phase.get("granted_authorities", ())))
    forbidden = tuple(map(str, phase.get("forbidden_writes", ())))
    assessments = tuple(
        assess_mechanic(
            mechanic,
            obligation_states=states,
            granted_authorities=granted,
            forbidden_writes=forbidden,
        )
        for mechanic in mechanics
    )
    return mechanics, assessments


def _build_computation(state: ResearchState, phase: Mapping[str, object]):
    rows = phase.get("computation_actions", ())
    actions = tuple(
        build_computation_action(
            action_id=str(row["action_id"]),
            claim_id=state.claim_id,
            kind=str(row["kind"]),
            expected_decision_value=float(row["expected_decision_value"]),
            cost=float(row["cost"]),
            hard_requirements=tuple(map(str, row.get("hard_requirements", ()))),
            discharges_obligations=tuple(map(str, row.get("discharges_obligations", ()))),
            required_authorities=tuple(map(str, row.get("required_authorities", ()))),
        )
        for row in rows
    )
    requirement_states = {
        str(k): ComputationActionState(str(v))
        for k, v in phase.get("computation_requirement_states", {}).items()
    }
    available_authorities = tuple(map(str, phase.get("available_computation_authorities", ())))
    assessments = tuple(
        assess_computation_action(
            action,
            requirement_states=requirement_states,
            available_authorities=available_authorities,
        )
        for action in actions
    )
    return actions, assessments, select_epistemic_computation(
        actions,
        assessments,
        active_hard_obligations=state.active_hard_obligations,
    )


def _bindings(phase: Mapping[str, object]) -> dict[str, tuple[str, ...]]:
    return {
        str(hypothesis_id): tuple(map(str, mechanic_ids))
        for hypothesis_id, mechanic_ids in phase.get("responsibility_bindings", {}).items()
    }


def _shadow_control(
    *,
    state: ResearchState,
    phase: Mapping[str, object],
    responsibility,
    interface,
    mechanics: Sequence[object],
    assessments: Sequence[object],
    computation,
):
    allowed = phase.get("shadow_allowed_revision_ids")
    if allowed is None:
        return None
    allowed_ids = set(map(str, allowed))
    kept_pairs = [
        (m, a) for m, a in zip(mechanics, assessments, strict=True) if m.mechanic_id in allowed_ids
    ]
    if not kept_pairs:
        return None
    shadow_mechanics = tuple(pair[0] for pair in kept_pairs)
    shadow_assessments = tuple(pair[1] for pair in kept_pairs)
    shadow_bindings = {
        hyp: tuple(mid for mid in mids if mid in allowed_ids)
        for hyp, mids in _bindings(phase).items()
    }
    shadow_revision = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=shadow_mechanics,
        assessments=shadow_assessments,
        responsibility_bindings=shadow_bindings,
    )
    return compose_epistemic_control(
        revision=shadow_revision,
        computation=computation,
    )


def decide_native(state: ResearchState, manifest: Mapping[str, object]) -> NativeDecisionReceipt:
    state.verify()
    if manifest.get("claim_id") != state.claim_id:
        raise ValueError("manifest/state claim mismatch")
    phase = _phase(manifest, state.phase_id)
    if phase.get("terminal") is True:
        raise ValueError("terminal phase has no native decision")

    _hypotheses, responsibility = _build_responsibility(state, phase)
    interface = _build_interface(phase)
    mechanics, mechanic_assessments = _build_mechanics(state, phase)
    revision = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=mechanic_assessments,
        responsibility_bindings=_bindings(phase),
    )
    _actions, _action_assessments, computation = _build_computation(state, phase)
    control = compose_epistemic_control(revision=revision, computation=computation)
    shadow = _shadow_control(
        state=state,
        phase=phase,
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=mechanic_assessments,
        computation=computation,
    )

    if control.selected_computation_action_id is not None:
        selected_kind = "COMPUTATION"
        selected_id = control.selected_computation_action_id
    elif control.selected_revision_mechanic_id is not None:
        selected_kind = "REVISION"
        selected_id = control.selected_revision_mechanic_id
    else:
        selected_kind = None
        selected_id = None

    unsigned = {
        "version": "ORIONQ.NativeDecisionReceipt.v1",
        "phase_id": state.phase_id,
        "selected_kind": selected_kind,
        "selected_id": selected_id,
        "responsibility": responsibility.unsigned(),
        "interface": interface.unsigned(),
        "revision": revision.unsigned(),
        "computation": computation.unsigned(),
        "control": control.unsigned(),
        "shadow_control": None if shadow is None else shadow.unsigned(),
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_revision_authority": False,
        "grants_adoption_authority": False,
        "grants_promotion_authority": False,
        "grants_merge_authority": False,
        "grants_global_task_stop_authority": False,
        "r6_authority": False,
    }
    receipt = NativeDecisionReceipt(
        phase_id=state.phase_id,
        selected_kind=selected_kind,
        selected_id=selected_id,
        responsibility=responsibility.unsigned(),
        interface=interface.unsigned(),
        revision=revision.unsigned(),
        computation=computation.unsigned(),
        control=control.unsigned(),
        shadow_control=None if shadow is None else shadow.unsigned(),
        digest=content_digest(unsigned),
    )
    receipt.verify()
    return receipt
