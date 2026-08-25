from __future__ import annotations

from typing import Any, Mapping

from orion.self_orion.epistemic_control import compose_epistemic_control
from orion.self_orion.revision_gate import assess_revision_gate
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

from .campaign_protocol import CampaignDecision, CampaignState, authority_false
from .protocol import content_digest


def manifest_digest(manifest: Mapping[str, Any]) -> str:
    return content_digest(dict(manifest))


def _phase(manifest: Mapping[str, Any], phase_id: str) -> Mapping[str, Any]:
    phases = manifest.get("phases")
    if not isinstance(phases, Mapping) or phase_id not in phases:
        raise ValueError(f"unknown campaign phase: {phase_id}")
    phase = phases[phase_id]
    if not isinstance(phase, Mapping):
        raise TypeError("campaign phase must be an object")
    return phase


def _strict_bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a boolean")
    return value


def _array(value: Any, name: str) -> tuple[Any, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise TypeError(f"{name} must be an array")
    return tuple(value)


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    if not isinstance(manifest, Mapping):
        raise TypeError("campaign manifest must be an object")
    if manifest.get("schema") != "ORION.ResearchCampaignManifest.v1":
        raise ValueError("unsupported research campaign manifest")
    for key in ("campaign_id", "claim_id", "initial_phase"):
        if not isinstance(manifest.get(key), str) or not str(manifest[key]).strip():
            raise ValueError(f"campaign manifest requires {key}")
    phases = manifest.get("phases")
    if not isinstance(phases, Mapping) or not phases:
        raise ValueError("campaign manifest requires phases")
    if manifest["initial_phase"] not in phases:
        raise ValueError("initial_phase is absent from phases")
    capabilities = manifest.get("capabilities", {})
    if not isinstance(capabilities, Mapping):
        raise TypeError("campaign capabilities must be an object")
    for capability_id, spec in capabilities.items():
        if not isinstance(capability_id, str) or not capability_id.strip():
            raise ValueError("capability id must be non-empty")
        if not isinstance(spec, Mapping):
            raise TypeError("capability spec must be an object")
        if not isinstance(spec.get("host_capability"), str) or not spec["host_capability"].strip():
            raise ValueError(f"capability {capability_id} missing host_capability")
        if not isinstance(spec.get("payload"), Mapping):
            raise TypeError(f"capability {capability_id} payload must be an object")
        if not isinstance(spec.get("next_phase"), str):
            raise TypeError(f"capability {capability_id} next_phase must be a string")
    for phase_id, phase in phases.items():
        if not isinstance(phase, Mapping):
            raise TypeError(f"phase {phase_id} must be an object")
        if phase.get("terminal") is True:
            continue
        for field in (
            "responsibility_hypotheses",
            "interface_checks",
            "revision_mechanics",
            "computation_actions",
            "responsibility_bindings",
        ):
            if field not in phase:
                raise ValueError(f"phase {phase_id} missing {field}")
        hypothesis_ids = []
        for row in _array(phase["responsibility_hypotheses"], "responsibility_hypotheses"):
            if not isinstance(row, Mapping):
                raise TypeError("responsibility hypothesis must be an object")
            hypothesis_id = row.get("hypothesis_id")
            if not isinstance(hypothesis_id, str) or not hypothesis_id.strip():
                raise TypeError("hypothesis_id must be a non-empty string")
            hypothesis_ids.append(hypothesis_id)
            expected = row.get("expected_observations")
            if not isinstance(expected, Mapping):
                raise TypeError("expected_observations must be an object")
            for values in expected.values():
                _array(values, "expected observation values")

        mechanic_ids = []
        for row in _array(phase["revision_mechanics"], "revision_mechanics"):
            if not isinstance(row, Mapping):
                raise TypeError("revision mechanic must be an object")
            mechanic_id = row.get("mechanic_id")
            if not isinstance(mechanic_id, str) or not mechanic_id.strip():
                raise TypeError("mechanic_id must be a non-empty string")
            mechanic_ids.append(mechanic_id)

        action_ids = []
        for row in _array(phase["computation_actions"], "computation_actions"):
            if not isinstance(row, Mapping):
                raise TypeError("computation action must be an object")
            action_id = row.get("action_id")
            if not isinstance(action_id, str) or not action_id.strip():
                raise TypeError("action_id must be a non-empty string")
            action_ids.append(action_id)

        for row in _array(phase["interface_checks"], "interface_checks"):
            if not isinstance(row, Mapping):
                raise TypeError("interface check must be an object")
            _strict_bool(row.get("required", True), "interface required")

        if len(hypothesis_ids) != len(set(hypothesis_ids)):
            raise ValueError(f"phase {phase_id} duplicates responsibility hypothesis")
        if len(mechanic_ids) != len(set(mechanic_ids)):
            raise ValueError(f"phase {phase_id} duplicates revision mechanic")
        if len(action_ids) != len(set(action_ids)):
            raise ValueError(f"phase {phase_id} duplicates computation action")
        bindings = phase["responsibility_bindings"]
        if not isinstance(bindings, Mapping):
            raise TypeError("responsibility_bindings must be an object")
        for hypothesis_id, bound_ids in bindings.items():
            if str(hypothesis_id) not in hypothesis_ids:
                raise ValueError(f"binding references unknown hypothesis: {hypothesis_id}")
            unknown = set(map(str, _array(bound_ids, "binding mechanic ids"))) - set(mechanic_ids)
            if unknown:
                raise ValueError(f"binding references unknown mechanics: {sorted(unknown)}")
        shadow_ids = phase.get("shadow_allowed_revision_ids")
        if shadow_ids is not None:
            allowed = tuple(map(str, _array(shadow_ids, "shadow_allowed_revision_ids")))
            if not allowed:
                raise ValueError("configured shadow revision allowlist cannot be empty")
            unknown = set(allowed) - set(mechanic_ids)
            if unknown:
                raise ValueError(
                    f"shadow allowlist references unknown mechanics: {sorted(unknown)}"
                )
        selected = phase.get("selected_capabilities", {})
        if not isinstance(selected, Mapping):
            raise TypeError("selected_capabilities must be an object")
        for _, capability_id in selected.items():
            if str(capability_id) not in capabilities:
                raise ValueError(f"phase {phase_id} selects unknown capability {capability_id}")
    for capability_id, spec in capabilities.items():
        if spec["next_phase"] not in phases:
            raise ValueError(
                f"capability {capability_id} points to unknown phase {spec['next_phase']}"
            )


def _responsibility(state: CampaignState, phase: Mapping[str, Any]):
    hypotheses = tuple(
        build_responsibility_hypothesis(
            hypothesis_id=str(row["hypothesis_id"]),
            claim_id=state.claim_id,
            expected_observations={
                str(key): tuple(values) for key, values in row["expected_observations"].items()
            },
            support_evidence_ids=tuple(map(str, row.get("support_evidence_ids", ()))),
            defeater_evidence_ids=tuple(map(str, row.get("defeater_evidence_ids", ()))),
        )
        for row in phase["responsibility_hypotheses"]
    )
    return assess_responsibility(hypotheses, observed_outcomes=state.observation_map)


def _interface(phase: Mapping[str, Any]):
    checks = []
    for row in phase["interface_checks"]:
        required = row.get("required", True)
        _strict_bool(required, "interface check required")
        checks.append(
            build_interface_check(
                check_id=str(row["check_id"]),
                scope=str(row["scope"]),
                state=InterfaceCheckState(str(row["state"])),
                evidence_ids=tuple(map(str, row.get("evidence_ids", ()))),
                required=required,
            )
        )
    return assess_interface_adequacy(tuple(checks))


def _mechanics(state: CampaignState, phase: Mapping[str, Any]):
    mechanics = tuple(
        build_mechanic(
            mechanic_id=str(row["mechanic_id"]),
            claim_id=state.claim_id,
            kind=str(row.get("kind", "GENERIC")),
            read_coordinates=tuple(map(str, row.get("read_coordinates", ()))),
            write_coordinates=tuple(map(str, row.get("write_coordinates", ()))),
            preconditions=tuple(map(str, row.get("preconditions", ()))),
            hard_requirements=tuple(map(str, row.get("hard_requirements", ()))),
            preservation_obligations=tuple(map(str, row.get("preservation_obligations", ()))),
            required_authorities=tuple(map(str, row.get("required_authorities", ()))),
            cost=float(row.get("cost", 0.0)),
        )
        for row in phase["revision_mechanics"]
    )
    obligation_states = {
        str(key): ObligationState(str(value))
        for key, value in phase.get("mechanic_obligation_states", {}).items()
    }
    assessments = tuple(
        assess_mechanic(
            mechanic,
            obligation_states=obligation_states,
            granted_authorities=tuple(map(str, phase.get("granted_authorities", ()))),
            forbidden_writes=tuple(map(str, phase.get("forbidden_writes", ()))),
        )
        for mechanic in mechanics
    )
    return mechanics, assessments


def _computation(state: CampaignState, phase: Mapping[str, Any]):
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
        for row in phase["computation_actions"]
    )
    if not actions:
        raise ValueError("nonterminal phase requires computation_actions")
    requirement_states = {
        str(key): ComputationActionState(str(value))
        for key, value in phase.get("computation_requirement_states", {}).items()
    }
    assessments = tuple(
        assess_computation_action(
            action,
            requirement_states=requirement_states,
            available_authorities=tuple(
                map(str, phase.get("available_computation_authorities", ()))
            ),
        )
        for action in actions
    )
    return select_epistemic_computation(
        actions,
        assessments,
        active_hard_obligations=state.active_hard_obligations,
    )


