from __future__ import annotations


def _interface_checks():
    return [
        {
            "check_id": "IFACE:ACCESS_CONTRACT_MATCHED",
            "scope": "ACCESS_MODEL",
            "state": "PASS",
            "evidence_ids": ["r5h-same-jw-access"],
        },
        {
            "check_id": "IFACE:NONCOMPENSATORY_RESOURCES_PRESENT",
            "scope": "RESOURCE_VECTOR",
            "state": "PASS",
            "evidence_ids": ["r5h-lambda-cnot-t-blocks-ancilla"],
        },
    ]


def _revision_mechanics():
    return [
        {
            "mechanic_id": "REV:SEARCH_CURRENT_ALPHABET",
            "kind": "SEARCH_MORE",
            "read_coordinates": ["EVIDENCE", "METHOD_LANGUAGE"],
            "write_coordinates": ["SEARCH_POLICY"],
            "preservation_obligations": ["PRESERVE:ACCESS", "PRESERVE:RESOURCE_VECTOR"],
            "cost": 1.0,
        },
        {
            "mechanic_id": "REV:ABSORB_DONOR",
            "kind": "ABSORB_DONOR",
            "read_coordinates": ["EVIDENCE", "DONOR_REGISTRY"],
            "write_coordinates": ["DONOR_REGISTRY"],
            "preservation_obligations": ["PRESERVE:ACCESS", "PRESERVE:RESOURCE_VECTOR"],
            "cost": 1.0,
        },
        {
            "mechanic_id": "REV:CHANGE_INTERFACE",
            "kind": "CHANGE_INTERFACE",
            "read_coordinates": ["EVIDENCE", "INTERFACE"],
            "write_coordinates": ["INTERFACE"],
            "preservation_obligations": [
                "PRESERVE:SCIENTIFIC_TARGET",
                "PRESERVE:RESOURCE_VECTOR",
            ],
            "cost": 2.0,
        },
        {
            "mechanic_id": "REV:GROW_METHOD_LANGUAGE",
            "kind": "GROW_LANGUAGE",
            "read_coordinates": ["EVIDENCE", "METHOD_LANGUAGE", "REPRESENTATION"],
            "write_coordinates": ["METHOD_LANGUAGE", "REPRESENTATION"],
            "preservation_obligations": [
                "PRESERVE:ACCESS",
                "PRESERVE:SCIENTIFIC_TARGET",
                "PRESERVE:RESOURCE_VECTOR",
            ],
            "cost": 3.0,
        },
    ]


def _bindings():
    return {
        "RESP:CURRENT_SEARCH_INCOMPLETE": ["REV:SEARCH_CURRENT_ALPHABET"],
        "RESP:DONOR_CLOSURE_INCOMPLETE": ["REV:ABSORB_DONOR"],
        "RESP:DONOR_GENERAL_M_INCOMPLETE": ["REV:ABSORB_DONOR"],
        "RESP:DONOR_INTERFACE_UNRESOLVED": ["REV:ABSORB_DONOR"],
        "RESP:INTERFACE_INADEQUATE": ["REV:CHANGE_INTERFACE"],
        "RESP:METHOD_LANGUAGE_INADEQUATE": ["REV:GROW_METHOD_LANGUAGE"],
    }


_N0_HYPOTHESES = [
    {
        "hypothesis_id": "RESP:CURRENT_SEARCH_INCOMPLETE",
        "expected_observations": {"R5H_CURRENT_ALPHABET_EXACT": ["NO"]},
        "support_evidence_ids": ["r5h-search-space-status"],
    },
    {
        "hypothesis_id": "RESP:DONOR_CLOSURE_INCOMPLETE",
        "expected_observations": {
            "R5H_CURRENT_ALPHABET_EXACT": ["YES"],
            "GENERAL_M_DONOR_OUTCOME": ["UNRESOLVED", "DOMINATES_OR_INCONCLUSIVE"],
            "FOQCS_GENERIC_PREP_OUTCOME": ["UNRESOLVED"],
        },
        "support_evidence_ids": ["r5h-donor-absorption"],
    },
    {
        "hypothesis_id": "RESP:INTERFACE_INADEQUATE",
        "expected_observations": {
            "R5H_CURRENT_ALPHABET_EXACT": ["YES"],
            "GENERAL_M_DONOR_OUTCOME": ["NONDOMINATING_OR_CLOSED"],
            "FOQCS_GENERIC_PREP_OUTCOME": ["GENERIC_MATCHED_ROUTE_AVAILABLE"],
        },
        "support_evidence_ids": ["outer-select-donor-open"],
    },
    {
        "hypothesis_id": "RESP:METHOD_LANGUAGE_INADEQUATE",
        "expected_observations": {
            "R5H_CURRENT_ALPHABET_EXACT": ["YES"],
            "GENERAL_M_DONOR_OUTCOME": ["NONDOMINATING_OR_CLOSED"],
            "FOQCS_GENERIC_PREP_OUTCOME": ["NO_GENERIC_MATCHED_ROUTE"],
        },
        "support_evidence_ids": ["r5h-mixed-collapse"],
    },
]

