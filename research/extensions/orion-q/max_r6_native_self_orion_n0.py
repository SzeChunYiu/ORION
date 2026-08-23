#!/usr/bin/env python3
"""Native Self-ORION N0 control experiment for ORION-Q MAX-R6.

Unlike the earlier quantum-method scripts, this file does not implement its own
responsibility, revision-selection, computation-allocation, or control policy.
It adapts the blinded R5H state into the existing ORION formal control stack.

Protocol:
  development/orion-q-max-r0/MAX_R6_NATIVE_SELF_ORION_CONTROL_PROTOCOL.md
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.self_orion.epistemic_control import (
    EpistemicControlStatus,
    compose_epistemic_control,
)
from orion.self_orion.revision_gate import assess_revision_gate
from orion.transfer.v2.epistemic_computation import (
    ComputationActionState,
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

CLAIM = "orion-q:max-r6-native-controller"
HERE = Path(__file__).resolve().parent
STATE_PATH = HERE / "MAX_R6_NATIVE_CONTROL_N0_STATE.json"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_state() -> tuple[dict, str]:
    raw = STATE_PATH.read_bytes()
    state = json.loads(raw)
    if state["version"] != "ORIONQ.MAXR6.NativeControlState.v1":
        raise ValueError("unexpected native-control state version")
    if state["stage"] != "N0" or state["frozen_before_native_decision"] is not True:
        raise ValueError("N0 state not prospectively frozen")
    if state["operator_proposed_quantum_candidate_hidden"] is not True:
        raise ValueError("operator-proposed candidate is not blinded")
    if state["fresh_r6_subject_coefficients_accessed"] is not False:
        raise ValueError("fresh R6 subject was accessed before native control")
    return state, sha_bytes(raw)


def build_responsibility(observed: dict[str, str]):
    hypotheses = (
        build_responsibility_hypothesis(
            hypothesis_id="RESP:CURRENT_SEARCH_INCOMPLETE",
            claim_id=CLAIM,
            expected_observations={"R5H_CURRENT_ALPHABET_EXACT": ("NO",)},
            support_evidence_ids=("r5h-search-space-status",),
        ),
        build_responsibility_hypothesis(
            hypothesis_id="RESP:DONOR_CLOSURE_INCOMPLETE",
            claim_id=CLAIM,
            expected_observations={
                "R5H_CURRENT_ALPHABET_EXACT": ("YES",),
                "GENERAL_M_DONOR_OUTCOME": ("UNRESOLVED", "DOMINATES_OR_INCONCLUSIVE"),
                "FOQCS_GENERIC_PREP_OUTCOME": ("UNRESOLVED",),
            },
            support_evidence_ids=("r5h-donor-absorption",),
        ),
        build_responsibility_hypothesis(
            hypothesis_id="RESP:INTERFACE_INADEQUATE",
            claim_id=CLAIM,
            expected_observations={
                "R5H_CURRENT_ALPHABET_EXACT": ("YES",),
                "GENERAL_M_DONOR_OUTCOME": ("NONDOMINATING_OR_CLOSED",),
                "FOQCS_GENERIC_PREP_OUTCOME": ("GENERIC_MATCHED_ROUTE_AVAILABLE",),
            },
            support_evidence_ids=("outer-select-donor-open",),
        ),
        build_responsibility_hypothesis(
            hypothesis_id="RESP:METHOD_LANGUAGE_INADEQUATE",
            claim_id=CLAIM,
            expected_observations={
                "R5H_CURRENT_ALPHABET_EXACT": ("YES",),
                "GENERAL_M_DONOR_OUTCOME": ("NONDOMINATING_OR_CLOSED",),
                "FOQCS_GENERIC_PREP_OUTCOME": ("NO_GENERIC_MATCHED_ROUTE",),
            },
            support_evidence_ids=("r5h-mixed-collapse",),
        ),
    )
    return hypotheses, assess_responsibility(hypotheses, observed_outcomes=observed)


def build_interface():
    checks = (
        build_interface_check(
            check_id="IFACE:ACCESS_CONTRACT_MATCHED",
            scope="ACCESS_MODEL",
            state=InterfaceCheckState.PASS,
            evidence_ids=("r5h-same-jw-access",),
        ),
        build_interface_check(
            check_id="IFACE:NONCOMPENSATORY_RESOURCES_PRESENT",
            scope="RESOURCE_VECTOR",
            state=InterfaceCheckState.PASS,
            evidence_ids=("r5h-lambda-cnot-t-blocks-ancilla",),
        ),
    )
    return assess_interface_adequacy(checks)


def build_mechanics():
    mechanics = (
        build_mechanic(
            mechanic_id="REV:SEARCH_CURRENT_ALPHABET",
            claim_id=CLAIM,
            kind="SEARCH_MORE",
            read_coordinates=("EVIDENCE", "METHOD_LANGUAGE"),
            write_coordinates=("SEARCH_POLICY",),
            preservation_obligations=("PRESERVE:ACCESS", "PRESERVE:RESOURCE_VECTOR"),
            cost=1.0,
        ),
        build_mechanic(
            mechanic_id="REV:ABSORB_DONOR",
            claim_id=CLAIM,
            kind="ABSORB_DONOR",
            read_coordinates=("EVIDENCE", "DONOR_REGISTRY"),
            write_coordinates=("DONOR_REGISTRY",),
            preservation_obligations=("PRESERVE:ACCESS", "PRESERVE:RESOURCE_VECTOR"),
            cost=1.0,
        ),
        build_mechanic(
            mechanic_id="REV:CHANGE_INTERFACE",
            claim_id=CLAIM,
            kind="CHANGE_INTERFACE",
            read_coordinates=("EVIDENCE", "INTERFACE"),
            write_coordinates=("INTERFACE",),
            preservation_obligations=("PRESERVE:SCIENTIFIC_TARGET", "PRESERVE:RESOURCE_VECTOR"),
            cost=2.0,
        ),
        build_mechanic(
            mechanic_id="REV:GROW_METHOD_LANGUAGE",
            claim_id=CLAIM,
            kind="GROW_LANGUAGE",
            read_coordinates=("EVIDENCE", "METHOD_LANGUAGE", "REPRESENTATION"),
            write_coordinates=("METHOD_LANGUAGE", "REPRESENTATION"),
            preservation_obligations=(
                "PRESERVE:ACCESS",
                "PRESERVE:SCIENTIFIC_TARGET",
                "PRESERVE:RESOURCE_VECTOR",
            ),
            cost=3.0,
        ),
    )
    assessments = tuple(
        assess_mechanic(mechanic, obligation_states={}) for mechanic in mechanics
    )
    return mechanics, assessments


def build_computation(active_obligations: tuple[str, ...]):
    actions = (
        build_computation_action(
            action_id="COMPUTE:DONOR_CLOSURE_PACKET",
            claim_id=CLAIM,
            kind="VERIFY_DONOR_CLOSURE",
            expected_decision_value=2.0,
            cost=1.0,
            discharges_obligations=(
                "DONOR_GENERAL_M_TARE_CLOSURE",
                "DONOR_FOQCS_GENERIC_PREP_CLOSURE",
            ),
        ),
        build_computation_action(
            action_id="COMPUTE:CURRENT_ALPHABET_REPLAY",
            claim_id=CLAIM,
            kind="REPLAY_CURRENT_LANGUAGE",
            expected_decision_value=0.25,
            cost=1.0,
        ),
    )
    assessments = tuple(
        assess_computation_action(
            action,
            requirement_states={
                name: ComputationActionState.SATISFIED for name in action.hard_requirements
            },
        )
        for action in actions
    )
    selection = select_epistemic_computation(
        actions,
        assessments,
        active_hard_obligations=active_obligations,
    )
    return actions, assessments, selection


def main():
    state, state_sha = load_state()
    observed = {
        "R5H_CURRENT_ALPHABET_EXACT": state["visible_evidence"]["R5H_CURRENT_ALPHABET_EXACT"]
    }
    hypotheses, responsibility = build_responsibility(observed)
    interface = build_interface()
    mechanics, mechanic_assessments = build_mechanics()

    bindings = {
        "RESP:CURRENT_SEARCH_INCOMPLETE": ("REV:SEARCH_CURRENT_ALPHABET",),
        "RESP:DONOR_CLOSURE_INCOMPLETE": ("REV:ABSORB_DONOR",),
        "RESP:INTERFACE_INADEQUATE": ("REV:CHANGE_INTERFACE",),
        "RESP:METHOD_LANGUAGE_INADEQUATE": ("REV:GROW_METHOD_LANGUAGE",),
    }
    revision = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=mechanic_assessments,
        responsibility_bindings=bindings,
    )

    active = tuple(state["unresolved_donor_obligations"])
    _actions, _action_assessments, computation = build_computation(active)
    control = compose_epistemic_control(
        revision=revision,
        computation=computation,
    )

    # P9/no-P10 shadow: same evidence + computation actions. Since responsibility
    # is unresolved at N0, its revision gate is intentionally irrelevant to hard
    # computation precedence; use only non-language mechanics.
    shadow_mechanics = mechanics[:3]
    shadow_assessments = mechanic_assessments[:3]
    shadow_bindings = {
        "RESP:CURRENT_SEARCH_INCOMPLETE": ("REV:SEARCH_CURRENT_ALPHABET",),
        "RESP:DONOR_CLOSURE_INCOMPLETE": ("REV:ABSORB_DONOR",),
        "RESP:INTERFACE_INADEQUATE": ("REV:CHANGE_INTERFACE",),
        "RESP:METHOD_LANGUAGE_INADEQUATE": (),
    }
    shadow_revision = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=shadow_mechanics,
        assessments=shadow_assessments,
        responsibility_bindings=shadow_bindings,
    )
    shadow_control = compose_epistemic_control(
        revision=shadow_revision,
        computation=computation,
    )

    gates = {
        "state_blinded": state["operator_proposed_quantum_candidate_hidden"] is True,
        "fresh_subject_unopened": state["fresh_r6_subject_coefficients_accessed"] is False,
        "native_responsibility_unresolved_before_donor_closure": responsibility.status
        is ResponsibilityStatus.UNRESOLVED,
        "native_control_requires_computation": control.status
        is EpistemicControlStatus.COMPUTATION_REQUIRED,
        "native_control_selects_donor_closure": control.selected_computation_action_id
        == "COMPUTE:DONOR_CLOSURE_PACKET",
        "no_revision_selected_before_donor_closure": control.selected_revision_mechanic_id is None,
        "shadow_same_hard_computation": shadow_control.status
        is EpistemicControlStatus.COMPUTATION_REQUIRED
        and shadow_control.selected_computation_action_id
        == "COMPUTE:DONOR_CLOSURE_PACKET",
    }
    if not all(gates.values()):
        raise AssertionError({"gates": gates, "control": control.unsigned()})

    out = {
        "schema": "ORIONQ.MAXR6.NativeSelfOrionN0.v1",
        "authority": "N0_NATIVE_SELF_ORION_CONTROL_GREEN__COMPUTATION_REQUIRED__NOT_R6",
        "state_sha256": state_sha,
        "visible_observations": observed,
        "responsibility": responsibility.unsigned(),
        "interface": interface.unsigned(),
        "revision_gate": revision.unsigned(),
        "computation_selection": computation.unsigned(),
        "self_orion_control": control.unsigned(),
        "shadow_control": shadow_control.unsigned(),
        "responsibility_hypothesis_ids": [h.hypothesis_id for h in hypotheses],
        "revision_mechanic_ids": [m.mechanic_id for m in mechanics],
        "active_hard_obligations": list(active),
        "gates": gates,
        "r6_authority": False,
    }
    print("ORIONQ_MAX_R6_NATIVE_N0=" + json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