def _bindings(
    phase: Mapping[str, Any], *, allowed: set[str] | None = None
) -> dict[str, tuple[str, ...]]:
    bindings: dict[str, tuple[str, ...]] = {}
    for hypothesis_id, mechanic_ids in phase["responsibility_bindings"].items():
        ids = tuple(map(str, mechanic_ids))
        if allowed is not None:
            ids = tuple(item for item in ids if item in allowed)
        bindings[str(hypothesis_id)] = ids
    return bindings


def decide_campaign(state: CampaignState, manifest: Mapping[str, Any]) -> CampaignDecision:
    state.validate()
    validate_manifest(manifest)
    if state.manifest_digest != manifest_digest(manifest):
        raise ValueError("campaign manifest changed after freeze")
    phase = _phase(manifest, state.phase_id)
    if phase.get("terminal") is True:
        raise ValueError("terminal phase has no decision")
    responsibility = _responsibility(state, phase)
    interface = _interface(phase)
    mechanics, assessments = _mechanics(state, phase)
    revision = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=assessments,
        responsibility_bindings=_bindings(phase),
    )
    computation = _computation(state, phase)
    control = compose_epistemic_control(revision=revision, computation=computation)
    shadow_control = None
    shadow_ids = phase.get("shadow_allowed_revision_ids")
    if shadow_ids is not None:
        allowed = set(map(str, shadow_ids))
        pairs = [
            (mechanic, assessment)
            for mechanic, assessment in zip(mechanics, assessments, strict=True)
            if mechanic.mechanic_id in allowed
        ]
        if not pairs:
            raise ValueError("configured shadow control selected no registered mechanics")
        shadow_revision = assess_revision_gate(
            responsibility=responsibility,
            interface=interface,
            mechanics=tuple(row[0] for row in pairs),
            assessments=tuple(row[1] for row in pairs),
            responsibility_bindings=_bindings(phase, allowed=allowed),
        )
        shadow_control = compose_epistemic_control(
            revision=shadow_revision,
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
        "schema": "ORION.ResearchCampaignDecision.v1",
        "phase_id": state.phase_id,
        "selected_kind": selected_kind,
        "selected_id": selected_id,
        "responsibility": responsibility.unsigned(),
        "interface": interface.unsigned(),
        "revision": revision.unsigned(),
        "computation": computation.unsigned(),
        "control": control.unsigned(),
        "shadow_control": (None if shadow_control is None else shadow_control.unsigned()),
        **authority_false(),
    }
    decision = CampaignDecision(
        phase_id=state.phase_id,
        selected_kind=selected_kind,
        selected_id=selected_id,
        responsibility=responsibility.unsigned(),
        interface=interface.unsigned(),
        revision=revision.unsigned(),
        computation=computation.unsigned(),
        control=control.unsigned(),
        shadow_control=None if shadow_control is None else shadow_control.unsigned(),
        decision_digest=content_digest(unsigned),
    )
    decision.validate()
    return decision


__all__ = ["decide_campaign", "manifest_digest", "validate_manifest"]