_N2_ATOMIC_HYPOTHESES = [
    {
        "hypothesis_id": "RESP:CURRENT_SEARCH_INCOMPLETE",
        "expected_observations": {"R5H_CURRENT_ALPHABET_EXACT": ["NO"]},
        "support_evidence_ids": ["r5h-search-space-status"],
    },
    {
        "hypothesis_id": "RESP:DONOR_GENERAL_M_INCOMPLETE",
        "expected_observations": {
            "R5H_CURRENT_ALPHABET_EXACT": ["YES"],
            "GENERAL_M_DONOR_OUTCOME": ["DOMINATES_OR_INCONCLUSIVE"],
        },
        "support_evidence_ids": ["general-m-donor-closure-status"],
    },
    {
        "hypothesis_id": "RESP:DONOR_INTERFACE_UNRESOLVED",
        "expected_observations": {
            "R5H_CURRENT_ALPHABET_EXACT": ["YES"],
            "FOQCS_INTERFACE_ENVELOPE": ["UNRESOLVED"],
        },
        "support_evidence_ids": ["foqcs-interface-closure-status"],
    },
    {
        "hypothesis_id": "RESP:INTERFACE_INADEQUATE",
        "expected_observations": {
            "R5H_CURRENT_ALPHABET_EXACT": ["YES"],
            "GENERAL_M_DONOR_OUTCOME": ["NONDOMINATING_OR_CLOSED"],
            "FOQCS_INTERFACE_ENVELOPE": ["OPTIMISTIC_BOUND_REGISTERED"],
            "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR": ["YES", "UNRESOLVED"],
        },
        "support_evidence_ids": ["foqcs-interface-envelope"],
    },
    {
        "hypothesis_id": "RESP:METHOD_LANGUAGE_INADEQUATE",
        "expected_observations": {
            "R5H_CURRENT_ALPHABET_EXACT": ["YES"],
            "GENERAL_M_DONOR_OUTCOME": ["NONDOMINATING_OR_CLOSED"],
            "FOQCS_INTERFACE_ENVELOPE": ["OPTIMISTIC_BOUND_REGISTERED"],
            "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR": ["NO"],
            "CURRENT_METHOD_INCREMENTAL_VALUE_ON_H4": [
                "NONE_OVER_DIRECT_CLIQUE_DONOR"
            ],
        },
        "support_evidence_ids": ["r5h-mixed-collapse", "foqcs-optimistic-envelope"],
    },
]


