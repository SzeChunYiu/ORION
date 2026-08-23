#!/usr/bin/env python3
"""Native Self-ORION N1 control after the N0-selected donor closure packet.

No operator-authored quantum construction is visible. This stage asks the
existing ORION formal stack to attribute the residual and nominate only the
registered class of next revision.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.self_orion.epistemic_control import EpistemicControlStatus, compose_epistemic_control
from orion.self_orion.revision_gate import RevisionGateStatus, assess_revision_gate
from orion.transfer.v2.epistemic_computation import (
    ComputationActionState,
    assess_computation_action,
    build_computation_action,
    select_epistemic_computation,
)
from orion.transfer.v2.epistemic_responsibility import ResponsibilityStatus

import max_r6_native_self_orion_n0 as n0

HERE = Path(__file__).resolve().parent
STATE_PATH = HERE / "MAX_R6_NATIVE_CONTROL_N1_STATE.json"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_state():
    raw = STATE_PATH.read_bytes()
    state = json.loads(raw)
    if state["version"] != "ORIONQ.MAXR6.NativeControlState.v1":
        raise ValueError("unexpected state version")
    if state["stage"] != "N1" or state["frozen_after_selected_donor_closure"] is not True:
        raise ValueError("N1 state is not frozen after donor closure")
    if state["operator_proposed_quantum_candidate_hidden"] is not True:
        raise ValueError("operator-proposed candidate is visible")
    if state["fresh_r6_subject_coefficients_accessed"] is not False:
        raise ValueError("fresh R6 subject was accessed before native N1")
    return state, sha_bytes(raw)


def n1_computation():
    # Optional evidence work only. There are no remaining N0 hard obligations.
    # A bounded revision candidate, if available, has precedence in the existing
    # Self-ORION controller over these optional computations.
    actions = (
        build_computation_action(
            action_id="COMPUTE:FOQCS_PREP_RESOURCE_PACKET",
            claim_id=n0.CLAIM,
            kind="COST_CANDIDATE_INTERFACE",
            expected_decision_value=1.5,
            cost=1.0,
        ),
        build_computation_action(
            action_id="COMPUTE:R5H_REPLAY",
            claim_id=n0.CLAIM,
            kind="REPLAY_CURRENT_LANGUAGE",
            expected_decision_value=0.1,
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
    return select_epistemic_computation(actions, assessments, active_hard_obligations=())


def main():
    state, state_sha = load_state()
    observed = {
        "R5H_CURRENT_ALPHABET_EXACT": state["visible_evidence"]["R5H_CURRENT_ALPHABET_EXACT"],
        "GENERAL_M_DONOR_OUTCOME": state["visible_evidence"]["GENERAL_M_DONOR_OUTCOME"],
        "FOQCS_GENERIC_PREP_OUTCOME": state["visible_evidence"]["FOQCS_GENERIC_PREP_OUTCOME"],
    }

    _hypotheses, responsibility = n0.build_responsibility(observed)
    interface = n0.build_interface()
    mechanics, assessments = n0.build_mechanics()
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
        assessments=assessments,
        responsibility_bindings=bindings,
    )
    computation = n1_computation()
    control = compose_epistemic_control(revision=revision, computation=computation)

    # Donor-composed P9/no-P10 shadow can search or absorb donors but cannot edit
    # representation/interface/method language. It receives the same observations
    # and optional computation menu.
    shadow_mechanics = mechanics[:2]
    shadow_assessments = assessments[:2]
    shadow_bindings = {
        "RESP:CURRENT_SEARCH_INCOMPLETE": ("REV:SEARCH_CURRENT_ALPHABET",),
        "RESP:DONOR_CLOSURE_INCOMPLETE": ("REV:ABSORB_DONOR",),
        "RESP:INTERFACE_INADEQUATE": (),
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
        "responsibility_identified": responsibility.status is ResponsibilityStatus.IDENTIFIED,
        "responsibility_is_interface": responsibility.identified_hypothesis_id
        == "RESP:INTERFACE_INADEQUATE",
        "revision_candidate_selected": revision.status is RevisionGateStatus.CANDIDATE_SELECTED,
        "selected_revision_is_interface": revision.selected_mechanic_id == "REV:CHANGE_INTERFACE",
        "native_control_is_revision_candidate": control.status is EpistemicControlStatus.REVISION_CANDIDATE,
        "native_control_selects_interface": control.selected_revision_mechanic_id
        == "REV:CHANGE_INTERFACE",
        "shadow_does_not_select_interface_revision": shadow_control.selected_revision_mechanic_id is None,
    }
    if not all(gates.values()):
        raise AssertionError(
            {
                "gates": gates,
                "responsibility": responsibility.unsigned(),
                "revision": revision.unsigned(),
                "control": control.unsigned(),
                "shadow": shadow_control.unsigned(),
            }
        )

    out = {
        "schema": "ORIONQ.MAXR6.NativeSelfOrionN1.v1",
        "authority": "N1_NATIVE_SELF_ORION_INTERFACE_REVISION_SELECTED__NONAUTHORIZING__NOT_R6",
        "state_sha256": state_sha,
        "observed_outcomes": observed,
        "responsibility": responsibility.unsigned(),
        "revision_gate": revision.unsigned(),
        "computation_selection": computation.unsigned(),
        "self_orion_control": control.unsigned(),
        "shadow_control": shadow_control.unsigned(),
        "gates": gates,
        "selected_revision_class": control.selected_revision_mechanic_id,
        "operator_proposed_quantum_candidate_used": False,
        "fresh_r6_subject_coefficients_accessed": False,
        "r6_authority": False,
    }
    print("ORIONQ_MAX_R6_NATIVE_N1=" + json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
