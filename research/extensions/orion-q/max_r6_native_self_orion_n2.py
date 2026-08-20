#!/usr/bin/env python3
"""Native Self-ORION N2 after system-selected interface closure.

This stage uses the production ORION responsibility/revision/control stack.
No operator-authored quantum construction is visible or imported.
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
from orion.transfer.v2.epistemic_responsibility import (
    ResponsibilityStatus,
    assess_responsibility,
    build_responsibility_hypothesis,
)

import max_r6_native_self_orion_n0 as n0

HERE = Path(__file__).resolve().parent
STATE_PATH = HERE / "MAX_R6_NATIVE_CONTROL_N2_STATE.json"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_state():
    raw = STATE_PATH.read_bytes()
    state = json.loads(raw)
    if state["version"] != "ORIONQ.MAXR6.NativeControlState.v1":
        raise ValueError("unexpected state version")
    if state["stage"] != "N2" or state["frozen_after_interface_closure"] is not True:
        raise ValueError("N2 state is not frozen after interface closure")
    if state["operator_proposed_quantum_candidate_hidden"] is not True:
        raise ValueError("operator-proposed candidate is visible")
    if state["fresh_r6_subject_coefficients_accessed"] is not False:
        raise ValueError("fresh R6 subject was accessed before native N2")
    return state, sha_bytes(raw)


def build_responsibility(state):
    ev = state["visible_evidence"]
    hypotheses = (
        build_responsibility_hypothesis(
            hypothesis_id="RESP:CURRENT_SEARCH_INCOMPLETE",
            claim_id=n0.CLAIM,
            expected_observations={"R5H_CURRENT_ALPHABET_EXACT": ("NO",)},
            support_evidence_ids=("r5h-search-space-status",),
        ),
        build_responsibility_hypothesis(
            hypothesis_id="RESP:DONOR_CLOSURE_INCOMPLETE",
            claim_id=n0.CLAIM,
            expected_observations={
                "R5H_CURRENT_ALPHABET_EXACT": ("YES",),
                "GENERAL_M_DONOR_OUTCOME": ("DOMINATES_OR_INCONCLUSIVE",),
                "FOQCS_INTERFACE_ENVELOPE": ("UNRESOLVED",),
            },
            support_evidence_ids=("donor-closure-status",),
        ),
        build_responsibility_hypothesis(
            hypothesis_id="RESP:INTERFACE_INADEQUATE",
            claim_id=n0.CLAIM,
            expected_observations={
                "R5H_CURRENT_ALPHABET_EXACT": ("YES",),
                "GENERAL_M_DONOR_OUTCOME": ("NONDOMINATING_OR_CLOSED",),
                "FOQCS_INTERFACE_ENVELOPE": ("OPTIMISTIC_BOUND_REGISTERED",),
                "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR": ("YES", "UNRESOLVED"),
            },
            support_evidence_ids=("foqcs-interface-envelope",),
        ),
        build_responsibility_hypothesis(
            hypothesis_id="RESP:METHOD_LANGUAGE_INADEQUATE",
            claim_id=n0.CLAIM,
            expected_observations={
                "R5H_CURRENT_ALPHABET_EXACT": ("YES",),
                "GENERAL_M_DONOR_OUTCOME": ("NONDOMINATING_OR_CLOSED",),
                "FOQCS_INTERFACE_ENVELOPE": ("OPTIMISTIC_BOUND_REGISTERED",),
                "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR": ("NO",),
                "CURRENT_METHOD_INCREMENTAL_VALUE_ON_H4": (
                    "NONE_OVER_DIRECT_CLIQUE_DONOR",
                ),
            },
            support_evidence_ids=("r5h-mixed-collapse", "foqcs-optimistic-envelope",),
        ),
    )
    observed = {
        "R5H_CURRENT_ALPHABET_EXACT": ev["R5H_CURRENT_ALPHABET_EXACT"],
        "GENERAL_M_DONOR_OUTCOME": ev["GENERAL_M_DONOR_OUTCOME"],
        "FOQCS_INTERFACE_ENVELOPE": ev["FOQCS_INTERFACE_ENVELOPE"],
        "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR": ev[
            "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR"
        ],
        "CURRENT_METHOD_INCREMENTAL_VALUE_ON_H4": ev[
            "CURRENT_METHOD_INCREMENTAL_VALUE_ON_H4"
        ],
    }
    return hypotheses, observed, assess_responsibility(hypotheses, observed_outcomes=observed)


def optional_computation():
    actions = (
        build_computation_action(
            action_id="COMPUTE:FOQCS_REAL_PREP_RESOURCES",
            claim_id=n0.CLAIM,
            kind="REFINE_ABSORBED_INTERFACE_COST",
            expected_decision_value=0.5,
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
    hypotheses, observed, responsibility = build_responsibility(state)
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
    computation = optional_computation()
    control = compose_epistemic_control(revision=revision, computation=computation)

    # P9/no-P10 shadow receives identical evidence but cannot grow method language.
    shadow_mechanics = mechanics[:3]
    shadow_assessments = assessments[:3]
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
        "responsibility_identified": responsibility.status is ResponsibilityStatus.IDENTIFIED,
        "responsibility_is_method_language": responsibility.identified_hypothesis_id
        == "RESP:METHOD_LANGUAGE_INADEQUATE",
        "revision_candidate_selected": revision.status is RevisionGateStatus.CANDIDATE_SELECTED,
        "selected_revision_is_grow_language": revision.selected_mechanic_id
        == "REV:GROW_METHOD_LANGUAGE",
        "native_control_is_revision_candidate": control.status
        is EpistemicControlStatus.REVISION_CANDIDATE,
        "native_control_selects_grow_language": control.selected_revision_mechanic_id
        == "REV:GROW_METHOD_LANGUAGE",
        "shadow_cannot_select_grow_language": shadow_control.selected_revision_mechanic_id is None,
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
        "schema": "ORIONQ.MAXR6.NativeSelfOrionN2.v1",
        "authority": "N2_NATIVE_SELF_ORION_METHOD_LANGUAGE_GROWTH_SELECTED__NONAUTHORIZING__NOT_R6",
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
    print("ORIONQ_MAX_R6_NATIVE_N2=" + json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