MAX_R6_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-q:max-r6-live",
    "claim_id": "orion-q:max-r6-native-controller",
    "description": "Native Self-ORION MAX-R6 campaign through donor closure, interface closure, and candidate-blind P10 generation.",
    "authority_ceiling": "BELOW_R6_UNTIL_PROTECTED_PROMOTION",
    "initial_phase": "N0",
    "initial_observations": {
        "R5H_CURRENT_ALPHABET_EXACT": "YES",
    },
    "protected_refs": [
        {
            "ref_id": "FRESH:R6:STRETCHED_N2_DUCC2",
            "path": "N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt",
            "blob": "6ab53f2a83c1f8ab5cc3bf4309525fb1ec7421dd",
            "released": False,
        }
    ],
    "capabilities": {
        "orion_q.donor_closure": {
            "host_capability": "SHELL",
            "payload": {
                "argv": ["python", "max_r6_donor_closure_h4_fast.py"],
                "cwd": "research/extensions/orion-q",
                "timeout": 120,
            },
            "declared_read_paths": [
                "research/extensions/orion-q/max_r6_donor_closure_h4_fast.py",
                "research/extensions/orion-q/max_r6_donor_closure_h4.py",
                "research/extensions/orion-q/max_r5h_mixed_cardinality_development.py",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": "ORIONQ_MAX_R6_DONOR_CLOSURE=",
                "required_payload_values": [
                    {
                        "path": ["authority"],
                        "equals": "NATIVE_SELECTED_DONOR_CLOSURE_EVIDENCE_ONLY__NOT_R6",
                    },
                    {"path": ["fresh_r6_subject_coefficients_accessed"], "equals": False},
                ],
                "evidence_rules": [
                    {
                        "evidence_key": "GENERAL_M_DONOR_OUTCOME",
                        "path": ["GENERAL_M_DONOR_OUTCOME"],
                        "transform": "STRING",
                    },
                    {
                        "evidence_key": "FOQCS_GENERIC_PREP_OUTCOME",
                        "path": ["FOQCS_GENERIC_PREP_OUTCOME"],
                        "transform": "STRING",
                    },
                ],
            },
            "next_phase": "N1",
        },
        "orion_q.interface_envelope": {
            "host_capability": "SHELL",
            "payload": {
                "argv": ["python", "max_r6_foqcs_interface_envelope.py"],
                "cwd": "research/extensions/orion-q",
                "timeout": 120,
            },
            "declared_read_paths": [
                "research/extensions/orion-q/max_r6_foqcs_interface_envelope.py"
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": "ORIONQ_MAX_R6_FOQCS_INTERFACE=",
                "required_payload_values": [
                    {"path": ["authority"], "equals": "INTERFACE_CANNOT_DOMINATE_EVEN_OPTIMISTIC"},
                    {"path": ["pass"], "equals": True},
                    {"path": ["fresh_r6_subject_coefficients_accessed"], "equals": False},
                ],
                "evidence_rules": [
                    {
                        "evidence_key": "FOQCS_INTERFACE_ENVELOPE",
                        "literal": "OPTIMISTIC_BOUND_REGISTERED",
                    },
                    {
                        "evidence_key": "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR",
                        "path": ["foqcs_dominates_incumbent"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "CURRENT_METHOD_INCREMENTAL_VALUE_ON_H4",
                        "path": ["current_method_incremental_value_on_h4"],
                        "transform": "STRING",
                    },
                ],
            },
            "next_phase": "N2",
        },
        "orion_q.r6_prospective_replay": {
            "host_capability": "SHELL",
            "payload": {
                "argv": ["python", "max_r6_exact_tare3_prospective_replay.py"],
                "cwd": "research/extensions/orion-q",
                "timeout": 120,
            },
            "declared_read_paths": [
                "research/extensions/orion-q/max_r6_exact_tare3_prospective_replay.py",
                "research/extensions/orion-q/max_r6_exact_tare3_prospective_primary.py",
                "research/extensions/orion-q/max_r6_exact_tare3_end_to_end_verify.py",
                "research/extensions/orion-q/max_r6_exact_tare3_joint_frame_dp.py",
                "research/extensions/orion-q/max_r6_p10_candidate_blind_frame_optimizer.py",
                "research/extensions/orion-q/max_r5h_mixed_cardinality_development.py",
                "research/extensions/orion-q/max_r4d_h2o_ducc_confirmation.py",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": "ORIONQ_MAX_R6_EXACT_TARE3_PROSPECTIVE_REPLAY=",
                "required_payload_values": [
                    {"path": ["novelty_blob_ok"], "equals": True},
                ],
                "evidence_rules": [
                    {
                        "evidence_key": "R6_EARNED",
                        "path": ["r6_earned"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "R6_PROSPECTIVE_AUTHORITY",
                        "path": ["authority"],
                        "transform": "STRING",
                    },
                    {
                        "evidence_key": "R6_PROTECTED_SUBJECT_ACCESSED",
                        "path": ["protected_stretched_n2_accessed"],
                        "transform": "BOOL_YES_NO",
                    },
                ],
            },
            "next_phase": "R6_VERDICT",
        },
        "orion_q.p10_frame": {
            "host_capability": "SHELL",
            "payload": {
                "argv": ["python", "max_r6_p10_candidate_blind_frame_optimizer.py"],
                "cwd": "research/extensions/orion-q",
                "timeout": 120,
            },
            "declared_read_paths": [
                "research/extensions/orion-q/max_r6_p10_candidate_blind_frame_optimizer.py",
                "research/extensions/orion-q/max_r5h_mixed_cardinality_development.py",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": "ORIONQ_MAX_R6_P10_FRAME=",
                "required_payload_values": [
                    {"path": ["reserved_stretched_n2_accessed"], "equals": False}
                ],
                "evidence_rules": [
                    {
                        "evidence_key": "P10_FRAME_CANDIDATE_GENERATED",
                        "path": ["candidate_generated"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "P10_FRAME_GENERATION_TERMINAL",
                        "path": ["authority"],
                        "transform": "STRING",
                    },
                ],
            },
            "next_phase": "P10_RESULT",
        },
    },
    "phases": {
        "N0": {
            "active_hard_obligations": [
                "DONOR_GENERAL_M_TARE_CLOSURE",
                "DONOR_FOQCS_GENERIC_PREP_CLOSURE",
            ],
            "responsibility_hypotheses": _N0_HYPOTHESES,
            "interface_checks": _interface_checks(),
            "revision_mechanics": _revision_mechanics(),
            "computation_actions": [
                {
                    "action_id": "COMPUTE:DONOR_CLOSURE_PACKET",
                    "kind": "VERIFY_DONOR_CLOSURE",
                    "expected_decision_value": 2.0,
                    "cost": 1.0,
                    "discharges_obligations": [
                        "DONOR_GENERAL_M_TARE_CLOSURE",
                        "DONOR_FOQCS_GENERIC_PREP_CLOSURE",
                    ],
                },
                {
                    "action_id": "COMPUTE:CURRENT_ALPHABET_REPLAY",
                    "kind": "REPLAY_CURRENT_LANGUAGE",
                    "expected_decision_value": 0.25,
                    "cost": 1.0,
                },
            ],
            "responsibility_bindings": _bindings(),
            "shadow_allowed_revision_ids": [
                "REV:SEARCH_CURRENT_ALPHABET",
                "REV:ABSORB_DONOR",
                "REV:CHANGE_INTERFACE",
            ],
            "selected_capabilities": {
                "COMPUTE:DONOR_CLOSURE_PACKET": "orion_q.donor_closure"
            },
        },
        "N1": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": _N0_HYPOTHESES,
            "interface_checks": _interface_checks(),
            "revision_mechanics": _revision_mechanics(),
            "computation_actions": [
                {
                    "action_id": "COMPUTE:FOQCS_PREP_RESOURCE_PACKET",
                    "kind": "COST_CANDIDATE_INTERFACE",
                    "expected_decision_value": 1.5,
                    "cost": 1.0,
                },
                {
                    "action_id": "COMPUTE:R5H_REPLAY",
                    "kind": "REPLAY_CURRENT_LANGUAGE",
                    "expected_decision_value": 0.1,
                    "cost": 1.0,
                },
            ],
            "responsibility_bindings": _bindings(),
            "shadow_allowed_revision_ids": [
                "REV:SEARCH_CURRENT_ALPHABET",
                "REV:ABSORB_DONOR",
            ],
            "selected_capabilities": {
                "REV:CHANGE_INTERFACE": "orion_q.interface_envelope"
            },
        },
        "N2": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": _N2_ATOMIC_HYPOTHESES,
            "interface_checks": _interface_checks(),
            "revision_mechanics": _revision_mechanics(),
            "computation_actions": [
                {
                    "action_id": "COMPUTE:FOQCS_REAL_PREP_RESOURCES",
                    "kind": "REFINE_ABSORBED_INTERFACE_COST",
                    "expected_decision_value": 0.5,
                    "cost": 1.0,
                },
                {
                    "action_id": "COMPUTE:R5H_REPLAY",
                    "kind": "REPLAY_CURRENT_LANGUAGE",
                    "expected_decision_value": 0.1,
                    "cost": 1.0,
                },
            ],
            "responsibility_bindings": _bindings(),
            "shadow_allowed_revision_ids": [
                "REV:SEARCH_CURRENT_ALPHABET",
                "REV:ABSORB_DONOR",
                "REV:CHANGE_INTERFACE",
            ],
            "selected_capabilities": {
                "REV:GROW_METHOD_LANGUAGE": "orion_q.p10_frame"
            },
        },
        "P10_RESULT": {
            "active_hard_obligations": ["R6_PROSPECTIVE_GATE_EVALUATION"],
            "responsibility_hypotheses": _N2_ATOMIC_HYPOTHESES,
            "interface_checks": _interface_checks(),
            "revision_mechanics": _revision_mechanics(),
            "computation_actions": [
                {
                    "action_id": "COMPUTE:R6_PROSPECTIVE_REPLAY",
                    "kind": "VERIFY_FROZEN_PROSPECTIVE_GATE",
                    "expected_decision_value": 2.0,
                    "cost": 1.0,
                    "discharges_obligations": ["R6_PROSPECTIVE_GATE_EVALUATION"],
                },
                {
                    "action_id": "COMPUTE:R5H_REPLAY",
                    "kind": "REPLAY_CURRENT_LANGUAGE",
                    "expected_decision_value": 0.1,
                    "cost": 1.0,
                },
            ],
            "responsibility_bindings": _bindings(),
            "shadow_allowed_revision_ids": [
                "REV:SEARCH_CURRENT_ALPHABET",
                "REV:ABSORB_DONOR",
                "REV:CHANGE_INTERFACE",
            ],
            "selected_capabilities": {
                "COMPUTE:R6_PROSPECTIVE_REPLAY": "orion_q.r6_prospective_replay"
            },
        },
        "R6_VERDICT": {
            "terminal": True,
            "terminal_name": "R6_PROSPECTIVE_VERDICT_RECORDED__NOT_SELF_AUTHORIZING",
            "active_hard_obligations": [],
        },
    },
}
