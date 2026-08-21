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


def _string(value: Any, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{name} must be a non-empty string")
    return value


def _array(value: Any, *, name: str) -> tuple[Any, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (tuple, list)):
        raise TypeError(f"{name} must be an array")
    return tuple(value)


def _strings(value: Any, *, name: str) -> tuple[str, ...]:
    return tuple(_string(item, name=f"{name} entry") for item in _array(value, name=name))


def _number(value: Any, *, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{name} must be numeric")
    return float(value)


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


def _validate_string_array_field(row: Mapping[str, Any], field: str) -> None:
    if field in row:
        _strings(row[field], name=field)


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    if not isinstance(manifest, Mapping):
        raise TypeError("research campaign manifest must be an object")
    if manifest.get("schema") != "ORION.ResearchCampaignManifest.v1":
        raise ValueError("unsupported research campaign manifest")
    campaign_id = _string(manifest.get("campaign_id"), name="campaign_id")
    _string(manifest.get("claim_id"), name="claim_id")
    initial = _string(manifest.get("initial_phase"), name="initial_phase")
    if "authority_ceiling" in manifest:
        _string(manifest["authority_ceiling"], name="authority_ceiling")

    initial_observations = manifest.get("initial_observations", {})
    if not isinstance(initial_observations, Mapping):
        raise TypeError("initial_observations must be an object")
    for key, value in initial_observations.items():
        _string(key, name="initial observation key")
        _string(value, name="initial observation value")

    protected_refs = manifest.get("protected_refs", ())
    for raw in _array(protected_refs, name="protected_refs"):
        if not isinstance(raw, Mapping):
            raise TypeError("protected reference must be an object")
        _string(raw.get("ref_id"), name="protected ref_id")
        path = raw.get("path", "")
        blob = raw.get("blob", "")
        if not isinstance(path, str) or not isinstance(blob, str):
            raise TypeError("protected path/blob must be strings")
        if not path and not blob:
            raise ValueError("protected reference requires path or blob")
        released = raw.get("released", False)
        if not isinstance(released, bool):
            raise TypeError("protected released must be a boolean")

    phases = manifest.get("phases")
    if not isinstance(phases, Mapping) or not phases:
        raise ValueError("campaign manifest requires phases")
    if initial not in phases:
        raise ValueError("campaign initial_phase missing from phases")
    for phase_id in phases:
        _string(phase_id, name="phase id")

    capabilities = manifest.get("capabilities", {})
    if not isinstance(capabilities, Mapping):
        raise TypeError("campaign capabilities must be an object")
    capability_ids: set[str] = set()
    for capability_id, spec in capabilities.items():
        cid = _string(capability_id, name="capability id")
        if cid in capability_ids:
            raise ValueError(f"duplicate campaign capability: {cid}")
        capability_ids.add(cid)
        if not isinstance(spec, Mapping):
            raise TypeError("capability spec must be an object")
        _string(spec.get("host_capability"), name=f"{cid}.host_capability")
        if not isinstance(spec.get("payload"), Mapping):
            raise TypeError(f"{cid}.payload must be an object")
        _string(spec.get("next_phase"), name=f"{cid}.next_phase")
        _validate_string_array_field(spec, "declared_read_paths")
        _validate_string_array_field(spec, "release_protected_refs_on_success")
        contract = spec.get("result_contract", {})
        if not isinstance(contract, Mapping):
            raise TypeError(f"{cid}.result_contract must be an object")
        if "kind" in contract:
            _string(contract["kind"], name=f"{cid}.result_contract.kind")
        if contract.get("kind") == "SHELL_JSON_TOKEN":
            _string(contract.get("prefix"), name=f"{cid}.result_contract.prefix")
        for field in ("required_payload_values", "evidence_rules"):
            for contract_row in _array(contract.get(field, ()), name=f"{cid}.{field}"):
                if not isinstance(contract_row, Mapping):
                    raise TypeError(f"{cid}.{field} entries must be objects")
                if field == "required_payload_values" and "equals" not in contract_row:
                    raise ValueError(f"{cid}.{field} entry requires equals")
                if field == "evidence_rules":
                    _string(contract_row.get("evidence_key"), name="evidence_key")
                    if "literal" in contract_row and not isinstance(contract_row["literal"], str):
                        raise TypeError("evidence literal must be a string")
                    if "transform" in contract_row:
                        _string(contract_row["transform"], name="evidence transform")
                if "path" in contract_row:
                    path = _strings(contract_row["path"], name="contract path")
                    if not path:
                        raise ValueError("contract path cannot be empty")

    for phase_id, raw in phases.items():
        if not isinstance(raw, Mapping):
            raise TypeError(f"phase {phase_id} must be an object")
        terminal = raw.get("terminal", False)
        if not isinstance(terminal, bool):
            raise TypeError(f"phase {phase_id}.terminal must be a boolean")
        if terminal:
            if "terminal_name" in raw:
                _string(raw["terminal_name"], name=f"phase {phase_id}.terminal_name")
            _strings(raw.get("active_hard_obligations", ()), name="active_hard_obligations")
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
        _strings(raw.get("active_hard_obligations", ()), name="active_hard_obligations")

        hypothesis_ids: list[str] = []
        for row in _array(raw["responsibility_hypotheses"], name="responsibility_hypotheses"):
            if not isinstance(row, Mapping):
                raise TypeError("responsibility hypothesis must be an object")
            hid = _string(row.get("hypothesis_id"), name="hypothesis_id")
            hypothesis_ids.append(hid)
            expected = row.get("expected_observations")
            if not isinstance(expected, Mapping) or not expected:
                raise TypeError("expected_observations must be a non-empty object")
            for key, values in expected.items():
                _string(key, name="expected observation key")
                allowed = _strings(values, name="expected observation values")
                if not allowed:
                    raise ValueError("expected observation values cannot be empty")
            _validate_string_array_field(row, "support_evidence_ids")
            _validate_string_array_field(row, "defeater_evidence_ids")
        if len(hypothesis_ids) != len(set(hypothesis_ids)):
            raise ValueError(f"phase {phase_id} has duplicate responsibility hypotheses")

        for row in _array(raw["interface_checks"], name="interface_checks"):
            if not isinstance(row, Mapping):
                raise TypeError("interface check must be an object")
            _string(row.get("check_id"), name="check_id")
            _string(row.get("scope"), name="interface scope")
            _string(row.get("state"), name="interface state")
            required = row.get("required", True)
            if not isinstance(required, bool):
                raise TypeError("interface required must be a boolean")
            _validate_string_array_field(row, "evidence_ids")

        mechanic_ids: list[str] = []
        for row in _array(raw["revision_mechanics"], name="revision_mechanics"):
            if not isinstance(row, Mapping):
                raise TypeError("revision mechanic must be an object")
            mid = _string(row.get("mechanic_id"), name="mechanic_id")
            mechanic_ids.append(mid)
            _string(row.get("kind", "GENERIC"), name="mechanic kind")
            for field in (
                "read_coordinates",
                "write_coordinates",
                "preconditions",
                "hard_requirements",
                "preservation_obligations",
                "required_authorities",
            ):
                _validate_string_array_field(row, field)
            _number(row.get("cost", 0.0), name="mechanic cost")
        if len(mechanic_ids) != len(set(mechanic_ids)):
            raise ValueError(f"phase {phase_id} has duplicate revision mechanics")

        action_ids: list[str] = []
        for row in _array(raw["computation_actions"], name="computation_actions"):
            if not isinstance(row, Mapping):
                raise TypeError("computation action must be an object")
            aid = _string(row.get("action_id"), name="action_id")
            action_ids.append(aid)
            _string(row.get("kind"), name="computation kind")
            _number(row.get("expected_decision_value"), name="expected_decision_value")
            _number(row.get("cost"), name="computation cost")
            _validate_string_array_field(row, "hard_requirements")
            _validate_string_array_field(row, "discharges_obligations")
            _validate_string_array_field(row, "required_authorities")
        if len(action_ids) != len(set(action_ids)):
            raise ValueError(f"phase {phase_id} has duplicate computation actions")

        bindings = raw["responsibility_bindings"]
        if not isinstance(bindings, Mapping):
            raise TypeError("responsibility_bindings must be an object")
        for hypothesis_id, bound_ids in bindings.items():
            hid = _string(hypothesis_id, name="binding hypothesis id")
            if hid not in hypothesis_ids:
                raise ValueError(f"binding references unknown hypothesis: {hid}")
            for mechanic_id in _strings(bound_ids, name="binding mechanic ids"):
                if mechanic_id not in mechanic_ids:
                    raise ValueError(f"binding references unknown mechanic: {mechanic_id}")

        shadow_ids = raw.get("shadow_allowed_revision_ids")
        if shadow_ids is not None:
            allowed = _strings(shadow_ids, name="shadow_allowed_revision_ids")
            if not allowed:
                raise ValueError("configured shadow revision allowlist cannot be empty")
            unknown = set(allowed) - set(mechanic_ids)
            if unknown:
                raise ValueError(f"shadow allowlist references unknown mechanics: {sorted(unknown)}")

        selected = raw.get("selected_capabilities", {})
        if not isinstance(selected, Mapping):
            raise TypeError("selected_capabilities must be an object")
        selectable_ids = set(action_ids) | set(mechanic_ids)
        for selected_id, capability_id in selected.items():
            sid = _string(selected_id, name="selected capability source id")
            cid = _string(capability_id, name="selected capability id")
            if sid not in selectable_ids:
                raise ValueError(f"phase {phase_id} maps unknown selected id {sid}")
            if cid not in capability_ids:
                raise ValueError(
                    f"phase {phase_id} maps {sid} to unknown capability {cid}"
                )

    for cid, spec in capabilities.items():
        if spec["next_phase"] not in phases:
            raise ValueError(f"capability {cid} points to unknown phase {spec['next_phase']}")

    if not campaign_id:
        raise AssertionError("validated campaign id unexpectedly empty")


def _responsibility(state: CampaignState, phase: Mapping[str, Any]):
    hypotheses = tuple(
        build_responsibility_hypothesis(
            hypothesis_id=row["hypothesis_id"],
            claim_id=state.claim_id,
            expected_observations={
                key: tuple(values)
                for key, values in row["expected_observations"].items()
            },
            support_evidence_ids=tuple(row.get("support_evidence_ids", ())),
            defeater_evidence_ids=tuple(row.get("defeater_evidence_ids", ())),
        )
        for row in phase["responsibility_hypotheses"]
    )
    return assess_responsibility(hypotheses, observed_outcomes=state.observation_map)


def _interface(phase: Mapping[str, Any]):
    checks = tuple(
        build_interface_check(
            check_id=row["check_id"],
            scope=row["scope"],
            state=InterfaceCheckState(row["state"]),
            evidence_ids=tuple(row.get("evidence_ids", ())),
            required=row.get("required", True),
        )
        for row in phase["interface_checks"]
    )
    return assess_interface_adequacy(checks)


def _mechanics(state: CampaignState, phase: Mapping[str, Any]):
    mechanics = tuple(
        build_mechanic(
            mechanic_id=row["mechanic_id"],
            claim_id=state.claim_id,
            kind=row.get("kind", "GENERIC"),
            read_coordinates=tuple(row.get("read_coordinates", ())),
            write_coordinates=tuple(row.get("write_coordinates", ())),
            preconditions=tuple(row.get("preconditions", ())),
            hard_requirements=tuple(row.get("hard_requirements", ())),
            preservation_obligations=tuple(row.get("preservation_obligations", ())),
            required_authorities=tuple(row.get("required_authorities", ())),
            cost=float(row.get("cost", 0.0)),
        )
        for row in phase["revision_mechanics"]
    )
    obligation_states = {
        key: ObligationState(value)
        for key, value in phase.get("mechanic_obligation_states", {}).items()
    }
    assessments = tuple(
        assess_mechanic(
            mechanic,
            obligation_states=obligation_states,
            granted_authorities=tuple(phase.get("granted_authorities", ())),
            forbidden_writes=tuple(phase.get("forbidden_writes", ())),
        )
        for mechanic in mechanics
    )
    return mechanics, assessments


def _computation(state: CampaignState, phase: Mapping[str, Any]):
    actions = tuple(
        build_computation_action(
            action_id=row["action_id"],
            claim_id=state.claim_id,
            kind=row["kind"],
            expected_decision_value=float(row["expected_decision_value"]),
            cost=float(row["cost"]),
            hard_requirements=tuple(row.get("hard_requirements", ())),
            discharges_obligations=tuple(row.get("discharges_obligations", ())),
            required_authorities=tuple(row.get("required_authorities", ())),
        )
        for row in phase["computation_actions"]
    )
    if not actions:
        raise ValueError("nonterminal campaign phase requires at least one computation action")
    requirement_states = {
        key: ComputationActionState(value)
        for key, value in phase.get("computation_requirement_states", {}).items()
    }
    assessments = tuple(
        assess_computation_action(
            action,
            requirement_states=requirement_states,
            available_authorities=tuple(
                phase.get("available_computation_authorities", ())
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
        ids = tuple(mechanic_ids)
        if allowed is not None:
            ids = tuple(item for item in ids if item in allowed)
        out[hypothesis_id] = ids
    return out


def decide_campaign(state: CampaignState, manifest: Mapping[str, Any]) -> CampaignDecision:
    state.validate()
    validate_manifest(manifest)
    if state.manifest_digest != manifest_digest(manifest):
        raise ValueError("campaign manifest changed after state freeze")
    if state.campaign_id != manifest["campaign_id"]:
        raise ValueError("campaign identity mismatch")
    if state.claim_id != manifest["claim_id"]:
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
        allowed = set(shadow_ids)
        pairs = [
            (mechanic, assessment)
            for mechanic, assessment in zip(mechanics, mechanic_assessments, strict=True)
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
