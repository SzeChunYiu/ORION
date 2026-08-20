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

from .campaign_protocol import CampaignDecision, CampaignState
from .protocol import content_digest


def manifest_digest(manifest: Mapping[str, Any]) -> str:
    return content_digest(dict(manifest))


def _phase(manifest: Mapping[str, Any], phase_id: str) -> Mapping[str, Any]:
    phases = manifest.get("phases")
    if not isinstance(phases, Mapping) or phase_id not in phases:
        raise ValueError(f"unknown campaign phase: {phase_id}")
    phase = phases[phase_id]
    if not isinstance(phase, Mapping):
        raise ValueError("campaign phase must be an object")
    return phase


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    if manifest.get("schema") != "ORION.ResearchCampaignManifest.v1":
        raise ValueError("unsupported research campaign manifest")
    if not str(manifest.get("campaign_id", "")) or not str(manifest.get("claim_id", "")):
        raise ValueError("campaign manifest identities are required")
    phases = manifest.get("phases")
    if not isinstance(phases, Mapping) or not phases:
        raise ValueError("campaign manifest requires phases")
    initial = str(manifest.get("initial_phase", ""))
    if initial not in phases:
        raise ValueError("campaign initial_phase missing from phases")

    capability_ids = set()
    for capability_id, spec in manifest.get("capabilities", {}).items():
        cid = str(capability_id)
        if cid in capability_ids:
            raise ValueError(f"duplicate campaign capability: {cid}")
        capability_ids.add(cid)
        if not isinstance(spec, Mapping):
            raise ValueError("capability spec must be an object")
        if "host_capability" not in spec or "payload" not in spec:
            raise ValueError(f"capability missing host contract: {cid}")

    for phase_id, raw in phases.items():
        if not isinstance(raw, Mapping):
            raise ValueError(f"phase {phase_id} must be an object")
        if raw.get("terminal") is True:
            continue
        for field in (
            "responsibility_hypotheses",
            "interface_checks",
            "revision_mechanics",
            "computation_actions",
            "responsibility_bindings",
        ):
            if field not in raw:
                raise ValueError(f"phase {phase_id} missing {field}")
        ids = [str(row["hypothesis_id"]) for row in raw["responsibility_hypotheses"]]
        if len(ids) != len(set(ids)):
            raise ValueError(f"phase {phase_id} has duplicate responsibility hypotheses")
        mids = [str(row["mechanic_id"]) for row in raw["revision_mechanics"]]
        if len(mids) != len(set(mids)):
            raise ValueError(f"phase {phase_id} has duplicate revision mechanics")
        aids = [str(row["action_id"]) for row in raw["computation_actions"]]
        if len(aids) != len(set(aids)):
            raise ValueError(f"phase {phase_id} has duplicate computation actions")
        for selected_id, capability_id in raw.get("selected_capabilities", {}).items():
            if str(capability_id) not in capability_ids:
                raise ValueError(
                    f"phase {phase_id} maps {selected_id} to unknown capability {capability_id}"
                )


def _responsibility(state: CampaignState, phase: Mapping[str, Any]):
    hypotheses = tuple(
        build_responsibility_hypothesis(
            hypothesis_id=str(row["hypothesis_id"]),
            claim_id=state.claim_id,
            expected_observations={
                str(key): tuple(map(str, values))
                for key, values in row["expected_observations"].items()
            },
            support_evidence_ids=tuple(map(str, row.get("support_evidence_ids", ()))),
            defeater_evidence_ids=tuple(map(str, row.get("defeater_evidence_ids", ()))),
        )
        for row in phase["responsibility_hypotheses"]
    )
    return assess_responsibility(hypotheses, observed_outcomes=state.observation_map)


def _interface(phase: Mapping[str, Any]):
    checks = tuple(
        build_interface_check(
            check_id=str(row["check_id"]),
            scope=str(row["scope"]),
            state=InterfaceCheckState(str(row["state"])),
            evidence_ids=tuple(map(str, row.get("evidence_ids", ()))),
            required=bool(row.get("required", True)),
        )
        for row in phase["interface_checks"]
    )
    return assess_interface_adequacy(checks)


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
            preservation_obligations=tuple(
                map(str, row.get("preservation_obligations", ()))
            ),
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
        raise ValueError("nonterminal campaign phase requires at least one computation action")
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


def _bindings(phase: Mapping[str, Any], *, allowed: set[str] | None = None):
    out = {}
    for hypothesis_id, mechanic_ids in phase["responsibility_bindings"].items():
        ids = tuple(map(str, mechanic_ids))
        if allowed is not None:
            ids = tuple(item for item in ids if item in allowed)
        out[str(hypothesis_id)] = ids
    return out


def decide_campaign(state: CampaignState, manifest: Mapping[str, Any]) -> CampaignDecision:
    state.validate()
    validate_manifest(manifest)
    if state.manifest_digest != manifest_digest(manifest):
        raise ValueError("campaign manifest changed after state freeze")
    if state.campaign_id != str(manifest["campaign_id"]):
        raise ValueError("campaign identity mismatch")
    if state.claim_id != str(manifest["claim_id"]):
        raise ValueError("campaign claim mismatch")

    phase = _phase(manifest, state.phase_id)
    if phase.get("terminal") is True:
        raise ValueError("terminal campaign phase has no native decision")

    responsibility = _responsibility(state, phase)
    interface = _interface(phase)
    mechanics, mechanic_assessments = _mechanics(state, phase)
    revision = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=mechanic_assessments,
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
            for mechanic, assessment in zip(mechanics, mechanic_assessments, strict=True)
            if mechanic.mechanic_id in allowed
        ]
        if pairs:
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
        "shadow_control": None if shadow_control is None else shadow_control.unsigned(),
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_adoption_authority": False,
        "grants_promotion_authority": False,
        "grants_merge_authority": False,
        "grants_global_task_stop_authority": False,
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
